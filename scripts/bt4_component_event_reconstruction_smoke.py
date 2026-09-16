from __future__ import annotations

"""BT4 bounded historical component-event reconstruction smoke.

Research-only. This deliberately does not invent N/S semantics or M evidence.
It verifies that governed OHLCV can be read causally for the deterministic BT3
sample and reconstructs only frozen L evidence where its exact implementation is
available in this repository. O'Neil execution is kept pinned to the frozen
external dependency and is not reimplemented here.
"""
import argparse, io, json, os, subprocess
from datetime import datetime, timezone

import boto3
import pandas as pd

from canslim_research.leader_candidate_selector_cycle1_v1 import (
    MembershipRecord, select_candidate_cohort, VERSION as L_VERSION,
)

ONEIL_SHA = "c433cc1e35a5aa32a46f732cd8c5545935e36e40"
FORBIDDEN = "CANSLIM_ELIGIBLE"


def need(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"missing {name}")
    return value


def client():
    return boto3.client("s3", endpoint_url=need("R2_ENDPOINT"), region_name="auto",
        aws_access_key_id=need("R2_ACCESS_KEY_ID"), aws_secret_access_key=need("R2_SECRET_ACCESS_KEY"))


def git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def read_parquet(s3, bucket: str, key: str) -> pd.DataFrame:
    body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    frame = pd.read_parquet(io.BytesIO(body))
    frame.columns = [str(c).lower() for c in frame.columns]
    date_col = next((c for c in ("date", "session_date", "datetime") if c in frame.columns), None)
    close_col = next((c for c in ("adj_close", "adjusted_close", "close") if c in frame.columns), None)
    if date_col is None or close_col is None:
        raise RuntimeError(f"{key}: date/close columns unavailable: {list(frame.columns)}")
    frame = frame[[date_col, close_col]].rename(columns={date_col:"date", close_col:"close"}).dropna()
    frame["date"] = pd.to_datetime(frame["date"], utc=True, errors="coerce").dt.tz_localize(None)
    frame = frame.dropna().sort_values("date").drop_duplicates("date", keep="last")
    if len(frame) < 252:
        raise RuntimeError(f"{key}: fewer than 252 usable bars")
    return frame


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--bt3-manifest", default="bt3-component-smoke-manifest.json")
    p.add_argument("--output", default="bt4-component-event-smoke.json")
    args=p.parse_args()
    bt3=json.load(open(args.bt3_manifest, encoding="utf-8"))
    if bt3.get("oneil_dependency_sha") != ONEIL_SHA:
        raise RuntimeError("BT3 O'Neil dependency pin mismatch")
    keys=list(bt3.get("smoke_sample_keys") or [])
    ids=list(bt3.get("smoke_sample_identities") or [])
    if not keys or len(keys) != len(ids):
        raise RuntimeError("BT3 sample is empty or malformed")

    s3=client(); bucket=need("R2_BUCKET_NAME")
    frames={sid:read_parquet(s3,bucket,key) for sid,key in zip(ids,keys)}
    common=set.intersection(*(set(f.date) for f in frames.values()))
    common_dates=sorted(common)
    if len(common_dates) < 252:
        raise RuntimeError(f"sample has only {len(common_dates)} common sessions")
    decision_date=common_dates[-1]
    histories={}
    for sid,frame in frames.items():
        causal=frame[frame.date <= decision_date].tail(252)
        if len(causal) < 252: raise RuntimeError(f"{sid}: insufficient causal window")
        histories[sid]=causal.close.astype(float).tolist()

    # L is cross-sectional. The frozen implementation requires a benchmark.
    # BT4 smoke does not fabricate/substitute one; use the deterministic sample
    # median path only as a mechanics input and explicitly mark L semantic output
    # NOT_AUTHORIZED until canonical benchmark alignment is wired.
    matrix=pd.DataFrame({sid:histories[sid] for sid in ids})
    mechanics_benchmark=matrix.median(axis=1).tolist()
    membership=[MembershipRecord(security_id=sid,symbol=sid) for sid in ids]
    mechanics=select_candidate_cohort(membership,histories,mechanics_benchmark)

    output={
      "contract":"BT4_COMPONENT_EVENT_RECONSTRUCTION_SMOKE_V1",
      "status":"MECHANICS_PASS_SEMANTIC_GATES_PRESERVED",
      "generated_at":datetime.now(timezone.utc).isoformat(),
      "repository_sha":git_sha(),"bt3_repository_sha":bt3.get("repository_sha"),
      "oneil_dependency_sha":ONEIL_SHA,"decision_date":decision_date.date().isoformat(),
      "sample_size":len(ids),"common_sessions":len(common_dates),
      "causal_window_sessions":252,"future_information_used":False,
      "strategy_returns_inspected":False,"production_eligibility_emitted":False,
      "forbidden_production_label":FORBIDDEN,
      "components":{
        "ONEIL":{"state":"PINNED_NOT_EXECUTED_IN_REPO_SMOKE","reason":"FROZEN_EXTERNAL_DEPENDENCY_NOT_REIMPLEMENTED","dependency_sha":ONEIL_SHA},
        "N":{"state":"NOT_EVALUABLE","reason":"NO_FROZEN_HISTORICAL_N_RECONSTRUCTOR_IDENTIFIED_IN_REPOSITORY"},
        "S":{"state":"NOT_EVALUABLE","reason":"NO_FROZEN_HISTORICAL_S_RECONSTRUCTOR_IDENTIFIED_IN_REPOSITORY"},
        "L":{"state":"MECHANICS_ONLY_NOT_SEMANTICALLY_AUTHORIZED","reason":"CANONICAL_SP500_BENCHMARK_NOT_WIRED_IN_THIS_BOUNDED_SMOKE","implementation_version":L_VERSION,
             "mechanics_state_counts":{state:sum(r.state==state for r in mechanics) for state in sorted(set(r.state for r in mechanics))}},
        "M":{"state":"NOT_EVALUABLE","reason":"BLOCKED_ON_HISTORICAL_M_SEMANTIC_EVIDENCE"}
      },
      "next_phase":"BT4_WIRE_CANONICAL_COMPONENT_INPUTS"
    }
    payload=json.dumps(output,indent=2,sort_keys=True)+"\n"
    open(args.output,"w",encoding="utf-8").write(payload); print(payload,end="")

if __name__ == "__main__": main()
