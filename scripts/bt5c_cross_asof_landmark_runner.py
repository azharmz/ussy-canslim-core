from __future__ import annotations
import io, json, os
from datetime import date
import boto3
import pandas as pd
from bt5c_cross_asof_landmark_probe import run_probe

ONEIL_SHA="c433cc1e35a5aa32a46f732cd8c5545935e36e40"
CASES={
 "BE6360403164":["2026-08-26","2026-09-02","2026-09-09"],
 "AU0000421851":["2026-08-26","2026-09-02","2026-09-09"],
 "BMG9460G1015":["2026-08-26","2026-09-02","2026-09-09"],
}

def need(n):
 v=os.getenv(n)
 if not v: raise RuntimeError(f"missing {n}")
 return v

def normalize(raw):
 f=raw.copy(); f.columns=[str(c).lower() for c in f.columns]
 dc=next((c for c in ("date","session_date","datetime") if c in f.columns),None)
 if dc is None: raise RuntimeError("date unavailable")
 aliases={"adjusted_open":"open","adjusted_high":"high","adjusted_low":"low","adjusted_close":"close","adjusted_volume":"volume","adj_close":"close"}
 rename={dc:"date"}
 for s,d in aliases.items():
  if s in f.columns and d not in f.columns: rename[s]=d
 f=f.rename(columns=rename)
 req=["date","open","high","low","close","volume"]
 miss=[c for c in req if c not in f.columns]
 if miss: raise RuntimeError(f"missing {miss}")
 f=f[req].copy(); f["date"]=pd.to_datetime(f["date"],utc=True,errors="raise").dt.tz_localize(None)
 for c in req[1:]: f[c]=pd.to_numeric(f[c],errors="raise")
 return f.dropna().sort_values("date").drop_duplicates("date",keep="last").reset_index(drop=True)

def main():
 s3=boto3.client("s3",endpoint_url=need("R2_ENDPOINT"),region_name="auto",aws_access_key_id=need("R2_ACCESS_KEY_ID"),aws_secret_access_key=need("R2_SECRET_ACCESS_KEY")); bucket=need("R2_BUCKET_NAME")
 results=[]
 for sid, ds in CASES.items():
  key=f"backtest/ohlcv/{sid}.parquet"
  raw=pd.read_parquet(io.BytesIO(s3.get_object(Bucket=bucket,Key=key)["Body"].read())); frame=normalize(raw)
  result=run_probe(frame,[date.fromisoformat(x) for x in ds]); result["security_id"]=sid; result["r2_key"]=key; results.append(result)
  print(sid,result["verdict"],"all_exact=",result["all_exact"])
 payload={"contract":"BT5C_CROSS_ASOF_LANDMARK_MULTI_SECURITY_V1","frozen_oneil_sha":ONEIL_SHA,"results":results,"all_exact":all(x["all_exact"] for x in results),"landmark_cross_asof_reuse_authorized":False,"morphology_cross_asof_reuse_authorized":False,"strategy_returns_computed":False}
 payload["verdict"]="LANDMARK_REUSE_EQUIVALENCE_OBSERVED_MORE_CASES_REQUIRED" if payload["all_exact"] else "LANDMARK_REUSE_NOT_EXACT_FAIL_CLOSED"
 open("bt5c-landmark-probe.json","w").write(json.dumps(payload,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"verdict":payload["verdict"],"all_exact":payload["all_exact"]},indent=2))
 if not payload["all_exact"]: raise SystemExit(2)
if __name__=="__main__": main()
