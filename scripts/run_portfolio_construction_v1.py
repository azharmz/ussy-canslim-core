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

from run_entry_timing_basis_test import load_history, simulate_variant  # noqa: E402
from run_e1_e4_static_trade_diagnostics import generate_candidates  # noqa: E402
from run_e0_static_history_candidates import s3_client  # noqa: E402

OUT = ROOT / "results" / "portfolio-construction-v1"
INITIAL_EQUITY = 100_000.0
MAX_POSITIONS = 7
ENTRY_COST_RATE = 0.001
EXIT_COST_RATE = 0.001
VARIANTS = ("X1", "X3")


def max_drawdown(equity: pd.Series):
    x = pd.to_numeric(equity, errors="coerce").dropna()
    if x.empty:
        return None
    peak = x.cummax()
    dd = x / peak - 1.0
    return float(dd.min())


def cagr(equity: pd.Series, dates: pd.Series):
    x = pd.to_numeric(equity, errors="coerce")
    d = pd.to_datetime(dates, errors="coerce")
    mask = x.notna() & d.notna()
    x, d = x[mask], d[mask]
    if len(x) < 2 or x.iloc[0] <= 0 or x.iloc[-1] <= 0:
        return None
    days = (d.iloc[-1] - d.iloc[0]).days
    if days <= 0:
        return None
    return float((x.iloc[-1] / x.iloc[0]) ** (365.25 / days) - 1.0)


def annual_returns(curve: pd.DataFrame, col: str) -> pd.DataFrame:
    x = curve[["date", col]].copy()
    x["year"] = pd.to_datetime(x["date"]).dt.year
    rows = []
    prev = INITIAL_EQUITY
    for year, g in x.groupby("year", sort=True):
        end = float(g.iloc[-1][col])
        rows.append({"year": int(year), "curve": col, "return": end / prev - 1.0})
        prev = end
    return pd.DataFrame(rows)


def prepare_trade_candidates(variant: str, candidates: pd.DataFrame, histories: dict[str, pd.DataFrame]) -> pd.DataFrame:
    trades, _ = simulate_variant(variant, candidates, histories)
    if trades.empty:
        return trades
    feat = candidates[["security_id", "date", "rs_percentile", "volume_ratio"]].copy()
    feat["security_id"] = feat["security_id"].astype(str)
    feat["date"] = pd.to_datetime(feat["date"], errors="coerce").dt.normalize()
    t = trades.copy()
    t["security_id"] = t["security_id"].astype(str)
    t["signal_date"] = pd.to_datetime(t["signal_date"], errors="coerce").dt.normalize()
    t["entry_date"] = pd.to_datetime(t["entry_date"], errors="coerce").dt.normalize()
    t["exit_date"] = pd.to_datetime(t["exit_date"], errors="coerce").dt.normalize()
    t = t.merge(
        feat,
        left_on=["security_id", "signal_date"],
        right_on=["security_id", "date"],
        how="left",
        validate="one_to_one",
    ).drop(columns=["date"])
    if t[["rs_percentile", "volume_ratio"]].isna().any().any():
        raise RuntimeError(f"Missing allocation-priority features for {variant}")
    return t


