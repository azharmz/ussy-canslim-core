from __future__ import annotations

import hashlib
import io
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from run_e0_static_history_candidates import read_bytes, s3_client, verify  # noqa: E402
from run_e1_e4_static_trade_diagnostics import generate_candidates  # noqa: E402
from run_entry_timing_basis_test import load_history  # noqa: E402
from run_portfolio_construction_v1 import prepare_trade_candidates, run_portfolio  # noqa: E402
from run_robustness_v1 import apply_frozen_censored_accounting  # noqa: E402

OUT = ROOT / "results" / "forward-validation-v1"
FORWARD_BOUNDARY = pd.Timestamp("2026-09-09")
FORWARD_START = pd.Timestamp("2026-09-10")
MIN_MONTHS = 12
MIN_CLOSED_X3 = 50
VARIANTS = ("X1", "X3")
R2_PREFIX = "research/ussy-canslim-research/fwd1"


def json_dump(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, default=str))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def complete_months(start: pd.Timestamp, end: pd.Timestamp) -> int:
    if end < start:
        return 0
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day < start.day:
        months -= 1
    return max(0, int(months))


def load_spy_asof(s3, bucket: str, spy_pointer: dict) -> pd.Timestamp:
    payload = read_bytes(s3, bucket, spy_pointer["parquet_key"])
    verify(payload, spy_pointer.get("sha256"), "SPY")
    spy = pd.read_parquet(io.BytesIO(payload), columns=["date"])
    d = pd.to_datetime(spy["date"], errors="coerce").dropna()
    if d.empty:
        raise RuntimeError("SPY source has no valid dates")
    return pd.Timestamp(d.max()).normalize()


def load_histories(s3, bucket: str, security_ids: list[str]) -> dict[str, pd.DataFrame]:
    histories: dict[str, pd.DataFrame] = {}
    failures = []
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = {pool.submit(load_history, s3, bucket, sid): sid for sid in security_ids}
        for fut in as_completed(futures):
            sid = futures[fut]
            try:
                histories[sid] = fut.result()
            except Exception as exc:
                failures.append({"security_id": sid, "error": str(exc)[:300]})
    if failures:
        raise RuntimeError(f"Forward history load failures: {failures[:5]}")
    return histories


def empty_portfolio_summary(variant: str, as_of: pd.Timestamp) -> dict:
    return {
        "variant": variant,
        "candidate_trade_count": 0,
        "portfolio_entry_count": 0,
        "closed_portfolio_trade_count": 0,
        "capacity_skip_count": 0,
        "cash_skip_count": 0,
        "already_open_skip_count": 0,
        "gross_total_return": 0.0,
        "gross_cagr": None,
        "gross_max_drawdown": 0.0,
        "cost20bp_rt_total_return": 0.0,
        "cost20bp_rt_cagr": None,
        "cost20bp_rt_max_drawdown": 0.0,
        "final_censored_position_count": 0,
        "first_date": None,
        "last_date": str(as_of.date()),
    }


