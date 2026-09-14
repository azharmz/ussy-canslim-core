# #47 Market Input Data Contract — Specification v1

Date: 2026-09-14
Status: PREREGISTERED BEFORE IMPLEMENTATION
Contract: `47-market-input-data-contract-v1`

## Purpose

Define the production input boundary that may feed frozen #46 `46-market-state-classification-v1` without changing #46 semantics.

#47 is a data/provenance contract. It does not classify the market, alter #45 exposure, place trades, or optimize anything from historical returns.

## Authoritative index set

IBD/CAN SLIM market-direction guidance explicitly evaluates the major U.S. indexes including:

- Nasdaq Composite
- S&P 500
- Dow Jones Industrial Average

The canonical #47 v1 index identities are therefore:

```text
NASDAQ_COMPOSITE
SP500
DJIA
```

At least one canonical major-index series must be evaluable for #46; missing series remain explicit. #47 does not require all three to fabricate a state.

## No ETF substitution

`QQQ` is not the Nasdaq Composite index and `SPY` is not the S&P 500 index. Existing `ussy-data` SPY/QQQ benchmark datasets may remain useful for other research, but they MUST NOT be silently relabeled as canonical #46 major-index series.

This matters especially because #46 follow-through/distribution semantics use index price **and volume**. ETF trading volume is a different observable from index/market volume.

## Required daily fields

Each canonical series must provide, for each completed U.S. trading session:

```text
index_id
date
open
high
low
close
volume
source_provider
source_symbol
fetched_at
source_contract_version
```

#46 currently requires `low`, `close`, and `volume`; OHLC is retained so the upstream dataset remains auditable and extensible without reconstructing history.

## Price and volume semantics

- Use the provider's raw/unadjusted index close for day-to-day market-state calculations.
- Do not use adjusted ETF prices as a substitute for an index close.
- `volume` must be the provider's daily volume observable associated with the declared canonical index series and must be non-negative when present.
- A missing/unusable volume value remains missing. It MUST NOT be synthesized from SPY, QQQ, another index, or constituent stocks.
- A source whose historical volume semantics are absent, zero-filled, discontinuous, or otherwise not auditable cannot be promoted to canonical production use until a source audit passes.

## Provider boundary

The exact provider is an infrastructure decision, not an O'Neil theory term. #47 therefore separates identity from provider.

Initial production-source candidate may be Yahoo/yfinance because `ussy-data` already has guarded Yahoo ingestion infrastructure, but this specification does **not** declare Yahoo canonical merely because it is convenient. Each of the three index symbols must first pass a source audit for:

1. identity correctness;
2. completed-session date continuity;
3. OHLC validity;
4. usable daily volume semantics;
5. historical overlap/revision behavior;
6. latest-session freshness;
7. reproducible source symbol/provider metadata.

If a candidate provider fails volume audit for an index, #47 requires `NOT_EVALUABLE` for that series until another reviewed source is adopted. No proxy substitution is allowed.

## PIT / causality

A daily index bar for session D becomes available to #46 only after D is completed and the upstream data pipeline has observed/published it.

The record must preserve `fetched_at` and source provenance. Historical backtests may use the bar only for `asof_date >= D` and must not backdate later source revisions.

## Leadership and weakening provenance

#47 covers major-index OHLCV only. The explicit PIT booleans consumed by #46:

- `leadership_confirming`
- `weakening_confirmed`

remain separate evidence contracts and MUST carry their own `asof_date`, methodology/version, and provenance. They may not be inferred ad hoc inside the index adapter.

## Consumer validation

Before data reaches #46, the adapter must reject or mark not evaluable when:

- `index_id` is outside the canonical set;
- an ETF identity (`SPY`, `QQQ`, etc.) is supplied as a canonical index;
- dates are duplicated or non-monotonic;
- OHLC is invalid;
- required provenance is missing;
- volume is negative;
- the record claims availability before its completed session.

Missing volume is allowed structurally but #46 volume-dependent evidence must then remain `NOT_EVALUABLE` rather than be imputed.

## Explicit non-claims

- No provider is promoted without a source audit.
- No ETF is treated as an index proxy for #46.
- No breadth/distribution-count threshold is added.
- No #46 state-transition threshold is changed.
- No #45 exposure transition is changed.
- No historical-return tuning is permitted.
- No FWD1/X3/EXH2 semantics are changed.