def run_portfolio(variant: str, trade_candidates: pd.DataFrame, histories: dict[str, pd.DataFrame]):
    if trade_candidates.empty:
        raise RuntimeError(f"No trade candidates for {variant}")

    all_dates = sorted(set().union(*[set(g["date"].tolist()) for g in histories.values()]))
    first_entry = trade_candidates["entry_date"].min()
    last_date = max(g["date"].max() for g in histories.values())
    dates = [d for d in all_dates if d >= first_entry and d <= last_date]

    close_maps = {
        sid: dict(zip(g["date"], g["close"].astype(float)))
        for sid, g in histories.items()
    }

    entries_by_date = {d: g.copy() for d, g in trade_candidates.groupby("entry_date")}
    cash = INITIAL_EQUITY
    prior_close_equity = INITIAL_EQUITY
    cumulative_cost = 0.0
    open_positions: dict[str, dict] = {}
    accepted_rows = []
    skip_rows = []
    curve_rows = []

    for d in dates:
        todays = entries_by_date.get(d)
        if todays is not None and len(todays):
            todays = todays.sort_values(
                ["rs_percentile", "volume_ratio", "ticker"],
                ascending=[False, False, True],
            )
            target_notional = prior_close_equity / MAX_POSITIONS
            for r in todays.itertuples(index=False):
                sid = str(r.security_id)
                if sid in open_positions:
                    skip_rows.append({"variant": variant, "security_id": sid, "ticker": r.ticker, "entry_date": d, "reason": "SKIP_ALREADY_OPEN_PORTFOLIO"})
                    continue
                if len(open_positions) >= MAX_POSITIONS:
                    skip_rows.append({"variant": variant, "security_id": sid, "ticker": r.ticker, "entry_date": d, "reason": "SKIP_CAPACITY"})
                    continue
                if cash + 1e-9 < target_notional:
                    skip_rows.append({"variant": variant, "security_id": sid, "ticker": r.ticker, "entry_date": d, "reason": "SKIP_CASH"})
                    continue

                shares = target_notional / float(r.entry_price)
                cash -= target_notional
                cumulative_cost += target_notional * ENTRY_COST_RATE
                pos = {
                    "variant": variant,
                    "security_id": sid,
                    "ticker": r.ticker,
                    "signal_date": pd.Timestamp(r.signal_date),
                    "entry_date": d,
                    "entry_price": float(r.entry_price),
                    "shares": shares,
                    "entry_notional": target_notional,
                    "exit_date": pd.Timestamp(r.exit_date),
                    "exit_price": float(r.exit_price),
                    "exit_reason": r.exit_reason,
                    "rs_percentile": float(r.rs_percentile),
                    "volume_ratio": float(r.volume_ratio),
                }
                open_positions[sid] = pos
                accepted_rows.append(pos.copy())

        # Entries at the Open occur before intraday exits; exit proceeds cannot fund same-day morning entries.
        exiting = [sid for sid, p in open_positions.items() if p["exit_date"] == d]
        for sid in exiting:
            p = open_positions.pop(sid)
            proceeds = p["shares"] * p["exit_price"]
            cash += proceeds
            cumulative_cost += proceeds * EXIT_COST_RATE

        market_value = 0.0
        for sid, p in open_positions.items():
            close = close_maps.get(sid, {}).get(d)
            if close is None:
                # US-listed series should share the session calendar; defensively use last close <= d.
                g = histories[sid]
                prev = g[g["date"] <= d]
                if prev.empty:
                    raise RuntimeError(f"No mark for {sid} on {d}")
                close = float(prev.iloc[-1]["close"])
            market_value += p["shares"] * float(close)

        gross_equity = cash + market_value
        cost_equity = gross_equity - cumulative_cost
        curve_rows.append({
            "variant": variant,
            "date": d,
            "cash": cash,
            "market_value": market_value,
            "gross_equity": gross_equity,
            "cost20bp_rt_equity": cost_equity,
            "cumulative_cost": cumulative_cost,
            "position_count": len(open_positions),
            "gross_exposure": market_value / gross_equity if gross_equity > 0 else np.nan,
        })
        prior_close_equity = gross_equity

    curve = pd.DataFrame(curve_rows)
    accepted = pd.DataFrame(accepted_rows)
    skipped = pd.DataFrame(skip_rows)

    # Attach realized contribution for accepted trades; censored/open individual trades use their marked final close in the frozen simulator.
    if not accepted.empty:
        accepted["exit_notional"] = accepted["shares"] * accepted["exit_price"]
        accepted["gross_pnl"] = accepted["exit_notional"] - accepted["entry_notional"]
        contrib = accepted.groupby("ticker")["gross_pnl"].sum().abs().sort_values(ascending=False)
        total_abs = float(contrib.sum())
        top1 = float(contrib.iloc[0] / total_abs) if total_abs > 0 else None
        top5 = float(contrib.head(5).sum() / total_abs) if total_abs > 0 else None
    else:
        top1 = top5 = None

    summary = {
        "variant": variant,
        "candidate_trade_count": int(len(trade_candidates)),
        "portfolio_entry_count": int(len(accepted)),
        "capacity_skip_count": int((skipped.get("reason") == "SKIP_CAPACITY").sum()) if len(skipped) else 0,
        "cash_skip_count": int((skipped.get("reason") == "SKIP_CASH").sum()) if len(skipped) else 0,
        "already_open_skip_count": int((skipped.get("reason") == "SKIP_ALREADY_OPEN_PORTFOLIO").sum()) if len(skipped) else 0,
        "gross_total_return": float(curve.iloc[-1]["gross_equity"] / INITIAL_EQUITY - 1.0),
        "gross_cagr": cagr(curve["gross_equity"], curve["date"]),
        "gross_max_drawdown": max_drawdown(curve["gross_equity"]),
        "cost20bp_rt_total_return": float(curve.iloc[-1]["cost20bp_rt_equity"] / INITIAL_EQUITY - 1.0),
        "cost20bp_rt_cagr": cagr(curve["cost20bp_rt_equity"], curve["date"]),
        "cost20bp_rt_max_drawdown": max_drawdown(curve["cost20bp_rt_equity"]),
        "median_position_count": float(curve["position_count"].median()),
        "max_position_count": int(curve["position_count"].max()),
        "median_gross_exposure": float(curve["gross_exposure"].median()),
        "top1_abs_pnl_contribution_share": top1,
        "top5_abs_pnl_contribution_share": top5,
        "first_date": str(pd.Timestamp(curve.iloc[0]["date"]).date()),
        "last_date": str(pd.Timestamp(curve.iloc[-1]["date"]).date()),
    }
    return accepted, skipped, curve, summary


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = s3_client()
    bucket = os.environ["R2_BUCKET_NAME"]
    candidates, membership, spy_pointer = generate_candidates(s3, bucket)
    candidates = candidates.copy()
    candidates["security_id"] = candidates["security_id"].astype(str)
    candidates["date"] = pd.to_datetime(candidates["date"], errors="coerce").dt.normalize()

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

    summaries = []
    accepted_all = []
    skipped_all = []
    curves_all = []
    annual_all = []

    for variant in VARIANTS:
        trade_candidates = prepare_trade_candidates(variant, candidates, histories)
        accepted, skipped, curve, summary = run_portfolio(variant, trade_candidates, histories)
        summaries.append(summary)
        accepted_all.append(accepted)
        skipped_all.append(skipped)
        curves_all.append(curve)
        annual_all.append(annual_returns(curve, "gross_equity").assign(variant=variant))
        annual_all.append(annual_returns(curve, "cost20bp_rt_equity").assign(variant=variant))

    pd.concat(accepted_all, ignore_index=True).to_csv(OUT / "portfolio_trades.csv", index=False)
    pd.concat(skipped_all, ignore_index=True).to_csv(OUT / "portfolio_skips.csv", index=False)
    pd.concat(curves_all, ignore_index=True).to_csv(OUT / "equity_curves.csv", index=False)
    pd.concat(annual_all, ignore_index=True).to_csv(OUT / "annual_returns.csv", index=False)
    pd.DataFrame(summaries).to_csv(OUT / "portfolio_summary.csv", index=False)

    summary = {
        "experiment": "PORTFOLIO_CONSTRUCTION_V1",
        "methodology": "docs/methodology/portfolio-construction-v1.md",
        "methodology_frozen_before_outcome_review": True,
        "research_universe": "CURRENT_COMPLIANT_UNIVERSE_FROZEN_AT_2026_08_28",
        "candidate_count": int(len(candidates)),
        "candidate_symbols": int(candidates["security_id"].nunique()),
        "initial_equity": INITIAL_EQUITY,
        "max_positions": MAX_POSITIONS,
        "target_notional_fraction_of_prior_close_equity": 1.0 / MAX_POSITIONS,
        "approx_initial_stop_risk_fraction": 0.01,
        "entry_priority": ["rs_percentile DESC", "volume_ratio DESC", "ticker ASC"],
        "entry_before_same_day_exit": True,
        "gross_primary": True,
        "cost_sensitivity": {"entry_bps": 10, "exit_bps": 10, "allocations_identical_to_gross": True},
        "variants": summaries,
        "c_filter_applied": False,
        "a_filter_applied": False,
        "exhaustion_filter_applied": False,
        "spy_parquet_key": spy_pointer.get("parquet_key"),
        "spy_sha256": spy_pointer.get("sha256"),
        "warning": "Portfolio metrics apply to frozen X1/X3 BASE tracks on the frozen current-compliant research universe; they are not literal IBD/O'Neil replication and remain subject to holdout/forward validation.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))
    (OUT / "membership_snapshot.json").write_text(json.dumps(membership, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
