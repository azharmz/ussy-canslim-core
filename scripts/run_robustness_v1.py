from __future__ import annotations

import io
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

from run_e0_static_history_candidates import read_bytes, s3_client, verify  # noqa: E402
from run_e1_e4_static_trade_diagnostics import generate_candidates  # noqa: E402
from run_entry_timing_basis_test import load_history  # noqa: E402
from run_portfolio_construction_v1 import (  # noqa: E402
    INITIAL_EQUITY,
    cagr,
    max_drawdown,
    prepare_trade_candidates,
    run_portfolio,
)

OUT = ROOT / "results" / "robustness-v1"
VARIANTS = ("X1", "X3")
COST_COLS = ("gross_equity", "cost20bp_rt_equity")
PORT1_VALIDATION_RUN = "34485765478"
EXIT_COST_RATE = 0.001


def profit_factor(values: pd.Series):
    x = pd.to_numeric(values, errors="coerce").dropna()
    gp = float(x[x > 0].sum())
    gl = float(-x[x < 0].sum())
    return gp / gl if gl > 0 else None


def apply_frozen_censored_accounting(
    variant: str,
    accepted: pd.DataFrame,
    curve: pd.DataFrame,
    port_summary: dict,
) -> tuple[pd.DataFrame, dict, dict]:
    """Mirror the validated PORT1 finalizer in memory for ROB1 diagnostics.

    CENSORED_OPEN positions at the portfolio boundary are marks, not liquidations.
    Any mid-sample censor is a hard failure because allocation would need replay.
    """
    curve = curve.copy()
    curve["date"] = pd.to_datetime(curve["date"], errors="coerce").dt.normalize()
    accepted = accepted.copy()
    accepted["exit_date"] = pd.to_datetime(accepted["exit_date"], errors="coerce").dt.normalize()
    last_date = curve["date"].max()
    censored = accepted[accepted["exit_reason"].eq("CENSORED_OPEN")].copy()
    bad = censored[censored["exit_date"] != last_date]
    if len(bad):
        raise RuntimeError(
            f"{variant}: {len(bad)} censored positions end before portfolio sample boundary; "
            "ROB1 must not reinterpret frozen PORT1 allocation"
        )

    final_mask = curve["date"].eq(last_date)
    if int(final_mask.sum()) != 1:
        raise RuntimeError(f"{variant}: expected exactly one final portfolio curve row")

    phantom_exit_cost = 0.0
    if len(censored):
        marked_value = float((censored["shares"] * censored["exit_price"]).sum())
        phantom_exit_cost = marked_value * EXIT_COST_RATE
        curve.loc[final_mask, "cash"] -= marked_value
        curve.loc[final_mask, "market_value"] += marked_value
        curve.loc[final_mask, "cumulative_cost"] -= phantom_exit_cost
        curve.loc[final_mask, "cost20bp_rt_equity"] += phantom_exit_cost
        curve.loc[final_mask, "position_count"] += len(censored)
        gross_equity = float(curve.loc[final_mask, "gross_equity"].iloc[0])
        curve.loc[final_mask, "gross_exposure"] = (
            float(curve.loc[final_mask, "market_value"].iloc[0]) / gross_equity
            if gross_equity > 0 else np.nan
        )

    corrected = dict(port_summary)
    final = curve.loc[final_mask].iloc[0]
    corrected["cost20bp_rt_total_return"] = float(final["cost20bp_rt_equity"] / INITIAL_EQUITY - 1.0)
    corrected["cost20bp_rt_cagr"] = cagr(curve["cost20bp_rt_equity"], curve["date"])
    corrected["cost20bp_rt_max_drawdown"] = max_drawdown(curve["cost20bp_rt_equity"])
    corrected["final_censored_position_count"] = int(len(censored))
    corrected["phantom_exit_cost_removed"] = float(phantom_exit_cost)

    audit = {
        "variant": variant,
        "portfolio_last_date": str(last_date.date()),
        "censored_positions": int(len(censored)),
        "mid_sample_censored_positions": int(len(bad)),
        "phantom_exit_cost_removed": float(phantom_exit_cost),
        "censored_treated_as_mark_to_market_not_exit": True,
    }
    return curve, corrected, audit


def trade_quality(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "count": 0,
            "realized_count": 0,
            "pf": None,
            "median_realized_return": None,
            "median_pre_exit_mfe": None,
            "median_pre_exit_mae": None,
            "target_rate": None,
            "stop_rate": None,
            "censored_rate": None,
        }
    realized = pd.to_numeric(df["realized_return"], errors="coerce")
    reasons = df["exit_reason"].astype(str)
    return {
        "count": int(len(df)),
        "realized_count": int(realized.notna().sum()),
        "pf": profit_factor(realized),
        "median_realized_return": float(realized.dropna().median()) if realized.notna().any() else None,
        "median_pre_exit_mfe": float(pd.to_numeric(df["pre_exit_mfe"], errors="coerce").median()),
        "median_pre_exit_mae": float(pd.to_numeric(df["pre_exit_mae"], errors="coerce").median()),
        "target_rate": float(reasons.str.contains("TARGET").mean()),
        "stop_rate": float(reasons.str.contains("STOP").mean()),
        "censored_rate": float(reasons.eq("CENSORED_OPEN").mean()),
    }


