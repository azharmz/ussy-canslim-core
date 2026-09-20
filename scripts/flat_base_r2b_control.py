#!/usr/bin/env python3
import json
import pandas as pd
import yfinance as yf

CASES={
 "FICO":{"start":"2019-08-05","end":"2019-09-09","role":"FIVE_WEEK_FLAT_BASE_WIDE_LOOSE","pivot":371.91},
 "VZIO":{"start":"2021-03-25","end":"2021-04-28","role":"IPO_BASE_WIDE_LOOSE","pivot":25.90},
}
def metrics(z):
 hi=float(z.high.max()); lo=float(z.low.min()); mc=float(z.close.mean())
 z=z.copy(); z["week"]=z.date.dt.to_period("W-FRI")
 w=z.groupby("week").agg(high=("high","max"),low=("low","min"),close=("close","last"))
 chg=w.close.pct_change().dropna(); s=[1 if x>0 else -1 if x<0 else 0 for x in chg]
 wr=(w.high-w.low)/w.high; prior=wr.iloc[:-2]
 return {"sessions":len(z),"trading_weeks":len(w),"normalized_range":(hi-lo)/hi,
 "close_dispersion":float(z.close.std(ddof=0))/mc,
 "weekly_close_span_pct":float((w.close.max()-w.close.min())/w.close.max()),
 "weekly_median_range_pct":float(wr.median()),
 "weekly_close_change_abs_median":float(chg.abs().median()) if len(chg) else None,
 "weekly_direction_changes":sum(a and b and a!=b for a,b in zip(s[:-1],s[1:])),
 "late_base_contraction_ratio":None if len(prior)==0 else float(wr.iloc[-2:].median()/prior.median())}
out=[]
for sym,c in CASES.items():
 print("R2-B control start:",sym,flush=True)
 raw=yf.download(sym,start=c["start"],end=(pd.Timestamp(c["end"])+pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                 auto_adjust=False,actions=False,repair=False,progress=False,threads=False)
 if isinstance(raw.columns,pd.MultiIndex): raw.columns=raw.columns.get_level_values(0)
 f=pd.DataFrame({"date":pd.to_datetime(raw.index),"open":raw.Open.to_numpy(),"high":raw.High.to_numpy(),
 "low":raw.Low.to_numpy(),"close":raw.Close.to_numpy(),"adj_close":raw["Adj Close"].to_numpy(),"volume":raw.Volume.to_numpy()})
 factor=f.adj_close/f.close
 for col in ["open","high","low","close"]: f[col]=f[col]*factor
 out.append({"symbol":sym,**c,"price_basis":"ADJUSTED_OHLC_FROM_ADJ_CLOSE_FACTOR",**metrics(f)})
print("R2B_RESULT="+json.dumps(out,separators=(",",":")))
