from __future__ import annotations
import io,json,os,time
from dataclasses import asdict,replace
import boto3
import pandas as pd
from oneil_patterns.landmarks.candidate import LandmarkCandidate
from oneil_patterns.landmarks.confirmed_window import ConfirmedWindowParams,extract_confirmed_window_landmarks
from oneil_patterns.landmarks.boundary import to_candidate_with_boundary
from oneil_patterns.landmarks.model import LandmarkType
from oneil_patterns.production.engine import analyze_security
import oneil_patterns.validation.canonical_predictions as canonical
from oneil_patterns.validation.structural_assembly import assemble_multiturn_double_bottoms,DB_LOCAL_TURN_ASSEMBLY_VERSION
ONEIL_SHA="c433cc1e35a5aa32a46f732cd8c5545935e36e40"; DEFAULT_PREFIX="history/ohlcv/"; UPSTREAM_CONTRACT="azharmz/ussy-data:HISTORY_PREFIX=history/ohlcv/"; PARAMS=ConfirmedWindowParams(confirm_sessions=3,min_excursion_pct=0.0); ORIGINAL_LOCAL_TURN=canonical.assemble_local_turn_double_bottoms
def log(x): print(x,flush=True)
def need(n):
 v=os.getenv(n)
 if not v: raise RuntimeError(f"missing {n}")
 return v
def config():
 prefix=os.getenv("BT5C_HISTORY_PREFIX",DEFAULT_PREFIX)
 if not prefix.endswith("/"): prefix+="/"
 discovery=int(os.getenv("BT5C_DISCOVERY_SAMPLE","24")); target=int(os.getenv("BT5C_FINAL_SAMPLE","4")); max_bars=int(os.getenv("BT5C_FINAL_MAX_BARS","800")); offsets=tuple(int(x) for x in os.getenv("BT5C_EARLIER_OFFSETS","10,40").split(",") if x.strip())
 if min(discovery,target,max_bars)<1 or target>discovery or not offsets or any(x<=0 for x in offsets): raise RuntimeError("invalid BT5C final-output probe configuration")
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
def raw_extract(frame): return extract_confirmed_window_landmarks(frame,PARAMS)
def reuse_structural(frame,latest_raw,asof):
 raw=[m for m in latest_raw if m.confirmed_date<=asof and m.price_date<=asof]; candidates=[]
 for mark in raw:
  prominence=mark.evidence.get("prominence_pct"); c=to_candidate_with_boundary(frame,mark,prominence_pct=float(prominence) if prominence is not None else None)
  candidates.append(LandmarkCandidate.from_landmark(mark,amplitude_pct=c.amplitude_pct,prominence_pct=c.prominence_pct,separation_sessions=c.separation_sessions,boundary=c.boundary,extra_evidence={**c.evidence,"p8_auxiliary_role":"DOUBLE_BOTTOM_LOCAL_TURN","p8_auxiliary_version":DB_LOCAL_TURN_ASSEMBLY_VERSION}))
 geometries=assemble_multiturn_double_bottoms(frame,candidates,asof_date=asof); highs=[x for x in candidates if x.type==LandmarkType.SWING_HIGH and x.confirmed_date<=asof]
 return [replace(g,evidence={**dict(g.evidence),"p8_auxiliary_version":DB_LOCAL_TURN_ASSEMBLY_VERSION,"p8_local_right_edge_open":not any(x.price_date>g.trough_2.price_date for x in highs)}) for g in geometries]
