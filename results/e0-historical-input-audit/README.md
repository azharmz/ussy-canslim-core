# E0 Historical Input Audit — 2026-09-10

Workflow run: `34433104954` — **SUCCESS**

## Findings

- Full OHLCV objects under `backtest/ohlcv/{security_id}.parquet`: **1,300**
- Historical Musaffa membership snapshots under `universe/membership/`: **1**
- Sole membership snapshot: **2026-08-28**
- Records in that snapshot: **1,327**
- SPY benchmark objects: **5**
- QQQ benchmark objects: **0**

## Methodological consequence

There is no defensible expanded-universe PIT membership history before 2026-08-28 in the current `ussy-data` contract. Long historical OHLCV does not solve that eligibility-history problem.

Therefore:

- `E0-PIT-FORWARD` can be valid only from 2026-08-28 onward and will grow as new membership snapshots accumulate.
- `E0-HIST-STATIC` may use the 2026-08-28 membership frozen backward for exploratory mechanism work, but must be labeled survivorship/eligibility biased and must not be presented as unbiased historical CAN SLIM performance.
- Current membership must never be silently backfilled historically and called PIT.
- M-v1 remains incomplete relative to the frozen SPY-or-QQQ specification until a QQQ benchmark contract exists; static/rolling exploratory studies may use SPY-only only when explicitly labeled.
