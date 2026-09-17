from __future__ import annotations

import hashlib
import io
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import boto3
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from canslim_research.technical import (  # noqa: E402
    BASE_DEPTH_MAX,
    BUY_ZONE_MAX,
    DISTRIBUTION_BLOCK_COUNT,
    DISTRIBUTION_RETURN_MAX,
    FTD_RETURN_MIN,
    PRICE_FLOOR,
    RS_PERCENTILE_MIN,
    VOLUME_RATIO_MIN,
)

OUT = ROOT / "results" / "e0-static-history-candidates-v1"
MEMBERSHIP_KEY = "universe/membership/2026-08-28.json"
SPY_POINTER = "benchmarks/SPY/current.json"
# Canonical namespace after the verified R2 historical OHLCV migration.
OHLCV_PREFIX = "history/ohlcv/"


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


def read_bytes(s3, bucket: str, key: str) -> bytes:
    return s3.get_object(Bucket=bucket, Key=key)["Body"].read()


def read_json(s3, bucket: str, key: str) -> dict:
    return json.loads(read_bytes(s3, bucket, key))


def verify(payload: bytes, expected_sha256: str | None, label: str) -> None:
    if expected_sha256 and hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise RuntimeError(f"SHA256 mismatch for {label}")


def list_keys(s3, bucket: str, prefix: str) -> set[str]:
    out: set[str] = set()
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        out.update(str(x["Key"]) for x in page.get("Contents", []))
    return out


def build_spy_market_state(spy: pd.DataFrame) -> pd.DataFrame:
    x = spy.sort_values("date").copy()
    x["date"] = pd.to_datetime(x["date"], errors="raise").dt.normalize()
    x["ret1"] = x["close"].pct_change()
    x["prev_volume"] = x["volume"].shift(1)
    x["distribution"] = (x["ret1"] <= DISTRIBUTION_RETURN_MAX) & (x["volume"] > x["prev_volume"])
    x["distribution_count_25"] = x["distribution"].rolling(25, min_periods=1).sum().astype(int)
    prior_10_low = x["close"].shift(1).rolling(10, min_periods=10).min()

    confirmed = False
    waiting_positive_after_low = False
    rally_day = 0
    rally_low = np.nan
    active_values: list[bool] = []
    rally_days: list[int] = []
    ftd_events: list[bool] = []

    for i, row in x.iterrows():
        close = float(row["close"])
        ret1 = row["ret1"]
        volume = row["volume"]
        prev_volume = row["prev_volume"]
        is_10_low = pd.notna(prior_10_low.loc[i]) and close <= float(prior_10_low.loc[i])

        if confirmed and pd.notna(rally_low) and close < float(rally_low):
            confirmed = False
            rally_day = 0
            waiting_positive_after_low = False
            rally_low = np.nan
        if is_10_low and not confirmed:
            waiting_positive_after_low = True
            rally_day = 0
            rally_low = close if pd.isna(rally_low) else min(float(rally_low), close)

        ftd = False
        if not confirmed:
            if waiting_positive_after_low and pd.notna(ret1) and float(ret1) > 0:
                rally_day = 1
                waiting_positive_after_low = False
            elif rally_day > 0:
                rally_day += 1
            if (
                rally_day >= 4
                and pd.notna(ret1)
                and float(ret1) >= FTD_RETURN_MIN
                and pd.notna(prev_volume)
                and float(volume) > float(prev_volume)
            ):
                confirmed = True
                ftd = True

        active_values.append(bool(confirmed))
        rally_days.append(int(rally_day))
        ftd_events.append(bool(ftd))

    x["spy_ftd_active"] = active_values
    x["spy_rally_day"] = rally_days
    x["spy_ftd_event"] = ftd_events
    x["M_pass_spy_only"] = x["spy_ftd_active"] & (x["distribution_count_25"] < DISTRIBUTION_BLOCK_COUNT)
    return x[["date", "distribution_count_25", "spy_ftd_event", "spy_ftd_active", "spy_rally_day", "M_pass_spy_only"]]


