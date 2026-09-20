# Flat Base vNext R2-A — development-set registry

Status: **DEVELOPMENT ORACLES FROZEN BEFORE REPLAY**

Freeze date: 2026-09-20

Purpose: develop candidate Flat Base vNext morphology semantics after R1-E closure. This set is intentionally separate from both the original 40-case golden reconstruction and the R1-E independent holdout.

## Anti-leakage rule

The following cases MUST NOT be used here: the 10 Flat Base golden cases (AAPL, SNPS, META, TW, NOW, DECK, CROX, CPRT, AMZN, KKR) and all R1-E cases (TRV, TSM, KNTK, EQT, MELI, TOST, ULS, BK).

R2-A is a **development set**, so candidate metrics/rules may be explored here. Any rule selected from R2-A must then be frozen before a new untouched validation set is assembled.

## Frozen positive development cases

| ID | Symbol | Source as-of | Source evidence | Oracle pivot |
| --- | --- | --- | --- | ---: |
| D01 | MSFT | 2024-06-04 | IBD/MarketSurge explicitly identifies a Flat Base | 430.82 |
| D02 | BRK.B | 2024-06-04 | IBD/MarketSurge explicitly identifies a Flat Base | 430.00 |
| D03 | ANET | 2024-03-15 | IBD says shares were on track to complete a Flat Base | 292.66 |
| D04 | ARES | 2024-03-15 | IBD says shares were due to complete a Flat Base | 139.48 |
| D05 | HUBS | 2024-03-15 | IBD says shares were on track to forge a Flat Base/base-on-base | 660.00 |
| D06 | ALL | 2024-03-05 | IBD identifies a six-week Flat Base | 168.05 |
| D07 | TDG | 2019-10-29 | IBD Stock Of The Day / MarketSmith identifies a second-stage Flat Base | 542.20 |

## Source evidence

- MSFT / BRK.B: https://www.investors.com/research/sp-500-stocks-to-buy-and-watch-in-todays-market/
- ANET / ARES / HUBS: https://www.investors.com/market-trend/stock-market-today/dow-jones-futures-microsoft-google-buy-signals-adobe-dives/
- ALL: https://www.investors.com/news/large-cap-stocks-allstate-target-royal-caribbean-earnings/
- TDG: IBD Top Stocks 2019 booklet, adapted from the 2019-10-29 IBD Stock Of The Day article.

## Data-basis contract

R2-A replay is **fail-closed on canonical input**. It accepts only the frozen engine development router's R2 source. Yahoo/Tiingo fallback output may be logged diagnostically but MUST NOT enter morphology development statistics. This prevents a repeat of the BK raw/unadjusted comparability problem.

## Development questions

1. Does the frozen engine reconstruct the source pivot/boundary for each positive case?
2. For source-aligned candidates, how do explicit trading-week duration and source-backed <=15% depth behave?
3. How do H2 weekly descriptors behave independently of whole-base depth?
4. Which descriptor combinations distinguish sideways/local tightness without reintroducing a circular whole-base range gate?
5. Can a candidate vNext rule be specified without using R1-E or Golden cases for parameter selection?

R2-A is positive-case development only. Before selecting a final morphology rule, a negative/control development cohort must be frozen so the rule is not optimized only for recall.
