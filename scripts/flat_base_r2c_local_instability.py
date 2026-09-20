#!/usr/bin/env python3
import json, pandas as pd, yfinance as yf
CASES={
 "ANET":{"start":"2024-02-12","end":"2024-03-15","role":"POSITIVE"},
 "HUBS":{"start":"2024-02-09","end":"2024-03-15","role":"POSITIVE"},
 "FICO":{"start":"2019-08-05","end":"2019-09-09","role":"WIDE_LOOSE_CONTROL"},
}
def calc(sym,c):
 raw=yf.download(sym,start=c["start"],end=(pd.Timestamp(c["end"])+pd.Timedelta(days=1)).strftime("%Y-%m-%d"),auto_adjust=False,actions=False,repair=False,progress=False,threads=False)
 if isinstance(raw.columns,pd.MultiIndex): raw.columns=raw.columns.get_level_values(0)
 f=pd.DataFrame({"date":pd.to_datetime(raw.index),"open":raw.Open.to_numpy(),"high":raw.High.to_numpy(),"low":raw.Low.to_numpy(),"close":raw.Close.to_numpy(),"adj_close":raw["Adj Close"].to_numpy()})
 factor=f.adj_close/f.close
 for col in ["open","high","low","close"]: f[col]=f[col]*factor
 ret=f.close.pct_change().dropna().abs()
 prev=f.close.shift(1); tr=pd.concat([(f.high-f.low),(f.high-prev).abs(),(f.low-prev).abs()],axis=1).max(axis=1)
 trpct=(tr/prev).dropna()
 mid=max(1,len(trpct)//2); early=trpct.iloc[:mid]; late=trpct.iloc[mid:]
 return {"symbol":sym,**c,"sessions":len(f),"daily_abs_return_median":float(ret.median()),"daily_abs_return_p90":float(ret.quantile(.9)),
 "large_move_fraction_1pct":float((ret>=.01).mean()),"large_move_fraction_2pct":float((ret>=.02).mean()),
 "max_abs_daily_return":float(ret.max()),"daily_true_range_pct_median":float(trpct.median()),
 "daily_true_range_pct_p90":float(trpct.quantile(.9)),
 "late_vs_early_daily_range_ratio":float(late.median()/early.median()) if len(early) and early.median()>0 else None}
out=[calc(s,c) for s,c in CASES.items()]
print("R2C_RESULT="+json.dumps(out,separators=(",",":")))
