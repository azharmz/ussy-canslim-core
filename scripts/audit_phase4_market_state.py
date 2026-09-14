from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

import boto3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from canslim_research.market_state_consumer import consume_market_state

OUT = ROOT / "results" / "remediation-phase4-market-state"


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"missing {name}")
    return value


def client():
    return boto3.client(
        "s3",
        endpoint_url=env("R2_ENDPOINT"),
        aws_access_key_id=env("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=env("R2_SECRET_ACCESS_KEY"),
        region_name="auto",
    )


def raw(s3, bucket: str, key: str) -> bytes:
    return s3.get_object(Bucket=bucket, Key=key)["Body"].read()


def js(s3, bucket: str, key: str) -> dict:
    return json.loads(raw(s3, bucket, key))


def latest_ready_date(s3, bucket: str):
    ptr = js(s3, bucket, "production/ready/current.json")
    payload = raw(s3, bucket, ptr["parquet_key"])
    frame = pd.read_parquet(io.BytesIO(payload))
    return pd.to_datetime(frame["date"], errors="raise").dt.date.max()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = client()
    bucket = env("R2_BUCKET_NAME")
    decision_date = latest_ready_date(s3, bucket)
    pointer = js(s3, bucket, "market/state/official.json")
    state_bytes = raw(s3, bucket, pointer["state_key"])
    decision = consume_market_state(
        pointer=pointer,
        state_bytes=state_bytes,
        decision_session_date=decision_date,
    )
    summary = {
        "status": "PASS",
        "decision_session_date": decision_date.isoformat(),
        "market_asof_date": decision.asof_date,
        "market_state": decision.market_state,
        "M_entry_state": decision.M_entry_state,
        "reason": decision.reason,
        "consumer_version": decision.consumer_version,
        "classifier_version": decision.classifier_version,
        "market_action_version": decision.market_action_version,
        "state_key": decision.state_key,
        "state_sha256": decision.state_sha256,
        "source_index_run_id": decision.source_index_run_id,
        "source_manifest_key": decision.source_manifest_key,
        "source_manifest_sha256": decision.source_manifest_sha256,
        "future_state_allowed": False,
        "stale_state_allowed": False,
        "local_spy_recalculation_used": False,
        "strategy_returns_inspected": False,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
