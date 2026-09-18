from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import boto3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from canslim_research.candidate_v2 import CandidateEvidence, DailyBar
from canslim_research.candidate_v2_adapters import l_screen_state
from canslim_research.fa_first_backtest import FundamentalPassInterval, monitor_pass_interval
from canslim_research.historical_i_adapter import HistoricalIEvent, resolve_historical_i
from canslim_research.historical_market_adapter import decision_on, replay_historical_market
from canslim_research.market_state_v1 import IndexBar

PINNED_ONEIL_SHA = "c433cc1e35a5aa32a46f732cd8c5545935e36e40"
DEFAULT_INTERVAL = FundamentalPassInterval(
    interval_id="MEDP-2021-07-27__2021-10-26",
    security_id="US58506Q1094",
    ticker="MEDP",
    start_date="2021-07-27",
    end_date="2021-10-26",
    state_identity="historical-fundamental-screener-v1:35175083156:MEDP:2021-07-27",
)


def need(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"missing {name}")
    return value


def s3_client():
    return boto3.client(
        "s3", endpoint_url=need("R2_ENDPOINT"), region_name="auto",
        aws_access_key_id=need("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=need("R2_SECRET_ACCESS_KEY"),
    )


def raw(s3, bucket: str, key: str) -> bytes:
    return s3.get_object(Bucket=bucket, Key=key)["Body"].read()


def js(s3, bucket: str, key: str) -> dict:
    return json.loads(raw(s3, bucket, key))


def pq(s3, bucket: str, key: str) -> pd.DataFrame:
    return pd.read_parquet(io.BytesIO(raw(s3, bucket, key)))


def historical_ohlcv(s3, bucket: str, security_id: str) -> pd.DataFrame:
    """Read the canonical full-history object backing frozen #35 semantics."""
    key = f"history/ohlcv/{security_id}.parquet"
    try:
        return pq(s3, bucket, key)
    except s3.exceptions.NoSuchKey as exc:
        raise RuntimeError(f"HISTORICAL_OHLCV_MISSING:{security_id}:{key}") from exc


def ensure_oneil_checkout(target: Path) -> None:
    subprocess.run(["git", "clone", "-q", "https://github.com/azharmz/ussy-oneil-patterns.git", str(target)], check=True)
    subprocess.run(["git", "-C", str(target), "checkout", "-q", PINNED_ONEIL_SHA], check=True)
    sys.path.insert(0, str(target / "src"))


def daily_bars(df: pd.DataFrame) -> list[DailyBar]:
    x = df.copy()
    x["date"] = pd.to_datetime(x["date"], errors="raise").dt.date.astype(str)
    return [
        DailyBar(str(r.date), float(r.open), float(r.high), float(r.low), float(r.close), float(r.volume))
        for r in x.sort_values("date").itertuples(index=False)
    ]


def _index_object_key(index_meta: dict, *, index_id: str) -> str:
    """Resolve #49 market-index manifest objects without changing frozen M semantics."""
    for field in ("key", "parquet_key", "object_key"):
        value = index_meta.get(field)
        if isinstance(value, str) and value:
            return value
    raise RuntimeError(
        f"MARKET_INDEX_MANIFEST_KEY_UNRESOLVED:{index_id}:fields={sorted(index_meta)}"
    )


def market_replay(s3, bucket: str):
    ptr = js(s3, bucket, "market/indexes/official.json")
    manifest = js(s3, bucket, ptr["manifest_key"])
    indexes = manifest.get("indexes")
    if not isinstance(indexes, dict):
        raise RuntimeError("MARKET_INDEX_MANIFEST_INDEXES_INVALID")
    series = {}
    for index_id in ("NASDAQ_COMPOSITE", "SP500", "DJIA"):
        meta = indexes.get(index_id)
        if not isinstance(meta, dict):
            raise RuntimeError(f"MARKET_INDEX_MANIFEST_INDEX_MISSING:{index_id}")
        df = pq(s3, bucket, _index_object_key(meta, index_id=index_id))
        df["date"] = pd.to_datetime(df["date"], errors="raise").dt.date.astype(str)
        series[index_id] = tuple(
            IndexBar(str(r.date), float(r.low), float(r.close), None if pd.isna(r.volume) else float(r.volume))
            for r in df.sort_values("date").itertuples(index=False)
        )
    return replay_historical_market(index_series=series)


def historical_i_events(s3, bucket: str, security_id: str) -> list[HistoricalIEvent]:
    ptr = js(s3, bucket, "institutional_sponsorship/current.json")
    hist = pq(s3, bucket, ptr["history_state_events_key"])
    cusip = security_id[2:11]
    hist = hist[hist["cusip"].astype(str).str.upper().eq(cusip)].copy()
    return [
        HistoricalIEvent(
            cusip=str(r.cusip), period_of_report=str(r.period_of_report),
            available_on=str(r.available_on), manager_count=int(r.I_manager_count),
            uncertain=str(r.lineage_action).startswith("AMBIGUOUS"),
        )
        for r in hist.sort_values(["available_on", "period_of_report"]).itertuples(index=False)
    ]


def rs_percentile_for_day(s3, bucket: str, asof: str) -> float | None:
    # Production L ranks the full governed cross-section, not the PASS subset.
    # Read each frozen full-history object only through as-of and reproduce
    # production add_rs() semantics.
    ready = js(s3, bucket, "production/ready/current.json")
    universe = pq(s3, bucket, ready["parquet_key"])[["security_id"]].drop_duplicates()
    values = []
    target_raw = None
    for sid in universe["security_id"].astype(str):
        try:
            df = historical_ohlcv(s3, bucket, sid)
        except Exception:
            continue
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date.astype(str)
        g = df[df["date"].le(asof)].sort_values("date")
        if len(g) <= 252:
            continue
        a = g["adj_close"].astype(float)
        raw_value = .40*(a.iloc[-1]/a.iloc[-64]-1)+.20*(a.iloc[-1]/a.iloc[-127]-1)+.20*(a.iloc[-1]/a.iloc[-190]-1)+.20*(a.iloc[-1]/a.iloc[-253]-1)
        values.append((sid, raw_value))
        if sid == DEFAULT_INTERVAL.security_id:
            target_raw = raw_value
    if target_raw is None or not values:
        return None
    s = pd.Series([v for _, v in values])
    # exact pandas production rank(pct=True, method='average')
    pct = float(s.rank(pct=True, method="average").iloc[[v for _,v in values].index(target_raw)] * 100.0)
    return pct


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--interval", default="MEDP_2021", choices=["MEDP_2021"])
    p.add_argument("--output", type=Path, default=Path("artifacts/fa_first_medp_2021.json"))
    a = p.parse_args()

    s3 = s3_client(); bucket = need("R2_BUCKET_NAME")
    interval = DEFAULT_INTERVAL
    stock = historical_ohlcv(s3, bucket, interval.security_id)
    bars = daily_bars(stock)
    m_decisions = market_replay(s3, bucket)
    i_events = historical_i_events(s3, bucket, interval.security_id)

    # L is cross-sectional and materially more expensive than the other evidence.
    # Compute it only on dates on which #33 emits an assessment, never for the
    # whole universe x all dates.
    l_cache: dict[str, float | None] = {}

    with tempfile.TemporaryDirectory() as td:
        oneil = Path(td) / "oneil"
        ensure_oneil_checkout(oneil)
        from oneil_patterns.production.engine import analyze_security

        def pattern_runner(security_id: str, decision_date: str, prefix):
            frame = pd.DataFrame([{
                "date": b.session_date, "security_id": security_id, "ticker": interval.ticker,
                "open": b.open, "high": b.high, "low": b.low, "close": b.close,
                "adj_close": float(stock.loc[pd.to_datetime(stock["date"]).dt.date.astype(str).eq(b.session_date), "adj_close"].iloc[-1]),
                "volume": b.volume,
            } for b in prefix])
            decision_day = pd.Timestamp(decision_date).date()
            return [r.to_dict() for r in analyze_security(security_id, interval.ticker, frame, decision_day)]

        def evidence_provider(_interval, decision_date):
            m = decision_on(m_decisions, decision_date)
            inst = resolve_historical_i(security_id=interval.security_id, asof_date=decision_date, events=i_events)
            if decision_date not in l_cache:
                l_cache[decision_date] = rs_percentile_for_day(s3, bucket, decision_date)
            l_pct = l_cache[decision_date]
            l_state, _ = l_screen_state(l_pct)
            return CandidateEvidence(
                C_screen_state="PASS", A_screen_state="PASS",
                L_individual_leadership_state=l_state,
                M_entry_state=m.M_entry_state,
                I_evidence_state=inst.state,
                rs_rating_proxy_percentile=l_pct,
                M_market_state=m.market_state,
            )

        events = monitor_pass_interval(interval, bars, pattern_runner=pattern_runner, evidence_provider=evidence_provider)

    out = {
        "runner": "fa-first-medp-2021-one-interval-v0.1",
        "oneil_sha": PINNED_ONEIL_SHA,
        "interval": interval.__dict__ if hasattr(interval, "__dict__") else {
            k: getattr(interval, k) for k in interval.__dataclass_fields__
        },
        "event_count": len(events),
        "signal_count": sum(e.signal for e in events),
        "events": [{k: getattr(e, k) for k in e.__dataclass_fields__} for e in events],
        "strategy_returns_inspected": False,
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k:v for k,v in out.items() if k != "events"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
