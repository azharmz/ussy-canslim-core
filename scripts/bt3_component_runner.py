from __future__ import annotations

"""BT3 reproducible component-runner scaffold.

This runner is deliberately fail-closed: it inventories governed historical OHLCV,
selects a deterministic bounded smoke sample, records provenance, and emits only
BT_PV_COMPONENT_* research metadata. It does not manufacture M evidence and does
not emit CANSLIM_ELIGIBLE or strategy performance.
"""
import argparse, hashlib, json, os, subprocess
from datetime import datetime, timezone
import boto3

LABEL = "BT_PV_COMPONENT_INPUT_READY"
FORBIDDEN = "CANSLIM_ELIGIBLE"
ONEIL_SHA = "c433cc1e35a5aa32a46f732cd8c5545935e36e40"


def need(name: str) -> str:
    v=os.getenv(name)
    if not v: raise RuntimeError(f"missing {name}")
    return v


def s3():
    return boto3.client("s3", endpoint_url=need("R2_ENDPOINT"), region_name="auto",
        aws_access_key_id=need("R2_ACCESS_KEY_ID"), aws_secret_access_key=need("R2_SECRET_ACCESS_KEY"))


def list_keys(client,bucket,prefix):
    out=[]; token=None
    while True:
        kw={"Bucket":bucket,"Prefix":prefix}
        if token: kw["ContinuationToken"]=token
        r=client.list_objects_v2(**kw); out += [x["Key"] for x in r.get("Contents",[])]
        if not r.get("IsTruncated"): return sorted(out)
        token=r["NextContinuationToken"]


def git_sha():
    return subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()


def main():
    p=argparse.ArgumentParser(); p.add_argument("--prefix",default="backtest/ohlcv/"); p.add_argument("--sample-size",type=int,default=10); p.add_argument("--output",default="bt3-component-smoke-manifest.json"); a=p.parse_args()
    if a.sample_size < 1: raise RuntimeError("sample-size must be positive")
    client=s3(); bucket=need("R2_BUCKET_NAME"); keys=[k for k in list_keys(client,bucket,a.prefix) if k.endswith(".parquet")]
    if not keys: raise RuntimeError("no governed historical OHLCV parquet objects found")
    sample=keys[:min(a.sample_size,len(keys))]
    identities=[k.rsplit("/",1)[-1].removesuffix(".parquet") for k in sample]
    out={
      "contract":"BT3_COMPONENT_RUNNER_V1","status":LABEL,"generated_at":datetime.now(timezone.utc).isoformat(),
      "repository_sha":git_sha(),"oneil_dependency_sha":ONEIL_SHA,"ohlcv_prefix":a.prefix,"ohlcv_object_count":len(keys),
      "smoke_sample_size":len(sample),"smoke_sample_keys":sample,"smoke_sample_identities":identities,
      "sample_selection":"lexicographically_first_N_v1","m_status":"NOT_EVALUABLE",
      "m_blocker":"NO_HISTORICAL_GOVERNED_LEADERSHIP_WEAKENING_CORRECTION_RESET_EVIDENCE",
      "production_eligibility_emitted":False,"forbidden_production_label":FORBIDDEN,"strategy_returns_inspected":False,
      "future_information_used":False,"next_phase":"BT4_COMPONENT_EVENT_RECONSTRUCTION_SMOKE"
    }
    payload=json.dumps(out,indent=2,sort_keys=True)+"\n"; open(a.output,"w",encoding="utf-8").write(payload); print(payload,end="")

if __name__=="__main__": main()
