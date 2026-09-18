# Historical Golden-Case Reconstruction v1

Status: ACTIVE / VALIDATION ONLY / NEVER PRODUCTION

This workstream is isolated from CAN SLIM v2 production. It must not modify production READY pointers, candidate publication, frozen O'Neil Pattern Engine semantics, or live execution/lifecycle state.

## Purpose

Replay documented historical O'Neil/CAN SLIM examples using historical data available at the relevant date, then compare the frozen engine's observed result with a source-backed reference oracle. This is not a backtest.

## Non-negotiable boundaries

- Reconstruction means historical/as-of data, not current 2026 READY data.
- C/A may be accepted as REFERENCE_PASS when an authoritative example explicitly documents the relevant fundamental evidence.
- Expected pattern/pivot/breakout facts are oracle fields only; never detector inputs.
- Canonical frozen O'Neil Pattern Engine: azharmz/ussy-oneil-patterns at c433cc1e35a5aa32a46f732cd8c5545935e36e40; schema oneil-pattern-output-v2; engine 33-core-p8-frozen-v1.
- Mismatch is validation evidence, not permission to tune morphology.
- Artifacts: HISTORICAL_RECONSTRUCTION_FIXTURE / NEVER_PRODUCTION.

## Two entry layers

Original O'Neil/source-faithful: assess the breakout-day T buy opportunity from proper base, pivot/buy point, price-volume action and buy zone. Do not impose USSY T+1 Open.

USSY adaptation: after completed T daily data is known, evaluate the frozen causal T+1 Open contract. A valid original breakout may coexist with USSY MISSED_EXTENDED; classify that as an execution-adaptation gap.

Daily OHLCV cannot reconstruct exact intraday ordering/cumulative volume at crossing; label this limitation explicitly.

## Methodology classification

Tag every reconstructed field/rule: ORIGINAL, OPERATIONALIZATION, DATA_ADAPTATION, PROXY, ENGINEERING, or UNAVAILABLE. USSY cross-sectional RS is a proxy/data adaptation, not the proprietary IBD RS Rating.

## Golden Case 001 — LRCX 2020 — ORACLE VERIFIED

Authoritative source:
- Investor's Business Daily, "How To Buy Stocks: Lam Research's Cup With Handle Launched A 75% Advance"
- https://www.investors.com/how-to-invest/investors-corner/how-to-buy-stocks-lam-research-cup-with-handle-launched-75-percent-advance/

Source facts verified directly for the reconstruction oracle:
- expected family: CUP_WITH_HANDLE
- reported pivot/buy point: 381.96
- reported breakout date: 2020-11-04
- base duration: 13 weeks
- base depth: 24%
- handle duration: two weeks
- prior advance: more than 113%
- quarterly earnings growth: 78%
- sales/revenue growth: 47%
- the later ~75% advance is context only and MUST NOT be supplied to signal-time reconstruction

Oracle state: FROZEN_SOURCE_ORACLE_V1.
Do not silently add facts not explicitly supported by the source. Subsequent return is not a validation target.

## Required data by component

| Component | Reconstruction input |
|---|---|
| C | authoritative reference fact where documented |
| A | authoritative reference fact where documented; if annual evidence is not explicit, do not infer it |
| N | reference fact if documented; otherwise NOT_DOCUMENTED |
| S | historical OHLCV/volume; broader supply evidence only if available |
| L | historical comparison universe on same date; official historical RS separately if available |
| I | reference fact if documented; otherwise NOT_DOCUMENTED |
| M | historical market context through T only |
| Pattern/base | candidate historical OHLCV only |
| Pivot | engine-derived; 381.96 is oracle only |
| Breakout | historical price/volume |
| Original entry | breakout-day/source-faithful assessment |
| USSY execution | historical T+1 Open |
| Lifecycle | future historical bars revealed causally |

NOT_DOCUMENTED and NOT_EVALUABLE are not FAIL.

## Replay stages

1. Freeze authoritative source oracle. COMPLETE for LRCX v1.
2. Acquire/freeze candidate historical OHLCV with sufficient pre-base warm-up.
3. Run frozen O'Neil Pattern Engine on candidate data truncated as-of T.
4. Compare observed family, landmarks, pivot and ambiguity state against oracle.
5. Reconstruct breakout-day price/volume and original O'Neil entry opportunity.
6. Only after morphology/pivot replay, freeze comparison-universe identity/OHLCV for L and reconstruct M.
7. Assemble CAN SLIM v2 reconstruction evidence preserving NOT_DOCUMENTED.
8. Cross explicit boundary into USSY adaptation and reveal T+1 Open.
9. Evaluate USSY execution without retroactive fills.
10. Reveal later bars causally and replay lifecycle.
11. Publish expected-vs-observed discrepancies with lineage.

## Output contract

Preserve: case_id; symbol; decision/breakout date; authoritative source; source retrieval date; oracle facts/version; OHLCV provider/price basis/corporate-action policy/range/checksum; comparison-universe identity/checksum; M input identity; frozen Pattern Engine SHA/version; expected/observed pattern and pivot; breakout price/volume; original_oneil_entry; USSY T+1 execution; adaptation gap; lifecycle result; discrepancy classification; producer commit/run identity.

## Coverage matrix

| Area | LRCX 2020 | Next |
|---|---|---|
| Source oracle | VERIFIED/FROZEN v1 | preserve provenance |
| C quarterly reference | VERIFIED | reference only |
| A annual reference | NOT YET DOCUMENTED | do not infer |
| Cup with handle | VERIFIED oracle | execute replay |
| Pivot | VERIFIED 381.96 | execute replay |
| Breakout | VERIFIED 2020-11-04 | execute replay |
| S / breakout volume | source context + OHLCV needed | freeze OHLCV |
| L | not reconstructed | after morphology replay |
| I | not frozen | source fact or NOT_DOCUMENTED |
| N | not frozen | source fact or NOT_DOCUMENTED |
| M | not reconstructed | after morphology replay |
| Original entry | not reconstructed | breakout-day assessment |
| T+1 adaptation | not reconstructed | next-session open |
| Lifecycle | not reconstructed | causal future-bar replay |
| DOUBLE_BOTTOM | uncovered | authoritative case needed |
| FLAT_BASE | uncovered | authoritative case needed |
| CUP_WITHOUT_HANDLE | uncovered | authoritative case needed |

## Recovery boundary

Freeze reusable stages with lineage:
source oracle -> candidate OHLCV -> morphology raw result -> comparison-universe manifest -> L/M raw reconstruction -> execution/lifecycle -> report.

Semantic changes to source, price basis, universe, decision date, methodology contract or frozen engine identity invalidate affected downstream checkpoints.

## Progress accounting

CAN SLIM v2 engineering implementation remains 100% complete.

Historical reconstruction progress is separate. LRCX source oracle is now verified/frozen; executable historical OHLCV replay is the next stage.
