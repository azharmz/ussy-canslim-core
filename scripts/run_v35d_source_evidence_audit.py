from __future__ import annotations

import io
import json
import os
from pathlib import Path

import boto3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evidence" / "v35" / "frozen_case_ids_v1.csv"
OUT = ROOT / "results" / "v35d-source-evidence"


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


def read_json(s3, bucket: str, key: str) -> dict:
    return json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())


def read_parquet(s3, bucket: str, key: str) -> pd.DataFrame:
    payload = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    return pd.read_parquet(io.BytesIO(payload))


def list_history_keys(s3, bucket: str) -> list[str]:
    keys: list[str] = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix="backtest/ohlcv/"):
        keys.extend(x["Key"] for x in page.get("Contents", []) if x["Key"].endswith(".parquet"))
    return sorted(keys)


def load_histories(s3, bucket: str) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    for key in list_history_keys(s3, bucket):
        sid = key.removeprefix("backtest/ohlcv/").removesuffix(".parquet")
        frame = read_parquet(s3, bucket, key)
        frame["date"] = pd.to_datetime(frame["date"], errors="raise").dt.normalize()
        out[sid] = frame.sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)
    return out


def rs_for_date(histories: dict[str, pd.DataFrame], asof: pd.Timestamp) -> dict[str, float]:
    raw: dict[str, float] = {}
    for sid, frame in histories.items():
        x = frame[frame["date"] <= asof]
        if len(x) < 253 or "adj_close" not in x.columns:
            continue
        v = x["adj_close"].astype(float)
        if v.iloc[-253] <= 0:
            continue
        rets = [v.iloc[-1] / v.iloc[-1-n] - 1.0 for n in (63, 126, 189, 252)]
        raw[sid] = 0.40 * rets[0] + 0.20 * rets[1] + 0.20 * rets[2] + 0.20 * rets[3]
    if not raw:
        return {}
    s = pd.Series(raw, dtype=float)
    return (s.rank(pct=True, method="average") * 100.0).to_dict()


def build_market_states(spy: pd.DataFrame) -> pd.DataFrame:
    x = spy.sort_values("date").copy()
    x["date"] = pd.to_datetime(x["date"], errors="raise").dt.normalize()
    x["ret1"] = x["close"].pct_change()
    x["prev_volume"] = x["volume"].shift(1)
    x["distribution"] = (x["ret1"] <= -0.002) & (x["volume"] > x["prev_volume"])
    x["distribution_count_25"] = x["distribution"].rolling(25, min_periods=1).sum().astype(int)
    prior_10_low = x["close"].shift(1).rolling(10, min_periods=10).min()
    confirmed = False
    waiting = False
    rally_day = 0
    rally_low = None
    states: list[str] = []
    for i, row in x.iterrows():
        close = float(row["close"])
        ret1 = row["ret1"]
        prev_volume = row["prev_volume"]
        is_low = pd.notna(prior_10_low.loc[i]) and close <= float(prior_10_low.loc[i])
        if confirmed and rally_low is not None and close < rally_low:
            confirmed = False
            waiting = False
            rally_day = 0
            rally_low = None
        if is_low and not confirmed:
            waiting = True
            rally_day = 0
            rally_low = close if rally_low is None else min(rally_low, close)
        if not confirmed:
            if waiting and pd.notna(ret1) and float(ret1) > 0:
                rally_day = 1
                waiting = False
            elif rally_day > 0:
                rally_day += 1
            if rally_day >= 4 and pd.notna(ret1) and float(ret1) >= 0.01 and pd.notna(prev_volume) and float(row["volume"]) > float(prev_volume):
                confirmed = True
        if not confirmed:
            states.append("CORRECTION")
        elif int(row["distribution_count_25"]) >= 6:
            states.append("UPTREND_UNDER_PRESSURE")
        else:
            states.append("CONFIRMED_UPTREND")
    x["M_market_state"] = states
    return x[["date", "M_market_state"]]


def pick_col(df: pd.DataFrame, names: list[str]) -> str | None:
    return next((x for x in names if x in df.columns), None)


