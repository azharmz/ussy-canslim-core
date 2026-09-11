from __future__ import annotations

import io
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

from canslim_research.technical import (  # noqa: E402
    BASE_DEPTH_MAX, BUY_ZONE_MAX, DISTRIBUTION_BLOCK_COUNT,
    DISTRIBUTION_RETURN_MAX, FTD_RETURN_MIN, PRICE_FLOOR,
    RS_PERCENTILE_MIN, VOLUME_RATIO_MIN,
)
from run_e0_static_history_candidates import (  # noqa: E402
    MEMBERSHIP_KEY, list_keys, load_security, read_bytes, read_json, s3_client, verify,
)
from run_entry_timing_basis_test import load_history  # noqa: E402
from run_portfolio_construction_v1 import prepare_trade_candidates, run_portfolio  # noqa: E402
from run_robustness_v1 import apply_frozen_censored_accounting  # noqa: E402

OUT = ROOT / "results" / "full-m-validation-v1"
SPY_POINTER = "benchmarks/SPY/current.json"
QQQ_POINTER = "benchmarks/QQQ/current.json"


def build_market_state(frame: pd.DataFrame, prefix: str) -> pd.DataFrame:
    x = frame.sort_values("date").copy()
    x["date"] = pd.to_datetime(x["date"], errors="raise").dt.normalize()
    x["ret1"] = x["close"].pct_change()
    x["prev_volume"] = x["volume"].shift(1)
    x["distribution"] = (x["ret1"] <= DISTRIBUTION_RETURN_MAX) & (x["volume"] > x["prev_volume"])
    x[f"{prefix}_distribution_count_25"] = x["distribution"].rolling(25, min_periods=1).sum().astype(int)
    prior_10_low = x["close"].shift(1).rolling(10, min_periods=10).min()
    confirmed = False
    waiting = False
    rally_day = 0
    rally_low = np.nan
    active = []
    for i, row in x.iterrows():
        close = float(row["close"])
        ret1 = row["ret1"]
        vol = row["volume"]
        prev_vol = row["prev_volume"]
        is_10_low = pd.notna(prior_10_low.loc[i]) and close <= float(prior_10_low.loc[i])
        if confirmed and pd.notna(rally_low) and close < float(rally_low):
            confirmed, waiting, rally_day, rally_low = False, False, 0, np.nan
        if is_10_low and not confirmed:
            waiting = True
            rally_day = 0
            rally_low = close if pd.isna(rally_low) else min(float(rally_low), close)
        if not confirmed:
            if waiting and pd.notna(ret1) and float(ret1) > 0:
                rally_day, waiting = 1, False
            elif rally_day > 0:
                rally_day += 1
            if (rally_day >= 4 and pd.notna(ret1) and float(ret1) >= FTD_RETURN_MIN
                    and pd.notna(prev_vol) and float(vol) > float(prev_vol)):
                confirmed = True
        active.append(bool(confirmed))
    x[f"{prefix}_ftd_active"] = active
    return x[["date", f"{prefix}_distribution_count_25", f"{prefix}_ftd_active"]]


def load_pointer_frame(s3, bucket: str, key: str, ticker: str) -> tuple[dict, pd.DataFrame]:
    pointer = read_json(s3, bucket, key)
    if pointer.get("ticker") != ticker:
        raise RuntimeError(f"{ticker} pointer identity mismatch")
    payload = read_bytes(s3, bucket, pointer["parquet_key"])
    verify(payload, pointer.get("sha256"), ticker)
    frame = pd.read_parquet(io.BytesIO(payload))
    return pointer, frame


