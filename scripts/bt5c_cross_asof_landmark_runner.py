from __future__ import annotations
import io,json,os,time,tracemalloc
from dataclasses import asdict
import boto3
import pandas as pd
from oneil_patterns.landmarks.confirmed_window import extract_confirmed_window_landmarks
from oneil_patterns.landmarks.excursion import extract_excursion_landmarks
from oneil_patterns.production.engine import analyze_security
import oneil_patterns.validation.canonical_predictions as canonical

ONEIL_SHA="c433cc1e35a5aa32a46f732cd8c5545935e36e40"
DEFAULT_PREFIX="history/ohlcv/"
UPSTREAM_CONTRACT="azharmz/ussy-data:HISTORY_PREFIX=history/ohlcv/"
ORIGINAL_EXCURSION=canonical.extract_excursion_landmarks
ORIGINAL_CONFIRMED=canonical.extract_confirmed_window_landmarks

def log(x): print(x,flush=True)
def need(n):
 v=os.getenv(n)
 if not v: raise RuntimeError(f"missing {n}")
 return v

def config():
 prefix=os.getenv("BT5C_HISTORY_PREFIX",DEFAULT_PREFIX)
 if not prefix.endswith("/"): prefix+="/"
 discovery=int(os.getenv("BT5C_DISCOVERY_SAMPLE","96")); target=int(os.getenv("BT5C_FINAL_SAMPLE","4")); max_bars=int(os.getenv("BT5C_FINAL_MAX_BARS","800")); offsets=tuple(int(x) for x in os.getenv("BT5C_EARLIER_OFFSETS","10,40").split(",") if x.strip())
 if min(discovery,target,max_bars)<1 or target>discovery or not offsets or any(x<=0 for x in offsets): raise RuntimeError("invalid BT5C-6 configuration")
 return prefix,discovery,target,max_bars,offsets

def list_parquet_keys(s3,bucket,prefix):
 out=[]; token=None
 while True:
  kw={"Bucket":bucket,"Prefix":prefix}
  if token: kw["ContinuationToken"]=token
  r=s3.list_objects_v2(**kw); out.extend(x["Key"] for x in r.get("Contents",[]) if x["Key"].endswith(".parquet"))
  if not r.get("IsTruncated"): return sorted(out)
  token=r["NextContinuationToken"]

