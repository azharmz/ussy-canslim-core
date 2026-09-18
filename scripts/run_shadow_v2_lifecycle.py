"""Read-only v2 execution -> lifecycle shadow boundary.

Truthfully emits NOT_OPENED for non-filled decisions and OPEN for a real T+1
fill until downstream frozen exit channels have enough subsequent observations.
It never writes production state or synthesizes an exit.
"""
from __future__ import annotations
import hashlib,io,json,os,sys
import boto3, pandas as pd
from dataclasses import asdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from canslim_research.position_lifecycle_v2 import ExitCandidate,arbitrate_position_lifecycle_v2,validate_position_lifecycle_v2
from canslim_research.sell_risk_v1 import SELL_RISK_VERSION, DailyBar as RiskBar, evaluate_sell_risk, validate_sell_risk
from canslim_research.technical_deterioration_action_v1 import ACTION_VERSION as TECH_VERSION, DailyBar as TechBar, WeeklyEvidence, decide_technical_deterioration_action, validate_action
from canslim_research.round_trip_action_v1 import ACTION_VERSION as ROUND_VERSION, DailyBar as RoundBar, decide_round_trip_action, validate_round_trip_action
from canslim_research.weekly_10w_v1 import DailyBar as WeekBar, aggregate_completed_weeks

def env(n):
 v=os.getenv(n)
 if not v: raise RuntimeError(f"missing {n}")
 return v
