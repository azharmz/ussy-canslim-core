from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

from run_entry_timing_basis_test import load_history, simulate_variant  # noqa: E402
from run_e1_e4_static_trade_diagnostics import generate_candidates  # noqa: E402
from run_e0_static_history_candidates import s3_client  # noqa: E402
import run_historical_ca_attachment as ca_hist  # noqa: E402

OUT = ROOT / "results" / "fundamental-ablation-v1"
CA_OUT = ROOT / "results" / "historical-ca-attachment-v1"
PINNED_FUNDAMENTALS_SOURCE_RUN_ID = "34470910341"
VARIANTS = ("X1", "X3")
FILTERS = ("BASE", "C", "CA")


def profit_factor(values: pd.Series):
    x = pd.to_numeric(values, errors="coerce").dropna()
    gp = float(x[x > 0].sum())
    gl = float(-x[x < 0].sum())
    return gp / gl if gl > 0 else None


def pf_ex_top10(values: pd.Series):
    x = pd.to_numeric(values, errors="coerce").dropna().sort_values(ascending=False)
    if len(x) > 10:
        x = x.iloc[10:]
    else:
        x = x.iloc[0:0]
    return profit_factor(x) if len(x) else None


def summarize_trades(variant: str, filt: str, eligible: pd.DataFrame, trades: pd.DataFrame) -> dict:
    realized = pd.to_numeric(trades.get("realized_return"), errors="coerce").dropna() if len(trades) else pd.Series(dtype=float)
    ticker_counts = trades["ticker"].value_counts() if len(trades) else pd.Series(dtype=int)
    return {
        "variant": variant,
        "filter": filt,
        "eligible_candidate_count": int(len(eligible)),
        "eligible_security_count": int(eligible["security_id"].nunique()) if len(eligible) else 0,
        "entry_count": int(len(trades)),
        "entry_rate_vs_eligible": float(len(trades) / len(eligible)) if len(eligible) else None,
        "realized_trade_count": int(len(realized)),
        "descriptive_trade_level_pf": profit_factor(realized),
        "pf_ex_top10": pf_ex_top10(realized),
        "median_realized_return": float(realized.median()) if len(realized) else None,
        "target_rate": float(trades["exit_reason"].str.contains("TARGET").mean()) if len(trades) else None,
        "stop_rate": float(trades["exit_reason"].str.contains("STOP").mean()) if len(trades) else None,
        "top_symbol": str(ticker_counts.index[0]) if len(ticker_counts) else None,
        "top_symbol_trade_share": float(ticker_counts.iloc[0] / len(trades)) if len(trades) else None,
        "top5_symbol_trade_share": float(ticker_counts.head(5).sum() / len(trades)) if len(trades) else None,
    }


