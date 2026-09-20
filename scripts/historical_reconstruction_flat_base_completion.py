#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
ENGINE_REPO="https://github.com/azharmz/ussy-oneil-patterns.git"
ENGINE_SHA="c433cc1e35a5aa32a46f732cd8c5545935e36e40"
# Source registry: IBD/MarketSurge primary evidence frozen in validation notes; corporate-action factors are explicit fixture adaptations.
CASES={
 "meta_2024":("META",602.95,date(2024,12,3),date(2024,12,10),1.0,"IBD 2024-12-03 flat-base breakout 602.95"),
 "tw_2024":("TW",136.13,date(2024,11,20),date(2024,12,10),1.0,"IBD 2024-12-27 retrospective stage-two flat base 136.13, breakout Nov 20"),
 "now_2024":("NOW",850.33,date(2024,8,30),date(2024,9,10),5.0,"IBD 2024-09-03 flat-base breakout Aug 30 at 850.33; later 5-for-1 split restored"),
 "deck_2023":("DECK",568.47,date(2023,10,23),date(2023,11,10),6.0,"IBD 2024-03-22 retrospective flat base 568.47, breakout week ending Oct 27; later 6-for-1 split restored"),
 "crox_2021":("CROX",109.91,date(2021,6,14),date(2021,6,30),1.0,"MarketSmith Stock Guide Q4 2021 flat base 109.91, breakout June 15"),
 "cprt_2020":("CPRT",92.51,date(2019,12,26),date(2020,1,10),4.0,"IBD Top Stocks 2019 five-week flat base 92.51, breakout Thursday Jan 2; later 2-for-1 split restored"),
 "amzn_2020":("AMZN",3344.39,date(2020,8,3),date(2020,9,15),20.0,"IBD Top Stocks 2020 five-week flat base 3344.39; later 20-for-1 split restored"),
 "kkr_2024":("KKR",103.48,date(2024,5,10),date(2024,7,15),1.0,"IBD 2024-05-10 stage-three flat base 103.48 buy point"),
}
def normalize(frame,factor):
 frame=frame.copy()
 if factor!=1:
  for c in ("open","high","low","close","adj_close"):
   if c in frame.columns: frame[c]=frame[c].astype(float)*factor
  frame["volume"]=frame["volume"].astype(float)/factor
 return frame
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("case",choices=CASES); a=ap.parse_args()
 symbol,pivot,search_start,search_end,factor,source_note=CASES[a.case]
 eng=Path(".tmp/ussy-oneil-patterns")
 if not eng.exists():
  eng.parent.mkdir(exist_ok=True); subprocess.run(["git","clone","--quiet",ENGINE_REPO,str(eng)],check=True)
 subprocess.run(["git","-C",str(eng),"checkout","--quiet",ENGINE_SHA],check=True)
 subprocess.run([sys.executable,"-m","pip","install","-q","-e",f"{eng}[validation]"],check=True)
 sys.path.insert(0,str(eng/"src"))
 from oneil_patterns.validation.external_ohlcv import fetch_yfinance
 from oneil_patterns.production.engine import analyze_security
 start=search_start-timedelta(days=550); end=search_end+timedelta(days=10)
 frame=fetch_yfinance(symbol,start,end); frame["date"]=pd.to_datetime(frame["date"]); frame=normalize(frame,factor)
 window=frame[(frame.date.dt.date>=search_start)&(frame.date.dt.date<=search_end)&(frame["close"]>=pivot)]
 if window.empty: raise RuntimeError(f"No daily close crossing for {symbol} {pivot} in frozen source-bounded window")
 asof=window.iloc[0].date.date(); after=frame[frame.date.dt.date>asof]
 if after.empty: raise RuntimeError("No T+1 bar")
 t1date=after.iloc[0].date.date(); detector=frame[frame.date.dt.date<=asof].copy()
 observed=analyze_security(symbol,symbol,detector,asof)
 bar=frame[frame.date.dt.date==asof].iloc[0]; t1=frame[frame.date.dt.date==t1date].iloc[0]
 avg50=float(detector.iloc[:-1].tail(50)["volume"].mean())
 obs=[r.to_dict() if hasattr(r,"to_dict") else r.__dict__ for r in observed]
 root=Path(f"artifacts/historical-reconstruction/{a.case.replace('_','-')}"); root.mkdir(parents=True,exist_ok=True)
 csv=root/"ohlcv-oracle-basis.csv"; frame.to_csv(csv,index=False)
 payload={"fixture_class":"HISTORICAL_RECONSTRUCTION_FIXTURE","production_use":"NEVER_PRODUCTION","symbol":symbol,"asof_date":asof.isoformat(),
 "engine":{"repo":"azharmz/ussy-oneil-patterns","sha":ENGINE_SHA},
 "oracle":{"pattern":"FLAT_BASE","pivot":pivot,"source_note":source_note,"breakout_date_method":"first daily close >= oracle pivot inside frozen source-bounded chronology window","search_start":search_start.isoformat(),"search_end":search_end.isoformat()},
 "source":{"provider":"Yahoo via yfinance","auto_adjust":False,"start":start.isoformat(),"end":end.isoformat(),"rows":len(frame),"sha256":hashlib.sha256(csv.read_bytes()).hexdigest()},
 "price_basis":{"factor":factor,"price_transform":"identity" if factor==1 else f"multiply_{factor:g}","volume_transform":"identity" if factor==1 else f"divide_{factor:g}"},
 "breakout_day":{"date":asof.isoformat(),"open":float(bar.open),"high":float(bar.high),"low":float(bar.low),"close":float(bar.close),"volume":float(bar.volume),"high_above_pivot":bool(bar.high>=pivot),"close_above_pivot":bool(bar.close>=pivot),"close_vs_pivot_pct":float(bar.close)/pivot-1,"prior_50_avg_volume":avg50,"volume_ratio":float(bar.volume)/avg50},
 "ussy_t1_observation":{"classification":"OPERATIONALIZATION","date":t1date.isoformat(),"open":float(t1.open),"open_vs_pivot_pct":float(t1.open)/pivot-1,"in_original_5pct_buy_zone":bool(pivot<=float(t1.open)<=pivot*1.05)},"observed":obs}
 (root/"replay.json").write_text(json.dumps(payload,indent=2,default=str)+"\n"); print(json.dumps(payload,indent=2,default=str))
if __name__=="__main__": main()
