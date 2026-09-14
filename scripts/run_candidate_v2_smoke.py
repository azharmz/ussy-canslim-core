from __future__ import annotations

import io
import json
import os
import sys
from datetime import date
from pathlib import Path

import boto3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from canslim_research.candidate_v2 import DailyBar, PatternAssessment, build_candidate
from canslim_research.candidate_v2_adapters import AnnualEpsObservation, build_candidate_evidence
from canslim_research.decision_time import regular_close_cutoff
from canslim_research.institutional_pit import resolve_institutional_pit, validate_institutional_pointer
from canslim_research.technical import DISTRIBUTION_BLOCK_COUNT, DISTRIBUTION_RETURN_MAX, FTD_RETURN_MIN
from oneil_patterns.production.engine import analyze_security
from oneil_patterns.production.runner import run_from_r2

OUT = ROOT / "results" / "candidate-v2-smoke"
SPY_POINTER = "benchmarks/SPY/current.json"
FUND_POINTER = "fundamentals/current.json"
I_POINTER = "institutional_sponsorship/current.json"


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


def read_parquet(s3, bucket: str, key: str) -> pd.DataFrame:
    return pd.read_parquet(io.BytesIO(read_bytes(s3, bucket, key)))


def read_csv(s3, bucket: str, key: str) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(read_bytes(s3, bucket, key)), dtype={"security_id": "string", "cusip": "string"})


def latest_asof_ready_date(s3, bucket: str) -> date:
    ptr = read_json(s3, bucket, "production/ready/current.json")
    frame = read_parquet(s3, bucket, ptr["parquet_key"])
    return pd.to_datetime(frame["date"], errors="raise").dt.date.max()


def build_spy_state(spy: pd.DataFrame) -> pd.DataFrame:
    # Temporary #34 smoke dependency only. Phase 4 replaces this local calculation
    # with the governed #49/#50 canonical M contract.
    x = spy.sort_values("date").copy()
    x["date"] = pd.to_datetime(x["date"], errors="raise").dt.normalize()
    x["ret1"] = x["close"].pct_change()
    x["prev_volume"] = x["volume"].shift(1)
    x["distribution"] = (x["ret1"] <= DISTRIBUTION_RETURN_MAX) & (x["volume"] > x["prev_volume"])
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
            rally_day = 0
            waiting = False
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
            if rally_day >= 4 and pd.notna(ret1) and float(ret1) >= FTD_RETURN_MIN and pd.notna(prev_volume) and float(row["volume"]) > float(prev_volume):
                confirmed = True
        dist = int(row["distribution_count_25"])
        if not confirmed:
            states.append("CORRECTION")
        elif dist >= DISTRIBUTION_BLOCK_COUNT:
            states.append("UPTREND_UNDER_PRESSURE")
        else:
            states.append("CONFIRMED_UPTREND")
    x["M_market_state"] = states
    return x[["date", "M_market_state"]]


def add_rs(prices: pd.DataFrame) -> pd.DataFrame:
    chunks = []
    for _, g in prices.groupby("security_id", sort=False):
        g = g.sort_values("date").copy()
        for n in (63, 126, 189, 252):
            g[f"ret_{n}"] = g["adj_close"] / g["adj_close"].shift(n) - 1.0
        g["rs_raw"] = 0.40*g["ret_63"] + 0.20*g["ret_126"] + 0.20*g["ret_189"] + 0.20*g["ret_252"]
        chunks.append(g)
    x = pd.concat(chunks, ignore_index=True)
    x["rs_percentile"] = x.groupby("date")["rs_raw"].rank(pct=True, method="average") * 100.0
    return x


