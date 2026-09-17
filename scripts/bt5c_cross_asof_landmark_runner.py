from __future__ import annotations
import io,json,os,time
from datetime import date
import boto3
import pandas as pd
from oneil_patterns.validation.structural_assembly import assemble_local_turn_double_bottoms

ONEIL_SHA="c433cc1e35a5aa32a46f732cd8c5545935e36e40"
# Isolate the stage implicated by the bounded diagnostic. Prefix lengths are
# capped so the Actions probe stays cheap; each invocation uses the untouched
# frozen O'Neil implementation on a complete causal prefix.
CASES={
 "BMG9460G1015":[250,500,750,1000,1250],
 "BMG4690M1010":[250,500,750,1000,1250,1500],
 "CA05156V1022":[250,500,750,1000,1250,1500,2000],
}

def log(msg): print(msg,flush=True)
def need(n):
 v=os.getenv(n)
 if not v: raise RuntimeError(f"missing {n}")
 return v

def normalize(raw):
 f=raw.copy(); f.columns=[str(c).lower() for c in f.columns]
 dc=next((c for c in ("date","session_date","datetime") if c in f.columns),None)
 if dc is None: raise RuntimeError("date unavailable")
 aliases={"adjusted_open":"open","adjusted_high":"high","adjusted_low":"low","adjusted_close":"close","adjusted_volume":"volume","adj_close":"close"}; rename={dc:"date"}
 for s,d in aliases.items():
  if s in f.columns and d not in f.columns: rename[s]=d
 f=f.rename(columns=rename); req=["date","open","high","low","close","volume"]; miss=[c for c in req if c not in f.columns]
 if miss: raise RuntimeError(f"missing {miss}")
 f=f[req].copy(); f["date"]=pd.to_datetime(f["date"],utc=True,errors="raise").dt.tz_localize(None)
 for c in req[1:]: f[c]=pd.to_numeric(f[c],errors="raise")
 return f.dropna().sort_values("date").drop_duplicates("date",keep="last").reset_index(drop=True)

def main():
 log("BT5C local-turn DB scaling profile START")
 s3=boto3.client("s3",endpoint_url=need("R2_ENDPOINT"),region_name="auto",aws_access_key_id=need("R2_ACCESS_KEY_ID"),aws_secret_access_key=need("R2_SECRET_ACCESS_KEY")); bucket=need("R2_BUCKET_NAME"); rows=[]
 for i,(sid,lengths) in enumerate(CASES.items(),1):
  key=f"backtest/ohlcv/{sid}.parquet"; log(f"[{i}/{len(CASES)}] {sid} download START")
  frame=normalize(pd.read_parquet(io.BytesIO(s3.get_object(Bucket=bucket,Key=key)["Body"].read()))); log(f"[{i}/{len(CASES)}] {sid} rows={len(frame)} profile START")
  for n in lengths:
   if n>len(frame): continue
   prefix=frame.iloc[:n].copy().reset_index(drop=True); asof=pd.Timestamp(prefix.iloc[-1]["date"]).date(); started=time.perf_counter(); out=assemble_local_turn_double_bottoms(prefix,asof_date=asof); elapsed=time.perf_counter()-started
   rec={"security_id":sid,"bars":n,"asof_date":asof.isoformat(),"geometry_count":len(out),"elapsed_sec":round(elapsed,6),"sec_per_100_bars":round(elapsed/n*100,6)}; rows.append(rec); log(f"[{i}/{len(CASES)}] {sid} bars={n} geometries={len(out)} elapsed_sec={elapsed:.3f}")
  log(f"[{i}/{len(CASES)}] {sid} DONE")
 by_security={}
 for sid in CASES:
  vals=[r for r in rows if r["security_id"]==sid]; ratios=[]
  for a,b in zip(vals,vals[1:]): ratios.append({"bars_ratio":round(b["bars"]/a["bars"],4),"time_ratio":round(b["elapsed_sec"]/a["elapsed_sec"],4) if a["elapsed_sec"] else None,"from_bars":a["bars"],"to_bars":b["bars"]})
  by_security[sid]=ratios
 payload={"contract":"BT5C_LOCAL_TURN_DB_SCALING_PROFILE_V1","frozen_oneil_sha":ONEIL_SHA,"stage":"assemble_local_turn_double_bottoms","untouched_frozen_implementation":True,"measurements":rows,"adjacent_growth_ratios":by_security,"production_eligibility_emitted":False,"strategy_returns_computed":False,"reuse_authorized":False,"verdict":"PROFILE_ONLY_NO_SEMANTIC_AUTHORIZATION"}
 open("bt5c-landmark-probe.json","w").write(json.dumps(payload,indent=2,sort_keys=True)+"\n"); log(f"BT5C local-turn DB scaling profile COMPLETE measurements={len(rows)}")
if __name__=="__main__": main()
