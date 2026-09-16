"""BT5C exact replay acceleration research harness.

Frozen O'Neil remains the only detector. This first prototype is deliberately
conservative: it caches only identical semantic inputs and therefore cannot yet
accelerate a new as-of date. It establishes exact-output/cache integrity before
any cross-as-of incremental optimization is attempted.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
import hashlib, json, time
from pathlib import Path
from typing import Any, Callable, Iterable
import pandas as pd

FROZEN_ONEIL_SHA="c433cc1e35a5aa32a46f732cd8c5545935e36e40"
EXPECTED_OUTPUT_SCHEMA="oneil-pattern-output-v2"
EXPECTED_ENGINE_VERSION="33-core-p8-frozen-v1"
CACHE_CONTRACT="BT5C_EXACT_FULL_HISTORY_CACHE_V1"
MATERIAL_FIELDS=("assessment_id","output_schema_version","engine_version","labelled_validation_status","security_id","ticker","asof_date","candidate_id","base_id","lineage_id","pattern","normalized_status","native_state","candidate_semantics","structural_signature","structural_start","structural_end","pivot_source_date","pivot_level","depth_pct","detector_faults","detector_contract_version")

def _jsonable(v: Any)->Any:
    if v is None or isinstance(v,(str,int,bool)): return v
    if isinstance(v,float): return None if pd.isna(v) else v
    if isinstance(v,(pd.Timestamp,date)): return str(v)
    if hasattr(v,"item"):
        try: return _jsonable(v.item())
        except (ValueError,TypeError): pass
    if isinstance(v,dict): return {str(k):_jsonable(x) for k,x in v.items()}
    if isinstance(v,(list,tuple,set)): return [_jsonable(x) for x in v]
    return str(v)

def canonical_rows(records: Iterable[Any])->list[dict[str,Any]]:
    out=[]
    for r in records:
        d=r if isinstance(r,dict) else r.to_dict() if hasattr(r,"to_dict") else None
        if d is None: raise TypeError(f"Unsupported O'Neil output: {type(r)!r}")
        row={f:_jsonable(d.get(f)) for f in MATERIAL_FIELDS}
        if row["output_schema_version"]!=EXPECTED_OUTPUT_SCHEMA or row["engine_version"]!=EXPECTED_ENGINE_VERSION:
            raise RuntimeError("Frozen O'Neil engine/schema mismatch")
        out.append(row)
    out.sort(key=lambda x:(str(x.get("assessment_id")),str(x.get("candidate_id"))))
    return out

def rows_digest(rows):
    return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def causal_frame(frame,asof):
    f=frame.copy(); f["date"]=pd.to_datetime(f["date"],errors="raise")
    return f.loc[f["date"].dt.date<=asof].sort_values("date").drop_duplicates("date").reset_index(drop=True)

def frame_digest(frame):
    payload=frame.to_json(orient="table",date_format="iso",date_unit="ns",index=False,double_precision=15)
    return hashlib.sha256(payload.encode()).hexdigest()

@dataclass(frozen=True)
class CacheKey:
    security_id:str; ticker:str; asof_date:str; frame_sha256:str
    oneil_sha:str=FROZEN_ONEIL_SHA; engine_version:str=EXPECTED_ENGINE_VERSION
    output_schema:str=EXPECTED_OUTPUT_SCHEMA; contract:str=CACHE_CONTRACT
    @property
    def digest(self): return hashlib.sha256(json.dumps(self.__dict__,sort_keys=True,separators=(",",":")).encode()).hexdigest()

class ExactReplayCache:
    def __init__(self,root): self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
    def _path(self,key): return self.root/f"{key.digest}.json"
    def load(self,key):
        p=self._path(key)
        if not p.exists(): return None
        x=json.loads(p.read_text())
        if x.get("cache_key")!=key.__dict__: raise RuntimeError("cache key mismatch")
        rows=x.get("rows")
        if not isinstance(rows,list) or rows_digest(rows)!=x.get("rows_sha256"): raise RuntimeError("cache integrity failure")
        return rows
    def store(self,key,rows):
        p=self._path(key); tmp=p.with_suffix(".tmp")
        tmp.write_text(json.dumps({"contract":CACHE_CONTRACT,"cache_key":key.__dict__,"rows_sha256":rows_digest(rows),"rows":rows},sort_keys=True,separators=(",",":")))
        tmp.replace(p)

def exact_cached_analyze(*,analyze_security:Callable[...,Iterable[Any]],cache:ExactReplayCache,security_id,ticker,frame,asof_date):
    causal=causal_frame(frame,asof_date); key=CacheKey(security_id,ticker,asof_date.isoformat(),frame_digest(causal)); start=time.perf_counter(); rows=cache.load(key)
    if rows is not None: return {"source":"EXACT_CACHE_HIT","rows":rows,"rows_sha256":rows_digest(rows),"elapsed_sec":round(time.perf_counter()-start,6),"cache_key":key.digest}
    rows=canonical_rows(analyze_security(security_id=security_id,ticker=ticker,frame=causal,asof_date=asof_date)); cache.store(key,rows)
    return {"source":"UNTOUCHED_FULL_HISTORY_ENGINE","rows":rows,"rows_sha256":rows_digest(rows),"elapsed_sec":round(time.perf_counter()-start,6),"cache_key":key.digest}

def validate_cache_case(*,analyze_security,cache,security_id,ticker,frame,asof_date):
    causal=causal_frame(frame,asof_date); t=time.perf_counter()
    oracle=canonical_rows(analyze_security(security_id=security_id,ticker=ticker,frame=causal,asof_date=asof_date)); oracle_sec=round(time.perf_counter()-t,6)
    first=exact_cached_analyze(analyze_security=analyze_security,cache=cache,security_id=security_id,ticker=ticker,frame=frame,asof_date=asof_date)
    second=exact_cached_analyze(analyze_security=analyze_security,cache=cache,security_id=security_id,ticker=ticker,frame=frame,asof_date=asof_date)
    exact1=oracle==first["rows"]; exact2=oracle==second["rows"]
    if not exact1 or not exact2 or second["source"]!="EXACT_CACHE_HIT": raise AssertionError("BT5C exact-cache equivalence failed")
    return {"contract":CACHE_CONTRACT,"security_id":security_id,"asof_date":asof_date.isoformat(),"causal_bars":len(causal),"oracle_elapsed_sec":oracle_sec,"oracle_sha256":rows_digest(oracle),"first_source":first["source"],"first_elapsed_sec":first["elapsed_sec"],"second_source":second["source"],"second_elapsed_sec":second["elapsed_sec"],"exact":True,"accelerator_scope":"IDENTICAL_SEMANTIC_INPUT_CACHE_ONLY","cross_asof_incremental_authorized":False,"bounded_replay_authorized":False,"production_eligibility_emitted":False,"strategy_returns_computed":False}
