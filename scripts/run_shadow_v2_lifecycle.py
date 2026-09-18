"""Read-only v2 execution -> lifecycle shadow boundary.

Truthfully emits NOT_OPENED for non-filled decisions and OPEN for a real T+1
fill until downstream frozen exit channels have enough subsequent observations.
It never writes production state or synthesizes an exit.
"""
from __future__ import annotations
import hashlib,json,os,sys
from dataclasses import asdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from canslim_research.position_lifecycle_v2 import ExitCandidate,arbitrate_position_lifecycle_v2,validate_position_lifecycle_v2
from canslim_research.sell_risk_v1 import SELL_RISK_VERSION
from canslim_research.technical_deterioration_action_v1 import ACTION_VERSION as TECH_VERSION
from canslim_research.round_trip_action_v1 import ACTION_VERSION as ROUND_VERSION

def env(n):
 v=os.getenv(n)
 if not v: raise RuntimeError(f"missing {n}")
 return v
def empty(channel,version): return ExitCandidate(channel=channel,execution_date=None,execution_price=None,execution_source=None,source_version=version)
def main():
 src=Path(env("CANSLIM_V2_EXECUTION_INPUT")); x=json.loads(src.read_text())
 if x.get("type")!="canslim_v2_shadow_execution": raise RuntimeError("EXECUTION_ARTIFACT_TYPE_MISMATCH")
 rows=[]
 for e in x.get("records",[]):
  filled=e.get("execution_state")=="EXECUTED_T1_OPEN"
  life=arbitrate_position_lifecycle_v2(candidate_id=str(e["candidate_id"]),security_id=str(e["security_id"]),
   entry_date=e.get("fill_date") if filled else None,fill_price=e.get("fill_price") if filled else None,
   source_entry_version=str(e.get("execution_version") or ""),
   capital_exit=empty("CAPITAL_PROTECTION_37",SELL_RISK_VERSION),
   technical_exit=empty("TECHNICAL_DETERIORATION_40",TECH_VERSION),
   round_trip_exit=empty("ROUND_TRIP_42",ROUND_VERSION))
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