def persist_r2(s3, bucket: str, run_id: str, files: list[Path], metadata: dict) -> dict:
    immutable_prefix = f"{R2_PREFIX}/runs/{run_id}"
    published = []
    for path in files:
        data = path.read_bytes()
        key = f"{immutable_prefix}/{path.name}"
        s3.put_object(Bucket=bucket, Key=key, Body=data)
        published.append({"key": key, "sha256": sha256_bytes(data), "bytes": len(data)})

    manifest = {**metadata, "immutable_prefix": immutable_prefix, "files": published}
    manifest_bytes = json.dumps(manifest, indent=2, sort_keys=True, default=str).encode("utf-8")
    manifest_key = f"{immutable_prefix}/manifest.json"
    s3.put_object(Bucket=bucket, Key=manifest_key, Body=manifest_bytes)
    pointer = {
        "run_id": run_id,
        "manifest_key": manifest_key,
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    s3.put_object(
        Bucket=bucket,
        Key=f"{R2_PREFIX}/latest.json",
        Body=json.dumps(pointer, indent=2, sort_keys=True).encode("utf-8"),
    )
    return {"status": "PUBLISHED", **pointer, "immutable_prefix": immutable_prefix, "published_file_count": len(published)}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for p in OUT.iterdir():
        if p.is_file():
            p.unlink()

    s3 = s3_client()
    bucket = os.environ["R2_BUCKET_NAME"]
    run_id = os.getenv("GITHUB_RUN_ID") or datetime.now(timezone.utc).strftime("manual-%Y%m%dT%H%M%SZ")
    code_sha = os.getenv("GITHUB_SHA") or "LOCAL_OR_UNKNOWN"
    collected_at = datetime.now(timezone.utc).isoformat()

    all_candidates, membership, spy_pointer = generate_candidates(s3, bucket)
    all_candidates = all_candidates.copy()
    all_candidates["security_id"] = all_candidates["security_id"].astype(str)
    all_candidates["date"] = pd.to_datetime(all_candidates["date"], errors="coerce").dt.normalize()
    forward = all_candidates[all_candidates["date"] > FORWARD_BOUNDARY].copy()
    forward = forward.sort_values(["date", "security_id"]).reset_index(drop=True)

    spy_asof = load_spy_asof(s3, bucket, spy_pointer)
    if (forward["date"] <= FORWARD_BOUNDARY).any():
        raise RuntimeError("Historical signal leaked into FWD1")

    forward.to_csv(OUT / "forward_candidates.csv", index=False)
    json_dump(OUT / "membership_snapshot.json", membership)
    json_dump(OUT / "spy_pointer.json", spy_pointer)

    histories: dict[str, pd.DataFrame] = {}
    if len(forward):
        histories = load_histories(s3, bucket, sorted(forward["security_id"].unique().tolist()))

    trade_frames = []
    portfolio_trade_frames = []
    skip_frames = []
    curve_frames = []
    censor_audits = []
    variants = []

    for variant in VARIANTS:
        if not len(forward):
            variants.append(empty_portfolio_summary(variant, spy_asof))
            continue

        trade_candidates = prepare_trade_candidates(variant, forward, histories)
        if not trade_candidates.empty:
            t = trade_candidates.copy()
            t.insert(0, "variant", variant)
            trade_frames.append(t)
        if trade_candidates.empty:
            variants.append(empty_portfolio_summary(variant, spy_asof))
            continue

        accepted, skipped, curve, port_summary = run_portfolio(variant, trade_candidates, histories)
        curve, port_summary, censor_audit = apply_frozen_censored_accounting(variant, accepted, curve, port_summary)
        censor_audits.append(censor_audit)

        accepted = accepted.copy()
        accepted["variant"] = variant
        skipped = skipped.copy()
        if not skipped.empty:
            skipped["variant"] = variant
        curve = curve.copy()
        curve["variant"] = variant

        port_summary["closed_portfolio_trade_count"] = int((~accepted["exit_reason"].eq("CENSORED_OPEN")).sum()) if len(accepted) else 0
        variants.append(port_summary)
        portfolio_trade_frames.append(accepted)
        if not skipped.empty:
            skip_frames.append(skipped)
        curve_frames.append(curve)

    trade_candidates_all = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    portfolio_trades = pd.concat(portfolio_trade_frames, ignore_index=True) if portfolio_trade_frames else pd.DataFrame()
    portfolio_skips = pd.concat(skip_frames, ignore_index=True) if skip_frames else pd.DataFrame()
    equity_curves = pd.concat(curve_frames, ignore_index=True) if curve_frames else pd.DataFrame()

    trade_candidates_all.to_csv(OUT / "forward_trade_candidates.csv", index=False)
    portfolio_trades.to_csv(OUT / "portfolio_trades.csv", index=False)
    portfolio_skips.to_csv(OUT / "portfolio_skips.csv", index=False)
    equity_curves.to_csv(OUT / "equity_curves.csv", index=False)
    pd.DataFrame(censor_audits).to_csv(OUT / "censored_accounting_audit.csv", index=False)

    months = complete_months(FORWARD_START, spy_asof)
    x3 = next(v for v in variants if v["variant"] == "X3")
    x3_closed = int(x3.get("closed_portfolio_trade_count") or 0)
    calendar_gate = months >= MIN_MONTHS
    trade_gate = x3_closed >= MIN_CLOSED_X3
    review_eligible = bool(calendar_gate and trade_gate)
    gate = {
        "status": "REVIEW_ELIGIBLE" if review_eligible else "ACCUMULATING",
        "forward_boundary_exclusive": str(FORWARD_BOUNDARY.date()),
        "forward_start": str(FORWARD_START.date()),
        "market_data_asof": str(spy_asof.date()),
        "completed_calendar_months": months,
        "minimum_calendar_months": MIN_MONTHS,
        "calendar_gate_pass": calendar_gate,
        "closed_x3_portfolio_trades": x3_closed,
        "minimum_closed_x3_portfolio_trades": MIN_CLOSED_X3,
        "trade_gate_pass": trade_gate,
        "production_ready": False,
        "note": "Passing both gates makes FWD1 review-eligible only; it never auto-promotes production.",
    }
    json_dump(OUT / "gate_status.json", gate)

    summary = {
        "experiment": "FWD1_FORWARD_VALIDATION",
        "methodology": "docs/methodology/forward-validation-v1.md",
        "methodology_frozen_before_forward_collection": True,
        "run_id": str(run_id),
        "code_sha": code_sha,
        "collected_at_utc": collected_at,
        "research_universe": "CURRENT_COMPLIANT_UNIVERSE_FROZEN_AT_2026_08_28",
        "forward_boundary_exclusive": str(FORWARD_BOUNDARY.date()),
        "market_data_asof": str(spy_asof.date()),
        "forward_candidate_count": int(len(forward)),
        "forward_candidate_symbols": int(forward["security_id"].nunique()) if len(forward) else 0,
        "variants": variants,
        "gate": gate,
        "hard_filters": {"C": False, "A": False, "EXH2": False},
        "x3_primary": True,
        "x1_mandatory_control": True,
        "guardrail": "Interim forward performance cannot change frozen FWD1 rules. Any rule change starts a new versioned forward clock.",
    }
    json_dump(OUT / "summary.json", summary)

    evidence_files = [
        OUT / "summary.json", OUT / "gate_status.json", OUT / "forward_candidates.csv",
        OUT / "forward_trade_candidates.csv", OUT / "portfolio_trades.csv", OUT / "portfolio_skips.csv",
        OUT / "equity_curves.csv", OUT / "censored_accounting_audit.csv", OUT / "membership_snapshot.json",
        OUT / "spy_pointer.json",
    ]
    try:
        publication = persist_r2(
            s3, bucket, str(run_id), evidence_files,
            {
                "experiment": "FWD1_FORWARD_VALIDATION",
                "code_sha": code_sha,
                "collected_at_utc": collected_at,
                "market_data_asof": str(spy_asof.date()),
                "forward_candidate_count": int(len(forward)),
                "gate_status": gate["status"],
            },
        )
    except ClientError as exc:
        code = str(exc.response.get("Error", {}).get("Code") or "CLIENT_ERROR")
        publication = {
            "status": "NOT_PUBLISHED",
            "reason": code,
            "note": "R2 credentials are read-only for this consumer. Canonical persistence is Git repository history; Actions artifact is the detailed mirror.",
        }
    json_dump(OUT / "r2_publication.json", publication)
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))
    print(json.dumps(publication, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