def deterministic_spread(keys,n):
 if not keys:return []
 n=min(n,len(keys))
 if n==1:return [keys[len(keys)//2]]
 return [keys[i] for i in dict.fromkeys(round(j*(len(keys)-1)/(n-1)) for j in range(n))]

def normalize(raw):
 f=raw.copy(); f.columns=[str(c).lower() for c in f.columns]; dc=next((c for c in ("date","session_date","datetime") if c in f.columns),None)
 if dc is None: raise RuntimeError("date unavailable")
 rename={dc:"date"}; aliases={"adjusted_open":"open","adjusted_high":"high","adjusted_low":"low","adjusted_close":"close","adjusted_volume":"volume","adj_close":"close"}
 for s,d in aliases.items():
  if s in f.columns and d not in f.columns: rename[s]=d
 f=f.rename(columns=rename); req=["date","open","high","low","close","volume"]; miss=[c for c in req if c not in f.columns]
 if miss: raise RuntimeError(f"missing {miss}")
 f=f[req].copy(); f["date"]=pd.to_datetime(f["date"],utc=True,errors="raise").dt.tz_localize(None)
 for c in req[1:]: f[c]=pd.to_numeric(f[c],errors="raise")
 return f.dropna().sort_values("date").drop_duplicates("date",keep="last").reset_index(drop=True)

def reusable_for_frame(latest,frame):
 cutoff=pd.Timestamp(frame.iloc[-1]["date"]).date(); dates=set(pd.to_datetime(frame["date"],errors="raise").dt.date)
 return [m for m in latest if m.price_date in dates and m.confirmed_date<=cutoff]

def frame_identity(frame):
 dates=pd.to_datetime(frame["date"],errors="raise")
 return (len(frame),dates.iloc[0].isoformat(),dates.iloc[-1].isoformat())

def guarded_reuse(latest,source_identity,local_frame):
 # Fail closed: reuse is permitted only for a causal prefix of the exact complete-history source.
 if local_frame.empty: raise RuntimeError("BT5C_REUSE_GUARD_EMPTY_FRAME")
 n=len(local_frame)
 if n>source_identity[0]: raise RuntimeError("BT5C_REUSE_GUARD_NOT_PREFIX")
 local_dates=pd.to_datetime(local_frame["date"],errors="raise").reset_index(drop=True)
 source_dates=source_identity[3]
 if not local_dates.equals(source_dates.iloc[:n].reset_index(drop=True)):
  raise RuntimeError("BT5C_REUSE_GUARD_NOT_PREFIX")
 return reusable_for_frame(latest,local_frame)

def measured(fn):
 tracemalloc.start(); t=time.perf_counter()
 try: value=fn(); sec=time.perf_counter()-t; _,peak=tracemalloc.get_traced_memory(); return value,sec,peak
 finally: tracemalloc.stop()

def record_sig(x): return json.dumps(asdict(x),sort_keys=True,default=str,separators=(",",":"))
def write(p): open("bt5c-landmark-probe.json","w").write(json.dumps(p,indent=2,sort_keys=True)+"\n")

def main():
 prefix,discovery,target,max_bars,offsets=config(); log("BT5C-6 runtime + memory + fail-closed validation START")
 s3=boto3.client("s3",endpoint_url=need("R2_ENDPOINT"),region_name="auto",aws_access_key_id=need("R2_ACCESS_KEY_ID"),aws_secret_access_key=need("R2_SECRET_ACCESS_KEY")); bucket=need("R2_BUCKET_NAME"); inventory=list_parquet_keys(s3,bucket,prefix); keys=deterministic_spread(inventory,discovery)
 selected=[]; frames={}; discovery_rows=[]
 for i,key in enumerate(keys,1):
  sid=key.rsplit("/",1)[-1].removesuffix(".parquet"); log(f"[discover {i}/{len(keys)}] {sid} START"); frame=normalize(pd.read_parquet(io.BytesIO(s3.get_object(Bucket=bucket,Key=key)["Body"].read()))); eligible=len(frame)<=max_bars and len(frame)>max(offsets)+10; discovery_rows.append({"security_id":sid,"bars":len(frame),"eligible":eligible}); log(f"[discover {i}/{len(keys)}] {sid} bars={len(frame)} eligible={eligible}")
  if eligible and len(selected)<target: selected.append(key); frames[key]=frame
  if len(selected)>=target: break
 if len(selected)<target:
  write({"contract":"BT5C_RUNTIME_MEMORY_FAIL_CLOSED_V1","verdict":"INCONCLUSIVE_INSUFFICIENT_CORPUS","selected":selected}); raise RuntimeError("insufficient deterministic corpus")
 results=[]; guard_tests=[]
 for si,key in enumerate(selected,1):
  sid=key.rsplit("/",1)[-1].removesuffix(".parquet"); frame=frames[key]; source_dates=pd.to_datetime(frame["date"],errors="raise").reset_index(drop=True); identity=(*frame_identity(frame),source_dates)
  (pre,pre_sec,pre_peak)=measured(lambda:(extract_excursion_landmarks(frame),extract_confirmed_window_landmarks(frame))); latest_primary,latest_aux=pre; log(f"[{si}/{len(selected)}] {sid} precompute_sec={pre_sec:.3f} peak_mb={pre_peak/1048576:.2f}")
  # Deliberately corrupt date ordering/content and prove the guard refuses reuse before engine execution.
  bad=frame.iloc[:-max(offsets)].copy().reset_index(drop=True)
  if len(bad)>2: bad.loc[1,"date"]=bad.loc[0,"date"]
  guard_ok=False; guard_error=None
  try: guarded_reuse(latest_primary,identity,bad)
  except RuntimeError as e: guard_error=str(e); guard_ok=guard_error=="BT5C_REUSE_GUARD_NOT_PREFIX"
  guard_tests.append({"security_id":sid,"corrupt_prefix_rejected":guard_ok,"error":guard_error}); log(f"[{si}] {sid} fail_closed_guard={guard_ok} error={guard_error}")
  if not guard_ok:
   write({"contract":"BT5C_RUNTIME_MEMORY_FAIL_CLOSED_V1","verdict":"FAIL_CLOSED_GUARD_FAILED","guard_tests":guard_tests}); raise RuntimeError(f"reuse guard failed for {sid}")
  for off in offsets:
   earlier=frame.iloc[:-off].copy().reset_index(drop=True); asof=pd.Timestamp(earlier.iloc[-1]["date"]).date()
   oracle,oracle_sec,oracle_peak=measured(lambda:analyze_security(security_id=sid,ticker=sid,frame=earlier,asof_date=asof)); calls={"excursion":0,"confirmed_window":0}
   def ax(local_frame): calls["excursion"]+=1; return guarded_reuse(latest_primary,identity,local_frame)
   def ac(local_frame): calls["confirmed_window"]+=1; return guarded_reuse(latest_aux,identity,local_frame)
   canonical.extract_excursion_landmarks=ax; canonical.extract_confirmed_window_landmarks=ac
   try: reused,reuse_sec,reuse_peak=measured(lambda:analyze_security(security_id=sid,ticker=sid,frame=earlier,asof_date=asof))
   finally: canonical.extract_excursion_landmarks=ORIGINAL_EXCURSION; canonical.extract_confirmed_window_landmarks=ORIGINAL_CONFIRMED
   exact=[record_sig(x) for x in oracle]==[record_sig(x) for x in reused]; row={"security_id":sid,"offset_sessions":off,"bars":len(earlier),"records":len(oracle),"exact":exact,"calls":calls,"oracle_sec":round(oracle_sec,6),"reuse_sec":round(reuse_sec,6),"speedup_ratio_excluding_precompute":round(oracle_sec/reuse_sec,6),"oracle_peak_mb":round(oracle_peak/1048576,4),"reuse_peak_mb":round(reuse_peak/1048576,4),"peak_memory_ratio_reuse_over_oracle":round(reuse_peak/oracle_peak,6) if oracle_peak else None,"complete_history_precompute_sec":round(pre_sec,6),"complete_history_precompute_peak_mb":round(pre_peak/1048576,4)}; results.append(row); log(f"[{sid}] off={off} exact={exact} speedup={oracle_sec/reuse_sec:.3f}x peak_oracle={oracle_peak/1048576:.2f}MB peak_reuse={reuse_peak/1048576:.2f}MB")
   if not exact or calls!={"excursion":1,"confirmed_window":1}:
    write({"contract":"BT5C_RUNTIME_MEMORY_FAIL_CLOSED_V1","verdict":"EXACTNESS_OR_EXERCISE_FAILURE","results":results,"guard_tests":guard_tests}); raise RuntimeError(f"BT5C-6 exactness/exercise failure {sid} off={off}")
 payload={"contract":"BT5C_RUNTIME_MEMORY_FAIL_CLOSED_V1","frozen_oneil_sha":ONEIL_SHA,"upstream_history_contract":UPSTREAM_CONTRACT,"history_prefix":prefix,"inventory_count":len(inventory),"selection":{"method":"deterministic_complete_history","target":target,"max_complete_history_bars":max_bars,"selected_keys":selected,"discovery":discovery_rows},"comparison_count":len(results),"all_exact":all(x["exact"] for x in results),"all_paths_exercised":all(x["calls"]=={"excursion":1,"confirmed_window":1} for x in results),"fail_closed_guard_pass":all(x["corrupt_prefix_rejected"] for x in guard_tests),"results":results,"guard_tests":guard_tests,"global_reuse_authorized":False,"history_truncated_for_selection":False,"production_eligibility_emitted":False,"strategy_returns_computed":False,"verdict":"BT5C6_TESTED_CASES_PASS"}; write(payload); log(f"BT5C-6 COMPLETE comparisons={len(results)} exact={payload['all_exact']} fail_closed={payload['fail_closed_guard_pass']}")
if __name__=="__main__": main()