def empty(channel,version): return ExitCandidate(channel=channel,execution_date=None,execution_price=None,execution_source=None,source_version=version)
def exitc(channel,d,p,s,v): return ExitCandidate(channel=channel,execution_date=d,execution_price=p,execution_source=s,source_version=v)
def raw(s3,b,k): return s3.get_object(Bucket=b,Key=k)["Body"].read()
def main():
 src=Path(env("CANSLIM_V2_EXECUTION_INPUT")); x=json.loads(src.read_text())
 if x.get("type")!="canslim_v2_shadow_execution": raise RuntimeError("EXECUTION_ARTIFACT_TYPE_MISMATCH")
 # Reuse the exact READY identity already pinned by execution; no current-pointer drift.
 s3=boto3.client("s3",endpoint_url=env("R2_ENDPOINT"),region_name="auto",aws_access_key_id=env("R2_ACCESS_KEY_ID"),aws_secret_access_key=env("R2_SECRET_ACCESS_KEY")); bucket=env("R2_BUCKET_NAME")
 rb=raw(s3,bucket,x["ready_key"])
 if hashlib.sha256(rb).hexdigest()!=x["ready_sha256"]: raise RuntimeError("READY_SHA256_MISMATCH")
 ready=pd.read_parquet(io.BytesIO(rb)); ready["date"]=pd.to_datetime(ready["date"],errors="raise").dt.normalize()
 rows=[]
 for e in x.get("records",[]):
  filled=e.get("execution_state")=="EXECUTED_T1_OPEN"
  cap=empty("CAPITAL_PROTECTION_37",SELL_RISK_VERSION); tech=empty("TECHNICAL_DETERIORATION_40",TECH_VERSION); rnd=empty("ROUND_TRIP_42",ROUND_VERSION)
  if filled:
   sid=str(e["security_id"]); ed=str(e["fill_date"]); pivot=float(e["pivot_level"]); fill=float(e["fill_price"])
   g=ready[ready["security_id"].astype(str).eq(sid)].sort_values("date")
   post=g[g["date"].dt.date>=pd.Timestamp(ed).date()]
   rbars=[RiskBar(z.date.date().isoformat(),float(z.open),float(z.high),float(z.low),float(z.close),float(z.volume)) for z in post.itertuples()]
   if rbars:
    sr=evaluate_sell_risk(candidate_id=str(e["candidate_id"]),security_id=sid,entry_date=ed,fill_price=fill,pivot_level=pivot,breakout_date=str(e["signal_date"]),bars_since_breakout=rbars,source_entry_version=str(e.get("execution_version") or ""))
    f=validate_sell_risk(sr)
    if f: raise RuntimeError(f"SELL_RISK_CONTRACT_VIOLATION:{e['candidate_id']}:{f}")
    if sr.sell_execution_date: cap=exitc("CAPITAL_PROTECTION_37",sr.sell_execution_date,sr.sell_execution_price,sr.sell_execution_source,SELL_RISK_VERSION)
    ract=decide_round_trip_action(candidate_id=str(e["candidate_id"]),security_id=sid,entry_date=ed,fill_price=fill,pivot_level=pivot,bars_since_entry=[RoundBar(b.date,b.open,b.high,b.low,b.close,b.volume) for b in rbars],source_entry_version=str(e.get("execution_version") or ""))
    f=validate_round_trip_action(ract)
    if f: raise RuntimeError(f"ROUND_TRIP_CONTRACT_VIOLATION:{e['candidate_id']}:{f}")
    if ract.execution_date: rnd=exitc("ROUND_TRIP_42",ract.execution_date,ract.execution_price,ract.execution_source,ROUND_VERSION)
    # Weekly #40 consumes only completed-week evidence.
    allbars=[WeekBar(z.date.date().isoformat(),float(z.open),float(z.high),float(z.low),float(z.close),float(z.volume)) for z in g.itertuples()]
    weeks=aggregate_completed_weeks(allbars)
    we=[]
    for i,w in enumerate(weeks):
     prior=weeks[max(0,i-10):i]; ma=None if i<9 else sum(q.close for q in weeks[i-9:i+1])/10.0
     vr=None
     if len(prior)==10 and w.volume is not None and all(q.volume is not None for q in prior):
      den=sum(float(q.volume) for q in prior)/10.0; vr=None if den<=0 else float(w.volume)/den
     we.append(WeeklyEvidence(w.first_date,w.last_date,float(w.close),ma,w.volume,vr))
    tact=decide_technical_deterioration_action(candidate_id=str(e["candidate_id"]),security_id=sid,entry_date=ed,fill_price=fill,weekly_evidence=we,daily_bars=[TechBar(b.date,b.open,b.high,b.low,b.close,b.volume) for b in rbars])
    f=validate_action(tact)
    if f: raise RuntimeError(f"TECH_ACTION_CONTRACT_VIOLATION:{e['candidate_id']}:{f}")
    if tact.execution_date: tech=exitc("TECHNICAL_DETERIORATION_40",tact.execution_date,tact.execution_price,tact.execution_source,TECH_VERSION)
  life=arbitrate_position_lifecycle_v2(candidate_id=str(e["candidate_id"]),security_id=str(e["security_id"]),
   entry_date=e.get("fill_date") if filled else None,fill_price=e.get("fill_price") if filled else None,
   source_entry_version=str(e.get("execution_version") or ""),capital_exit=cap,technical_exit=tech,round_trip_exit=rnd)
  findings=validate_position_lifecycle_v2(life)
  if findings: raise RuntimeError(f"LIFECYCLE_CONTRACT_VIOLATION:{e['candidate_id']}:{findings}")
  rows.append(asdict(life))
 out={"schema_version":1,"type":"canslim_v2_shadow_lifecycle_boundary","decision_date":x["decision_date"],
  "source_execution_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),"entry_decision_count":x["entry_decision_count"],
  "lifecycle_record_count":len(rows),"production_write":False,"synthetic_exit_used":False,
  "exit_channels_status":"AWAIT_SUBSEQUENT_OBSERVATIONS","records":rows}
 target=Path(os.getenv("CANSLIM_V2_LIFECYCLE_OUTPUT","shadow-v2-lifecycle.json"));target.write_text(json.dumps(out,sort_keys=True,default=str))
 print(json.dumps({"decision_date":out["decision_date"],"lifecycle_record_count":len(rows),"states":{s:sum(r["lifecycle_state"]==s for r in rows) for s in sorted({r["lifecycle_state"] for r in rows})}},sort_keys=True))
if __name__=="__main__":main()
