from __future__ import annotations

import io
import json
import os
from collections import Counter

import boto3
import pandas as pd

from canslim_research.market_state_v1 import IndexBar, MarketState, classify_market

INDEX_IDS = ("NASDAQ_COMPOSITE", "SP500", "DJIA")


def need(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"missing {name}")
    return value


def s3_client():
    return boto3.client("s3", endpoint_url=need("R2_ENDPOINT"), region_name="auto",
        aws_access_key_id=need("R2_ACCESS_KEY_ID"), aws_secret_access_key=need("R2_SECRET_ACCESS_KEY"))


def get_json(s3, bucket: str, key: str) -> dict:
    return json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())


def get_df(s3, bucket: str, key: str) -> pd.DataFrame:
    return pd.read_parquet(io.BytesIO(s3.get_object(Bucket=bucket, Key=key)["Body"].read()))


def main() -> None:
    s3 = s3_client(); bucket = need("R2_BUCKET_NAME")
    pointer = get_json(s3, bucket, "market/indexes/official.json")
    manifest = get_json(s3, bucket, pointer["manifest_key"])
    frames: dict[str, pd.DataFrame] = {}
    for index_id in INDEX_IDS:
        df = get_df(s3, bucket, manifest["indexes"][index_id]["key"])
        df["date"] = pd.to_datetime(df["date"], utc=True).dt.strftime("%Y-%m-%d")
        frames[index_id] = df.sort_values("date").reset_index(drop=True)

    common_dates = sorted(set.intersection(*(set(df["date"]) for df in frames.values())))
    prior_state = MarketState.NOT_EVALUABLE.value
    state_counts: Counter[str] = Counter(); reason_counts: Counter[str] = Counter()
    transitions: Counter[str] = Counter(); first_date: dict[str, str] = {}; previous_emitted = None
    for date in common_dates:
        series: dict[str, list[IndexBar]] = {}
        for index_id, df in frames.items():
            hist = df[df["date"] <= date]
            series[index_id] = [IndexBar(str(r.date), float(r.low), float(r.close), None if pd.isna(r.volume) else float(r.volume)) for r in hist.itertuples(index=False)]
        result = classify_market(index_series=series, prior_state=prior_state,
            leadership_confirming=None, weakening_confirmed=None, correction_reset=False)
        state_counts[result.state] += 1; reason_counts[result.reason] += 1; first_date.setdefault(result.state, date)
        if previous_emitted is not None and previous_emitted != result.state: transitions[f"{previous_emitted}->{result.state}"] += 1
        previous_emitted = result.state; prior_state = result.state

    mechanical_ready = bool(common_dates and len(common_dates) >= 1000)
    # The frozen production classifier accepts externally governed leadership,
    # weakening and correction-reset evidence. Historical canonical sources for
    # those inputs do not exist in BT1-M. Passing None/False is faithful to the
    # evidence boundary but cannot authorize a representative historical M replay.
    semantic_inputs_complete = False
    historical_authorized = mechanical_ready and semantic_inputs_complete
    out = {
        "audit":"BT1_MARKET_CAUSAL_REPLAY_V2","classifier_version":"46-market-state-classification-v1",
        "official_run_id":pointer["run_id"],"common_sessions":len(common_dates),
        "date_min":common_dates[0] if common_dates else None,"date_max":common_dates[-1] if common_dates else None,
        "initial_prior_state":MarketState.NOT_EVALUABLE.value,"leadership_confirming":None,
        "weakening_confirmed":None,"correction_reset":False,"unsupported_evidence_fabricated":False,
        "future_bars_supplied":False,"state_counts":dict(sorted(state_counts.items())),
        "reason_counts":dict(sorted(reason_counts.items())),"first_state_date":dict(sorted(first_date.items())),
        "transitions":dict(sorted(transitions.items())),"strategy_returns_inspected":False,
        "mechanical_long_history_ready":mechanical_ready,"historical_semantic_inputs_complete":semantic_inputs_complete,
        "semantic_blocker":"NO_HISTORICAL_GOVERNED_LEADERSHIP_WEAKENING_CORRECTION_RESET_EVIDENCE",
        "historical_m_replay_authorized":historical_authorized,
        "verdict":"BLOCKED_ON_HISTORICAL_M_SEMANTIC_EVIDENCE" if not historical_authorized else "AUTHORIZED"
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__": main()