def record_sig(x): return json.dumps(asdict(x),sort_keys=True,default=str,separators=(",",":"))
def write(p): open("bt5c-landmark-probe.json","w").write(json.dumps(p,indent=2,sort_keys=True)+"\n")
def main():
 prefix,discovery,target,max_bars,offsets=config(); log("BT5C-5 FINAL material-output equivalence probe START"); log("oracle=untouched analyze_security; reuse=only local-turn fallback replaced by BT5C-4 exact structural reuse")
 s3=boto3.client("s3",endpoint_url=need("R2_ENDPOINT"),region_name="auto",aws_access_key_id=need("R2_ACCESS_KEY_ID"),aws_secret_access_key=need("R2_SECRET_ACCESS_KEY")); bucket=need("R2_BUCKET_NAME"); inventory=list_parquet_keys(s3,bucket,prefix); discovery_keys=deterministic_spread(inventory,discovery)
 if not discovery_keys: raise RuntimeError(f"no parquet under {prefix}")
 selected=[]; frames={}; discovery_rows=[]
 for i,key in enumerate(discovery_keys,1):
  sid=key.rsplit("/",1)[-1].removesuffix(".parquet"); log(f"[discover {i}/{len(discovery_keys)}] {sid} download START"); frame=normalize(pd.read_parquet(io.BytesIO(s3.get_object(Bucket=bucket,Key=key)["Body"].read()))); eligible=len(frame)<=max_bars and len(frame)>max(offsets)+10; discovery_rows.append({"security_id":sid,"source_key":key,"bars":len(frame),"eligible":eligible}); log(f"[discover {i}/{len(discovery_keys)}] {sid} bars={len(frame)} eligible={eligible}")
  if eligible and len(selected)<target: selected.append(key); frames[key]=frame
 if len(selected)<target: raise RuntimeError(f"insufficient deterministic final-output corpus: need={target} got={len(selected)}")
 log(f"inventory={len(inventory)} selected={json.dumps(selected)}"); results=[]
 for si,key in enumerate(selected,1):
  sid=key.rsplit("/",1)[-1].removesuffix(".parquet"); frame=frames[key]; t=time.perf_counter(); latest_raw=raw_extract(frame); raw_sec=time.perf_counter()-t; log(f"[{si}/{len(selected)}] {sid} complete_history_bars={len(frame)} latest_raw={len(latest_raw)} raw_sec={raw_sec:.3f}")
  for oi,off in enumerate(offsets,1):
   earlier=frame.iloc[:-off].copy().reset_index(drop=True); asof=pd.Timestamp(earlier.iloc[-1].date).date(); t=time.perf_counter(); oracle=analyze_security(security_id=sid,ticker=sid,frame=earlier,asof_date=asof); oracle_sec=time.perf_counter()-t; calls={"count":0}
   def accelerated_local_turn(local_frame,*,asof_date): calls["count"]+=1; return reuse_structural(local_frame,latest_raw,asof_date)
   canonical.assemble_local_turn_double_bottoms=accelerated_local_turn
   try:
    t=time.perf_counter(); reused=analyze_security(security_id=sid,ticker=sid,frame=earlier,asof_date=asof); reuse_sec=time.perf_counter()-t
   finally: canonical.assemble_local_turn_double_bottoms=ORIGINAL_LOCAL_TURN
   a=[record_sig(x) for x in oracle]; b=[record_sig(x) for x in reused]; exact=a==b; first=None
   if not exact:
    lim=min(len(a),len(b)); first=next((j for j in range(lim) if a[j]!=b[j]),lim if len(a)!=len(b) else None)
   speedup=oracle_sec/reuse_sec if reuse_sec>0 else None; row={"security_id":sid,"source_key":key,"earlier_asof":asof.isoformat(),"offset_sessions":off,"bars":len(earlier),"oracle_record_count":len(oracle),"reuse_record_count":len(reused),"exact":exact,"first_difference_index":first,"local_turn_fallback_calls":calls["count"],"oracle_sec":round(oracle_sec,6),"reuse_sec":round(reuse_sec,6),"speedup_ratio":round(speedup,6) if speedup else None,"latest_raw_extract_sec":round(raw_sec,6)}; results.append(row); log(f"[{si}.{oi}] {sid} off={off} bars={len(earlier)} records={len(oracle)} exact={exact} local_turn_calls={calls['count']} oracle_sec={oracle_sec:.3f} reuse_sec={reuse_sec:.3f} speedup={speedup:.3f}x")
   if not exact:
    write({"contract":"BT5C_FINAL_OUTPUT_LOCAL_TURN_REUSE_EQUIVALENCE_V1","frozen_oneil_sha":ONEIL_SHA,"all_exact":False,"results":results,"verdict":"FINAL_OUTPUT_REUSE_COUNTEREXAMPLE_OBSERVED","global_reuse_authorized":False}); raise RuntimeError(f"final output mismatch {sid} offset={off} first={first}")
 exercised=sum(x["local_turn_fallback_calls"]>0 for x in results); payload={"contract":"BT5C_FINAL_OUTPUT_LOCAL_TURN_REUSE_EQUIVALENCE_V1","frozen_oneil_sha":ONEIL_SHA,"upstream_history_contract":UPSTREAM_CONTRACT,"history_prefix":prefix,"inventory_count":len(inventory),"selection":{"method":"deterministic_even_spread_then_complete-history-size-gate_v1","discovery_sample":discovery,"target_sample":target,"max_complete_history_bars":max_bars,"selected_keys":selected,"discovery":discovery_rows},"earlier_offsets":list(offsets),"comparison_count":len(results),"accelerated_path_exercised_count":exercised,"all_exact":bool(results) and all(x["exact"] for x in results),"results":results,"history_truncated_for_selection":False,"final_production_output_tested":True,"global_reuse_authorized":False,"production_eligibility_emitted":False,"strategy_returns_computed":False,"verdict":"FINAL_OUTPUT_REUSE_EXACT_OBSERVED_IN_TESTED_CASES"}; write(payload); log(f"BT5C-5 COMPLETE comparisons={len(results)} exercised={exercised} all_exact={payload['all_exact']}")
if __name__=="__main__": main()
