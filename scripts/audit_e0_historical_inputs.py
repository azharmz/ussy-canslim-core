from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

import boto3

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "e0-historical-input-audit"


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable {name}")
    return value


def client():
    return boto3.client(
        "s3",
        endpoint_url=env("R2_ENDPOINT"),
        aws_access_key_id=env("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=env("R2_SECRET_ACCESS_KEY"),
        region_name="auto",
    )


def list_keys(s3, bucket: str, prefix: str) -> list[str]:
    out: list[str] = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        out.extend(str(x["Key"]) for x in page.get("Contents", []))
    return sorted(out)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = client()
    bucket = env("R2_BUCKET_NAME")

    membership_keys = [k for k in list_keys(s3, bucket, "universe/membership/") if k.endswith(".json")]
    membership_dates: list[str] = []
    membership_counts: list[dict] = []
    for key in membership_keys:
        name = key.rsplit("/", 1)[-1].removesuffix(".json")
        try:
            datetime.strptime(name, "%Y-%m-%d")
        except ValueError:
            continue
        payload = json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
        records = payload.get("records", [])
        membership_dates.append(name)
        membership_counts.append({
            "snapshot_date": name,
            "records": len(records),
            "statuses": {str(status): sum(1 for r in records if str(r.get("status")) == str(status)) for status in sorted({r.get("status") for r in records})},
        })

    ohlcv_keys = [k for k in list_keys(s3, bucket, "backtest/ohlcv/") if k.endswith(".parquet")]
    spy_keys = [k for k in list_keys(s3, bucket, "benchmarks/SPY/") if k.endswith(".json") or k.endswith(".parquet")]
    qqq_keys = [k for k in list_keys(s3, bucket, "benchmarks/QQQ/") if k.endswith(".json") or k.endswith(".parquet")]

    summary = {
        "audit": "E0_HISTORICAL_INPUTS_V1",
        "membership_snapshot_count": len(membership_dates),
        "membership_first_date": min(membership_dates) if membership_dates else None,
        "membership_last_date": max(membership_dates) if membership_dates else None,
        "membership_dates": sorted(membership_dates),
        "membership_counts": membership_counts,
        "backtest_ohlcv_objects": len(ohlcv_keys),
        "spy_objects": len(spy_keys),
        "qqq_objects": len(qqq_keys),
        "qqq_contract_present": bool(qqq_keys),
        "interpretation": "Historical OHLCV objects can support long lookbacks, but PIT universe history is only defensible from the first available membership snapshot onward unless an older eligibility source is introduced.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
