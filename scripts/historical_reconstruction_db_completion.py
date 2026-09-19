#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from datetime import date, timedelta
from pathlib import Path
import pandas as pd

ENGINE_REPO="https://github.com/azharmz/ussy-oneil-patterns.git"
ENGINE_SHA="c433cc1e35a5aa32a46f732cd8c5545935e36e40"
CASES={
 "lly_2024":("LLY",793.67,date(2024,5,1),date(2024,7,1),"IBD/MarketSurge double-bottom 793.67"),
 "fis_2024":("FIS",77.83,date(2024,8,6),date(2024,10,1),"IBD/MarketSurge stage-one double-bottom 77.83"),
 "cag_2024":("CAG",29.89,date(2024,4,1),date(2024,5,1),"IBD double-bottom elements / 29.89 entry"),
 "strl_2024":("STRL",130.89,date(2024,9,18),date(2024,10,15),"IBD/MarketSurge first-stage double-bottom 130.89"),
 "uri_2024":("URI",715.34,date(2024,7,1),date(2024,8,1),"IBD/MarketSurge double-bottom view 715.34"),
 "ubs_2024":("UBS",31.45,date(2024,8,14),date(2024,10,15),"IBD/MarketSurge double-bottom 31.45"),
 "nxpi_2024":("NXPI",251.96,date(2024,5,1),date(2024,7,15),"IBD double-bottom 251.96"),
}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("case",choices=CASES); a=ap.parse_args()
 symbol,pivot,search_start,search_end,source_note=CASES[a.case]
 eng=Path(".tmp/ussy-oneil-patterns")
 if not eng.exists():
  eng.parent.mkdir(exist_ok=True); subprocess.run(["git","clone","--quiet",ENGINE_REPO,str(eng)],check=True)
 subprocess.run(["git","-C",str(eng),"checkout","--quiet",ENGINE_SHA],check=True)
 subprocess.run([sys.executable,"-m","pip","install","-q","-e",f"{eng}[validation]"],check=True)
 sys.path.insert(0,str(eng/"src"))
 from oneil_patterns.validation.external_ohlcv import fetch_yfinance
 from oneil_patterns.production.engine import analyze_security
 start=search_start-timedelta(days=550); end=search_end+timedelta(days=10)
 frame=fetch_yfinance(symbol,start,end)
 frame["date"]=pd.to_datetime(frame["date"])
 window=frame[(frame.date.dt.date>=search_start)&(frame.date.dt.date<=search_end)&(frame["close"]>=pivot)]
 if window.empty: raise RuntimeError(f"No daily close crossing for {symbol} {pivot} in frozen search window")
 asof=window.iloc[0].date.date()
 after=frame[frame.date.dt.date>asof]
 if after.empty: raise RuntimeError("No T+1 bar")
 t1date=after.iloc[0].date.date()
 detector=frame[frame.date.dt.date<=asof].copy()
 observed=analyze_security(symbol,symbol,detector,asof)
 bar=frame[frame.date.dt.date==asof].iloc[0]; t1=frame[frame.date.dt.date==t1date].iloc[0]
 avg50=float(detector.iloc[:-1].tail(50)["volume"].mean())
 obs=[r.to_dict() if hasattr(r,"to_dict") else r.__dict__ for r in observed]
 root=Path(f"artifacts/historical-reconstruction/{a.case.replace('_','-')}"); root.mkdir(parents=True,exist_ok=True)
 csv=root/"ohlcv-provider-basis.csv"; frame.to_csv(csv,index=False)
 payload={
  "fixture_class":"HISTORICAL_RECONSTRUCTION_FIXTURE","production_use":"NEVER_PRODUCTION",
  "symbol":symbol,"asof_date":asof.isoformat(),
  "engine":{"repo":"azharmz/ussy-oneil-patterns","sha":ENGINE_SHA},
  "oracle":{"pattern":"DOUBLE_BOTTOM","pivot":pivot,"source_note":source_note,
            "breakout_date_method":"first daily close >= oracle pivot inside source-bounded chronology window",
            "search_start":search_start.isoformat(),"search_end":search_end.isoformat()},
  "source":{"provider":"Yahoo via yfinance","auto_adjust":False,"start":start.isoformat(),"end":end.isoformat(),
            "rows":len(frame),"sha256":hashlib.sha256(csv.read_bytes()).hexdigest()},
  "breakout_day":{"date":asof.isoformat(),"open":float(bar.open),"high":float(bar.high),"low":float(bar.low),"close":float(bar.close),
    "volume":float(bar.volume),"high_above_pivot":bool(bar.high>=pivot),"close_above_pivot":bool(bar.close>=pivot),
    "close_vs_pivot_pct":float(bar.close)/pivot-1,"prior_50_avg_volume":avg50,"volume_ratio":float(bar.volume)/avg50},
  "ussy_t1_observation":{"classification":"OPERATIONALIZATION","date":t1date.isoformat(),"open":float(t1.open),
    "open_vs_pivot_pct":float(t1.open)/pivot-1,"in_original_5pct_buy_zone":bool(pivot<=float(t1.open)<=pivot*1.05)},
  "observed":obs
 }
 (root/"replay.json").write_text(json.dumps(payload,indent=2,default=str)+"\n")
 print(json.dumps(payload,indent=2,default=str))
if __name__=="__main__": main()