def load_fundamentals(s3, bucket: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    ptr = read_json(s3, bucket, FUND_POINTER)
    manifest = read_json(s3, bucket, ptr["manifest_key"])
    artifacts = manifest["artifacts"]
    wide = read_parquet(s3, bucket, artifacts["fundamentals_point_in_time.parquet"]["key"])
    long = read_parquet(s3, bucket, artifacts["fundamentals_point_in_time_long.parquet"]["key"])
    return wide, long


def load_institutional(s3, bucket: str) -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ptr = read_json(s3, bucket, I_POINTER)
    manifest = read_json(s3, bucket, ptr["manifest_key"])
    validate_institutional_pointer(ptr, manifest)
    live = read_csv(s3, bucket, ptr["live_sponsorship_mapped_key"])
    history = read_parquet(s3, bucket, ptr["history_state_events_key"])
    uncertainty = read_parquet(s3, bucket, ptr["uncertainty_state_events_key"])
    provenance = {
        "pointer_schema_version": ptr["schema_version"],
        "snapshot_prefix": ptr["snapshot_prefix"],
        "manifest_key": ptr["manifest_key"],
        "publisher_run_id": str(ptr["publisher_run_id"]),
        "live_source_run_id": str(ptr["live_source_run_id"]),
        "live_availability": ptr["live_availability"],
    }
    return provenance, live, history, uncertainty


def pick_col(df: pd.DataFrame, names: list[str]) -> str | None:
    return next((name for name in names if name in df.columns), None)


def fundamental_evidence(wide: pd.DataFrame, long: pd.DataFrame, ticker: str, asof: str):
    session_date = date.fromisoformat(asof)
    information_cutoff = pd.Timestamp(regular_close_cutoff(session_date))
    w_symbol = pick_col(wide, ["symbol", "ticker"])
    w_accept = pick_col(wide, ["accepted_at", "filed_at"])
    eps_yoy = pick_col(wide, ["quarterly_eps_yoy", "eps_yoy"])
    if not all([w_symbol, w_accept, eps_yoy]):
        return None, None, []
    w = wide[wide[w_symbol].astype(str) == ticker].copy()
    if w.empty:
        return None, None, []
    w[w_accept] = pd.to_datetime(w[w_accept], errors="coerce", utc=True)
    w = w[w[w_accept] <= information_cutoff].sort_values(w_accept)
    if w.empty:
        return None, None, []
    latest = w.iloc[-1]
    q_eps = None if pd.isna(latest[eps_yoy]) else float(latest[eps_yoy])
    q_available = latest[w_accept].isoformat()
    l_symbol = pick_col(long, ["symbol", "ticker"])
    l_fy = pick_col(long, ["fiscal_year", "fy"])
    l_accept = pick_col(long, ["accepted_at", "filed_at"])
    l_eps = pick_col(long, ["annual_eps"])
    annual: list[AnnualEpsObservation] = []
    if all([l_symbol, l_fy, l_accept, l_eps]):
        rows = long[long[l_symbol].astype(str) == ticker].copy()
        if "form" in rows.columns:
            rows = rows[rows["form"].astype(str).str.upper().isin(["10-K", "10-K/A"])]
        rows[l_accept] = pd.to_datetime(rows[l_accept], errors="coerce", utc=True)
        rows = rows[rows[l_accept] <= information_cutoff].sort_values([l_fy, l_accept]).drop_duplicates(l_fy, keep="last")
        for _, r in rows.iterrows():
            if pd.notna(r[l_fy]) and pd.notna(r[l_eps]) and pd.notna(r[l_accept]):
                annual.append(AnnualEpsObservation(int(r[l_fy]), float(r[l_eps]), r[l_accept].isoformat()))
    return q_eps, q_available, annual


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = s3_client()
    bucket = env("R2_BUCKET_NAME")
    asof = latest_asof_ready_date(s3, bucket)
    p33 = run_from_r2(s3, bucket=bucket, asof_date=asof, analyze_security=analyze_security)
    pattern_rows = [PatternAssessment.from_mapping(r.to_dict()) for r in p33.records]
    ready_ptr = read_json(s3, bucket, "production/ready/current.json")
    prices = read_parquet(s3, bucket, ready_ptr["parquet_key"])
    prices["date"] = pd.to_datetime(prices["date"], errors="raise").dt.normalize()
    prices = add_rs(prices)
    spy_ptr = read_json(s3, bucket, SPY_POINTER)
    spy = read_parquet(s3, bucket, spy_ptr["parquet_key"])
    market = build_spy_state(spy)
    wide, long = load_fundamentals(s3, bucket)
    i_provenance, i_live, i_history, i_uncertainty = load_institutional(s3, bucket)

    latest_date = pd.Timestamp(asof)
    rs_day = prices[prices["date"] == latest_date][["security_id", "rs_percentile"]].copy()
    rs_map = dict(zip(rs_day["security_id"].astype(str), rs_day["rs_percentile"]))
    m_rows = market[market["date"] <= latest_date]
    market_state = None if m_rows.empty else str(m_rows.iloc[-1]["M_market_state"])
    by_security = {str(k): g.sort_values("date") for k, g in prices.groupby("security_id")}
    output = []
    i_counts: dict[str, int] = {}
    for p in pattern_rows:
        g = by_security.get(p.security_id)
        if g is None:
            continue
        bars = [DailyBar(r.date.date().isoformat(), float(r.open), float(r.high), float(r.low), float(r.close), float(r.volume)) for r in g.itertuples()]
        q_eps, q_available, annual = fundamental_evidence(wide, long, p.ticker, p.asof_date)
        cutoff = regular_close_cutoff(date.fromisoformat(p.asof_date))
        inst = resolve_institutional_pit(
            security_id=p.security_id, decision_cutoff=cutoff,
            live_state=i_live, history_events=i_history, uncertainty_events=i_uncertainty)
        i_counts[inst.state] = i_counts.get(inst.state, 0) + 1
        adapted = build_candidate_evidence(
            asof_date=p.asof_date,
            quarterly_eps_yoy=q_eps, quarterly_available_on=q_available, annual_eps=annual,
            rs_rating_proxy_percentile=None if pd.isna(rs_map.get(p.security_id)) else float(rs_map[p.security_id]),
            market_state=market_state,
            fund_count_latest=inst.fund_count_latest,
            fund_count_prior=inst.fund_count_prior,
            institutional_available_on=p.asof_date if inst.fund_count_latest is not None and inst.fund_count_prior is not None else None,
        )
        candidate = build_candidate(p, bars, adapted.evidence)
        row = candidate.__dict__ if hasattr(candidate, "__dict__") else {name: getattr(candidate, name) for name in candidate.__dataclass_fields__}
        row["rs_rating_proxy_percentile"] = adapted.rs_rating_proxy_percentile
        row["annual_eps_growth_measure"] = adapted.annual_eps_growth_measure
        row["evidence_adapter_reason_codes"] = list(adapted.reason_codes)
        row["I_pit_state"] = inst.state
        row["I_pit_reason"] = inst.reason
        row["I_fund_count_latest"] = inst.fund_count_latest
        row["I_fund_count_prior"] = inst.fund_count_prior
        row["I_latest_period"] = inst.latest_period
        row["I_prior_period"] = inst.prior_period
        row["I_latest_available_at"] = inst.latest_available_at
        row["I_prior_available_on"] = inst.prior_available_on
        row["I_cusip"] = inst.cusip
        row["I_snapshot_prefix"] = i_provenance["snapshot_prefix"]
        row["I_publisher_run_id"] = i_provenance["publisher_run_id"]
        row["I_live_source_run_id"] = i_provenance["live_source_run_id"]
        output.append(row)

    (OUT / "patterns.jsonl").write_text(p33.jsonl, encoding="utf-8")
    (OUT / "pattern_manifest.json").write_text(json.dumps(p33.manifest.__dict__ if hasattr(p33.manifest, "__dict__") else {name: getattr(p33.manifest, name) for name in p33.manifest.__dataclass_fields__}, indent=2, sort_keys=True, default=str), encoding="utf-8")
    pd.DataFrame(output).to_json(OUT / "candidates.jsonl", orient="records", lines=True)
    counts = pd.Series([x["candidate_stage"] for x in output]).value_counts().to_dict() if output else {}
    status_counts = pd.Series([x["pattern_status"] for x in output]).value_counts().to_dict() if output else {}
    summary = {
        "workstream": 34, "mode": "LIVE_R2_SMOKE", "asof_date": asof.isoformat(),
        "decision_asof_timestamp": regular_close_cutoff(asof).isoformat(),
        "market_session": "REGULAR_US_SESSION_CLOSE", "information_cutoff": regular_close_cutoff(asof).isoformat(),
        "pattern_schema": "oneil-pattern-output-v2", "pattern_record_count": len(pattern_rows),
        "candidate_record_count": len(output), "candidate_stage_counts": {str(k): int(v) for k, v in counts.items()},
        "pattern_status_counts": {str(k): int(v) for k, v in status_counts.items()},
        "advanced_patterns_allowed": False, "trading_performance_metrics_used": False,
        "m_proxy": "SPY_ONLY_TRANSPARENT_PROXY_PHASE4_DEBT",
        "i_contract": "CANONICAL_R2_LIVE_EXACT_ACCEPTED_AT_PLUS_CONSERVATIVE_PRIOR",
        "i_state_counts": i_counts, "i_provenance": i_provenance,
        "industry_state": "NOT_IMPLEMENTED",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
