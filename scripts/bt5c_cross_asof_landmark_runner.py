from __future__ import annotations
import io,json,os,time
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
 discovery=int(os.getenv("BT5C_DISCOVERY_SAMPLE","96"))
 target=int(os.getenv("BT5C_FINAL_SAMPLE","4"))
 max_bars=int(os.getenv("BT5C_FINAL_MAX_BARS","800"))
 offsets=tuple(int(x) for x in os.getenv("BT5C_EARLIER_OFFSETS","10,40").split(",") if x.strip())
 if min(discovery,target,max_bars)<1 or target>discovery or not offsets or any(x<=0 for x in offsets):
  raise RuntimeError("invalid BT5C final-output probe configuration")
 return prefix,discovery,target,max_bars,offsets

def list_parquet_keys(s3,bucket,prefix):
 out=[]; token=None
 while True:
  kw={"Bucket":bucket,"Prefix":prefix}
  if token: kw["ContinuationToken"]=token
  r=s3.list_objects_v2(**kw)
  out.extend(x["Key"] for x in r.get("Contents",[]) if x["Key"].endswith(".parquet"))
  if not r.get("IsTruncated"): return sorted(out)
  token=r["NextContinuationToken"]

def deterministic_spread(keys,n):
 if not keys:return []
 n=min(n,len(keys))
 if n==1:return [keys[len(keys)//2]]
 return [keys[i] for i in dict.fromkeys(round(j*(len(keys)-1)/(n-1)) for j in range(n))]

def normalize(raw):
 f=raw.copy(); f.columns=[str(c).lower() for c in f.columns]
 dc=next((c for c in ("date","session_date","datetime") if c in f.columns),None)
 if dc is None: raise RuntimeError("date unavailable")
 rename={dc:"date"}; aliases={"adjusted_open":"open","adjusted_high":"high","adjusted_low":"low","adjusted_close":"close","adjusted_volume":"volume","adj_close":"close"}
 for s,d in aliases.items():
  if s in f.columns and d not in f.columns: rename[s]=d
 f=f.rename(columns=rename); req=["date","open","high","low","close","volume"]
 miss=[c for c in req if c not in f.columns]
 if miss: raise RuntimeError(f"missing {miss}")
 f=f[req].copy(); f["date"]=pd.to_datetime(f["date"],utc=True,errors="raise").dt.tz_localize(None)
 for c in req[1:]: f[c]=pd.to_numeric(f[c],errors="raise")
 return f.dropna().sort_values("date").drop_duplicates("date",keep="last").reset_index(drop=True)

def reusable_for_frame(latest,frame):
 cutoff=pd.Timestamp(frame.iloc[-1]["date"]).date()
 dates=set(pd.to_datetime(frame["date"],errors="raise").dt.date)
 return [m for m in latest if m.price_date in dates and m.confirmed_date<=cutoff]

def record_sig(x): return json.dumps(asdict(x),sort_keys=True,default=str,separators=(",",":"))
def write(p): open("bt5c-landmark-probe.json","w").write(json.dumps(p,indent=2,sort_keys=True)+"\n")

def main():
 prefix,discovery,target,max_bars,offsets=config()
 log("BT5C-5B FINAL material-output equivalence probe START")
 log("oracle=untouched analyze_security; reuse=standard raw excursion+confirmed-window landmarks reused from complete history; fusion and all downstream logic untouched/recomputed per asof")
 s3=boto3.client("s3",endpoint_url=need("R2_ENDPOINT"),region_name="auto",aws_access_key_id=need("R2_ACCESS_KEY_ID"),aws_secret_access_key=need("R2_SECRET_ACCESS_KEY"))
 bucket=need("R2_BUCKET_NAME"); inventory=list_parquet_keys(s3,bucket,prefix); discovery_keys=deterministic_spread(inventory,discovery)
 if not discovery_keys: raise RuntimeError(f"no parquet under {prefix}")
 selected=[]; frames={}; discovery_rows=[]
 for i,key in enumerate(discovery_keys,1):
  sid=key.rsplit("/",1)[-1].removesuffix(".parquet"); log(f"[discover {i}/{len(discovery_keys)}] {sid} download START")
  frame=normalize(pd.read_parquet(io.BytesIO(s3.get_object(Bucket=bucket,Key=key)["Body"].read())))
  eligible=len(frame)<=max_bars and len(frame)>max(offsets)+10
  discovery_rows.append({"security_id":sid,"source_key":key,"bars":len(frame),"eligible":eligible}); log(f"[discover {i}/{len(discovery_keys)}] {sid} bars={len(frame)} eligible={eligible}")
  if eligible and len(selected)<target: selected.append(key); frames[key]=frame
  if len(selected)>=target:
   log(f"deterministic corpus target reached after {i} discoveries; stopping discovery early"); break
 if len(selected)<target:
  payload={"contract":"BT5C_FINAL_OUTPUT_STANDARD_RAW_REUSE_EQUIVALENCE_V1","frozen_oneil_sha":ONEIL_SHA,"history_prefix":prefix,"selection":{"discovery_cap":discovery,"target_sample":target,"selected_keys":selected,"discovery":discovery_rows},"all_exact":False,"final_production_output_tested":False,"verdict":"INCONCLUSIVE_INSUFFICIENT_DETERMINISTIC_CORPUS"}; write(payload); raise RuntimeError(f"insufficient deterministic final-output corpus: need={target} got={len(selected)}")
 log(f"inventory={len(inventory)} selected={json.dumps(selected)}"); results=[]
 for si,key in enumerate(selected,1):
  sid=key.rsplit("/",1)[-1].removesuffix(".parquet"); frame=frames[key]
  t=time.perf_counter(); latest_primary=extract_excursion_landmarks(frame); latest_aux=extract_confirmed_window_landmarks(frame); precompute_sec=time.perf_counter()-t
  log(f"[{si}/{len(selected)}] {sid} complete_history_bars={len(frame)} primary={len(latest_primary)} auxiliary={len(latest_aux)} precompute_sec={precompute_sec:.3f}")
  for oi,off in enumerate(offsets,1):
   earlier=frame.iloc[:-off].copy().reset_index(drop=True); asof=pd.Timestamp(earlier.iloc[-1].date).date()
   t=time.perf_counter(); oracle=analyze_security(security_id=sid,ticker=sid,frame=earlier,asof_date=asof); oracle_sec=time.perf_counter()-t
   calls={"excursion":0,"confirmed_window":0}
   def accelerated_excursion(local_frame):
    calls["excursion"]+=1; return reusable_for_frame(latest_primary,local_frame)
   def accelerated_confirmed(local_frame):
    calls["confirmed_window"]+=1; return reusable_for_frame(latest_aux,local_frame)
   canonical.extract_excursion_landmarks=accelerated_excursion; canonical.extract_confirmed_window_landmarks=accelerated_confirmed
   try:
    t=time.perf_counter(); reused=analyze_security(security_id=sid,ticker=sid,frame=earlier,asof_date=asof); reuse_sec=time.perf_counter()-t
   finally:
    canonical.extract_excursion_landmarks=ORIGINAL_EXCURSION; canonical.extract_confirmed_window_landmarks=ORIGINAL_CONFIRMED
   a=[record_sig(x) for x in oracle]; b=[record_sig(x) for x in reused]; exact=a==b; first=None
   if not exact:
    lim=min(len(a),len(b)); first=next((j for j in range(lim) if a[j]!=b[j]),lim if len(a)!=len(b) else None)
   speedup=oracle_sec/reuse_sec if reuse_sec>0 else None
   row={"security_id":sid,"source_key":key,"earlier_asof":asof.isoformat(),"offset_sessions":off,"bars":len(earlier),"oracle_record_count":len(oracle),"reuse_record_count":len(reused),"exact":exact,"first_difference_index":first,"standard_raw_calls":calls,"oracle_sec":round(oracle_sec,6),"reuse_sec":round(reuse_sec,6),"speedup_ratio_excluding_amortized_precompute":round(speedup,6) if speedup else None,"complete_history_precompute_sec":round(precompute_sec,6)}
   results.append(row); log(f"[{si}.{oi}] {sid} off={off} bars={len(earlier)} records={len(oracle)} exact={exact} raw_calls={calls} oracle_sec={oracle_sec:.3f} reuse_sec={reuse_sec:.3f} speedup={speedup:.3f}x")
   if not exact:
    write({"contract":"BT5C_FINAL_OUTPUT_STANDARD_RAW_REUSE_EQUIVALENCE_V1","frozen_oneil_sha":ONEIL_SHA,"all_exact":False,"results":results,"verdict":"FINAL_OUTPUT_STANDARD_RAW_REUSE_COUNTEREXAMPLE_OBSERVED","global_reuse_authorized":False}); raise RuntimeError(f"final output mismatch {sid} offset={off} first={first}")
 exercised=sum(x["standard_raw_calls"]["excursion"]>0 and x["standard_raw_calls"]["confirmed_window"]>0 for x in results)
 payload={"contract":"BT5C_FINAL_OUTPUT_STANDARD_RAW_REUSE_EQUIVALENCE_V1","frozen_oneil_sha":ONEIL_SHA,"upstream_history_contract":UPSTREAM_CONTRACT,"history_prefix":prefix,"inventory_count":len(inventory),"selection":{"method":"deterministic_even_spread_expanded_until_target_or_cap_v2","discovery_cap":discovery,"actual_discoveries":len(discovery_rows),"target_sample":target,"max_complete_history_bars":max_bars,"selected_keys":selected,"discovery":discovery_rows},"earlier_offsets":list(offsets),"comparison_count":len(results),"accelerated_path_exercised_count":exercised,"all_exact":bool(results) and all(x["exact"] for x in results),"results":results,"history_truncated_for_selection":False,"fusion_recomputed_per_asof":True,"downstream_frozen_logic_untouched":True,"final_production_output_tested":True,"global_reuse_authorized":False,"production_eligibility_emitted":False,"strategy_returns_computed":False,"verdict":"FINAL_OUTPUT_STANDARD_RAW_REUSE_EXACT_OBSERVED_IN_TESTED_CASES"}; write(payload)
 log(f"BT5C-5B COMPLETE comparisons={len(results)} exercised={exercised} all_exact={payload['all_exact']}")
if __name__=="__main__": main()
