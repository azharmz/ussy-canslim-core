from __future__ import annotations

import io
import json
import os
from pathlib import Path

import boto3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "bt1-historical-readiness"


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"missing {name}")
    return value


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
    return pd.read_csv(io.BytesIO(raw(s3, bucket, key)), low_memory=False)


def keys(s3, bucket: str, prefix: str) -> list[str]:
    out = []
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
        out.extend(str(x["Key"]) for x in page.get("Contents", []))
    return sorted(out)


def dt_summary(df: pd.DataFrame, col: str, *, utc: bool = True) -> dict:
    if col not in df.columns:
        return {"column_present": False}
    s = pd.to_datetime(df[col], errors="coerce", utc=utc)
    return {
        "column_present": True,
        "non_null": int(s.notna().sum()),
        "min": s.min().isoformat() if s.notna().any() else None,
        "max": s.max().isoformat() if s.notna().any() else None,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = client(); bucket = env("R2_BUCKET_NAME")

    # C/A immutable PIT source currently consumed by production.
    fptr = js(s3, bucket, "fundamentals/current.json")
    fman = js(s3, bucket, fptr["manifest_key"])
    fart = fman["artifacts"]
    wide = pq(s3, bucket, fart["fundamentals_point_in_time.parquet"]["key"])
    long = pq(s3, bucket, fart["fundamentals_point_in_time_long.parquet"]["key"])

    # I canonical prospective source plus historical state events.
    iptr = js(s3, bucket, "institutional_sponsorship/current.json")
    iman = js(s3, bucket, iptr["manifest_key"])
    live = csv(s3, bucket, iptr["live_sponsorship_mapped_key"])
    hist = pq(s3, bucket, iptr["history_state_events_key"])
    unc = pq(s3, bucket, iptr["uncertainty_state_events_key"])

    # M: inventory the actual canonical namespace rather than assuming that the
    # current official pointer implies historical replay availability.
    market_keys = keys(s3, bucket, "market/state/")
    market_json = [k for k in market_keys if k.endswith(".json")]
    market_states = []
    for key in market_json:
        try:
            payload = js(s3, bucket, key)
        except Exception as exc:
            market_states.append({"key": key, "read_error": type(exc).__name__})
            continue
        market_states.append({
            "key": key,
            "asof_date": payload.get("asof_date") or payload.get("market_asof_date") or payload.get("session_date"),
            "state_key": payload.get("state_key"),
            "market_state": payload.get("market_state"),
            "M_entry_state": payload.get("M_entry_state"),
            "classifier_version": payload.get("classifier_version"),
        })

    ohlcv = [k for k in keys(s3, bucket, "backtest/ohlcv/") if k.endswith(".parquet")]
    membership = [k for k in keys(s3, bucket, "universe/membership/") if k.endswith(".json")]

    summary = {
        "audit": "BT1_HISTORICAL_READINESS_V1",
        "strategy_returns_inspected": False,
        "fundamentals": {
            "manifest_key": fptr["manifest_key"],
            "wide_rows": int(len(wide)), "long_rows": int(len(long)),
            "wide_accepted_at": dt_summary(wide, "accepted_at"),
            "wide_annual_eps_accepted_at": dt_summary(wide, "annual_eps_accepted_at"),
            "long_accepted_at": dt_summary(long, "accepted_at"),
            "symbols": int(wide["symbol"].nunique()) if "symbol" in wide.columns else None,
        },
        "institutional": {
            "manifest_key": iptr["manifest_key"],
            "live_availability": iptr.get("live_availability"),
            "live_rows": int(len(live)), "history_rows": int(len(hist)), "uncertainty_rows": int(len(unc)),
            "live_accepted_at": dt_summary(live, "I_available_at"),
            "history_available_on": dt_summary(hist, "available_on", utc=False),
            "history_period_of_report": dt_summary(hist, "period_of_report", utc=False),
            "history_cusips": int(hist["cusip"].nunique()) if "cusip" in hist.columns else None,
        },
        "market": {
            "namespace_object_count": len(market_keys),
            "json_object_count": len(market_json),
            "objects": market_states,
            "historical_replay_authorized": False,
            "note": "Inventory only. Historical M is authorized only if dated canonical states or a frozen causal reconstruction contract are demonstrated.",
        },
        "ohlcv": {"object_count": len(ohlcv)},
        "membership": {"snapshot_count": len(membership), "keys": membership},
        "oneil": {
            "pinned_sha": "c433cc1e35a5aa32a46f732cd8c5545935e36e40",
            "assessment": "CODE_PINNED_OHLCV_REPLAY_MECHANICALLY_FEASIBLE; historical full-CANSLIM authorization still depends on intersection of mandatory PIT evidence",
        },
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
