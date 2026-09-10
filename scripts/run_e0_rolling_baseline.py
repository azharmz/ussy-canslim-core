from __future__ import annotations

import hashlib
import io
import json
import os
import sys
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

OUT = ROOT / "results" / "e0-rolling-baseline-v1"
READY_POINTER = "production/ready/current.json"
SPY_POINTER = "benchmarks/SPY/current.json"


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


def normalize_price_frame(frame: pd.DataFrame) -> pd.DataFrame:
    required = {"date", "security_id", "ticker", "open", "high", "low", "close", "adj_close", "volume"}
    missing = required - set(frame.columns)
    if missing:
        raise RuntimeError(f"Ready OHLCV missing columns: {sorted(missing)}")
    x = frame[list(required)].copy()
    x["date"] = pd.to_datetime(x["date"], errors="raise").dt.normalize()
    x = x.sort_values(["security_id", "date"]).reset_index(drop=True)
    if x.duplicated(["security_id", "date"]).any():
        raise RuntimeError("Duplicate security_id/date rows in ready OHLCV")
    return x


def build_spy_market_state(spy: pd.DataFrame) -> pd.DataFrame:
    """Transparent SPY-only implementation of the frozen M proxy for E0 smoke work.

    The final dual-index M-v1 remains SPY OR QQQ. E0 is explicitly limited to
    SPY because `ussy-data` currently exposes no QQQ benchmark contract.
    """
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
    return x[["date", "ret1", "distribution", "distribution_count_25", "spy_ftd_event", "spy_ftd_active", "spy_rally_day", "M_pass_spy_only"]]


