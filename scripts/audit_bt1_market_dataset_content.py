from __future__ import annotations

import io
import json
import os
from pathlib import Path

import boto3
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "results" / "bt1-market-dataset-content"
INDEXES = ("NASDAQ_COMPOSITE", "SP500", "DJIA")
PREFIX = "market/indexes/runs/"


def need(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"missing {name}")
    return value


def s3_client():
    return boto3.client(
        "s3", endpoint_url=need("R2_ENDPOINT"), region_name="auto",
        aws_access_key_id=need("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=need("R2_SECRET_ACCESS_KEY"))


def get_json(s3, bucket: str, key: str) -> dict:
    return json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())


def get_parquet(s3, bucket: str, key: str) -> pd.DataFrame:
    raw = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    return pd.read_parquet(io.BytesIO(raw))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = s3_client(); bucket = need("R2_BUCKET_NAME")
    pointer = get_json(s3, bucket, "market/indexes/official.json")
    print("official pointer:", json.dumps(pointer, sort_keys=True))

    # Resolve the official run from the pointer without assuming field naming.
    text = json.dumps(pointer)
    run_ids = []
    for token in text.replace('\\/', '/').split('market/indexes/runs/') [1:]:
        run_ids.append(token.split('/')[0].split('"')[0])
    if not run_ids:
        # Fallback to an explicit run id field if present.
        for key in ("run_id", "github_run_id"):
            if pointer.get(key) is not None:
                run_ids.append(str(pointer[key]))
    if not run_ids:
        raise RuntimeError("cannot resolve official market index run")
    run_id = run_ids[0]
    manifest_key = f"{PREFIX}{run_id}/manifest.json"
    manifest = get_json(s3, bucket, manifest_key)

    result = {
        "audit": "BT1_MARKET_DATASET_CONTENT_V1",
        "strategy_returns_inspected": False,
        "official_pointer": pointer,
        "official_run_id": run_id,
        "manifest_key": manifest_key,
        "manifest": manifest,
        "indexes": {},
    }
    common_start = None; common_end = None
    all_valid = True
    for index_id in INDEXES:
        key = f"{PREFIX}{run_id}/{index_id}.parquet"
        df = get_parquet(s3, bucket, key)
        cols = list(map(str, df.columns))
        date_col = next((c for c in df.columns if str(c).lower() in ("date", "session_date", "datetime", "timestamp")), None)
        if date_col is None:
            dates = pd.to_datetime(df.index, errors="coerce", utc=True)
            date_source = "index"
        else:
            dates = pd.to_datetime(df[date_col], errors="coerce", utc=True)
            date_source = str(date_col)
        valid_dates = pd.Series(dates).dropna()
        start = valid_dates.min().isoformat() if len(valid_dates) else None
        end = valid_dates.max().isoformat() if len(valid_dates) else None
        common_start = start if common_start is None or (start and start > common_start) else common_start
        common_end = end if common_end is None or (end and end < common_end) else common_end
        lower = {str(c).lower(): c for c in df.columns}
        required = ["open", "high", "low", "close", "volume"]
        missing = [x for x in required if x not in lower]
        nulls = {x: int(df[lower[x]].isna().sum()) for x in required if x in lower}
        duplicates = int(pd.Series(dates).duplicated().sum())
        monotonic = bool(pd.Series(dates).dropna().is_monotonic_increasing)
        valid = len(df) > 0 and not missing and start is not None and end is not None and duplicates == 0
        all_valid = all_valid and valid
        result["indexes"][index_id] = {
            "key": key, "rows": int(len(df)), "columns": cols,
            "date_source": date_source, "date_min": start, "date_max": end,
            "missing_required_ohlcv": missing, "null_counts": nulls,
            "duplicate_dates": duplicates, "date_monotonic_increasing": monotonic,
            "content_valid": valid,
        }
    result["common_date_min"] = common_start
    result["common_date_max"] = common_end
    result["content_ready_for_causal_replay_contract"] = all_valid
    (OUT / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
