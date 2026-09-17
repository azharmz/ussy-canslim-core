from __future__ import annotations

import argparse
from dataclasses import asdict, is_dataclass
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
from typing import Any

import boto3
import pandas as pd
from oneil_patterns.landmarks.confirmed_window import extract_confirmed_window_landmarks
from oneil_patterns.landmarks.excursion import extract_excursion_landmarks
from oneil_patterns.production.engine import analyze_security
import oneil_patterns.validation.canonical_predictions as canonical

from bt5c_authorized_reuse import FROZEN_ONEIL_SHA, analyze_with_authorized_reuse, normalize_ohlcv, precompute_raw_landmarks
from historical_bt5_checkpoint import BT5_CONTRACT, CANONICAL_HISTORY_PREFIX, ReplayLineage, config_sha256, inventory_sha256, make_checkpoint, validate_checkpoint

OUTPUT_SCHEMA = "HISTORICAL_BT5_COMPONENT_OUTPUT_V1"
DEFAULT_OUTPUT_PREFIX = "research/canslim/historical_bt5/v1/"


def need(name: str) -> str:
    value = os.getenv(name)
    if not value: raise RuntimeError(f"BT5_MISSING_ENV:{name}")
    return value


def s3_client():
    return boto3.client("s3", endpoint_url=need("R2_ENDPOINT"), region_name="auto", aws_access_key_id=need("R2_ACCESS_KEY_ID"), aws_secret_access_key=need("R2_SECRET_ACCESS_KEY"))


def list_inventory(s3, bucket: str, prefix: str) -> list[dict[str, Any]]:
    rows=[]; token=None
    while True:
        kw={"Bucket":bucket,"Prefix":prefix}
        if token: kw["ContinuationToken"]=token
        r=s3.list_objects_v2(**kw)
        for obj in r.get("Contents",[]):
            if obj["Key"].endswith(".parquet"):
                rows.append({"key":obj["Key"],"etag":str(obj.get("ETag","")).strip('"'),"size":int(obj["Size"])})
        if not r.get("IsTruncated"): break
        token=r["NextContinuationToken"]
    return sorted(rows,key=lambda x:x["key"])


def sha256_bytes(data: bytes) -> str: return hashlib.sha256(data).hexdigest()


def read_json_object(s3,bucket,key):
    try: raw=s3.get_object(Bucket=bucket,Key=key)["Body"].read()
    except s3.exceptions.NoSuchKey: return None
    return json.loads(raw)


def put_json(s3,bucket,key,payload):
    raw=(json.dumps(payload,sort_keys=True,separators=(",",":"),default=str)+"\n").encode()
    s3.put_object(Bucket=bucket,Key=key,Body=raw,ContentType="application/json")
    return {"key":key,"sha256":sha256_bytes(raw),"bytes":len(raw),"encoding":"identity"}


def put_json_gzip(s3,bucket,key,payload):
    logical=(json.dumps(payload,sort_keys=True,separators=(",",":"),default=str)+"\n").encode()
    stored=gzip.compress(logical,compresslevel=6,mtime=0)
    s3.put_object(Bucket=bucket,Key=key,Body=stored,ContentType="application/json",ContentEncoding="gzip")
    return {"key":key,"logical_sha256":sha256_bytes(logical),"stored_sha256":sha256_bytes(stored),"logical_bytes":len(logical),"stored_bytes":len(stored),"encoding":"gzip"}


def serialize_record(x):
    if is_dataclass(x): return asdict(x)
    if hasattr(x,"model_dump"): return x.model_dump()
    if isinstance(x,dict): return x
    raise TypeError(f"BT5_UNSUPPORTED_RECORD:{type(x).__name__}")


