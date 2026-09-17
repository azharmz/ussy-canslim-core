"""Durable BT5C authorized cross-as-of landmark reuse.

Research-only acceleration boundary frozen by issue #9. Only raw excursion and
confirmed-window landmarks may be reused from the exact same complete-history
source into an exact causal prefix. All fusion, segmentation, structural
assembly, detectors and output conversion remain inside untouched frozen
O'Neil analyze_security.
"""
from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib, json
from typing import Any, Callable, Iterable
import pandas as pd
FROZEN_ONEIL_SHA="c433cc1e35a5aa32a46f732cd8c5545935e36e40"; EXPECTED_OUTPUT_SCHEMA="oneil-pattern-output-v2"; EXPECTED_ENGINE_VERSION="33-core-p8-frozen-v1"; CONTRACT="BT5C_AUTHORIZED_RAW_LANDMARK_REUSE_V1"; AUTHORIZED_PATCHES=("extract_excursion_landmarks","extract_confirmed_window_landmarks")
def normalize_ohlcv(raw):
 f=raw.copy(); f.columns=[str(c).lower() for c in f.columns]; dc=next((c for c in("date","session_date","datetime") if c in f.columns),None)
 if dc is None: raise RuntimeError("BT5C_SOURCE_DATE_UNAVAILABLE")
 rename={dc:"date"}; aliases={"adjusted_open":"open","adjusted_high":"high","adjusted_low":"low","adjusted_close":"close","adjusted_volume":"volume","adj_close":"close"}
 for src,dst in aliases.items():
  if src in f.columns and dst not in f.columns: rename[src]=dst
 f=f.rename(columns=rename); req=["date","open","high","low","close","volume"]; missing=[c for c in req if c not in f.columns]
 if missing: raise RuntimeError(f"BT5C_SOURCE_COLUMNS_MISSING:{','.join(missing)}")
 f=f[req].copy(); f["date"]=pd.to_datetime(f["date"],utc=True,errors="raise").dt.tz_localize(None)
 for c in req[1:]: f[c]=pd.to_numeric(f[c],errors="raise")
 if f[req].isna().any().any(): raise RuntimeError("BT5C_SOURCE_NULL_OHLCV")
 f=f.sort_values("date").drop_duplicates("date",keep="last").reset_index(drop=True)
 if f.empty: raise RuntimeError("BT5C_SOURCE_EMPTY")
 return f
def frame_sha256(frame): return hashlib.sha256(frame.to_json(orient="table",date_format="iso",date_unit="ns",index=False,double_precision=15).encode()).hexdigest()
@dataclass(frozen=True)
class SourceIdentity:
 rows:int; start_date:str; end_date:str; frame_sha256:str; dates:tuple[str,...]
 @classmethod
 def from_frame(cls,frame):
  f=normalize_ohlcv(frame); dates=tuple(pd.to_datetime(f["date"]).dt.strftime("%Y-%m-%dT%H:%M:%S.%f").tolist()); return cls(len(f),dates[0],dates[-1],frame_sha256(f),dates)
 @property
 def lineage_sha256(self):
  d={"rows":self.rows,"start_date":self.start_date,"end_date":self.end_date,"frame_sha256":self.frame_sha256,"dates":self.dates,"oneil_sha":FROZEN_ONEIL_SHA,"contract":CONTRACT}; return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def assert_exact_causal_prefix(source,local_frame):
 local=normalize_ohlcv(local_frame); n=len(local)
 if n>source.rows: raise RuntimeError("BT5C_REUSE_GUARD_NOT_PREFIX")
 dates=tuple(pd.to_datetime(local["date"]).dt.strftime("%Y-%m-%dT%H:%M:%S.%f").tolist())
 if dates!=source.dates[:n]: raise RuntimeError("BT5C_REUSE_GUARD_NOT_PREFIX")
 return local
def reusable_for_frame(landmarks,frame):
 cutoff=pd.Timestamp(frame.iloc[-1]["date"]).date(); dates=set(pd.to_datetime(frame["date"]).dt.date); return [m for m in landmarks if m.price_date in dates and m.confirmed_date<=cutoff]
@dataclass
class RawLandmarkState: source:SourceIdentity; excursion:list[Any]; confirmed_window:list[Any]
def precompute_raw_landmarks(frame,*,excursion_extractor,confirmed_extractor):
 complete=normalize_ohlcv(frame); return RawLandmarkState(SourceIdentity.from_frame(complete),list(excursion_extractor(complete)),list(confirmed_extractor(complete)))
@contextmanager
def _authorized_patch(canonical_module,state):
 oe=canonical_module.extract_excursion_landmarks; oc=canonical_module.extract_confirmed_window_landmarks
 def excursion(local_frame): return reusable_for_frame(state.excursion,assert_exact_causal_prefix(state.source,local_frame))
 def confirmed(local_frame): return reusable_for_frame(state.confirmed_window,assert_exact_causal_prefix(state.source,local_frame))
 canonical_module.extract_excursion_landmarks=excursion; canonical_module.extract_confirmed_window_landmarks=confirmed
 try: yield
 finally: canonical_module.extract_excursion_landmarks=oe; canonical_module.extract_confirmed_window_landmarks=oc
def analyze_with_authorized_reuse(*,analyze_security,canonical_module,state,security_id,ticker,frame,asof_date,fallback_to_oracle=True):
 try: local=assert_exact_causal_prefix(state.source,frame)
 except RuntimeError:
  if not fallback_to_oracle: raise
  return {"source":"UNTOUCHED_ORACLE_FALLBACK","records":list(analyze_security(security_id=security_id,ticker=ticker,frame=frame,asof_date=asof_date)),"reuse_guard":"FAILED"}
 with _authorized_patch(canonical_module,state): records=list(analyze_security(security_id=security_id,ticker=ticker,frame=local,asof_date=asof_date))
 return {"source":"BT5C_AUTHORIZED_RAW_REUSE","records":records,"reuse_guard":"PASS"}
