from __future__ import annotations
import io,json,os,time
import boto3
import pandas as pd
from oneil_patterns.validation.structural_assembly import assemble_local_turn_double_bottoms

ONEIL_SHA="c433cc1e35a5aa32a46f732cd8c5545935e36e40"
# Canonical upstream contract is owned by azharmz/ussy-data bootstrap_ohlcv.py.
# Legacy backtest/ohlcv/ was migrated and deliberately removed after coverage verification.
PREFIX="history/ohlcv/"
UPSTREAM_CONTRACT="azharmz/ussy-data:HISTORY_PREFIX=history/ohlcv/"
PRIORITY=["AN8068571086","AU000000BHP4","BMG6331P1041","BMG9460G1015","BMG4690M1010","AU0000421851","BE6360403164"]
LENGTHS=[250,500,750,1000,1250,1500]

def log(msg): print(msg,flush=True)
def need(n):
 v=os.getenv(n)
 if not v: raise RuntimeError(f"missing {n}")
 return v

def list_keys(s3,bucket):
 out=[]; token=None
 while True:
  kw={"Bucket":bucket,"Prefix":PREFIX}
  if token: kw["ContinuationToken"]=token
  r=s3.list_objects_v2(**kw); out.extend(x["Key"] for x in r.get("Contents",[]) if x["Key"].endswith(".parquet"))
  if not r.get("IsTruncated"): return sorted(out)
  token=r["NextContinuationToken"]

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
 log(f"upstream_contract={UPSTREAM_CONTRACT}")
 s3=boto3.client("s3",endpoint_url=need("R2_ENDPOINT"),region_name="auto",aws_access_key_id=need("R2_ACCESS_KEY_ID"),aws_secret_access_key=need("R2_SECRET_ACCESS_KEY")); bucket=need("R2_BUCKET_NAME")
 keys=list_keys(s3,bucket); keyset=set(keys); log(f"R2 inventory prefix={PREFIX} parquet_count={len(keys)}")
 preferred=[f"{PREFIX}{sid}.parquet" for sid in PRIORITY if f"{PREFIX}{sid}.parquet" in keyset]
 fallback=[k for k in keys if k not in preferred]
 selected=(preferred+fallback)[:3]
 if not selected: raise RuntimeError(f"no governed historical OHLCV parquet objects found under canonical prefix {PREFIX}")
 log(f"selected_keys={json.dumps(selected)}")
 rows=[]; selected_meta=[]
 for i,key in enumerate(selected,1):
  sid=key.rsplit("/",1)[-1].removesuffix(".parquet"); log(f"[{i}/{len(selected)}] {sid} download START")
  frame=normalize(pd.read_parquet(io.BytesIO(s3.get_object(Bucket=bucket,Key=key)["Body"].read()))); selected_meta.append({"security_id":sid,"key":key,"rows":len(frame)}); log(f"[{i}/{len(selected)}] {sid} rows={len(frame)} profile START")
  tested=0
  for n in LENGTHS:
   if n>len(frame): continue
   tested+=1; prefix=frame.iloc[:n].copy().reset_index(drop=True); asof=pd.Timestamp(prefix.iloc[-1]["date"]).date(); started=time.perf_counter(); out=assemble_local_turn_double_bottoms(prefix,asof_date=asof); elapsed=time.perf_counter()-started
   rows.append({"security_id":sid,"bars":n,"asof_date":asof.isoformat(),"geometry_count":len(out),"elapsed_sec":round(elapsed,6),"sec_per_100_bars":round(elapsed/n*100,6)}); log(f"[{i}/{len(selected)}] {sid} bars={n} geometries={len(out)} elapsed_sec={elapsed:.3f}")
  log(f"[{i}/{len(selected)}] {sid} DONE tested_lengths={tested}")
 by_security={}
 for meta in selected_meta:
  sid=meta["security_id"]; vals=[r for r in rows if r["security_id"]==sid]; ratios=[]
  for a,b in zip(vals,vals[1:]): ratios.append({"bars_ratio":round(b["bars"]/a["bars"],4),"time_ratio":round(b["elapsed_sec"]/a["elapsed_sec"],4) if a["elapsed_sec"] else None,"from_bars":a["bars"],"to_bars":b["bars"]})
  by_security[sid]=ratios
 payload={"contract":"BT5C_LOCAL_TURN_DB_SCALING_PROFILE_V3","frozen_oneil_sha":ONEIL_SHA,"upstream_history_contract":UPSTREAM_CONTRACT,"history_prefix":PREFIX,"stage":"assemble_local_turn_double_bottoms","untouched_frozen_implementation":True,"r2_inventory_count":len(keys),"selection":"available_priority_then_lexicographic_fallback_v1","selected":selected_meta,"measurements":rows,"adjacent_growth_ratios":by_security,"production_eligibility_emitted":False,"strategy_returns_computed":False,"reuse_authorized":False,"verdict":"PROFILE_ONLY_NO_SEMANTIC_AUTHORIZATION"}
 open("bt5c-landmark-probe.json","w").write(json.dumps(payload,indent=2,sort_keys=True)+"\n"); log(f"BT5C local-turn DB scaling profile COMPLETE measurements={len(rows)}")
if __name__=="__main__": main()
