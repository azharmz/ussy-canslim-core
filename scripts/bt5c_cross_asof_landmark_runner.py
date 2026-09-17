from __future__ import annotations
import io,json,os,time
from datetime import date
import boto3
import pandas as pd
from bt5c_cross_asof_landmark_probe import run_probe

ONEIL_SHA="c433cc1e35a5aa32a46f732cd8c5545935e36e40"
# Structural-assembly diagnostic: intentionally small after the 8-security run
# was interrupted by runner shutdown. Two short-history securities, one earlier
# as-of comparison each. Expand only after stage timing is understood.
CASES={
 "BE6360403164":["2026-09-02","2026-09-09"],
 "AU0000421851":["2026-09-02","2026-09-09"],
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
 log("BT5C structural diagnostic START")
 s3=boto3.client("s3",endpoint_url=need("R2_ENDPOINT"),region_name="auto",aws_access_key_id=need("R2_ACCESS_KEY_ID"),aws_secret_access_key=need("R2_SECRET_ACCESS_KEY")); bucket=need("R2_BUCKET_NAME"); results=[]
 for i,(sid,ds) in enumerate(CASES.items(),1):
  started=time.perf_counter(); key=f"backtest/ohlcv/{sid}.parquet"; log(f"[{i}/{len(CASES)}] {sid} download START")
  raw=pd.read_parquet(io.BytesIO(s3.get_object(Bucket=bucket,Key=key)["Body"].read())); frame=normalize(raw); log(f"[{i}/{len(CASES)}] {sid} probe START rows={len(frame)} dates={ds}")
  result=run_probe(frame,[date.fromisoformat(x) for x in ds]); result["security_id"]=sid; result["r2_key"]=key; results.append(result)
  for case in result["cases"]:
   log(f"[{i}/{len(CASES)}] {sid} asof={case['asof_date']} exact={case['exact']} oracle={json.dumps(case['oracle_timing_sec'],sort_keys=True)} reuse={json.dumps(case['reuse_timing_sec'],sort_keys=True)}")
  log(f"[{i}/{len(CASES)}] {sid} DONE verdict={result['verdict']} elapsed_sec={time.perf_counter()-started:.2f}")
 payload={"contract":"BT5C_STRUCTURAL_ASSEMBLY_BOUNDED_DIAGNOSTIC_V1","frozen_oneil_sha":ONEIL_SHA,"security_count":len(results),"comparison_count":sum(len(x["cases"]) for x in results),"results":results,"all_exact":all(x["all_exact"] for x in results),"structural_assembly_cross_asof_reuse_authorized":False,"morphology_cross_asof_reuse_authorized":False,"strategy_returns_computed":False}
 payload["verdict"]="STRUCTURAL_ASSEMBLY_BOUNDED_EXACT_OBSERVED" if payload["all_exact"] else "STRUCTURAL_ASSEMBLY_BOUNDED_NOT_EXACT_FAIL_CLOSED"
 open("bt5c-landmark-probe.json","w").write(json.dumps(payload,indent=2,sort_keys=True)+"\n"); log(json.dumps({"verdict":payload["verdict"],"all_exact":payload["all_exact"],"security_count":payload["security_count"],"comparison_count":payload["comparison_count"]},sort_keys=True)); log("BT5C structural diagnostic COMPLETE")
 if not payload["all_exact"]: raise SystemExit(2)
if __name__=="__main__": main()