def split_five_equal_calendar_blocks(start: pd.Timestamp, end: pd.Timestamp) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    start = pd.Timestamp(start).normalize()
    end = pd.Timestamp(end).normalize()
    total_days = (end - start).days
    edges = [start + pd.Timedelta(days=round(total_days * i / 5)) for i in range(6)]
    edges[0], edges[-1] = start, end
    return [(edges[i], edges[i + 1]) for i in range(5)]


def block_metrics(curve: pd.DataFrame, variant: str) -> list[dict]:
    x = curve.sort_values("date").copy()
    x["date"] = pd.to_datetime(x["date"]).dt.normalize()
    blocks = split_five_equal_calendar_blocks(x["date"].min(), x["date"].max())
    rows = []
    for i, (lo, hi) in enumerate(blocks, start=1):
        start_rows = x[x["date"] <= lo]
        end_rows = x[x["date"] <= hi]
        if start_rows.empty or end_rows.empty:
            continue
        start_row = start_rows.iloc[-1]
        end_row = end_rows.iloc[-1]
        block_curve = x[(x["date"] >= start_row["date"]) & (x["date"] <= end_row["date"])].copy()
        for col in COST_COLS:
            start_eq = float(start_row[col])
            end_eq = float(end_row[col])
            rows.append({
                "variant": variant,
                "block": i,
                "curve": col,
                "start": str(pd.Timestamp(start_row["date"]).date()),
                "end": str(pd.Timestamp(end_row["date"]).date()),
                "total_return": end_eq / start_eq - 1.0 if start_eq > 0 else None,
                "cagr": cagr(block_curve[col], block_curve["date"]),
                "max_drawdown": max_drawdown(block_curve[col]),
            })
    return rows


def annual_metrics(curve: pd.DataFrame, variant: str) -> list[dict]:
    x = curve.copy()
    x["date"] = pd.to_datetime(x["date"])
    x["year"] = x["date"].dt.year
    rows = []
    for col in COST_COLS:
        annual = []
        prev = None
        for _, g in x.groupby("year", sort=True):
            end = float(g.iloc[-1][col])
            if prev is None:
                start = float(g.iloc[0][col])
                ret = end / start - 1.0 if start > 0 else np.nan
            else:
                ret = end / prev - 1.0 if prev > 0 else np.nan
            annual.append(ret)
            prev = end
        a = pd.Series(annual, dtype=float).dropna()
        rows.append({
            "variant": variant,
            "curve": col,
            "years": int(len(a)),
            "positive_years": int((a > 0).sum()),
            "negative_years": int((a < 0).sum()),
            "median_annual_return": float(a.median()) if len(a) else None,
            "worst_annual_return": float(a.min()) if len(a) else None,
            "best_annual_return": float(a.max()) if len(a) else None,
        })
    return rows


def spy_metrics(s3, bucket: str, spy_pointer: dict, first: pd.Timestamp, last: pd.Timestamp) -> dict:
    payload = read_bytes(s3, bucket, spy_pointer["parquet_key"])
    verify(payload, spy_pointer.get("sha256"), "SPY")
    spy = pd.read_parquet(io.BytesIO(payload)).copy()
    spy["date"] = pd.to_datetime(spy["date"], errors="coerce").dt.normalize()
    spy = spy.dropna(subset=["date", "close"]).drop_duplicates("date", keep="last").sort_values("date")
    x = spy[(spy["date"] >= pd.Timestamp(first)) & (spy["date"] <= pd.Timestamp(last))].copy()
    if len(x) < 2:
        raise RuntimeError("Insufficient SPY history for benchmark context")
    eq = pd.to_numeric(x["close"], errors="coerce") / float(x.iloc[0]["close"]) * INITIAL_EQUITY
    return {
        "benchmark": "SPY_PRICE_ONLY",
        "first_date": str(x.iloc[0]["date"].date()),
        "last_date": str(x.iloc[-1]["date"].date()),
        "total_return": float(x.iloc[-1]["close"] / x.iloc[0]["close"] - 1.0),
        "cagr": cagr(eq, x["date"]),
        "max_drawdown": max_drawdown(eq),
        "dividends_included": False,
    }


