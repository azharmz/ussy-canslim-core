"""BT5C exact cross-asof landmark + segmentation reuse probe.
Frozen O'Neil is imported unchanged. Later-prefix raw landmarks are filtered by
confirmed_date; fusion and segmentation are deliberately recomputed on each
earlier causal frame.  This tests the next exact-computation boundary without
changing any frozen detector code.
"""
from __future__ import annotations
from dataclasses import asdict,is_dataclass
from datetime import date
import hashlib,json,time
from typing import Any
import pandas as pd
from oneil_patterns.landmarks.excursion import extract_excursion_landmarks
from oneil_patterns.landmarks.confirmed_window import extract_confirmed_window_landmarks
from oneil_patterns.landmarks.fusion import fuse_landmark_sources
from oneil_patterns.segmentation.segmenter import segment_base_candidates
CONTRACT="BT5C_CROSS_ASOF_SEGMENTATION_EQUIVALENCE_PROBE_V1"
FROZEN_ONEIL_SHA="c433cc1e35a5aa32a46f732cd8c5545935e36e40"

def _jsonable(v:Any)->Any:
 if v is None or isinstance(v,(str,int,float,bool)): return v
 if isinstance(v,(date,pd.Timestamp)): return str(v)
 if isinstance(v,dict): return {str(k):_jsonable(x) for k,x in v.items()}
 if isinstance(v,(list,tuple,set)): return [_jsonable(x) for x in v]
 if is_dataclass(v): return _jsonable(asdict(v))
 if hasattr(v,"value"): return _jsonable(v.value)
 return str(v)
def canonical_landmark(x):
 return {"type":_jsonable(x.type),"price":float(x.price),"price_date":_jsonable(x.price_date),"confirmed_date":_jsonable(x.confirmed_date),"method":str(x.method),"evidence":_jsonable(x.evidence)}
def canonical(items):
 rows=[canonical_landmark(x) for x in items]; rows.sort(key=lambda x:(x["price_date"],x["confirmed_date"],x["type"],x["method"],json.dumps(x["evidence"],sort_keys=True,separators=(",",":")))); return rows
def canonical_segments(items):
 rows=[_jsonable(x) for x in items]; rows.sort(key=lambda x:json.dumps(x,sort_keys=True,separators=(",",":"))); return rows
def digest(rows): return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def prefix(frame,asof):
 f=frame.copy(); f["date"]=pd.to_datetime(f["date"],errors="raise"); return f.loc[f["date"].dt.date<=asof].sort_values("date").drop_duplicates("date").reset_index(drop=True)
def extract_all(frame,asof):
 t=time.perf_counter(); exc=extract_excursion_landmarks(frame); a=time.perf_counter(); win=extract_confirmed_window_landmarks(frame); b=time.perf_counter(); fused=fuse_landmark_sources(frame,exc,win); c=time.perf_counter(); seg=segment_base_candidates(frame,fused,asof_date=asof); d=time.perf_counter()
 return {"excursion_objects":exc,"window_objects":win,"excursion":canonical(exc),"window":canonical(win),"fused":canonical(fused),"segments":canonical_segments(seg),"timing_sec":{"excursion":round(a-t,6),"window":round(b-a,6),"fusion":round(c-b,6),"segmentation":round(d-c,6),"total":round(d-t,6)}}
def cmp(a,b): return {"exact":a==b,"oracle_count":len(a),"reused_count":len(b),"oracle_sha256":digest(a),"reused_sha256":digest(b)}
def run_probe(frame,asof_dates):
 dates=sorted(set(asof_dates)); latest=dates[-1]; lf=prefix(frame,latest); ls=extract_all(lf,latest); cases=[]; all_exact=True
 for asof in dates[:-1]:
  earlier=prefix(frame,asof); oracle=extract_all(earlier,asof)
  reused_exc_obj=[x for x in ls["excursion_objects"] if x.confirmed_date<=asof]
  reused_win_obj=[x for x in ls["window_objects"] if x.confirmed_date<=asof]
  t=time.perf_counter(); reused_fused_obj=fuse_landmark_sources(earlier,reused_exc_obj,reused_win_obj); a=time.perf_counter(); reused_seg_obj=segment_base_candidates(earlier,reused_fused_obj,asof_date=asof); b=time.perf_counter()
  components={"excursion":cmp(oracle["excursion"],canonical(reused_exc_obj)),"window":cmp(oracle["window"],canonical(reused_win_obj)),"fused_recomputed":cmp(oracle["fused"],canonical(reused_fused_obj)),"segmentation_recomputed":cmp(oracle["segments"],canonical_segments(reused_seg_obj))}
  exact=all(x["exact"] for x in components.values()); all_exact=all_exact and exact
  cases.append({"asof_date":asof.isoformat(),"bars":len(earlier),"oracle_timing_sec":oracle["timing_sec"],"reuse_timing_sec":{"fusion":round(a-t,6),"segmentation":round(b-a,6),"total":round(b-t,6)},"components":components,"exact":exact})
 return {"contract":CONTRACT,"frozen_oneil_sha":FROZEN_ONEIL_SHA,"latest_asof_date":latest.isoformat(),"latest_bars":len(lf),"latest_extraction_timing_sec":ls["timing_sec"],"cases":cases,"all_exact":all_exact,"raw_landmark_reuse_validation":"PRIOR_UNTOUCHED_8_SECURITIES_32_COMPARISONS_EXACT","segmentation_cross_asof_reuse_authorized":False,"morphology_cross_asof_reuse_authorized":False,"bounded_replay_authorized":False,"production_eligibility_emitted":False,"strategy_returns_computed":False,"verdict":"SEGMENTATION_RECOMPUTE_FROM_REUSED_RAW_LANDMARKS_EXACT_OBSERVED" if all_exact else "SEGMENTATION_REUSE_PATH_NOT_EXACT_FAIL_CLOSED"}
