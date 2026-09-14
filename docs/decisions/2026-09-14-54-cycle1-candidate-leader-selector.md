# Decision — #54 Experimental Cycle 1 Candidate Leader Selector

Date: 2026-09-14

Status: **SEMANTIC BASELINE FROZEN / PROSPECTIVE PIT VALIDATION PENDING / NOT PRODUCTION AUTHORIZED**

Selector: `54-cycle1-candidate-leader-selector-v1`

## Decision

Freeze the Cycle 1 research selector as the first candidate leader-cohort hypothesis inside #54.

The selector requires:

- valid PIT broad-market membership;
- non-ETF and non-test-issue security;
- 252 completed adjusted-close observations for stock and canonical `SP500` benchmark;
- project-defined 252-session relative-return percentile >= 80;
- adjusted close >= 90% of trailing 252-session adjusted-close high.

The 80 percentile and 10%-from-high anchors come from authoritative O'Neil/AAII CAN SLIM screening guidance. The exact 252-session return calculation and upper empirical-CDF percentile implementation are explicit project research conventions and are not represented as proprietary IBD RS Rating semantics.

## Validation

Canonical semantic CI:

- workflow: `54 Cycle 1 candidate leader selector`
- run: `34828024938`
- job: `103924556850`
- result: **SUCCESS**
- tests: **11 passed**
- head commit: `36f1423c9760223f9eef52bd3d14710d99f4f3b7`

The first CI attempt (`34827895169`) failed one boundary fixture because the synthetic path's actual maximum was 199.60 rather than the intended 200.00. The fixture was corrected without changing selector semantics.

## Production prohibition

This selector may produce only `LEADER_CANDIDATE`, `NOT_LEADER_CANDIDATE`, or `NOT_EVALUABLE` research states.

It may **not** directly emit:

- `leadership_confirming=True/False`; or
- `weakening_confirmed=True/False`.

A separate explicit PIT institutional-demand/selling evidence channel remains required by #51/#52.

## Next step inside #54

Use prospective #53 membership snapshots and PIT OHLCV to run descriptive/provenance validation of this frozen selector. Evaluate only coverage, missingness, cohort size, deterministic reproducibility, and turnover/stability. Do not tune thresholds from future returns or downstream #46/#45 outcomes.

Terminal status for Cycle 1 baseline:

**SEMANTIC BASELINE FROZEN / PROSPECTIVE PIT VALIDATION PENDING / NOT PRODUCTION AUTHORIZED**
