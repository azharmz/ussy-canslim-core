from __future__ import annotations

import io
import json
import os
from pathlib import Path

import boto3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "historical-ca-join-input-audit"


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing {name}")
    return value


def client():
    return boto3.client(
        "s3",
        endpoint_url=env("R2_ENDPOINT"),
        aws_access_key_id=env("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=env("R2_SECRET_ACCESS_KEY"),
        region_name="auto",
    )


def read_bytes(s3, bucket: str, key: str) -> bytes:
    return s3.get_object(Bucket=bucket, Key=key)["Body"].read()


def read_json(s3, bucket: str, key: str) -> dict:
    return json.loads(read_bytes(s3, bucket, key))


def frame_summary(df: pd.DataFrame) -> dict:
    out = {
        "rows": int(len(df)),
        "columns": list(map(str, df.columns)),
    }
    for col in ["accepted_at", "filed_at", "fiscal_period_end", "symbol", "ticker", "security_id", "cik", "form", "fiscal_year", "fiscal_period"]:
        if col in df.columns:
            if col in {"accepted_at", "filed_at", "fiscal_period_end"}:
                s = pd.to_datetime(df[col], errors="coerce", utc=True)
                out[f"{col}_min"] = str(s.min()) if s.notna().any() else None
                out[f"{col}_max"] = str(s.max()) if s.notna().any() else None
            else:
                out[f"{col}_non_null"] = int(df[col].notna().sum())
                out[f"{col}_unique"] = int(df[col].nunique(dropna=True))
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = client()
    bucket = env("R2_BUCKET_NAME")
    pointer = read_json(s3, bucket, "fundamentals/current.json")
    manifest = read_json(s3, bucket, pointer["manifest_key"])
    artifacts = manifest["artifacts"]
    wide = pd.read_parquet(io.BytesIO(read_bytes(s3, bucket, artifacts["fundamentals_point_in_time.parquet"]["key"])))
    long = pd.read_parquet(io.BytesIO(read_bytes(s3, bucket, artifacts["fundamentals_point_in_time_long.parquet"]["key"])))
    final_report = pd.read_csv(io.BytesIO(read_bytes(s3, bucket, artifacts["fundamentals_final_production_report.csv"]["key"])), dtype=str)

    summary = {
        "audit": "HISTORICAL_CA_JOIN_INPUTS_V1",
        "manifest_key": pointer["manifest_key"],
        "source_run_id": pointer.get("source_run_id"),
        "source_commit": pointer.get("source_commit"),
        "wide": frame_summary(wide),
        "long": frame_summary(long),
        "final_report": frame_summary(final_report),
        "identity_recommendation": "Prefer security_id if available. Otherwise use the strongest stable mapping exposed by the contracts; ticker-only joins must be explicitly labeled and audited for renames.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
