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

R2-A replay is **fail-closed on canonical price basis**, not on provider identity. The frozen router may use R2, Yahoo, or Tiingo, but a case enters morphology-development statistics only when raw OHLC plus adj_close are available and the replay constructs adjusted OHLC with the same contract used by ussy-data PREBACKTEST-GATE: factor = adj_close / close, applied to open/high/low/close; volume unchanged. Provider and fallback lineage remain explicit. Missing/invalid adj_close fails closed.

This supersedes the pre-replay provider-only wording above; the correction was made before any vNext morphology threshold was selected.

## Development questions

1. Does the frozen engine reconstruct the source pivot/boundary for each positive case?
2. For source-aligned candidates, how do explicit trading-week duration and source-backed <=15% depth behave?
3. How do H2 weekly descriptors behave independently of whole-base depth?
4. Which descriptor combinations distinguish sideways/local tightness without reintroducing a circular whole-base range gate?
5. Can a candidate vNext rule be specified without using R1-E or Golden cases for parameter selection?

R2-A is positive-case development only. Before selecting a final morphology rule, a negative/control development cohort must be frozen so the rule is not optimized only for recall.


## R2-A replay disposition

Authoritative adjusted-basis replay: Actions run `35514101081`, artifact `10606406123`.

Corporate-action price-basis audit: Actions run `35514292277`.

| Case | Oracle pivot | Engine pivot | Disposition |
| --- | ---: | ---: | --- |
| ANET | 292.66 | 73.16500092 | **SOURCE-ALIGNED after 2024-12-04 4-for-1 split normalization**. 292.66 / 4 = 73.165. Morphology evaluable. |
| HUBS | 660.00 | 660.00 | **SOURCE-ALIGNED exact**. Morphology evaluable. |
| MSFT | 430.82 | 422.59487524 | **NEAR / BOUNDARY REVIEW** (-1.91%). Do not use for threshold selection until source-boundary geometry is reconciled. |
| BRK.B | 430.00 | 373.33999634 | **UPSTREAM RECONSTRUCTION MISS** (-13.18%). Morphology not scored. |
| ARES | 139.48 | 102.14952292 | **UPSTREAM RECONSTRUCTION MISS** (-26.76%). Morphology not scored. |
| ALL | 168.05 | 130.62487813 | **UPSTREAM RECONSTRUCTION MISS** (-22.27%). Morphology not scored. |
| TDG | 542.20 | 426.06556352 | **UPSTREAM RECONSTRUCTION MISS** (-21.42%). Morphology not scored. |

ANET source-aligned open-right-edge evidence: 24 sessions / 5 trading weeks, depth 13.52%, frozen `TOO_SHORT + WIDE_LOOSE`, TIGHT=false.

HUBS source-aligned open-right-edge evidence: 25 sessions / 6 trading weeks, depth 12.42%, frozen `WIDE_LOOSE`, TIGHT=false.

### MSFT boundary review

MSFT is deliberately **not promoted to a clean morphology-development positive**. The nearest frozen-engine lineage starts 2024-03-21 and uses pivot 422.59487524; the source oracle is 430.82. The resulting 52-session/12-week open-edge window therefore is not the source-defined Flat Base boundary. The shorter confirmed lineage is 25 sessions/6 trading weeks but retains the same 422.59 pivot. With no corporate-action factor explaining the 1.91% delta, this is a boundary/pivot reconstruction discrepancy, not evidence for choosing a morphology threshold.

Accordingly, the clean positive morphology-development cohort from R2-A is **ANET + HUBS (2 cases)**. MSFT is retained as an upstream/boundary diagnostic case. BRK.B, ARES, ALL, and TDG are upstream misses and are not scored for source-target morphology.

No vNext threshold is selected from this positive-only cohort.