def pf_metrics(trades: pd.DataFrame) -> tuple[float | None, float | None, int]:
    r = pd.to_numeric(trades.get("realized_return"), errors="coerce").dropna() if len(trades) else pd.Series(dtype=float)
    def pf(s: pd.Series):
        gp = float(s[s > 0].sum())
        gl = float(-s[s < 0].sum())
        return gp / gl if gl > 0 else None
    base = pf(r)
    if len(r):
        top_idx = r.nlargest(min(10, len(r))).index
        ex = pf(r.drop(index=top_idx))
    else:
        ex = None
    return base, ex, int(len(r))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for p in OUT.iterdir():
        if p.is_file(): p.unlink()
    s3 = s3_client()
    bucket = os.environ["R2_BUCKET_NAME"]
    membership = read_json(s3, bucket, MEMBERSHIP_KEY)
    eligible = {str(r["security_id"]): str(r.get("ticker") or "") for r in membership.get("records", []) if r.get("sharia_compliance") == "COMPLIANT"}
    available = list_keys(s3, bucket, "backtest/ohlcv/")
    selected = [(sid, ticker) for sid, ticker in eligible.items() if f"backtest/ohlcv/{sid}.parquet" in available]

    frames, failures = [], []
    with ThreadPoolExecutor(max_workers=16) as pool:
        futs = {pool.submit(load_security, s3, bucket, sid, ticker): sid for sid, ticker in selected}
        for fut in as_completed(futs):
            sid = futs[fut]
            try:
                f = fut.result()
                if not f.empty: frames.append(f)
            except Exception as exc:
                failures.append({"security_id": sid, "error": str(exc)[:300]})
    if failures or not frames:
        raise RuntimeError(f"Feature load failure: {failures[:5]}")
    x = pd.concat(frames, ignore_index=True)
    x["rs_percentile"] = x.groupby("date")["rs_proxy_raw"].rank(pct=True, method="average") * 100.0

    spy_ptr, spy = load_pointer_frame(s3, bucket, SPY_POINTER, "SPY")
    qqq_ptr, qqq = load_pointer_frame(s3, bucket, QQQ_POINTER, "QQQ")
    market = build_market_state(spy, "spy").merge(build_market_state(qqq, "qqq"), on="date", how="outer")
    x = x.merge(market, on="date", how="left")

    x["non_m_pass"] = (
        (x["close"] >= PRICE_FLOOR)
        & x["pivot"].notna() & (x["base_depth"] <= BASE_DEPTH_MAX)
        & (x["close"] > x["pivot"]) & (x["close"] <= x["pivot"] * (1.0 + BUY_ZONE_MAX))
        & (x["volume_ratio"] >= VOLUME_RATIO_MIN)
        & (x["rs_percentile"] >= RS_PERCENTILE_MIN)
    )
    x["M0_SPY_ONLY"] = x["spy_ftd_active"].fillna(False) & (x["spy_distribution_count_25"].fillna(999) < DISTRIBUTION_BLOCK_COUNT)
    x["M1_DUAL"] = (
        (x["spy_ftd_active"].fillna(False) | x["qqq_ftd_active"].fillna(False))
        & (x[["spy_distribution_count_25", "qqq_distribution_count_25"]].max(axis=1, skipna=False).fillna(999) < DISTRIBUTION_BLOCK_COUNT)
    )
    base_cols = ["date", "security_id", "ticker", "close", "pivot", "base_depth", "volume_ratio", "rs_proxy_raw", "rs_percentile",
                 "tminus1_to_t0", "h1_open", "h1_gap", "t0_pivot_extension", "h1_fill_extension"]
    tracks = {
        "M0_SPY_ONLY": x.loc[x["non_m_pass"] & x["M0_SPY_ONLY"], base_cols].copy(),
        "M1_DUAL": x.loc[x["non_m_pass"] & x["M1_DUAL"], base_cols].copy(),
    }
    for df in tracks.values():
        df["security_id"] = df["security_id"].astype(str)
        df["date"] = pd.to_datetime(df["date"]).dt.normalize()

    keys0 = set(zip(tracks["M0_SPY_ONLY"].security_id, tracks["M0_SPY_ONLY"].date))
    keys1 = set(zip(tracks["M1_DUAL"].security_id, tracks["M1_DUAL"].date))
    overlap = {"both": len(keys0 & keys1), "m0_only": len(keys0 - keys1), "m1_only": len(keys1 - keys0)}

    ids = sorted(set().union(*[set(df.security_id) for df in tracks.values()]))
    histories, failures = {}, []
    with ThreadPoolExecutor(max_workers=16) as pool:
        futs = {pool.submit(load_history, s3, bucket, sid): sid for sid in ids}
        for fut in as_completed(futs):
            sid = futs[fut]
            try: histories[sid] = fut.result()
            except Exception as exc: failures.append({"security_id": sid, "error": str(exc)[:300]})
    if failures: raise RuntimeError(f"History load failure: {failures[:5]}")

    rows = []
    for track, candidates in tracks.items():
        candidates.to_csv(OUT / f"candidates-{track.lower()}.csv", index=False)
        for variant in ("X1", "X3"):
            tc = prepare_trade_candidates(variant, candidates, histories)
            pf, pf_ex10, realized_n = pf_metrics(tc)
            accepted, skipped, curve, port = run_portfolio(variant, tc, histories)
            curve, port, censor = apply_frozen_censored_accounting(variant, accepted, curve, port)
            rows.append({
                "track": track, "variant": variant,
                "candidate_count": int(len(candidates)), "candidate_trade_count": int(len(tc)),
                "realized_trade_count": realized_n, "trade_pf": pf, "trade_pf_ex_top10": pf_ex10,
                "portfolio_entries": int(port["portfolio_entry_count"]),
                "gross_cagr": port.get("gross_cagr"), "gross_max_drawdown": port.get("gross_max_drawdown"),
                "cost20bp_cagr": port.get("cost20bp_rt_cagr"), "cost20bp_max_drawdown": port.get("cost20bp_rt_max_drawdown"),
                "final_censored_positions": port.get("final_censored_position_count", 0),
            })
    result = pd.DataFrame(rows)
    result.to_csv(OUT / "comparison.csv", index=False)
    summary = {
        "experiment": "FULL_M_VALIDATION_V1",
        "evidence_class": "RETROSPECTIVE_HISTORICAL_SIDECAR_NOT_OOS",
        "methodology": "docs/methodology/full-m-validation-v1.md",
        "m0": "SPY FTD active AND SPY distribution_count_25 < 6",
        "m1": "(SPY OR QQQ FTD active) AND max(SPY,QQQ distribution_count_25) < 6",
        "candidate_overlap": overlap,
        "results": rows,
        "spy_pointer": {"parquet_key": spy_ptr.get("parquet_key"), "sha256": spy_ptr.get("sha256"), "last_date": spy_ptr.get("last_date")},
        "qqq_pointer": {"parquet_key": qqq_ptr.get("parquet_key"), "sha256": qqq_ptr.get("sha256"), "last_date": qqq_ptr.get("last_date")},
        "fwd1_modified": False,
        "guardrail": "No result from this retrospective sidecar changes frozen FWD1. Any promoted M1 requires a new versioned forward clock.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
