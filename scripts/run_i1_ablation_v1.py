from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

from run_entry_timing_basis_test import load_history, simulate_variant  # noqa: E402
from run_e1_e4_static_trade_diagnostics import generate_candidates  # noqa: E402
from run_e0_static_history_candidates import s3_client  # noqa: E402
from run_fundamental_ablation_v1 import profit_factor, pf_ex_top10  # noqa: E402
from run_portfolio_construction_v1 import prepare_trade_candidates, run_portfolio  # noqa: E402

OUT = ROOT / "results" / "i1-ablation-v1"
PINNED_SPONSORSHIP_PUBLISH_RUN = "34663714292"
VARIANTS = ("X1", "X3")
FILTERS = ("BASE_ALL", "I_EVALUABLE", "I_PASS")


def trade_summary(variant: str, filt: str, eligible: pd.DataFrame, trades: pd.DataFrame) -> dict:
    realized = pd.to_numeric(trades.get("realized_return"), errors="coerce").dropna() if len(trades) else pd.Series(dtype=float)
    return {
        "variant": variant,
        "filter": filt,
        "eligible_candidate_count": int(len(eligible)),
        "eligible_security_count": int(eligible["security_id"].nunique()) if len(eligible) else 0,
        "entry_count": int(len(trades)),
        "realized_trade_count": int(len(realized)),
        "descriptive_trade_level_pf": profit_factor(realized),
        "pf_ex_top10": pf_ex_top10(realized),
        "median_realized_return": float(realized.median()) if len(realized) else None,
        "target_rate": float(trades["exit_reason"].str.contains("TARGET").mean()) if len(trades) else None,
        "stop_rate": float(trades["exit_reason"].str.contains("STOP").mean()) if len(trades) else None,
    }


def main(labels_csv: Path, attachment_summary_json: Path) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    attachment = json.loads(attachment_summary_json.read_text(encoding="utf-8"))
    if attachment.get("strategy_returns_inspected") is not False:
        raise RuntimeError("Attachment evidence must be data-only")
    if int(attachment.get("critical_future_availability_violations", -1)) != 0:
        raise RuntimeError("Attachment leakage invariant failed")
    manifest_key = str(attachment.get("sponsorship_manifest_key", ""))
    if f"run-{PINNED_SPONSORSHIP_PUBLISH_RUN}/manifest.json" not in manifest_key:
        raise RuntimeError(f"Sponsorship snapshot drift: {manifest_key}")

    labels = pd.read_csv(labels_csv, dtype={"security_id": str})
    labels["signal_date"] = pd.to_datetime(labels["signal_date"], errors="coerce").dt.normalize()
    if len(labels) != int(attachment["candidate_count"]):
        raise RuntimeError("Label/summary candidate count mismatch")

    s3 = s3_client()
    bucket = os.environ["R2_BUCKET_NAME"]
    candidates, membership, spy_pointer = generate_candidates(s3, bucket)
    candidates = candidates.copy()
    candidates["security_id"] = candidates["security_id"].astype(str)
    candidates["date"] = pd.to_datetime(candidates["date"], errors="coerce").dt.normalize()

    lab = labels[["security_id", "signal_date", "I_v1_label"]].copy()
    merged = candidates.merge(
        lab,
        left_on=["security_id", "date"],
        right_on=["security_id", "signal_date"],
        how="left",
        validate="one_to_one",
    )
    if merged["I_v1_label"].isna().any():
        raise RuntimeError(f"Missing I attachment for {int(merged['I_v1_label'].isna().sum())} candidates")

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

    trade_summaries = []
    portfolio_summaries = []
    all_trades = []
    portfolio_trades = []
    portfolio_skips = []
    equity_curves = []

    for filt in FILTERS:
        if filt == "BASE_ALL":
            eligible = merged.copy()
        elif filt == "I_EVALUABLE":
            eligible = merged[merged["I_v1_label"].isin(["PASS", "FAIL"])].copy()
        else:
            eligible = merged[merged["I_v1_label"].eq("PASS")].copy()

        sim_candidates = eligible[candidates.columns].copy()
        for variant in VARIANTS:
            trades, _ = simulate_variant(variant, sim_candidates, histories)
            if len(trades):
                trades = trades.copy()
                trades["filter"] = filt
                trades["variant_filter"] = f"{variant}_{filt}"
            trade_summaries.append(trade_summary(variant, filt, eligible, trades))
            all_trades.append(trades)

            tc = prepare_trade_candidates(variant, sim_candidates, histories)
            if tc.empty:
                portfolio_summaries.append({"variant": variant, "filter": filt, "error": "NO_TRADE_CANDIDATES"})
                continue
            accepted, skipped, curve, psummary = run_portfolio(variant, tc, histories)
            psummary = dict(psummary)
            psummary["filter"] = filt
            portfolio_summaries.append(psummary)
            for df in (accepted, skipped, curve):
                if len(df):
                    df["filter"] = filt
            portfolio_trades.append(accepted)
            portfolio_skips.append(skipped)
            equity_curves.append(curve)

    pd.DataFrame(trade_summaries).to_csv(OUT / "trade_summary.csv", index=False)
    pd.DataFrame(portfolio_summaries).to_csv(OUT / "portfolio_summary.csv", index=False)
    if all_trades:
        pd.concat(all_trades, ignore_index=True).to_csv(OUT / "trades.csv", index=False)
    if portfolio_trades:
        pd.concat(portfolio_trades, ignore_index=True).to_csv(OUT / "portfolio_trades.csv", index=False)
    if portfolio_skips:
        pd.concat(portfolio_skips, ignore_index=True).to_csv(OUT / "portfolio_skips.csv", index=False)
    if equity_curves:
        pd.concat(equity_curves, ignore_index=True).to_csv(OUT / "equity_curves.csv", index=False)

    summary = {
        "experiment": "I1_ABLATION_V1",
        "evidence_class": "RETROSPECTIVE_HISTORICAL_NOT_OOS",
        "methodology": "docs/methodology/institutional-sponsorship-growth-v1.md",
        "sponsorship_manifest_key": manifest_key,
        "attachment_label_distribution": attachment.get("label_distribution"),
        "candidate_count": int(len(merged)),
        "i_evaluable_candidate_count": int(merged["I_v1_label"].isin(["PASS", "FAIL"]).sum()),
        "i_pass_candidate_count": int(merged["I_v1_label"].eq("PASS").sum()),
        "i_fail_candidate_count": int(merged["I_v1_label"].eq("FAIL").sum()),
        "i_not_evaluable_candidate_count": int(merged["I_v1_label"].eq("NOT_EVALUABLE").sum()),
        "trade_level": trade_summaries,
        "portfolio": portfolio_summaries,
        "rule_changed_after_outcome_review": False,
        "threshold_search_performed": False,
        "fwd1_modified": False,
        "spy_parquet_key": spy_pointer.get("parquet_key"),
        "spy_sha256": spy_pointer.get("sha256"),
        "comparison_guardrail": "I_PASS must be judged primarily against I_EVALUABLE, which uses the same I-data support. BASE_ALL is context only because SEC 13F history starts in 2013.",
        "guardrail": "Historical I-v1 ablation is descriptive retrospective evidence only. It cannot modify frozen FWD1 or justify production promotion by itself.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")
    (OUT / "attachment_summary.json").write_text(json.dumps(attachment, indent=2, sort_keys=True, default=str), encoding="utf-8")
    (OUT / "membership_snapshot.json").write_text(json.dumps(membership, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--labels", type=Path, required=True)
    p.add_argument("--attachment-summary", type=Path, required=True)
    a = p.parse_args()
    main(a.labels, a.attachment_summary)
