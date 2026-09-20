#!/usr/bin/env python3
import json
import yfinance as yf

CASES={
 "ANET":{"oracle":292.66,"asof":"2024-03-15"},
 "MSFT":{"oracle":430.82,"asof":"2024-06-04"},
 "BRK-B":{"oracle":430.00,"asof":"2024-06-04"},
 "ARES":{"oracle":139.48,"asof":"2024-03-15"},
 "HUBS":{"oracle":660.00,"asof":"2024-03-15"},
 "ALL":{"oracle":168.05,"asof":"2024-03-05"},
 "TDG":{"oracle":542.20,"asof":"2019-10-29"},
}
out={}
for sym,cfg in CASES.items():
 print(f"price-basis audit start: {sym}",flush=True)
 t=yf.Ticker(sym)
 hist=t.history(start="2018-01-01",end="2026-01-01",auto_adjust=False,actions=True)
 splits={idx.strftime("%Y-%m-%d"):float(v) for idx,v in hist.get("Stock Splits",[]).items() if float(v)!=0}
 pre={d:v for d,v in splits.items() if d<=cfg["asof"]}
 factor=1.0
 # Yahoo factor convention matches post/pre shares. A historical raw source
 # pivot becomes present-day split basis by dividing by subsequent factors.
 post={d:v for d,v in splits.items() if d>cfg["asof"]}
 for v in post.values(): factor*=v
 out[sym]={"oracle_pivot":cfg["oracle"],"source_asof":cfg["asof"],"split_events_through_asof":pre,
           "split_events_after_asof":post,"subsequent_split_factor":factor,
           "oracle_on_later_split_basis":cfg["oracle"]/factor if factor else None}
print("PRICE_BASIS_AUDIT="+json.dumps(out,separators=(",",":")))