def subperiod_table(trades: pd.DataFrame, variant: str, filt: str, edges: list[pd.Timestamp]) -> list[dict]:
    rows = []
    if not edges:
        return rows
    for i in range(len(edges) - 1):
        lo, hi = edges[i], edges[i + 1]
        if i == len(edges) - 2:
            g = trades[(trades["signal_date"] >= lo) & (trades["signal_date"] <= hi)]
        else:
            g = trades[(trades["signal_date"] >= lo) & (trades["signal_date"] < hi)]
        r = pd.to_numeric(g.get("realized_return"), errors="coerce").dropna() if len(g) else pd.Series(dtype=float)
        rows.append({
            "variant": variant,
            "filter": filt,
            "subperiod": i + 1,
            "start": str(lo.date()),
            "end": str(hi.date()),
            "trade_count": int(len(g)),
            "pf": profit_factor(r),
            "pf_ex_top10": pf_ex_top10(r),
        })
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    # Rebuild the exact historical C/A attachment using the frozen consumer logic.
    # Abort if fundamentals/current.json has moved away from the snapshot validated in CA-HIST v1.
    ca_hist.main()
    ca_summary = json.loads((CA_OUT / "summary.json").read_text())
    source_run = str(ca_summary.get("fundamentals_source_run_id"))
    if source_run != PINNED_FUNDAMENTALS_SOURCE_RUN_ID:
        raise RuntimeError(
            f"Fundamentals snapshot drift: expected source run {PINNED_FUNDAMENTALS_SOURCE_RUN_ID}, got {source_run}. "
            "Do not run ablation on an unvalidated attachment."
        )
    if int(ca_summary.get("critical_future_accepted_at_violations", -1)) != 0:
        raise RuntimeError("CA-HIST leakage invariant failed")
    if int(ca_summary.get("duplicate_candidate_attachment_rows", -1)) != 0:
        raise RuntimeError("CA-HIST duplicate invariant failed")

    labels = pd.read_csv(CA_OUT / "candidate_ca_labels.csv", dtype={"security_id": str})
    labels["signal_date"] = pd.to_datetime(labels["signal_date"], errors="coerce").dt.normalize()

    s3 = s3_client()
    bucket = os.environ["R2_BUCKET_NAME"]
    candidates, membership, spy_pointer = generate_candidates(s3, bucket)
    candidates = candidates.copy()
    candidates["security_id"] = candidates["security_id"].astype(str)
    candidates["date"] = pd.to_datetime(candidates["date"], errors="coerce").dt.normalize()

    lab = labels[["security_id", "signal_date", "c_state", "a_state", "ca_state"]].copy()
    merged = candidates.merge(
        lab,
        left_on=["security_id", "date"],
        right_on=["security_id", "signal_date"],
        how="left",
        validate="one_to_one",
    )
    if merged["c_state"].isna().any():
        raise RuntimeError(f"Missing CA attachment for {int(merged['c_state'].isna().sum())} candidates")

    histories = {}
    for sid in merged["security_id"].unique():
        histories[str(sid)] = load_history(s3, bucket, str(sid))

    dates = merged["date"].sort_values()
    quantiles = dates.quantile([0.0, 0.2, 0.4, 0.6, 0.8, 1.0]).drop_duplicates().tolist()
    edges = [pd.Timestamp(x).normalize() for x in quantiles]

    summaries = []
    subperiods = []
    all_trades = []
    all_events = []

    for filt in FILTERS:
        if filt == "BASE":
            eligible = merged.copy()
        elif filt == "C":
            eligible = merged[merged["c_state"].eq("PASS")].copy()
        else:
            eligible = merged[merged["ca_state"].eq("PASS")].copy()

        sim_candidates = eligible[candidates.columns].copy()
        for variant in VARIANTS:
            trades, events = simulate_variant(variant, sim_candidates, histories)
            if len(trades):
                trades["filter"] = filt
            if len(events):
                events["filter"] = filt
            summaries.append(summarize_trades(variant, filt, eligible, trades))
            subperiods.extend(subperiod_table(trades, variant, filt, edges))
            all_trades.append(trades)
            all_events.append(events)

    summary_df = pd.DataFrame(summaries)
    subperiod_df = pd.DataFrame(subperiods)
    trades_all = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    events_all = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()

    summary_df.to_csv(OUT / "ablation_summary.csv", index=False)
    subperiod_df.to_csv(OUT / "subperiod_summary.csv", index=False)
    trades_all.to_csv(OUT / "trades.csv", index=False)
    events_all.to_csv(OUT / "entry_events.csv", index=False)
    (OUT / "ca_hist_summary.json").write_text(json.dumps(ca_summary, indent=2, sort_keys=True, default=str))
    (OUT / "membership_snapshot.json").write_text(json.dumps(membership, indent=2, sort_keys=True))

    summary = {
        "experiment": "FUNDAMENTAL_ABLATION_V1",
        "research_universe": "CURRENT_COMPLIANT_UNIVERSE_FROZEN_AT_2026_08_28",
        "fundamentals_source_run_id": source_run,
        "ca_hist_validation_run": "34479060107",
        "candidate_count": int(len(merged)),
        "filters": {
            "BASE": int(len(merged)),
            "C": int(merged["c_state"].eq("PASS").sum()),
            "CA": int(merged["ca_state"].eq("PASS").sum()),
        },
        "variants": summaries,
        "portfolio_metrics_computed": False,
        "exhaustion_filter_applied": False,
        "thresholds_changed": False,
        "interpretation_guardrail": "Trade-level PF is descriptive ablation evidence, not portfolio return. C+A has extremely low event count and cannot support a strategy claim by itself.",
        "spy_parquet_key": spy_pointer.get("parquet_key"),
        "spy_sha256": spy_pointer.get("sha256"),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
