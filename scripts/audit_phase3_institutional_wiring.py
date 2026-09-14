from __future__ import annotations

import io
import json
import os
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import boto3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from canslim_research.decision_time import regular_close_cutoff
from canslim_research.institutional_pit import resolve_institutional_pit, validate_institutional_pointer

OUT = ROOT / "results" / "remediation-phase3-institutional"


def env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"missing {name}")
    return v


def client():
    return boto3.client(
        "s3", endpoint_url=env("R2_ENDPOINT"),
        aws_access_key_id=env("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=env("R2_SECRET_ACCESS_KEY"), region_name="auto")


def raw(s3, bucket: str, key: str) -> bytes:
    return s3.get_object(Bucket=bucket, Key=key)["Body"].read()


def js(s3, bucket: str, key: str) -> dict:
    return json.loads(raw(s3, bucket, key))


def pq(s3, bucket: str, key: str) -> pd.DataFrame:
    return pd.read_parquet(io.BytesIO(raw(s3, bucket, key)))


def csv(s3, bucket: str, key: str) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(raw(s3, bucket, key)), dtype={"security_id": "string", "cusip": "string"})


def latest_ready_date(s3, bucket: str) -> date:
    p = js(s3, bucket, "production/ready/current.json")
    f = pq(s3, bucket, p["parquet_key"])
    return pd.to_datetime(f["date"], errors="raise").dt.date.max()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = client()
    bucket = env("R2_BUCKET_NAME")
    ptr = js(s3, bucket, "institutional_sponsorship/current.json")
    manifest = js(s3, bucket, ptr["manifest_key"])
    validate_institutional_pointer(ptr, manifest)

    live = csv(s3, bucket, ptr["live_sponsorship_mapped_key"])
    hist = pq(s3, bucket, ptr["history_state_events_key"])
    unc = pq(s3, bucket, ptr["uncertainty_state_events_key"])
    asof = latest_ready_date(s3, bucket)
    cutoff = regular_close_cutoff(asof)

    # One result per deterministic security in the canonical live snapshot.
    states = Counter()
    reasons = Counter()
    examples = []
    security_ids = sorted(set(live["security_id"].dropna().astype(str)))
    for sid in security_ids:
        r = resolve_institutional_pit(
            security_id=sid, decision_cutoff=cutoff,
            live_state=live, history_events=hist, uncertainty_events=unc)
        states[r.state] += 1
        reasons[r.reason] += 1
        if len(examples) < 25:
            examples.append({
                "security_id": sid, "state": r.state, "reason": r.reason,
                "latest": r.fund_count_latest, "prior": r.fund_count_prior,
                "latest_period": r.latest_period, "prior_period": r.prior_period,
                "latest_available_at": r.latest_available_at,
                "prior_available_on": r.prior_available_on,
            })

    if not security_ids:
        raise RuntimeError("canonical live I snapshot contains no securities")
    if sum(states.values()) != len(security_ids):
        raise RuntimeError("institutional resolver did not classify every live security")
    if not any(states.get(x, 0) for x in ("POSITIVE", "NEUTRAL", "NEGATIVE")):
        raise RuntimeError("no evaluable institutional comparison exists in canonical data")

    summary = {
        "status": "PASS",
        "asof_date": asof.isoformat(),
        "information_cutoff": cutoff.isoformat(),
        "pointer_schema_version": ptr["schema_version"],
        "snapshot_prefix": ptr["snapshot_prefix"],
        "publisher_run_id": str(ptr["publisher_run_id"]),
        "live_source_run_id": str(ptr["live_source_run_id"]),
        "live_availability": ptr["live_availability"],
        "live_security_count": len(security_ids),
        "I_state_counts": dict(states),
        "I_reason_counts": dict(reasons),
        "examples": examples,
        "future_live_accepted_at_allowed": False,
        "quarter_end_used_as_availability": False,
        "identity_mapping": "US_ISIN_BODY_TO_CUSIP9",
        "strategy_returns_inspected": False,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