def load_fundamentals(s3, bucket: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    ptr = read_json(s3, bucket, "fundamentals/current.json")
    manifest = read_json(s3, bucket, ptr["manifest_key"])
    art = manifest["artifacts"]
    return (
        read_parquet(s3, bucket, art["fundamentals_point_in_time.parquet"]["key"]),
        read_parquet(s3, bucket, art["fundamentals_point_in_time_long.parquet"]["key"]),
    )


def fundamental_states(wide: pd.DataFrame, long: pd.DataFrame, ticker: str, asof: str) -> dict:
    cutoff = pd.Timestamp(asof, tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    w_symbol = pick_col(wide, ["symbol", "ticker"])
    w_accept = pick_col(wide, ["accepted_at", "filed_at"])
    eps_yoy_col = pick_col(wide, ["quarterly_eps_yoy", "eps_yoy"])
    q_eps = None
    q_available = None
    if all([w_symbol, w_accept, eps_yoy_col]):
        w = wide[wide[w_symbol].astype(str) == ticker].copy()
        w[w_accept] = pd.to_datetime(w[w_accept], errors="coerce", utc=True)
        w = w[w[w_accept] <= cutoff].sort_values(w_accept)
        if not w.empty:
            q = w.iloc[-1]
            q_available = q[w_accept].date().isoformat() if pd.notna(q[w_accept]) else None
            q_eps = None if pd.isna(q[eps_yoy_col]) else float(q[eps_yoy_col])
    if q_available is None:
        c_state = "NOT_EVALUABLE"
    elif q_eps is None:
        c_state = "NOT_EVALUABLE"
    else:
        c_state = "PASS" if q_eps >= 0.25 else "FAIL"

    l_symbol = pick_col(long, ["symbol", "ticker"])
    l_fy = pick_col(long, ["fiscal_year", "fy"])
    l_accept = pick_col(long, ["accepted_at", "filed_at"])
    l_eps = pick_col(long, ["annual_eps"])
    annual_rows: list[tuple[int, float, str]] = []
    if all([l_symbol, l_fy, l_accept, l_eps]):
        z = long[long[l_symbol].astype(str) == ticker].copy()
        if "form" in z.columns:
            z = z[z["form"].astype(str).str.upper().isin(["10-K", "10-K/A"])]
        z[l_accept] = pd.to_datetime(z[l_accept], errors="coerce", utc=True)
        z = z[z[l_accept] <= cutoff].sort_values([l_fy, l_accept]).drop_duplicates(l_fy, keep="last")
        for _, row in z.iterrows():
            if pd.notna(row[l_fy]) and pd.notna(row[l_eps]) and pd.notna(row[l_accept]):
                annual_rows.append((int(row[l_fy]), float(row[l_eps]), row[l_accept].date().isoformat()))
    a_growth = None
    a_state = "NOT_EVALUABLE"
    if len(annual_rows) >= 4:
        win = annual_rows[-4:]
        years = [x[0] for x in win]
        if years == list(range(years[0], years[0] + 4)) and win[0][1] > 0 and win[-1][1] > 0:
            a_growth = (win[-1][1] / win[0][1]) ** (1.0 / 3.0) - 1.0
            a_state = "PASS" if a_growth >= 0.25 else "FAIL"
    max_annual_available = max((x[2] for x in annual_rows), default=None)
    return {
        "observed_C_state": c_state,
        "quarterly_eps_yoy": q_eps,
        "quarterly_available_on": q_available,
        "observed_A_state": a_state,
        "observed_A_growth": a_growth,
        "annual_latest_available_on": max_annual_available,
        "annual_observation_count": len(annual_rows),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cases = pd.read_csv(CASES, dtype=str)
    s3 = s3_client()
    bucket = env("R2_BUCKET_NAME")
    histories = load_histories(s3, bucket)
    wide, long = load_fundamentals(s3, bucket)
    spy_ptr = read_json(s3, bucket, "benchmarks/SPY/current.json")
    spy = read_parquet(s3, bucket, spy_ptr["parquet_key"])
    market = build_market_states(spy)
    market["date"] = pd.to_datetime(market["date"]).dt.normalize()

    unique_dates = sorted(pd.to_datetime(cases["asof_date"]).dt.normalize().unique())
    rs_cache = {pd.Timestamp(d): rs_for_date(histories, pd.Timestamp(d)) for d in unique_dates}
    rows = []
    for case in cases.itertuples(index=False):
        asof = pd.Timestamp(case.asof_date)
        f = fundamental_states(wide, long, case.ticker, case.asof_date)
        rs = rs_cache[asof].get(case.security_id)
        l_state = "NOT_EVALUABLE" if rs is None else ("PASS" if float(rs) >= 80.0 else "FAIL")
        mr = market[market["date"] <= asof]
        m_market = "UNKNOWN" if mr.empty else str(mr.iloc[-1]["M_market_state"])
        m_map = {
            "CONFIRMED_UPTREND": "ALLOW_NEW_BUYS",
            "UPTREND_UNDER_PRESSURE": "CAUTION",
            "CORRECTION": "BLOCK_NEW_BUYS",
            "UNKNOWN": "NOT_EVALUABLE",
        }
        rows.append({
            "validation_case_id": case.validation_case_id,
            "security_id": case.security_id,
            "ticker": case.ticker,
            "asof_date": case.asof_date,
            **f,
            "observed_rs_percentile": rs,
            "observed_L_state": l_state,
            "observed_M_market_state": m_market,
            "observed_M_entry_state": m_map[m_market],
            "rs_uses_data_through": case.asof_date,
            "m_uses_data_through": case.asof_date,
        })
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "observed_source_evidence.csv", index=False)
    pit_bad = out[
        ((out["quarterly_available_on"].notna()) & (out["quarterly_available_on"] > out["asof_date"]))
        | ((out["annual_latest_available_on"].notna()) & (out["annual_latest_available_on"] > out["asof_date"]))
    ]
    summary = {
        "case_count": len(out),
        "history_object_count": len(histories),
        "pit_availability_violation_count": len(pit_bad),
        "future_performance_fields_used": False,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if len(out) != 60 or len(pit_bad):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
