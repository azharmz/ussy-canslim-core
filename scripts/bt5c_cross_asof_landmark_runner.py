from __future__ import annotations
import io,json,os,time
from dataclasses import asdict
import boto3
import pandas as pd
from oneil_patterns.landmarks.boundary import to_candidate_with_boundary
from oneil_patterns.landmarks.candidate import LandmarkCandidate
from oneil_patterns.landmarks.confirmed_window import ConfirmedWindowParams, extract_confirmed_window_landmarks
from oneil_patterns.landmarks.model import LandmarkType
from oneil_patterns.validation.structural_assembly import DB_LOCAL_TURN_ASSEMBLY_VERSION, assemble_multiturn_double_bottoms

ONEIL_SHA="c433cc1e35a5aa32a46f732cd8c5545935e36e40"
PREFIX="history/ohlcv/"
UPSTREAM_CONTRACT="azharmz/ussy-data:HISTORY_PREFIX=history/ohlcv/"
SECURITIES=["BMG9460G1015","BMG4690M1010","AU0000421851"]
EARLIER_OFFSETS=[5,10,20,40]
PARAMS=ConfirmedWindowParams(confirm_sessions=3,min_excursion_pct=0.0)

def log(x): print(x,flush=True)
def need(n):
 v=os.getenv(n)
 if not v: raise RuntimeError(f"missing {n}")
 return v

def normalize(raw):
 f=raw.copy(); f.columns=[str(c).lower() for c in f.columns]; dc=next((c for c in ("date","session_date","datetime") if c in f.columns),None)
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

def mark_sig(x):
 d=asdict(x); return json.dumps(d,sort_keys=True,default=str,separators=(",",":"))
def geom_sig(x):
 d=asdict(x); return json.dumps(d,sort_keys=True,default=str,separators=(",",":"))
def raw(frame): return extract_confirmed_window_landmarks(frame,PARAMS)

def geometries_from_raw(frame,marks,asof):
 candidates=[]
 for mark in marks:
  if mark.confirmed_date>asof: continue
  prominence=mark.evidence.get("prominence_pct")
  c=to_candidate_with_boundary(frame,mark,prominence_pct=float(prominence) if prominence is not None else None)
  c=LandmarkCandidate.from_landmark(mark,amplitude_pct=c.amplitude_pct,prominence_pct=c.prominence_pct,separation_sessions=c.separation_sessions,boundary=c.boundary,extra_evidence={**c.evidence,"p8_auxiliary_role":"DOUBLE_BOTTOM_LOCAL_TURN","p8_auxiliary_version":DB_LOCAL_TURN_ASSEMBLY_VERSION})
  candidates.append(c)
 geometries=assemble_multiturn_double_bottoms(frame,candidates,asof_date=asof)
 highs=[x for x in candidates if x.type==LandmarkType.SWING_HIGH and x.confirmed_date<=asof]
 # Exact comparison below uses structural DB geometry before final evidence-only right-edge decoration.
 # Right-edge decoration is deterministic from candidates and separately counted.
 return geometries,len(highs)

def main():
 log("BT5C local-turn raw reuse exactness probe START")
 s3=boto3.client("s3",endpoint_url=need("R2_ENDPOINT"),region_name="auto",aws_access_key_id=need("R2_ACCESS_KEY_ID"),aws_secret_access_key=need("R2_SECRET_ACCESS_KEY")); bucket=need("R2_BUCKET_NAME")
 results=[]
 for si,sid in enumerate(SECURITIES,1):
  key=f"{PREFIX}{sid}.parquet"; log(f"[{si}/{len(SECURITIES)}] {sid} download START")
  frame=normalize(pd.read_parquet(io.BytesIO(s3.get_object(Bucket=bucket,Key=key)["Body"].read())))
  latest_asof=pd.Timestamp(frame.iloc[-1].date).date(); t=time.perf_counter(); latest_raw=raw(frame); latest_sec=time.perf_counter()-t
  log(f"[{si}/{len(SECURITIES)}] {sid} bars={len(frame)} latest_raw={len(latest_raw)} extract_sec={latest_sec:.3f}")
  for oi,off in enumerate(EARLIER_OFFSETS,1):
   if len(frame)<=off+10: continue
   earlier=frame.iloc[:-off].copy().reset_index(drop=True); asof=pd.Timestamp(earlier.iloc[-1].date).date()
   t=time.perf_counter(); oracle=raw(earlier); oracle_sec=time.perf_counter()-t
   reused=[m for m in latest_raw if m.confirmed_date<=asof and m.price_date<=asof]
   raw_exact=[mark_sig(x) for x in oracle]==[mark_sig(x) for x in reused]
   t=time.perf_counter(); oracle_geom,oracle_highs=geometries_from_raw(earlier,oracle,asof); oracle_geom_sec=time.perf_counter()-t
   t=time.perf_counter(); reuse_geom,reuse_highs=geometries_from_raw(earlier,reused,asof); reuse_geom_sec=time.perf_counter()-t
   geometry_exact=[geom_sig(x) for x in oracle_geom]==[geom_sig(x) for x in reuse_geom]
   exact=raw_exact and geometry_exact and oracle_highs==reuse_highs
   row={"security_id":sid,"latest_asof":latest_asof.isoformat(),"earlier_asof":asof.isoformat(),"offset_sessions":off,"bars":len(earlier),"oracle_raw_count":len(oracle),"reused_raw_count":len(reused),"raw_exact":raw_exact,"oracle_geometry_count":len(oracle_geom),"reuse_geometry_count":len(reuse_geom),"geometry_exact":geometry_exact,"oracle_high_count":oracle_highs,"reuse_high_count":reuse_highs,"exact":exact,"oracle_raw_sec":round(oracle_sec,6),"oracle_geometry_sec":round(oracle_geom_sec,6),"reuse_geometry_sec":round(reuse_geom_sec,6)}; results.append(row)
   log(f"[{si}/{len(SECURITIES)}.{oi}] {sid} off={off} bars={len(earlier)} raw={len(oracle)} geom={len(oracle_geom)} raw_exact={raw_exact} geometry_exact={geometry_exact} exact={exact}")
   if not exact: raise RuntimeError(f"exactness mismatch {sid} offset={off}")
 all_exact=bool(results) and all(r["exact"] for r in results)
 payload={"contract":"BT5C_LOCAL_TURN_RAW_REUSE_EQUIVALENCE_PROBE_V1","frozen_oneil_sha":ONEIL_SHA,"upstream_history_contract":UPSTREAM_CONTRACT,"history_prefix":PREFIX,"params":{"confirm_sessions":3,"min_excursion_pct":0.0},"reuse_rule":"extract latest raw local-turn landmarks once; earlier reuse only if confirmed_date<=earlier_asof and price_date<=earlier_asof; recompute boundary candidates and DB geometry on complete earlier causal frame","security_count":len(set(r["security_id"] for r in results)),"comparison_count":len(results),"all_exact":all_exact,"results":results,"production_eligibility_emitted":False,"strategy_returns_computed":False,"global_reuse_authorized":False,"verdict":"LOCAL_TURN_RAW_REUSE_EXACT_OBSERVED_IN_TESTED_CASES" if all_exact else "COUNTEREXAMPLE_OBSERVED"}
 open("bt5c-landmark-probe.json","w").write(json.dumps(payload,indent=2,sort_keys=True)+"\n"); log(f"BT5C local-turn raw reuse exactness probe COMPLETE comparisons={len(results)} all_exact={all_exact}")
if __name__=="__main__": main()