def add_security_features(prices: pd.DataFrame) -> pd.DataFrame:
    chunks: list[pd.DataFrame] = []
    for _, g in prices.groupby("security_id", sort=False):
        g = g.sort_values("date").copy()
        g["pivot"] = g["high"].shift(1).rolling(35, min_periods=35).max()
        g["base_low"] = g["low"].shift(1).rolling(35, min_periods=35).min()
        g["base_depth"] = (g["pivot"] - g["base_low"]) / g["pivot"]
        g["avg_volume_50"] = g["volume"].shift(1).rolling(50, min_periods=50).mean()
        g["volume_ratio"] = g["volume"] / g["avg_volume_50"]
        for n in (63, 126, 189, 252):
            g[f"return_{n}d"] = g["adj_close"] / g["adj_close"].shift(n) - 1.0
        g["rs_proxy_raw"] = (
            0.40 * g["return_63d"]
            + 0.20 * g["return_126d"]
            + 0.20 * g["return_189d"]
            + 0.20 * g["return_252d"]
        )
        g["tminus1_to_t0"] = g["close"] / g["close"].shift(1) - 1.0
        g["h1_open"] = g["open"].shift(-1)
        g["h1_gap"] = g["h1_open"] / g["close"] - 1.0
        g["t0_pivot_extension"] = g["close"] / g["pivot"] - 1.0
        g["h1_fill_extension"] = g["h1_open"] / g["pivot"] - 1.0
        chunks.append(g)
    x = pd.concat(chunks, ignore_index=True)
    x["rs_percentile"] = x.groupby("date")["rs_proxy_raw"].rank(pct=True, method="average") * 100.0
    return x


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = s3_client()
    bucket = env("R2_BUCKET_NAME")

    ready_pointer = read_json(s3, bucket, READY_POINTER)
    if ready_pointer.get("schema_version") != 1:
        raise RuntimeError("Unsupported ready pointer schema")
    ready_payload = read_bytes(s3, bucket, ready_pointer["parquet_key"])
    verify(ready_payload, ready_pointer.get("sha256"), "ready OHLCV")
    prices = normalize_price_frame(pd.read_parquet(io.BytesIO(ready_payload)))
    if len(prices) != int(ready_pointer["rows"]):
        raise RuntimeError("Ready row count mismatch")
    if set(prices["security_id"].astype(str)) != set(map(str, ready_pointer["security_ids"])):
        raise RuntimeError("Ready security-id set mismatch")

    spy_pointer = read_json(s3, bucket, SPY_POINTER)
    spy_payload = read_bytes(s3, bucket, spy_pointer["parquet_key"])
    verify(spy_payload, spy_pointer.get("sha256"), "SPY benchmark")
    spy = pd.read_parquet(io.BytesIO(spy_payload)).copy()
    market = build_spy_market_state(spy)

    x = add_security_features(prices)
    x = x.merge(market, on="date", how="left")

    x["price_pass"] = x["close"] >= PRICE_FLOOR
    x["N_pass"] = (
        x["pivot"].notna()
        & (x["base_depth"] <= BASE_DEPTH_MAX)
        & (x["close"] > x["pivot"])
        & (x["close"] <= x["pivot"] * (1.0 + BUY_ZONE_MAX))
    )
    x["S_pass"] = x["volume_ratio"] >= VOLUME_RATIO_MIN
    x["L_pass"] = x["rs_percentile"] >= RS_PERCENTILE_MIN
    x["M_pass"] = x["M_pass_spy_only"].fillna(False)
    x["technical_pass"] = x[["price_pass", "N_pass", "S_pass", "L_pass", "M_pass"]].all(axis=1)

    eligible_feature_rows = x["rs_proxy_raw"].notna() & x["pivot"].notna() & x["avg_volume_50"].notna()
    eval_rows = x.loc[eligible_feature_rows].copy()
    candidates = eval_rows.loc[eval_rows["technical_pass"]].copy()

    candidate_cols = [
        "date", "security_id", "ticker", "close", "pivot", "base_depth", "volume_ratio",
        "rs_proxy_raw", "rs_percentile", "distribution_count_25", "spy_ftd_active",
        "tminus1_to_t0", "h1_open", "h1_gap", "t0_pivot_extension", "h1_fill_extension",
    ]
    candidates[candidate_cols].sort_values(["date", "ticker"]).to_csv(OUT / "candidates.csv", index=False)

    daily = eval_rows.groupby("date", as_index=False).agg(
        evaluable=("security_id", "nunique"),
        price_pass=("price_pass", "sum"),
        N_pass=("N_pass", "sum"),
        S_pass=("S_pass", "sum"),
        L_pass=("L_pass", "sum"),
        M_pass=("M_pass", "sum"),
        technical_pass=("technical_pass", "sum"),
    )
    daily.to_csv(OUT / "daily_summary.csv", index=False)

    summary = {
        "experiment": "E0-ROLLING-BASELINE-V1",
        "evidence_class": "ROLLING_CURRENT_MEMBERSHIP_SMOKE_NOT_FULL_PIT_BACKTEST",
        "trading_performance_metrics_used": False,
        "membership_scope": "current active compliant ready snapshot; historical bars are not historical membership",
        "market_proxy_scope": "SPY_ONLY; QQQ benchmark contract unavailable",
        "ready_pointer_key": READY_POINTER,
        "ready_snapshot_date": ready_pointer.get("snapshot_date"),
        "ready_created_at": ready_pointer.get("created_at"),
        "ready_parquet_key": ready_pointer.get("parquet_key"),
        "ready_parquet_sha256": ready_pointer.get("sha256"),
        "ready_securities": int(ready_pointer.get("securities", prices["security_id"].nunique())),
        "ready_rows": int(len(prices)),
        "price_first_date": str(prices["date"].min().date()),
        "price_last_date": str(prices["date"].max().date()),
        "spy_pointer_key": SPY_POINTER,
        "spy_parquet_key": spy_pointer.get("parquet_key"),
        "spy_sha256": spy_pointer.get("sha256"),
        "feature_evaluable_rows": int(len(eval_rows)),
        "feature_evaluable_dates": int(eval_rows["date"].nunique()),
        "technical_candidate_rows": int(len(candidates)),
        "technical_candidate_symbols": int(candidates["security_id"].nunique()),
        "technical_candidate_dates": int(candidates["date"].nunique()),
        "component_pass_rows": {
            "price": int(eval_rows["price_pass"].sum()),
            "N": int(eval_rows["N_pass"].sum()),
            "S": int(eval_rows["S_pass"].sum()),
            "L": int(eval_rows["L_pass"].sum()),
            "M_spy_only": int(eval_rows["M_pass"].sum()),
        },
        "frozen_thresholds": {
            "price_floor": PRICE_FLOOR,
            "base_lookback_sessions": 35,
            "max_base_depth": BASE_DEPTH_MAX,
            "buy_zone_max_extension": BUY_ZONE_MAX,
            "volume_ratio_min": VOLUME_RATIO_MIN,
            "rs_percentile_min": RS_PERCENTILE_MIN,
            "ftd_return_min": FTD_RETURN_MIN,
            "distribution_return_max": DISTRIBUTION_RETURN_MAX,
            "distribution_block_count": DISTRIBUTION_BLOCK_COUNT,
        },
        "limitations": [
            "Current ready membership is retroactively present across the rolling bars; this is not PIT historical membership.",
            "Ready OHLCV is capped at 300 bars per security, leaving only a short evaluable window after 252-day RS warm-up.",
            "M is SPY-only because no QQQ benchmark R2 contract is currently available.",
            "No PnL/PF/CAGR/drawdown verdict is permitted from this E0 smoke run.",
        ],
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    (OUT / "ready_pointer.json").write_text(json.dumps(ready_pointer, indent=2, sort_keys=True))
    (OUT / "spy_pointer.json").write_text(json.dumps(spy_pointer, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
