"""Read-only CAN SLIM v2 Candidate -> causal T+1 Open shadow execution artifact."""
from __future__ import annotations
import hashlib, io, json, os, sys
from collections import Counter
from dataclasses import asdict
from datetime import date, datetime, time as dtime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
import boto3, pandas as pd
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from canslim_research.execution_entry_v2 import decide_v2_t1_open_execution, validate_v2_execution_decision

def env(n):
    v=os.getenv(n)
    if not v: raise RuntimeError(f"missing {n}")
    return v
def raw(s3,b,k): return s3.get_object(Bucket=b,Key=k)["Body"].read()
def main():
    source=Path(env("CANSLIM_V2_CANDIDATE_INPUT"))
    c=json.loads(source.read_text())
    required={"decision_date","watchlist_sha256","ready_key","ready_sha256","eligibility_contract_version","records"}
    if required-set(c): raise RuntimeError(f"CANDIDATE_LINEAGE_INCOMPLETE:{sorted(required-set(c))}")
    if c["eligibility_contract_version"]!="canslim-eligibility-contract-v2": raise RuntimeError("ELIGIBILITY_CONTRACT_MISMATCH")
    signal=date.fromisoformat(str(c["decision_date"]))
    s3=boto3.client("s3",endpoint_url=env("R2_ENDPOINT"),region_name="auto",aws_access_key_id=env("R2_ACCESS_KEY_ID"),aws_secret_access_key=env("R2_SECRET_ACCESS_KEY")); bucket=env("R2_BUCKET_NAME")
    # Verify immutable signal-date READY lineage first.
    source_rb=raw(s3,bucket,c["ready_key"])
    if hashlib.sha256(source_rb).hexdigest()!=c["ready_sha256"]: raise RuntimeError("SOURCE_READY_SHA256_MISMATCH")
    # Observe T+1 from the current canonical READY, never by mutating/reinterpreting
    # the candidate's frozen signal-date READY.
    rptr=json.loads(raw(s3,bucket,"production/ready/current.json"))
    observation_key=rptr["parquet_key"]; rb=raw(s3,bucket,observation_key)
    expected=rptr.get("parquet_sha256") or rptr.get("sha256")
    observation_sha=hashlib.sha256(rb).hexdigest()
    if expected and observation_sha!=expected: raise RuntimeError("OBSERVATION_READY_SHA256_MISMATCH")
    ready=pd.read_parquet(io.BytesIO(rb)); ready["date"]=pd.to_datetime(ready["date"],errors="raise").dt.normalize()
    later=sorted({d for d in ready["date"].dt.date if d>signal})
    eligible=[r for r in c["records"] if r.get("candidate_stage")=="CANSLIM_V2_ELIGIBLE"]
    produced=c.get("produced_at")
    timely=None
    if later:
        if not produced:
            timely=False
        else:
            pa=datetime.fromisoformat(str(produced).replace("Z","+00:00"))
            if pa.tzinfo is None: timely=False
            else:
                t1=datetime.combine(later[0],dtime(9,30),ZoneInfo("America/New_York"))
                timely=pa.astimezone(timezone.utc)<t1.astimezone(timezone.utc)
    # This shadow artifact is truthful even before T+1 exists: eligible rows become
    # NO_NEXT_SESSION_BAR, never a guessed/recovered fill.
    decisions=[]
    for r in eligible:
        sid=str(r["security_id"])
        g=ready[ready["security_id"].astype(str).eq(sid)].sort_values("date")
        if later and timely is False:
            # Historical/recovered candidates are never granted a retroactive fill.
            continue
        nxt=g[g["date"].dt.date>signal]
        if nxt.empty: nd=no=None
        else:
            x=nxt.iloc[0]; nd=x["date"].date(); no=float(x["open"])
        prior=g[g["date"].dt.date<=signal]
        pc=None if prior.empty else float(prior.iloc[-1]["adj_close"])
        d=decide_v2_t1_open_execution(candidate_id=str(r["candidate_id"]),security_id=sid,signal_date=signal,
            candidate_stage=str(r["candidate_stage"]),pivot_level=r.get("pivot_level"),next_session_date=nd,next_open=no,
            prior_close=pc,source_candidate_version=str(r.get("candidate_generator_version") or ""))
        findings=validate_v2_execution_decision(d)
        if findings: raise RuntimeError(f"V2_EXECUTION_CONTRACT_VIOLATION:{r['candidate_id']}:{findings}")
        x=asdict(d); x["execution_state"]=d.execution_state.value
        for k,v in list(x.items()):
            if isinstance(v,date): x[k]=v.isoformat()
        decisions.append(x)
    states=Counter(x["execution_state"] for x in decisions)
    out={"schema_version":1,"type":"canslim_v2_shadow_execution","decision_date":c["decision_date"],
         "source_candidate_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
         "watchlist_sha256":c["watchlist_sha256"],"source_ready_key":c["ready_key"],"source_ready_sha256":c["ready_sha256"],
         "ready_key":observation_key,"ready_sha256":observation_sha,"observation_ready_key":observation_key,"observation_ready_sha256":observation_sha,
         "candidate_produced_at":produced,"candidate_timely_for_t1":timely,
         "eligible_candidate_count":len(eligible),"entry_decision_count":len(decisions),
         "execution_state_counts":dict(sorted(states.items())),"production_write":False,
         "retroactive_entry_allowed":False,"records":decisions}
    target=Path(os.getenv("CANSLIM_V2_EXECUTION_OUTPUT","shadow-v2-execution.json")); target.write_text(json.dumps(out,sort_keys=True,default=str))
    print(json.dumps({k:out[k] for k in ("decision_date","eligible_candidate_count","entry_decision_count","execution_state_counts")},sort_keys=True))
if __name__=="__main__": main()
