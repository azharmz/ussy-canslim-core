#!/usr/bin/env python3
from __future__ import annotations
from datetime import date
import hashlib, json, subprocess, sys
from pathlib import Path


ENGINE_REPO = "https://github.com/azharmz/ussy-oneil-patterns.git"
ENGINE_SHA = "c433cc1e35a5aa32a46f732cd8c5545935e36e40"
SYMBOL = "LRCX"
ASOF = date(2020,11,4)
START = date(2019,1,1)
ORACLE = {"pattern":"CUP_WITH_HANDLE","pivot":381.96,"breakout_date":"2020-11-04"}
# Lam Research effected a 10-for-1 forward split in 2024. Yahoo historical OHLC
# is split-adjusted even when yfinance auto_adjust=False; restore the 2020
# contemporaneous price/share basis before morphology comparison.
SPLIT_FACTOR = 10.0
ROOT=Path("artifacts/historical-reconstruction/lrcx-2020")
ROOT.mkdir(parents=True,exist_ok=True)

def main():
    eng=Path(".tmp/ussy-oneil-patterns")
    if not eng.exists():
        eng.parent.mkdir(exist_ok=True)
        subprocess.run(["git","clone","--quiet",ENGINE_REPO,str(eng)],check=True)
    subprocess.run(["git","-C",str(eng),"checkout","--quiet",ENGINE_SHA],check=True)
    subprocess.run([sys.executable,"-m","pip","install","-q","-e",f"{eng}[validation]"],check=True)

    sys.path.insert(0,str(eng/"src"))
    from oneil_patterns.validation.external_ohlcv import fetch_yfinance
    from oneil_patterns.production.engine import analyze_security

    frame=fetch_yfinance(SYMBOL,START,ASOF)
    raw_csv=ROOT/"ohlcv-yahoo-split-adjusted.csv"
    frame.to_csv(raw_csv,index=False)
    raw_sha=hashlib.sha256(raw_csv.read_bytes()).hexdigest()

    # DATA_ADAPTATION: restore the contemporaneous pre-2024 split price/share
    # basis. Scale OHLC + adj_close by 10 and volume by 1/10. This is a constant
    # transformation across the full as-of slice, so morphology percentages are
    # unchanged while absolute pivot becomes comparable with the 2020 IBD oracle.
    contemporaneous=frame.copy()
    for col in ["open","high","low","close","adj_close"]:
        contemporaneous[col] = contemporaneous[col] * SPLIT_FACTOR
    contemporaneous["volume"] = contemporaneous["volume"] / SPLIT_FACTOR

    csv=ROOT/"ohlcv-2020-contemporaneous-basis.csv"
    contemporaneous.to_csv(csv,index=False)
    sha=hashlib.sha256(csv.read_bytes()).hexdigest()
    observed=analyze_security("LRCX",SYMBOL,contemporaneous,ASOF)
    payload={
      "fixture_class":"HISTORICAL_RECONSTRUCTION_FIXTURE",
      "production_use":"NEVER_PRODUCTION",
      "symbol":SYMBOL,"asof_date":ASOF.isoformat(),
      "source":{"provider":"Yahoo via yfinance","auto_adjust":False,"start":START.isoformat(),"end":ASOF.isoformat(),"rows":len(frame),"yahoo_split_adjusted_sha256":raw_sha},
      "price_basis":{"classification":"DATA_ADAPTATION","corporate_action":"2024-10-02 10-for-1 forward split; post-split trading 2024-10-03","factor":SPLIT_FACTOR,"price_transform":"OHLC and adj_close * 10","volume_transform":"volume / 10","contemporaneous_sha256":sha},
      "engine":{"repo":"azharmz/ussy-oneil-patterns","sha":ENGINE_SHA},
      "oracle":ORACLE,
      "observed":[r.to_dict() if hasattr(r,"to_dict") else r.__dict__ for r in observed],
    }
    (ROOT/"replay.json").write_text(json.dumps(payload,indent=2,default=str)+"\n")
    print(json.dumps(payload,indent=2,default=str))

if __name__=="__main__":
    main()
