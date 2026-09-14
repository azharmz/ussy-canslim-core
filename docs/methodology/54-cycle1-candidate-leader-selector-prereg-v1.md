# 54 Experimental Cycle 1 — Candidate Leader Selector Preregistration v1

Status: **PREREGISTERED / RESEARCH-ONLY / NOT PRODUCTION AUTHORIZED**

Selector version: `54-cycle1-candidate-leader-selector-v1`

## Objective

Test whether a simple, theory-anchored, point-in-time stock-leader candidate selector can be defined reproducibly upstream of frozen `51-market-leadership-weakening-evidence-v1`, without using future returns and without pretending that price leadership alone proves institutional accumulation.

This is an experimental cycle inside #54. It is not a new production workstream and does not modify #51, #52, #53, #46, or #45.

## Authoritative anchors fixed before validation

The candidate selector uses only two numeric stock-leadership anchors that are explicitly supported in O'Neil/AAII CAN SLIM material:

1. **Relative-strength percentile >= 80.** O'Neil/AAII material describes seeking stocks with relative-strength percentage rank 80 or better when identifying leaders.
2. **Price >= 90% of the trailing 52-week high.** AAII's implementation of O'Neil's revised CAN SLIM screen operationalizes the `N`/new-high concept as current price within 10% of the 52-week high.

These values are theory/screen anchors, not values selected from project returns.

## Candidate selector

For security `s` on completed session `T`, `LEADER_CANDIDATE` requires all of:

- security is a valid member of the PIT broad-market membership snapshot applicable to T;
- security has at least 252 completed daily adjusted-close observations through T;
- benchmark has at least 252 completed daily adjusted-close observations through T;
- trailing 252-session stock return and benchmark-relative strength can be evaluated without future bars;
- cross-sectional RS percentile rank among all evaluable members at T is **>= 80.0**;
- current adjusted close / maximum adjusted close over the trailing 252 completed sessions is **>= 0.90**.

Otherwise the state is `NOT_LEADER_CANDIDATE` when fully evaluable, or `NOT_EVALUABLE` when required data/provenance are missing.

### RS definition for Cycle 1

Cycle 1 uses a transparent project calculation rather than claiming equivalence to proprietary IBD RS Rating:

`relative_return_252 = stock_total_price_return_252 - benchmark_total_price_return_252`

where each 252-session price return is:

`last_adj_close / first_adj_close - 1` over the latest 252 completed observations through T.

The cross-sectional percentile rank is frozen as:

`100 * count(relative_return_252 <= value_s) / N_evaluable`

Ties therefore receive the same upper empirical-CDF percentile. This is a preregistered implementation convention, not an O'Neil proprietary formula.

This metric is explicitly named `PROJECT_RS_PERCENTILE_252_V1`, not `IBD_RS_RATING`.

The 252-session calculation window is a preregistered research convention approximating one trading year. It is not claimed to be O'Neil's proprietary RS formula.

## Benchmark

Cycle 1 benchmark is the frozen canonical `SP500` market index identity from #47. Exact provider data must come through a PIT-valid production/research source contract; no ETF substitution is authorized.

## Institutional-demand boundary

`LEADER_CANDIDATE` is **not** sufficient for #51 `leadership_confirming=True`.

A separate PIT demand/accumulation channel is still required. Cycle 1 records, but does not fabricate:

- `institutional_demand_state`
- `institutional_selling_state`

Allowed values are `TRUE`, `FALSE`, or `NOT_EVALUABLE`.

Until a separately auditable source/calculation is frozen for these channels, a candidate cohort may be studied but may not be promoted to the production #51 booleans.

## Security-type boundary

#53 preserves ETF/test/status metadata. Cycle 1 eligible membership excludes records explicitly marked as:

- test issues; or
- ETFs.

Other security-type exclusions are not invented in Cycle 1. If later evidence shows ADR, preferred, warrant, unit, or other instrument handling requires a separate rule, that rule must be preregistered before validation.

## PIT and anti-leakage rules

- membership snapshot used for T must have been fetched/available no later than the decision process for T;
- no security can enter the cohort because of performance after T;
- the 252-session high includes T but no later bar;
- cross-sectional percentile uses only securities evaluable at T;
- missing membership, stock history, benchmark history, or identity is `NOT_EVALUABLE`;
- no backfill of historical membership using a later #53 snapshot;
- no threshold may be changed after seeing future returns, #46 market states, #45 exposure outcomes, CAGR, profit factor, or win rate.

## Validation plan

Cycle 1 validation order:

1. semantic/unit validation of the frozen selector;
2. provenance/PIT validation on prospective #53 snapshots;
3. descriptive cohort diagnostics only: cohort size, coverage, missingness, stability/turnover;
4. untouched prospective validation after enough snapshots accumulate.

Future returns are not an acceptance criterion for theory fidelity.

## Promotion gate

Cycle 1 cannot become production merely because it produces plausible cohorts.

Promotion requires all of:

- selector implementation matches this preregistration;
- PIT membership and OHLCV provenance are reproducible;
- untouched validation shows semantic/reproducibility integrity;
- a separate explicit institutional-demand/selling evidence channel satisfies #51/#52;
- governance decision explicitly approves promotion.

Until then:

**`RESEARCH-ONLY / NOT PRODUCTION AUTHORIZED`**
