from __future__ import annotations

import hashlib
import io
import json
import os
from datetime import datetime, timezone

import boto3
import pandas as pd
import yfinance as yf

INDEXES = {
    "NASDAQ_COMPOSITE": "^IXIC",
    "SP500": "^GSPC",
    "DJIA": "^DJI",
}
CONTRACT = "47-market-input-data-contract-v1"
PUBLISHER = "bt1-m-long-history-remediation-v1"


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


def parquet_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO(); df.to_parquet(buf, index=False); return buf.getvalue()


def main() -> None:
    s3 = s3_client(); bucket = need("R2_BUCKET_NAME")
    run_id = need("GITHUB_RUN_ID")
    apply = os.getenv("BT1_M_APPLY", "false").lower() == "true"
    prefix = f"market/indexes/runs/{run_id}"
    now = datetime.now(timezone.utc).isoformat()
    manifest = {
        "contract": CONTRACT, "publisher": PUBLISHER, "run_id": run_id,
        "created_at": now, "source": "yfinance", "apply": apply,
        "indexes": {}, "historical_replay_authorized": False,
    }
    payloads: dict[str, bytes] = {}
    common_start = None; common_end = None
    for index_id, ticker in INDEXES.items():
        raw = yf.download(ticker, period="max", interval="1d", auto_adjust=False,
                          actions=False, progress=False, threads=False)
        if raw.empty:
            raise RuntimeError(f"no data returned for {ticker}")
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        raw = raw.reset_index()
        rename = {c: str(c).lower().replace(" ", "_") for c in raw.columns}
        raw = raw.rename(columns=rename)
        required = ["date", "open", "high", "low", "close", "volume"]
        missing = [c for c in required if c not in raw.columns]
        if missing:
            raise RuntimeError(f"{ticker}: missing columns {missing}")
        df = raw[required].copy()
        df["date"] = pd.to_datetime(df["date"], errors="raise").dt.strftime("%Y-%m-%d")
        if df["date"].duplicated().any():
            raise RuntimeError(f"{ticker}: duplicate dates")
        if not df["date"].is_monotonic_increasing:
            raise RuntimeError(f"{ticker}: dates not monotonic")
        if df[["open", "high", "low", "close"]].isna().any().any():
            raise RuntimeError(f"{ticker}: null price values")
        start, end = df["date"].iloc[0], df["date"].iloc[-1]
        common_start = start if common_start is None or start > common_start else common_start
        common_end = end if common_end is None or end < common_end else common_end
        body = parquet_bytes(df)
        payloads[index_id] = body
        manifest["indexes"][index_id] = {
            "source_symbol": ticker, "rows": int(len(df)), "date_min": start,
            "date_max": end, "sha256": hashlib.sha256(body).hexdigest(),
            "bytes": len(body), "key": f"{prefix}/{index_id}.parquet",
        }
    manifest["common_date_min"] = common_start
    manifest["common_date_max"] = common_end
    # Coverage threshold is deliberately a data-readiness guard, not a trading rule.
    manifest["long_history_ready"] = bool(common_start and common_start <= "2000-01-01")
    if not manifest["long_history_ready"]:
        raise RuntimeError(f"insufficient common history: starts {common_start}")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    if not apply:
        print("DRY_RUN_ONLY: no R2 writes performed")
        return
    # Immutable run first. Pointer is advanced LAST.
    for index_id, body in payloads.items():
        s3.put_object(Bucket=bucket, Key=f"{prefix}/{index_id}.parquet", Body=body,
                      ContentType="application/octet-stream")
    manifest_body = json.dumps(manifest, indent=2, sort_keys=True).encode()
    s3.put_object(Bucket=bucket, Key=f"{prefix}/manifest.json", Body=manifest_body,
                  ContentType="application/json")
    pointer = {
        "contract": CONTRACT, "publisher": PUBLISHER, "run_id": run_id,
        "manifest_key": f"{prefix}/manifest.json", "updated_at": now,
        "historical_replay_authorized": False,
    }
    s3.put_object(Bucket=bucket, Key="market/indexes/official.json",
                  Body=json.dumps(pointer, indent=2, sort_keys=True).encode(),
                  ContentType="application/json")
    print("APPLIED: immutable canonical index run written; official pointer advanced LAST")


if __name__ == "__main__":
    main()