def key_frame(df: pd.DataFrame) -> pd.DataFrame:
    k = df[["security_id", "signal_date", "entry_date"]].copy()
    k["security_id"] = k["security_id"].astype(str)
    k["signal_date"] = pd.to_datetime(k["signal_date"]).dt.normalize()
    k["entry_date"] = pd.to_datetime(k["entry_date"]).dt.normalize()
    return k.drop_duplicates()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = s3_client()
    bucket = os.environ["R2_BUCKET_NAME"]
    candidates, membership, spy_pointer = generate_candidates(s3, bucket)
    candidates = candidates.copy()
    candidates["security_id"] = candidates["security_id"].astype(str)

    histories = {}
    failures = []
    ids = [str(x) for x in candidates["security_id"].unique()]
    with ThreadPoolExecutor(max_workers=16) as pool:
        futs = {pool.submit(load_history, s3, bucket, sid): sid for sid in ids}
        for fut in as_completed(futs):
            sid = futs[fut]
            try:
                histories[sid] = fut.result()
            except Exception as exc:
                failures.append({"security_id": sid, "error": str(exc)[:300]})
    if failures:
        raise RuntimeError(f"History failures: {failures[:5]}")

    variant_summaries = []
    opportunity_rows = []
    block_rows = []
    annual_rows = []
    benchmark_rows = []
    accepted_quality_rows = []
    censored_audits = []

    for variant in VARIANTS:
        trade_candidates = prepare_trade_candidates(variant, candidates, histories)
        accepted, skipped, curve, raw_port_summary = run_portfolio(variant, trade_candidates, histories)
        curve, port_summary, censor_audit = apply_frozen_censored_accounting(
            variant, accepted, curve, raw_port_summary
        )
        censored_audits.append(censor_audit)

        tc = trade_candidates.copy()
        tc["security_id"] = tc["security_id"].astype(str)
        tc["signal_date"] = pd.to_datetime(tc["signal_date"]).dt.normalize()
        tc["entry_date"] = pd.to_datetime(tc["entry_date"]).dt.normalize()
        ak = key_frame(accepted)
        merged = tc.merge(ak.assign(portfolio_accepted=True), on=["security_id", "signal_date", "entry_date"], how="left")
        merged["portfolio_accepted"] = merged["portfolio_accepted"].fillna(False).astype(bool)

        aq = trade_quality(merged[merged["portfolio_accepted"]])
        nq = trade_quality(merged[~merged["portfolio_accepted"]])
        for label, q in (("ACCEPTED", aq), ("NOT_ACCEPTED_CAPITAL_CONSTRAINT", nq)):
            opportunity_rows.append({"variant": variant, "group": label, **q})
        accepted_quality_rows.append({"variant": variant, **aq})

        block_rows.extend(block_metrics(curve, variant))
        annual_rows.extend(annual_metrics(curve, variant))
        bench = spy_metrics(s3, bucket, spy_pointer, curve["date"].min(), curve["date"].max())
        benchmark_rows.append({"variant": variant, **bench})

        gross_cagr = float(port_summary["gross_cagr"])
        variant_summaries.append({
            **port_summary,
            "accepted_trade_quality": aq,
            "not_accepted_trade_quality": nq,
            "spy_price_only": bench,
            "gross_cagr_minus_spy_price_cagr": gross_cagr - float(bench["cagr"]),
        })

    pd.DataFrame(opportunity_rows).to_csv(OUT / "opportunity_cost.csv", index=False)
    pd.DataFrame(block_rows).to_csv(OUT / "calendar_blocks.csv", index=False)
    pd.DataFrame(annual_rows).to_csv(OUT / "annual_robustness.csv", index=False)
    pd.DataFrame(benchmark_rows).to_csv(OUT / "benchmark_context.csv", index=False)
    pd.DataFrame(accepted_quality_rows).to_csv(OUT / "accepted_trade_quality.csv", index=False)
    pd.DataFrame(censored_audits).to_csv(OUT / "censored_accounting_audit.csv", index=False)

    summary = {
        "experiment": "ROBUSTNESS_V1",
        "methodology": "docs/methodology/robustness-v1.md",
        "methodology_frozen_before_outcome_review": True,
        "port1_validation_run": PORT1_VALIDATION_RUN,
        "research_universe": "CURRENT_COMPLIANT_UNIVERSE_FROZEN_AT_2026_08_28",
        "candidate_count": int(len(candidates)),
        "candidate_symbols": int(candidates["security_id"].nunique()),
        "historical_split_is_true_oos": False,
        "forward_validation_start_after": "2026-09-09",
        "production_gate": {"minimum_calendar_months": 12, "minimum_closed_x3_portfolio_trades": 50},
        "censored_accounting_matches_validated_port1": True,
        "censored_accounting_audit": censored_audits,
        "variants": variant_summaries,
        "spy_parquet_key": spy_pointer.get("parquet_key"),
        "spy_sha256": spy_pointer.get("sha256"),
        "guardrail": "Historical ROB1 is robustness evidence only. Do not call a post-hoc historical split OOS; do not change frozen X3/PORT1 rules from these diagnostics.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))
    (OUT / "membership_snapshot.json").write_text(json.dumps(membership, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
