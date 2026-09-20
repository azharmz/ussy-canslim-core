#!/usr/bin/env python3
from __future__ import annotations
import json,subprocess,sys
from datetime import date,timedelta
from pathlib import Path
ENGINE_REPO="https://github.com/azharmz/ussy-oneil-patterns.git";ENGINE_SHA="c433cc1e35a5aa32a46f732cd8c5545935e36e40"
CASES={"TRV":(269.56,date(2024,11,27)),"TSM":(212.60,date(2024,11,23)),"KNTK":(62.55,date(2025,1,2)),"EQT":(48.02,date(2025,1,2)),"MELI":(2635.88,date(2025,6,21)),"TOST":(45.56,date(2025,6,21)),"ULS":(72.81,date(2025,6,21)),"BK":(110.87,date(2025,11,10))}
def metrics(f,r):
 import pandas as pd
 s=pd.Timestamp(r["structural_start"]).date();e=pd.Timestamp(r["structural_end"]).date();z=f[(f.date.dt.date>=s)&(f.date.dt.date<=e)].copy()
 hi=float(z.high.max());lo=float(z.low.min());mc=float(z.close.mean());nr=(hi-lo)/hi;cd=float(z.close.std(ddof=0))/mc
 z["week"]=z.date.dt.to_period("W-FRI");w=z.groupby("week").agg(high=("high","max"),low=("low","min"),close=("close","last"));chg=w.close.pct_change().dropna();sgn=[1 if x>0 else -1 if x<0 else 0 for x in chg];sc=sum(a and b and a!=b for a,b in zip(sgn[:-1],sgn[1:]));wr=(w.high-w.low)/w.high;pr=wr.iloc[:-2]
 return {"duration_sessions":len(z),"trading_weeks":len(w),"depth_pct":r["depth_pct"],"normalized_range":nr,"close_dispersion":cd,"tight":nr<=.03 and cd<=.01,"wide_loose":nr>=.07 or cd>=.03,"weekly_close_span_pct":float((w.close.max()-w.close.min())/w.close.max()),"weekly_median_range_pct":float(wr.median()),"weekly_close_change_abs_median":float(chg.abs().median()) if len(chg) else None,"weekly_direction_changes":int(sc),"late_base_contraction_ratio":None if len(pr)==0 else float(wr.iloc[-2:].median()/pr.median())}
def main():
 import pandas as pd
 eng=Path(".tmp/ussy-oneil-patterns")
 if not eng.exists():eng.parent.mkdir(exist_ok=True);subprocess.run(["git","clone","--quiet",ENGINE_REPO,str(eng)],check=True)
 subprocess.run(["git","-C",str(eng),"checkout","--quiet",ENGINE_SHA],check=True);subprocess.run([sys.executable,"-m","pip","install","-q","-e",f"{eng}[validation]"],check=True);sys.path.insert(0,str(eng/"src"))
 from oneil_patterns.validation.external_ohlcv import fetch_yfinance
 from oneil_patterns.production.engine import analyze_security
 out=[]
 for sym,(pivot,asof) in CASES.items():
  print(f"R1-E case start: {sym}",flush=True);f=fetch_yfinance(sym,asof-timedelta(days=650),asof+timedelta(days=2));f["date"]=pd.to_datetime(f["date"]);d=f[f.date.dt.date<=asof].copy();obs=[x.to_dict() if hasattr(x,"to_dict") else x.__dict__ for x in analyze_security(sym,sym,d,asof)];fb=[x for x in obs if x.get("pattern")=="FLAT_BASE"]
  if not fb:out.append({"symbol":sym,"oracle_pivot":pivot,"result":"NO_FLAT_BASE_CANDIDATE"});continue
  fb.sort(key=lambda x:abs(float(x["pivot_level"])-pivot));p=float(fb[0]["pivot_level"]);lin=[x for x in fb if abs(float(x["pivot_level"])-p)<1e-6];out.append({"symbol":sym,"oracle_pivot":pivot,"nearest_delta_pct":p/pivot-1,"lineage":[{"semantics":x["candidate_semantics"],"state":x["normalized_status"],"start":x["structural_start"],"end":x["structural_end"],"pivot":x["pivot_level"],"faults":x["detector_faults"],**metrics(d,x)} for x in lin]})
 Path("artifacts/research").mkdir(parents=True,exist_ok=True);Path("artifacts/research/flat-base-r1e.json").write_text(json.dumps(out,indent=2)+"\n");print("R1E_RESULT="+json.dumps(out,separators=(",",":")))
if __name__=="__main__":main()