def checkpoint_key(prefix,experiment_id): return f"{prefix.rstrip('/')}/checkpoints/{experiment_id}.json"
def part_key(prefix,experiment_id,security_id): return f"{prefix.rstrip('/')}/parts/{experiment_id}/{security_id}.json.gz"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--experiment-id",required=True); p.add_argument("--runner-commit",required=True)
    p.add_argument("--output-prefix",default=DEFAULT_OUTPUT_PREFIX); p.add_argument("--history-prefix",default=CANONICAL_HISTORY_PREFIX)
    p.add_argument("--max-securities",type=int,default=0,help="0=all; deterministic inventory prefix for validation only")
    p.add_argument("--max-sessions",type=int,default=0,help="0=every available session; validation-only causal prefix bound")
    p.add_argument("--interrupt-after",type=int,default=0,help="test-only recovery injection; excluded from semantic lineage")
    args=p.parse_args()
    if args.history_prefix!=CANONICAL_HISTORY_PREFIX: raise RuntimeError("BT5_NONCANONICAL_HISTORY_PREFIX")
    if args.max_securities<0 or args.max_sessions<0 or args.interrupt_after<0: raise RuntimeError("BT5_INVALID_CONFIG")

    s3=s3_client(); bucket=need("R2_BUCKET_NAME"); inventory=list_inventory(s3,bucket,args.history_prefix)
    if not inventory: raise RuntimeError("BT5_EMPTY_CANONICAL_INVENTORY")
    if args.max_securities: inventory=inventory[:args.max_securities]
    cfg={"history_prefix":args.history_prefix,"output_prefix":args.output_prefix,"max_securities":args.max_securities,"max_sessions":args.max_sessions,"output_schema":OUTPUT_SCHEMA,"population":"CANONICAL_OHLCV_INVENTORY","asof_policy":"EVERY_AVAILABLE_SESSION" if not args.max_sessions else "VALIDATION_PREFIX_BOUND","component_only":True}
    lineage=ReplayLineage(args.experiment_id,args.runner_commit,inventory_sha256(inventory),config_sha256(cfg))
    cp_key=checkpoint_key(args.output_prefix,args.experiment_id); checkpoint=read_json_object(s3,bucket,cp_key)
    completed=[]; output_parts=[]
    if checkpoint is not None:
        validate_checkpoint(checkpoint,lineage); completed=list(checkpoint["completed_work_units"]); output_parts=list(checkpoint["output_parts"])
    done=set(completed); newly_completed=0

    for index,item in enumerate(inventory,1):
        source_key=item["key"]; security_id=Path(source_key).stem
        if security_id in done:
            print(f"[BT5 {index}/{len(inventory)}] {security_id} RESUME_SKIP",flush=True); continue
        print(f"[BT5 {index}/{len(inventory)}] {security_id} LOAD",flush=True)
        raw=s3.get_object(Bucket=bucket,Key=source_key)["Body"].read(); source_hash=sha256_bytes(raw)
        frame=normalize_ohlcv(pd.read_parquet(io.BytesIO(raw)))
        state=precompute_raw_landmarks(frame,excursion_extractor=extract_excursion_landmarks,confirmed_extractor=extract_confirmed_window_landmarks)
        replay_ends=range(1,len(frame)+1)
        if args.max_sessions:
            replay_ends=range(1,min(len(frame),args.max_sessions)+1)
        sessions=[]
        for end in replay_ends:
            local=frame.iloc[:end].copy(); asof=pd.Timestamp(local.iloc[-1]["date"]).date()
            try:
                result=analyze_with_authorized_reuse(analyze_security=analyze_security,canonical_module=canonical,state=state,security_id=security_id,ticker=security_id,frame=local,asof_date=asof,fallback_to_oracle=True)
                sessions.append({"asof_date":asof.isoformat(),"engine_source":result["source"],"reuse_guard":result["reuse_guard"],"oneil_assessments":[serialize_record(x) for x in result["records"]]})
            except Exception as exc:
                sessions.append({"asof_date":asof.isoformat(),"status":"NOT_EVALUABLE","reason":"ONEIL_ENGINE_NOT_EVALUABLE_AT_PREFIX","error_type":type(exc).__name__,"error":str(exc)[:500]})
        payload={"schema":OUTPUT_SCHEMA,"contract":BT5_CONTRACT,"lineage_sha256":lineage.sha256,"security_id":security_id,"ticker":security_id,"source_key":source_key,"source_sha256":source_hash,"oneil_sha":FROZEN_ONEIL_SHA,"sessions":sessions,"replay_session_count":len(sessions),"source_session_count":len(frame),"validation_session_bound":args.max_sessions or None,"components":{"N":{"status":"NOT_EVALUABLE","reason":"HISTORICAL_RECONSTRUCTOR_UNAVAILABLE"},"S":{"status":"NOT_EVALUABLE","reason":"HISTORICAL_RECONSTRUCTOR_UNAVAILABLE"},"L":{"status":"NOT_EVALUATED_IN_BT5_RUNNER","reason":"SEPARATE_FROZEN_CAUSAL_INPUT_REQUIRED"},"M":{"status":"NOT_EVALUABLE","reason":"GOVERNED_HISTORICAL_MARKET_SEMANTIC_EVIDENCE_UNAVAILABLE"}},"production_eligibility_emitted":False,"strategy_returns_computed":False,"bt6_t1_open_computed":False}
        part=put_json_gzip(s3,bucket,part_key(args.output_prefix,args.experiment_id,security_id),payload)
        completed.append(security_id); done.add(security_id); output_parts.append(part); newly_completed+=1
        put_json(s3,bucket,cp_key,make_checkpoint(lineage=lineage,completed_work_units=completed,output_parts=output_parts))
        print(f"[BT5 {index}/{len(inventory)}] {security_id} CHECKPOINT replay_sessions={len(sessions)} source_sessions={len(frame)}",flush=True)
        if args.interrupt_after and newly_completed>=args.interrupt_after:
            raise RuntimeError("BT5_TEST_INJECTED_INTERRUPTION_AFTER_DURABLE_CHECKPOINT")

    manifest={"schema":"HISTORICAL_BT5_MANIFEST_V1","contract":BT5_CONTRACT,"experiment_id":args.experiment_id,"lineage":asdict(lineage),"lineage_sha256":lineage.sha256,"inventory_count":len(inventory),"completed_count":len(completed),"output_parts":output_parts,"validation_session_bound":args.max_sessions or None,"production_eligibility_emitted":False,"strategy_returns_computed":False,"bt6_t1_open_computed":False,"status":"COMPLETE"}
    manifest_key=f"{args.output_prefix.rstrip('/')}/manifests/{args.experiment_id}.json"; put_json(s3,bucket,manifest_key,manifest)
    print(f"BT5 COMPLETE experiment={args.experiment_id} securities={len(completed)} manifest={manifest_key}",flush=True)

if __name__=="__main__": main()
