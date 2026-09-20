#!/usr/bin/env python3
from __future__ import annotations
import json,subprocess,sys
from datetime import date,timedelta
from pathlib import Path
import pandas as pd
ENGINE_REPO="https://github.com/azharmz/ussy-oneil-patterns.git"; ENGINE_SHA="c433cc1e35a5aa32a46f732cd8c5545935e36e40"
CASES={"VEEV":(291.69,date(2025,7,18)),"NVDA":(184.48,date(2025,9,26)),"EME":(667.64,date(2025,10,2)),"IBKR":(73.35,date(2025,11,11))}
def main():
 eng=Path(".tmp/ussy-oneil-patterns")
 if not eng.exists(): eng.parent.mkdir(exist_ok=True); subprocess.run(["git","clone","--quiet",ENGINE_REPO,str(eng)],check=True)
 subprocess.run(["git","-C",str(eng),"checkout","--quiet",ENGINE_SHA],check=True); subprocess.run([sys.executable,"-m","pip","install","-q","-e",f"{eng}[validation]"],check=True); sys.path.insert(0,str(eng/"src"))
 from oneil_patterns.validation.development_sources import route_development_ohlcv
 from oneil_patterns.production.engine import analyze_security
 out=[]
 for sym,(oracle,asof) in CASES.items():
  print("R2-E validation start:",sym,flush=True)
  try:
   routed=route_development_ohlcv(sym,asof-timedelta(days=500),asof+timedelta(days=2)); f=routed.frame.copy()
   source=routed.source.value if hasattr(routed.source,"value") else str(routed.source)
   f["date"]=pd.to_datetime(f["date"])
   if "adj_close" not in f: raise ValueError("adj_close required")
   factor=f.adj_close/f.close
   if factor.isna().any() or (factor<=0).any(): raise ValueError("invalid adjustment factor")
   for col in ["open","high","low","close"]: f[col]=f[col]*factor
   f["adj_close"]=f["close"]
   d=f[f.date.dt.date<=asof].copy()
   obs=[x.to_dict() if hasattr(x,"to_dict") else x.__dict__ for x in analyze_security(sym,sym,d,asof)]
   fb=[x for x in obs if x.get("pattern")=="FLAT_BASE"]
   if not fb: out.append({"symbol":sym,"oracle":oracle,"source":source,"result":"NO_FLAT_BASE_CANDIDATE"}); continue
   fb.sort(key=lambda x:abs(float(x["pivot_level"])-oracle)); p=float(fb[0]["pivot_level"]); lin=[x for x in fb if abs(float(x["pivot_level"])-p)<1e-6]
   rows=[]
   for x in lin:
    s=pd.Timestamp(x["structural_start"]).date(); e=pd.Timestamp(x["structural_end"]).date(); z=d[(d.date.dt.date>=s)&(d.date.dt.date<=e)].copy(); weeks=z.date.dt.to_period("W-FRI").nunique()
    eligible=weeks>=5 and float(x["depth_pct"])<=.15
    rows.append({"semantics":x["candidate_semantics"],"frozen_state":x["normalized_status"],"start":str(s),"end":str(e),"pivot":p,"sessions":len(z),"trading_weeks":int(weeks),"depth_pct":float(x["depth_pct"]),"r2d_candidate_state":"RECOGNIZED" if eligible else "REJECTED","faults":x["detector_faults"]})
   out.append({"symbol":sym,"oracle":oracle,"source":source,"nearest_delta_pct":p/oracle-1,"lineage":rows})
  except Exception as exc: out.append({"symbol":sym,"oracle":oracle,"result":"DATA_UNAVAILABLE","error":str(exc)})
 print("R2E_RESULT="+json.dumps(out,separators=(",",":")))
if __name__=="__main__": main()
