# Decision — Freeze #47 Market Input Data Contract v1

Date: 2026-09-14
Decision: `IMPLEMENTATION COMPLETE / FROZEN v1; PRODUCTION SOURCE AUDIT PENDING`
Contract: `47-market-input-data-contract-v1`

## Frozen boundary

#47 defines the only canonical major-index identities permitted to feed frozen #46 v1:

- `NASDAQ_COMPOSITE`
- `SP500`
- `DJIA`

This follows authoritative IBD market-direction guidance that evaluates the Nasdaq Composite, S&P 500 and Dow Jones Industrial Average as major indexes.

SPY, QQQ and other ETFs are explicitly not canonical substitutes. Their prices and trading volume are different observables from the underlying indexes, and #46 uses price/volume chronology for follow-through and distribution evidence.

## Data semantics

The frozen adapter preserves raw provider index OHLCV and provenance. Missing volume is preserved as missing; it is never imputed from an ETF, another index or constituents. A provider/index pair cannot be promoted to production until its source audit establishes usable volume semantics and provenance.

Yahoo/yfinance is only an initial infrastructure candidate because guarded Yahoo ingestion already exists in `ussy-data`; convenience does not constitute source validation.

Leadership/weakening PIT evidence remains a separate upstream contract and is not invented by #47.

## Validation

Canonical semantic-validation run:

- run `34806193999`
- job `103858438691`
- head commit `3ab46d1594ef9c23cb6e65cc390b70230eb441f7`
- result: `SUCCESS`
- tests: `13 passed in 0.04s`

Validated boundaries include canonical identity, ETF rejection, no volume imputation, OHLC validity, provenance, date ordering/uniqueness, causal fetch-date guard, and exact preservation into frozen #46 input objects.

## Governance consequence

#47 is frozen. The next task is an independent production source audit for the three canonical indexes. That audit may approve or reject a provider/index pair, but it may not change #46 thresholds, relabel SPY/QQQ as indexes, or tune source selection from strategy returns.

No #33-#46 contract, FWD1, X3 or EXH2 semantics are changed by this decision.
