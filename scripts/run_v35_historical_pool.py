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
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from canslim_research.candidate_v2 import DailyBar, PatternAssessment, build_candidate
from canslim_research.candidate_v2_adapters import build_candidate_evidence
from canslim_research.validation_corpus_v1 import select_corpus
from oneil_patterns.production.engine import analyze_security
from scripts.run_candidate_v2_smoke import build_spy_state, fundamental_evidence, load_fundamentals, read_json, read_parquet

OUT = ROOT / "results" / "v35-historical-pool"
ANCHORS = [f"{year}-{md}" for year in range(2021, 2026) for md in ("03-31", "06-30", "09-30", "12-31")]
SECURITY_SAMPLE_SIZE = 60
MIN_BARS = 300


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable {name}")
    return value


def s3_client():
    return boto3.client("s3", endpoint_url=env("R2_ENDPOINT"), aws_access_key_id=env("R2_ACCESS_KEY_ID"), aws_secret_access_key=env("R2_SECRET_ACCESS_KEY"), region_name="auto")


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
    resolved = []
    for anchor in ANCHORS:
        eligible = dates[dates <= pd.Timestamp(anchor)]
        if not eligible.empty:
            resolved.append(eligible.iloc[-1])
    return resolved


def rs_percentiles(histories: dict[str, pd.DataFrame], asof: pd.Timestamp) -> dict[str, float]:
    raw: dict[str, float] = {}
    for sid, frame in histories.items():
        x = frame[frame["date"] <= asof]
        if len(x) < 253 or "adj_close" not in x:
            continue
        values = x["adj_close"].astype(float)
        returns = [values.iloc[-1] / values.iloc[-1-n] - 1.0 for n in (63, 126, 189, 252)]
        raw[sid] = 0.40*returns[0] + 0.20*returns[1] + 0.20*returns[2] + 0.20*returns[3]
    if not raw:
        return {}
    scores = pd.Series(raw, dtype=float)
    return (scores.rank(pct=True, method="average") * 100.0).to_dict()


def as_dict(obj) -> dict:
    return {name: getattr(obj, name) for name in obj.__dataclass_fields__}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = s3_client()
    bucket = env("R2_BUCKET_NAME")
    keys = list_history_keys(s3, bucket)
    if not keys:
        raise RuntimeError("No backtest/ohlcv history objects found")

    histories: dict[str, pd.DataFrame] = {}
    tickers: dict[str, str] = {}
    for key in keys:
        sid = key.removeprefix("backtest/ohlcv/").removesuffix(".parquet")
        frame = load_history(s3, bucket, key)
        histories[sid] = frame
        tickers[sid] = str(frame["ticker"].iloc[-1]) if "ticker" in frame and not frame.empty else sid

    selected_ids = sorted(histories, key=security_rank)[:SECURITY_SAMPLE_SIZE]
    spy_ptr = read_json(s3, bucket, "benchmarks/SPY/current.json")
    spy = read_parquet(s3, bucket, spy_ptr["parquet_key"])
    dates = resolve_dates(spy)
    market = build_spy_state(spy)
    market["date"] = pd.to_datetime(market["date"]).dt.normalize()
    wide, long = load_fundamentals(s3, bucket)

    rows: list[dict] = []
    availability: list[dict] = []
    for asof in dates:
        rs_map = rs_percentiles(histories, asof)
        m = market[market["date"] <= asof]
        market_state = None if m.empty else str(m.iloc[-1]["M_market_state"])
        for sid in selected_ids:
            pit = histories[sid][histories[sid]["date"] <= asof].copy()
            if len(pit) < MIN_BARS:
                availability.append({"security_id": sid, "asof_date": asof.date().isoformat(), "state": "INSUFFICIENT_HISTORY", "bars": len(pit)})
                continue
            window = pit.tail(MIN_BARS).copy()
            ticker = tickers[sid]
            assessments = analyze_security(sid, ticker, window[["date", "open", "high", "low", "close", "volume"]], asof.date())
            availability.append({"security_id": sid, "asof_date": asof.date().isoformat(), "state": "EVALUATED", "bars": len(window), "assessments": len(assessments)})
            if not assessments:
                continue
            bars = [DailyBar(r.date.date().isoformat(), float(r.open), float(r.high), float(r.low), float(r.close), float(r.volume)) for r in window.itertuples()]
            q_eps, q_available, annual = fundamental_evidence(wide, long, ticker, asof.date().isoformat())
            adapted = build_candidate_evidence(asof_date=asof.date().isoformat(), quarterly_eps_yoy=q_eps, quarterly_available_on=q_available, annual_eps=annual, rs_rating_proxy_percentile=rs_map.get(sid), market_state=market_state)
            for item in assessments:
                pattern = PatternAssessment.from_mapping(item.to_dict())
                row = as_dict(build_candidate(pattern, bars, adapted.evidence))
                row["annual_eps_growth_measure"] = adapted.annual_eps_growth_measure
                row["evidence_adapter_reason_codes"] = list(adapted.reason_codes)
                rows.append(row)

    pd.DataFrame(rows).to_json(OUT / "observations.jsonl", orient="records", lines=True)
    pd.DataFrame(availability).to_csv(OUT / "availability.csv", index=False)
    selected = select_corpus(rows)
    (OUT / "selected_manifest.json").write_text(json.dumps(selected, indent=2, sort_keys=True, default=str), encoding="utf-8")
    summary = {
        "workstream": 35,
        "corpus_version": "v35-independent-corpus-v1",
        "anchors": ANCHORS,
        "resolved_asof_dates": [x.date().isoformat() for x in dates],
        "history_object_count": len(keys),
        "security_sample_size": len(selected_ids),
        "morphology_window_bars": MIN_BARS,
        "security_sampling": "sha256(v35-security-frame|security_id)",
        "observation_count": len(rows),
        "selected_case_count": len(selected),
        "selected_status_counts": pd.Series([x["pattern_status"] for x in selected]).value_counts().to_dict() if selected else {},
        "future_performance_fields_used": False,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
