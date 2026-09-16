from __future__ import annotations

"""BT4 bounded historical component-event reconstruction smoke.

Research-only. Uses the canonical official S&P 500 series for the frozen L
mechanics. It does not invent N/S semantics or M evidence. O'Neil stays pinned
to the frozen external dependency and is not reimplemented here.
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
MARKET_POINTER_KEY = "market/indexes/official.json"


def need(name: str) -> str:
    value=os.getenv(name)
    if not value: raise RuntimeError(f"missing {name}")
    return value


def client():
    return boto3.client("s3", endpoint_url=need("R2_ENDPOINT"), region_name="auto",
        aws_access_key_id=need("R2_ACCESS_KEY_ID"), aws_secret_access_key=need("R2_SECRET_ACCESS_KEY"))


def git_sha() -> str:
    return subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()


def get_json(s3,bucket,key):
    return json.loads(s3.get_object(Bucket=bucket,Key=key)["Body"].read())


def get_parquet(s3,bucket,key):
    return pd.read_parquet(io.BytesIO(s3.get_object(Bucket=bucket,Key=key)["Body"].read()))


def normalize(frame: pd.DataFrame, key: str) -> pd.DataFrame:
    frame=frame.copy(); frame.columns=[str(c).lower() for c in frame.columns]
    date_col=next((c for c in ("date","session_date","datetime") if c in frame.columns),None)
    close_col=next((c for c in ("adj_close","adjusted_close","close") if c in frame.columns),None)
    if date_col is None or close_col is None: raise RuntimeError(f"{key}: date/close unavailable")
    frame=frame[[date_col,close_col]].rename(columns={date_col:"date",close_col:"close"}).dropna()
    frame["date"]=pd.to_datetime(frame["date"],utc=True,errors="coerce").dt.tz_localize(None)
    return frame.dropna().sort_values("date").drop_duplicates("date",keep="last")


def read_parquet(s3,bucket,key):
    frame=normalize(get_parquet(s3,bucket,key),key)
    if len(frame)<252: raise RuntimeError(f"{key}: fewer than 252 usable bars")
    return frame


def main():
    p=argparse.ArgumentParser(); p.add_argument("--bt3-manifest",default="bt3-component-smoke-manifest.json"); p.add_argument("--output",default="bt4-component-event-smoke.json"); args=p.parse_args()
    bt3=json.load(open(args.bt3_manifest,encoding="utf-8"))
    if bt3.get("oneil_dependency_sha")!=ONEIL_SHA: raise RuntimeError("BT3 O'Neil dependency pin mismatch")
    keys=list(bt3.get("smoke_sample_keys") or []); ids=list(bt3.get("smoke_sample_identities") or [])
    if not keys or len(keys)!=len(ids): raise RuntimeError("BT3 sample is empty or malformed")

    s3=client(); bucket=need("R2_BUCKET_NAME")
    frames={sid:read_parquet(s3,bucket,key) for sid,key in zip(ids,keys)}
    common_dates=sorted(set.intersection(*(set(f.date) for f in frames.values())))
    if len(common_dates)<252: raise RuntimeError(f"sample has only {len(common_dates)} common sessions")
    decision_date=common_dates[-1]

    pointer=get_json(s3,bucket,MARKET_POINTER_KEY)
    manifest=get_json(s3,bucket,pointer["manifest_key"])
    sp_meta=manifest["indexes"]["SP500"]
    sp500=normalize(get_parquet(s3,bucket,sp_meta["key"]),sp_meta["key"])

    histories={}; aligned_dates=None
    for sid,frame in frames.items():
        dates=set(frame.loc[frame.date<=decision_date,"date"])
        aligned_dates=dates if aligned_dates is None else aligned_dates & dates
    aligned_dates=sorted(aligned_dates & set(sp500.loc[sp500.date<=decision_date,"date"]))[-252:]
    if len(aligned_dates)<252: raise RuntimeError("fewer than 252 stock/SP500 aligned causal sessions")
    for sid,frame in frames.items():
        indexed=frame.set_index("date"); histories[sid]=[float(indexed.loc[d,"close"]) for d in aligned_dates]
    sp_indexed=sp500.set_index("date"); benchmark=[float(sp_indexed.loc[d,"close"]) for d in aligned_dates]

    membership=[MembershipRecord(security_id=sid,symbol=sid) for sid in ids]
    l_results=select_candidate_cohort(membership,histories,benchmark)
    counts={state:sum(r.state==state for r in l_results) for state in sorted(set(r.state for r in l_results))}

    output={
      "contract":"BT4_COMPONENT_EVENT_RECONSTRUCTION_SMOKE_V2","status":"L_CANONICAL_BENCHMARK_WIRED",
      "generated_at":datetime.now(timezone.utc).isoformat(),"repository_sha":git_sha(),"bt3_repository_sha":bt3.get("repository_sha"),
      "oneil_dependency_sha":ONEIL_SHA,"decision_date":decision_date.date().isoformat(),"sample_size":len(ids),"common_sessions":len(common_dates),
      "causal_window_sessions":252,"future_information_used":False,"strategy_returns_inspected":False,"production_eligibility_emitted":False,"forbidden_production_label":FORBIDDEN,
      "components":{
        "ONEIL":{"state":"PINNED_NOT_EXECUTED_IN_REPO_SMOKE","reason":"FROZEN_EXTERNAL_DEPENDENCY_NOT_REIMPLEMENTED","dependency_sha":ONEIL_SHA},
        "N":{"state":"NOT_EVALUABLE","reason":"NO_FROZEN_HISTORICAL_N_RECONSTRUCTOR_IDENTIFIED_IN_REPOSITORY"},
        "S":{"state":"NOT_EVALUABLE","reason":"NO_FROZEN_HISTORICAL_S_RECONSTRUCTOR_IDENTIFIED_IN_REPOSITORY"},
        "L":{"state":"CANONICAL_INPUT_WIRED","implementation_version":L_VERSION,"benchmark_identity":"SP500","benchmark_pointer_key":MARKET_POINTER_KEY,"benchmark_manifest_key":pointer["manifest_key"],"benchmark_object_key":sp_meta["key"],"aligned_sessions":len(aligned_dates),"state_counts":counts},
        "M":{"state":"NOT_EVALUABLE","reason":"BLOCKED_ON_HISTORICAL_M_SEMANTIC_EVIDENCE"}
      },
      "next_phase":"BT4_IDENTIFY_FROZEN_N_S_AND_EXECUTE_PINNED_ONEIL"
    }
    payload=json.dumps(output,indent=2,sort_keys=True)+"\n"; open(args.output,"w",encoding="utf-8").write(payload); print(payload,end="")

if __name__=="__main__": main()
