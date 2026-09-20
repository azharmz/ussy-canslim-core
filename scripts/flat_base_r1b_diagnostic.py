#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from datetime import date, timedelta
from pathlib import Path

ENGINE_REPO="https://github.com/azharmz/ussy-oneil-patterns.git"
ENGINE_SHA="c433cc1e35a5aa32a46f732cd8c5545935e36e40"
CASES={
"AAPL":(221.37,date(2019,9,11),4.0),
"SNPS":(392.79,date(2023,5,18),1.0),
"META":(602.95,date(2024,12,3),1.0),
"TW":(136.13,date(2024,11,26),1.0),
"NOW":(850.33,date(2024,8,30),5.0),
"DECK":(568.47,date(2023,10,27),6.0),
"CROX":(109.91,date(2021,6,14),1.0),
"CPRT":(92.51,date(2020,1,2),4.0),
"AMZN":(3344.39,date(2020,8,25),20.0),
"KKR":(103.48,date(2024,5,15),1.0),
}
def norm(frame,f):
    import pandas as pd
    frame=frame.copy()
    if f!=1:
        for c in ("open","high","low","close","adj_close"):
            if c in frame.columns: frame[c]=frame[c].astype(float)*f
        frame["volume"]=frame["volume"].astype(float)/f
    frame["date"]=pd.to_datetime(frame["date"])
    return frame
def metrics(frame,r):
    import pandas as pd
    s=pd.Timestamp(r["structural_start"]).date(); e=pd.Timestamp(r["structural_end"]).date()
    d=frame["date"].dt.date
    z=frame[(d>=s)&(d<=e)]
    hi=float(z.high.max()); lo=float(z.low.min()); mc=float(z.close.mean())
    nr=(hi-lo)/hi; cd=float(z.close.std(ddof=0))/mc
    return {"duration_sessions":len(z),"depth_pct":r["depth_pct"],
            "normalized_range":nr,"close_dispersion":cd,
            "tight":nr<=.03 and cd<=.01,
            "wide_loose":nr>=.07 or cd>=.03}
def main():
    import pandas as pd
    eng=Path(".tmp/ussy-oneil-patterns")
    if not eng.exists():
        eng.parent.mkdir(exist_ok=True); subprocess.run(["git","clone","--quiet",ENGINE_REPO,str(eng)],check=True)
    subprocess.run(["git","-C",str(eng),"checkout","--quiet",ENGINE_SHA],check=True)
    subprocess.run([sys.executable,"-m","pip","install","-q","-e",f"{eng}[validation]"],check=True)
    sys.path.insert(0,str(eng/"src"))
    from oneil_patterns.validation.external_ohlcv import fetch_yfinance
    from oneil_patterns.production.engine import analyze_security
    out=[]
    for sym,(pivot,asof,factor) in CASES.items():
        print(f"R1-B case start: {sym} asof={asof} factor={factor:g}", flush=True)
        frame=norm(fetch_yfinance(sym,asof-timedelta(days=650),asof+timedelta(days=3)),factor)
        detector=frame[frame.date.dt.date<=asof].copy()
        obs=[x.to_dict() if hasattr(x,"to_dict") else x.__dict__ for x in analyze_security(sym,sym,detector,asof)]
        fb=[x for x in obs if x.get("pattern")=="FLAT_BASE"]
        fb.sort(key=lambda x:(abs(float(x["pivot_level"])-pivot),0 if str(x.get("candidate_semantics","")).startswith("OPEN_RIGHT_EDGE") else 1))
        nearest=fb[0]; target=float(nearest["pivot_level"])
        lineage=[x for x in fb if abs(float(x["pivot_level"])-target)<1e-6]
        rows=[]
        for x in sorted(lineage,key=lambda q:q.get("candidate_semantics","")):
            rows.append({"semantics":x["candidate_semantics"],"state":x["normalized_status"],
                         "start":x["structural_start"],"end":x["structural_end"],
                         "pivot":x["pivot_level"],"faults":x["detector_faults"],**metrics(detector,x)})
        out.append({"symbol":sym,"oracle_pivot":pivot,"nearest_delta_pct":target/pivot-1,"lineage":rows})
    Path("artifacts/research").mkdir(parents=True,exist_ok=True)
    Path("artifacts/research/flat-base-r1b.json").write_text(json.dumps(out,indent=2)+"\n")
    print("R1B_RESULT="+json.dumps(out,separators=(",",":")))
if __name__=="__main__": main()
