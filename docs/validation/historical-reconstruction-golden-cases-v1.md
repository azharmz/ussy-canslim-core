# Historical Golden-Case Reconstruction v1

Status: ACTIVE / VALIDATION ONLY / NEVER PRODUCTION

This workstream is isolated from CAN SLIM v2 production. It must not modify production READY pointers, candidate publication, frozen O'Neil Pattern Engine semantics, or live execution/lifecycle state.

## Purpose

Replay documented historical O'Neil/CAN SLIM examples using historical data available at the relevant date, then compare the frozen engine's observed result with a source-backed reference oracle.

This is not a backtest and must not be used to estimate CAGR, win rate, expectancy, or profitability.

## Non-negotiable boundaries

- Reconstruction means historical/as-of data, not current 2026 READY data.
- C/A may be accepted as REFERENCE_PASS when an authoritative example explicitly documents the relevant fundamental evidence. The reconstruction does not re-test the SEC fundamentals pipeline.
- Expected pattern/pivot/breakout facts are oracle fields only. They must never be injected as detector inputs.
- Canonical frozen O'Neil Pattern Engine: azharmz/ussy-oneil-patterns at c433cc1e35a5aa32a46f732cd8c5545935e36e40, schema oneil-pattern-output-v2, engine 33-core-p8-frozen-v1.
- A mismatch is evidence to classify and audit, not permission to tune morphology.
- Reconstruction artifacts must be labelled HISTORICAL_RECONSTRUCTION_FIXTURE and NEVER_PRODUCTION.

## Two entry layers

### Original O'Neil / source-faithful layer

Evaluate the historical breakout/buy opportunity on breakout day T using the documented pivot/buy point, proper base, price action, volume confirmation, and buy zone. Do not impose USSY T+1 Open on this oracle.

### USSY production-adaptation layer

After the completed T daily bar is known, evaluate the existing USSY causal execution contract at T+1 Open. A source-faithful valid breakout can therefore coexist with MISSED_EXTENDED under USSY. That is an execution-adaptation gap, not a pattern failure.

Daily OHLCV does not reveal exact intraday ordering or cumulative volume at the moment of crossing. When intraday data are absent, label that limitation explicitly.

## Methodology classification

Every reconstructed field/rule must be tagged as one of: ORIGINAL, OPERATIONALIZATION, DATA_ADAPTATION, PROXY, ENGINEERING, UNAVAILABLE.

Examples: proper pivot and buy zone are source-methodology concepts; T+1 Open is an operationalization; USSY cross-sectional RS is a proxy/data adaptation rather than the proprietary IBD RS Rating; R2 lineage/checkpoints are engineering.

## Required data by component

| Component | Reconstruction input |
|---|---|
| C | authoritative reference fact where documented |
| A | authoritative reference fact where documented |
| N | reference fact if documented; otherwise NOT_DOCUMENTED |
| S | historical OHLCV/volume; broader supply evidence only if available |
| L | historical comparison universe for the same decision date; official historical RS may be stored separately as oracle |
| I | reference fact if documented; otherwise NOT_DOCUMENTED |
| M | historical market context using information through T only |
| Pattern/base | candidate historical OHLCV only |
| Pivot | engine-derived; source value is oracle |
| Breakout | historical price/volume |
| Original entry | breakout-day/source-faithful assessment |
| USSY execution | historical T+1 Open |
| Lifecycle | future historical bars revealed causally |

NOT_DOCUMENTED and NOT_EVALUABLE are not equivalent to FAIL.

## Golden Case 001 — LRCX 2020

Initial official-source candidate: Lam Research (LRCX), 2020 cup-with-handle.

Reference facts to freeze only after direct source verification:
- expected family: CUP_WITH_HANDLE
- reported pivot/buy point: 381.96
- reported breakout date: 2020-11-04
- reported base duration: about 13 weeks
- reported base depth: about 24%
- reported handle duration: about two weeks
- reported quarterly EPS growth: +78%
- reported sales growth: +47%
- reported prior advance: >113%
- reported subsequent advance is context only and MUST NOT be supplied to signal-time reconstruction

The subsequent return is not a validation target.

## Replay stages

1. Freeze authoritative source oracle.
2. Acquire and freeze candidate historical OHLCV with enough warm-up before the base.
3. Freeze comparison-universe identity and historical OHLCV required for L.
4. Reconstruct M using only information available through T.
5. Run the frozen O'Neil Pattern Engine on candidate data truncated as-of T.
6. Compare observed family, landmarks, pivot and ambiguity state against the oracle.
7. Reconstruct breakout-day price/volume and original O'Neil entry opportunity.
8. Assemble CAN SLIM v2 reconstruction evidence while preserving NOT_DOCUMENTED states.
9. Cross the explicit boundary into USSY adaptation and reveal T+1 Open.
10. Evaluate USSY execution without retroactive fills.
11. Reveal later bars causally and replay lifecycle.
12. Publish expected-vs-observed discrepancies with lineage.

## Reconstruction output contract

Each case must preserve at least: case_id; symbol; decision/breakout date; authoritative source; source retrieval date; oracle facts; OHLCV provider/price basis/corporate-action policy/range/checksum; comparison-universe identity/checksum; M input identity; frozen Pattern Engine SHA/version; expected/observed pattern and pivot; breakout price/volume; original_oneil_entry; USSY T+1 execution; execution adaptation gap; lifecycle result; discrepancy classification; producer commit/run identity.

## Coverage matrix

| Area | LRCX 2020 initial coverage | Remaining need |
|---|---|---|
| C/A reference facts | candidate | verify/freeze source wording |
| Cup with handle | candidate | execute replay |
| Pivot | candidate: 381.96 | execute replay |
| Breakout | candidate: 2020-11-04 | execute replay |
| S / breakout volume | partial | freeze historical OHLCV |
| L | not yet reconstructed | historical comparison universe |
| I | not yet frozen | source fact or NOT_DOCUMENTED |
| N | not yet frozen | source fact or NOT_DOCUMENTED |
| M | not yet reconstructed | historical market replay |
| Original entry | not yet reconstructed | breakout-day assessment |
| T+1 adaptation | not yet reconstructed | next-session open |
| Lifecycle | not yet reconstructed | causal future-bar replay |
| DOUBLE_BOTTOM | uncovered | find authoritative golden case |
| FLAT_BASE | uncovered | find authoritative golden case |
| CUP_WITHOUT_HANDLE | uncovered | find authoritative golden case |

## Recovery boundary

Before expensive cross-sectional reconstruction, freeze:

source oracle -> candidate OHLCV -> comparison-universe manifest -> L/M raw reconstruction -> observed engine output -> report

Each expensive stage must be reusable only when lineage matches. Semantic changes to data source, price basis, universe, decision date, methodology contract, or frozen engine identity invalidate the relevant downstream checkpoint.

## Progress accounting

CAN SLIM v2 engineering implementation remains 100% complete.

Historical Golden-Case Reconstruction is a separate validation track. Creating this contract and source-backed first case establishes the workstream but does not count as an executed reconstruction.
