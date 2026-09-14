# Decision — #54 Cycle 1 Broad-Market OHLCV Source Audit

Date: 2026-09-14

Status: **PROVIDER STACK AUDITED / BROAD-MARKET OHLCV STILL NOT READY / SELECTOR EXECUTION BLOCKED**

## Context

Frozen `54-cycle1-candidate-leader-selector-v1` requires a PIT broad-market cross-section with 252 adjusted-close observations per evaluable security plus the canonical SP500 benchmark. Existing `ussy-data` production rolling OHLCV is restricted to the confirmed USSY/Musaffa-compliant universe and therefore cannot be used as a substitute for the broad-market #53 membership universe.

The project therefore ran read-only source audits against the live #53 membership snapshot `34823149519` without changing the frozen selector.

## Audit A — Tiingo only

Repository: `azharmz/ussy-data`

Workflow: `54 broad-market Tiingo coverage audit`

Canonical run: `34847652001`

Job: `103987413383`

Artifact: `54-broad-market-tiingo-34847652001`

Artifact ID: `10348671364`

Artifact ZIP SHA-256: `97ba227b22459d2f0b538a0e0f907ceb7a41cc3c271a36108362ec37477bf427`

Live #53 membership manifest SHA-256: `5f65ed271ff3520b3b290a2fd0d3f903dd33779443a43f868dea06eba813372b`

Deterministic sample:

- eligible non-ETF/non-test membership symbols: 7,504
- sample size: 100
- sample rule: ascending SHA-256 of `membership_run_id|symbol`
- required adjusted-close observations: 252
- symbols with successful Tiingo response: 68
- errors: 32
- symbols reported with >=252 adjusted-close observations: 56
- descriptive coverage: 56%

This is insufficient evidence to authorize Tiingo as the sole broad-market adjusted-close source.

## Audit B — Tiingo then Yahoo/yfinance fallback

Repository: `azharmz/ussy-data`

Workflow: `54 broad-market provider stack audit`

Canonical run: `34848036669`

Job: `103988656423`

Deterministic sample and #53 membership lineage were identical to Audit A.

Results:

- sample size: 100
- symbols with >=252 adjusted-close observations: 72
- descriptive coverage: 72%
- selected Tiingo: 0
- selected Yahoo/yfinance fallback: 72
- unresolved: 28
- helper tests: 7 passed

The unresolved sample includes provider/security-identity patterns such as preferred/share-class, warrant, and right-like symbols (examples observed in logs include `$`, `-W`, and `-R` symbol forms). These cannot be silently discarded because Cycle 1 preregistration currently excludes only ETFs and test issues.

## Audit inconsistency preserved

Audit A reported 56 sampled symbols with >=252 Tiingo adjusted-close observations, while Audit B selected Tiingo for 0 sampled symbols despite using the same membership run, deterministic sample rule, nominal lookback, and 252-bar requirement.

This discrepancy is not silently reconciled. It is preserved as source-audit debt requiring direct investigation of request semantics, provider response behavior, and/or audit implementation before Tiingo can be approved in any production broad-market panel.

## Decision

1. **Do not create or publish a production broad-market OHLCV panel yet.**
2. **Do not execute the frozen #54 Cycle 1 selector on the restricted USSY/Musaffa rolling dataset.**
3. **Do not execute the selector on a 72%-covered cross-section and call its RS percentile broad-market.** Doing so would change the cross-sectional reference population through provider availability and can introduce selection bias.
4. Tiingo is **not approved as a sole provider** from this audit.
5. The current Tiingo→Yahoo stack is **not approved as a complete broad-market source stack** because 28/100 sampled symbols remain unresolved and the Tiingo result inconsistency remains open.
6. Existing #53 membership semantics remain unchanged.
7. Frozen Cycle 1 thresholds and selector semantics remain unchanged.

## Required next internal #54 step

Perform a **security-type / provider-symbol identity audit** before any data publisher is authorized. The audit must determine, from explicit source evidence and preregistration:

- which #53 security types are valid constituents of the stock-leadership cross-section;
- how preferreds, rights, warrants, units, ADRs/share classes, and similar instruments are treated;
- canonical provider symbol mapping rules;
- whether provider availability is independent of leader-state selection;
- whether the Tiingo-only vs provider-stack discrepancy is reproducible and explainable.

Any new security-type exclusion must be preregistered before selector validation. It must not be chosen because it improves market-state history or future returns.

## Terminal verdict for this subcycle

**PROVIDER STACK AUDITED / BROAD-MARKET OHLCV STILL NOT READY / SELECTOR EXECUTION BLOCKED**