def ohlcv_key(security_id: str) -> str:
    return f"{OHLCV_PREFIX}{security_id}.parquet"


def load_security(s3, bucket: str, security_id: str, ticker: str) -> pd.DataFrame:
    key = ohlcv_key(security_id)
    payload = read_bytes(s3, bucket, key)
    g = pd.read_parquet(io.BytesIO(payload))
    required = {"date", "open", "high", "low", "close", "adj_close", "volume"}
    missing = required - set(g.columns)
    if missing:
        raise RuntimeError(f"{key} missing {sorted(missing)}")
    g = g[list(required)].copy()
    g["date"] = pd.to_datetime(g["date"], errors="coerce").dt.normalize()
    g = g.dropna(subset=["date"]).drop_duplicates("date", keep="last").sort_values("date")
    g["security_id"] = security_id
    g["ticker"] = ticker
    g["pivot"] = g["high"].shift(1).rolling(35, min_periods=35).max()
    g["base_low"] = g["low"].shift(1).rolling(35, min_periods=35).min()
    g["base_depth"] = (g["pivot"] - g["base_low"]) / g["pivot"]
    g["avg_volume_50"] = g["volume"].shift(1).rolling(50, min_periods=50).mean()
    g["volume_ratio"] = g["volume"] / g["avg_volume_50"]
    for n in (63, 126, 189, 252):
        g[f"return_{n}d"] = g["adj_close"] / g["adj_close"].shift(n) - 1.0
    g["rs_proxy_raw"] = 0.40 * g["return_63d"] + 0.20 * g["return_126d"] + 0.20 * g["return_189d"] + 0.20 * g["return_252d"]
    g["tminus1_to_t0"] = g["close"] / g["close"].shift(1) - 1.0
    g["h1_open"] = g["open"].shift(-1)
    g["h1_gap"] = g["h1_open"] / g["close"] - 1.0
    g["t0_pivot_extension"] = g["close"] / g["pivot"] - 1.0
    g["h1_fill_extension"] = g["h1_open"] / g["pivot"] - 1.0
    keep = [
        "date", "security_id", "ticker", "close", "pivot", "base_depth", "volume_ratio", "rs_proxy_raw",
        "tminus1_to_t0", "h1_open", "h1_gap", "t0_pivot_extension", "h1_fill_extension",
    ]
    return g.loc[g["rs_proxy_raw"].notna(), keep].copy()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = s3_client()
    bucket = env("R2_BUCKET_NAME")

    membership = read_json(s3, bucket, MEMBERSHIP_KEY)
    records = membership.get("records", [])
    eligible = {
        str(r["security_id"]): str(r.get("ticker") or "")
        for r in records
        if r.get("sharia_compliance") == "COMPLIANT"
    }
    if not eligible:
        raise RuntimeError("No COMPLIANT records in pinned membership snapshot")

    print(f"[historical-ohlcv] canonical_prefix={OHLCV_PREFIX} eligible={len(eligible)}", flush=True)
    available_keys = list_keys(s3, bucket, OHLCV_PREFIX)
    selected = [(sid, ticker) for sid, ticker in eligible.items() if ohlcv_key(sid) in available_keys]
    missing_ids = sorted(set(eligible) - {sid for sid, _ in selected})
    print(f"[historical-ohlcv] objects={len(available_keys)} selected={len(selected)} missing={len(missing_ids)}", flush=True)

    frames: list[pd.DataFrame] = []
    failures: list[dict] = []
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = {pool.submit(load_security, s3, bucket, sid, ticker): sid for sid, ticker in selected}
        for fut in as_completed(futures):
            sid = futures[fut]
            try:
                frame = fut.result()
                if not frame.empty:
                    frames.append(frame)
            except Exception as exc:
                failures.append({"security_id": sid, "error": str(exc)[:300]})
    if failures:
        raise RuntimeError(f"Failed to load {len(failures)} histories: {failures[:5]}")
    if not frames:
        raise RuntimeError(f"No feature-evaluable historical frames under canonical prefix {OHLCV_PREFIX}; selected={len(selected)} missing={len(missing_ids)}")

    x = pd.concat(frames, ignore_index=True)
    x["rs_percentile"] = x.groupby("date")["rs_proxy_raw"].rank(pct=True, method="average") * 100.0

    spy_pointer = read_json(s3, bucket, SPY_POINTER)
    spy_payload = read_bytes(s3, bucket, spy_pointer["parquet_key"])
    verify(spy_payload, spy_pointer.get("sha256"), "SPY")
    spy = pd.read_parquet(io.BytesIO(spy_payload))
    market = build_spy_market_state(spy)
    x = x.merge(market, on="date", how="left")

    x["price_pass"] = x["close"] >= PRICE_FLOOR
    x["N_pass"] = x["pivot"].notna() & (x["base_depth"] <= BASE_DEPTH_MAX) & (x["close"] > x["pivot"]) & (x["close"] <= x["pivot"] * (1.0 + BUY_ZONE_MAX))
    x["S_pass"] = x["volume_ratio"] >= VOLUME_RATIO_MIN
    x["L_pass"] = x["rs_percentile"] >= RS_PERCENTILE_MIN
    x["M_pass"] = x["M_pass_spy_only"].fillna(False)
    x["technical_pass"] = x[["price_pass", "N_pass", "S_pass", "L_pass", "M_pass"]].all(axis=1)

    candidates = x.loc[x["technical_pass"]].copy()
    cols = [
        "date", "security_id", "ticker", "close", "pivot", "base_depth", "volume_ratio", "rs_proxy_raw", "rs_percentile",
        "distribution_count_25", "spy_ftd_active", "tminus1_to_t0", "h1_open", "h1_gap", "t0_pivot_extension", "h1_fill_extension",
    ]
    candidates[cols].sort_values(["date", "ticker"]).to_csv(OUT / "candidates.csv", index=False)

    annual = candidates.assign(year=candidates["date"].dt.year).groupby("year", as_index=False).agg(
        candidate_rows=("security_id", "size"),
        candidate_symbols=("security_id", "nunique"),
        candidate_dates=("date", "nunique"),
    )
    annual.to_csv(OUT / "annual_candidate_counts.csv", index=False)

    summary = {
        "experiment": "E0-HIST-STATIC-CANDIDATES-V1",
        "evidence_class": "STATIC_2026_08_28_UNIVERSE_EXPLORATORY_NOT_PIT_UNIVERSE",
        "membership_key": MEMBERSHIP_KEY,
        "ohlcv_prefix": OHLCV_PREFIX,
        "membership_records": len(records),
        "eligible_compliant": len(eligible),
        "full_history_objects_available": len(selected),
        "eligible_missing_ohlcv": len(missing_ids),
        "feature_evaluable_rows": int(len(x)),
        "first_evaluable_date": str(x["date"].min().date()),
        "last_evaluable_date": str(x["date"].max().date()),
        "technical_candidate_rows": int(len(candidates)),
        "technical_candidate_symbols": int(candidates["security_id"].nunique()),
        "technical_candidate_dates": int(candidates["date"].nunique()),
        "candidate_first_date": str(candidates["date"].min().date()) if len(candidates) else None,
        "candidate_last_date": str(candidates["date"].max().date()) if len(candidates) else None,
        "market_proxy_scope": "SPY_ONLY",
        "trading_performance_metrics_used": False,
        "survivorship_warning": "2026-08-28 membership is held fixed across past dates. This can exclude historical constituents and include securities whose historical compliance state is unknown.",
        "allowed_use": "candidate-frequency, implementation diagnostics, and E1-E4 exploratory mechanism study only; not unbiased strategy performance inference",
        "spy_parquet_key": spy_pointer.get("parquet_key"),
        "spy_sha256": spy_pointer.get("sha256"),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    (OUT / "membership_snapshot.json").write_text(json.dumps(membership, indent=2, sort_keys=True))
    (OUT / "spy_pointer.json").write_text(json.dumps(spy_pointer, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
