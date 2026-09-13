from __future__ import annotations

import io
import json
import os
import sys
from hashlib import sha256
from pathlib import Path

import boto3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from canslim_research.candidate_v2 import DailyBar, PatternAssessment, build_candidate
from canslim_research.candidate_v2_adapters import build_candidate_evidence
from canslim_research.validation_corpus_v1 import select_corpus
from oneil_patterns.production.engine import analyze_security
from scripts.run_candidate_v2_smoke import build_spy_state, fundamental_evidence, load_fundamentals, read_json, read_parquet

OUT = ROOT / "results" / "v35-historical-pool"
ANCHORS = [f"{year}-{md}" for year in range(2021, 2026) for md in ("03-31", "06-30", "09-30", "12-31")]
SECURITY_SAMPLE_SIZE = 120
MIN_BARS = 300


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable {name}")
    return value


def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=env("R2_ENDPOINT"),
        aws_access_key_id=env("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=env("R2_SECRET_ACCESS_KEY"),
        region_name="auto",
    )


def list_history_keys(s3, bucket: str) -> list[str]:
    keys: list[str] = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix="backtest/ohlcv/"):
        keys.extend(item["Key"] for item in page.get("Contents", []) if item["Key"].endswith(".parquet"))
    return sorted(keys)


def load_history(s3, bucket: str, key: str) -> pd.DataFrame:
    payload = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    frame = pd.read_parquet(io.BytesIO(payload))
    frame["date"] = pd.to_datetime(frame["date"], errors="raise").dt.normalize()
    return frame.sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)


def security_rank(security_id: str) -> str:
    return sha256(f"v35-security-frame|{security_id}".encode()).hexdigest()


def resolve_dates(spy: pd.DataFrame) -> list[pd.Timestamp]:
    dates = pd.to_datetime(spy["date"], errors="raise").dt.normalize().drop_duplicates().sort_values()
    resolved: list[pd.Timestamp] = []
    for anchor in ANCHORS:
        eligible = dates[dates <= pd.Timestamp(anchor)]
        if not eligible.empty:
            resolved.append(eligible.iloc[-1])
    return resolved


def main() -> None:
    raise SystemExit("runner helpers installed; next commit adds calculation")


if __name__ == "__main__":
    main()
