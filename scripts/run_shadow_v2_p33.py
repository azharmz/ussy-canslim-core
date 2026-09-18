"""Run frozen #33 only for identities in a validated v2 watchlist checkpoint.

Shadow-only: reads R2, writes local artifact, never mutates production pointers.
"""
from __future__ import annotations
import hashlib, io, json, os, sys
from pathlib import Path
import boto3, pandas as pd
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from oneil_patterns.data.r2_ready import ReadyDataset, REQUIRED_COLUMNS
from oneil_patterns.production.engine import analyze_security
from oneil_patterns.production.runner import run_ready_dataset

ONEIL_REPO_SHA="c433cc1e35a5aa32a46f732cd8c5545935e36e40"

def env(n):
    v=os.getenv(n)
    if not v: raise RuntimeError(f"missing {n}")
    return v

def main():
    cp=json.loads(Path(env("CANSLIM_V2_WATCHLIST_INPUT")).read_text())
    if cp.get("contract_version")!="canslim-watchlist-contract-v2": raise RuntimeError("WATCHLIST_CONTRACT_MISMATCH")
    ids=set(map(str,cp.get("qualified_security_ids",[])))
    if len(ids)!=int(cp["qualified_count"]): raise RuntimeError("WATCHLIST_QUALIFIED_ID_COUNT_MISMATCH")
    lin=cp["lineage"]; decision=pd.Timestamp(lin["decision_date"]).date()

    s3=boto3.client("s3",endpoint_url=env("R2_ENDPOINT"),region_name="auto",aws_access_key_id=env("R2_ACCESS_KEY_ID"),aws_secret_access_key=env("R2_SECRET_ACCESS_KEY"))
    payload=s3.get_object(Bucket=env("R2_BUCKET_NAME"),Key=lin["ready_key"])["Body"].read()
    if hashlib.sha256(payload).hexdigest()!=lin["ready_sha256"]: raise RuntimeError("READY_SHA256_MISMATCH")
    ready=pd.read_parquet(io.BytesIO(payload)); missing=set(REQUIRED_COLUMNS)-set(ready.columns)
    if missing: raise RuntimeError(f"READY_MISSING_COLUMNS:{sorted(missing)}")
    frame=ready.loc[ready["security_id"].astype(str).isin(ids),REQUIRED_COLUMNS].copy()
    frame["date"]=pd.to_datetime(frame["date"],errors="raise").dt.normalize()
    frame=frame.loc[frame["date"].dt.date<=decision].sort_values(["security_id","date"]).reset_index(drop=True)
    actual=set(frame["security_id"].astype(str).unique())
    if actual!=ids: raise RuntimeError(f"QUALIFIED_READY_ID_MISMATCH expected={sorted(ids)} actual={sorted(actual)}")
    if frame.duplicated(["security_id","date"]).any(): raise RuntimeError("READY_DUPLICATE_SECURITY_DATE")

    dataset=ReadyDataset(frame=frame,manifest={"contract":"CANSLIM_V2_SHADOW_QUALIFIED_TO_FROZEN_ONEIL","watchlist_sha256":cp["content_sha256"],"oneil_repo_sha":ONEIL_REPO_SHA,"security_ids":sorted(ids)})
    result=run_ready_dataset(dataset,asof_date=decision,analyze_security=analyze_security)
    rows=[x.to_dict() for x in result.records]
    out={"decision_date":decision.isoformat(),"oneil_repo_sha":ONEIL_REPO_SHA,"watchlist_sha256":cp["content_sha256"],"scanned_security_ids":sorted(ids),"assessment_count":len(rows),"records":rows}
    target=Path(os.getenv("CANSLIM_V2_P33_OUTPUT","shadow-v2-p33.json")); target.write_text(json.dumps(out,default=str,sort_keys=True))
    print(json.dumps({"decision_date":decision.isoformat(),"scanned":sorted(ids),"assessments":len(rows),"output":str(target)}))

if __name__=="__main__": main()
