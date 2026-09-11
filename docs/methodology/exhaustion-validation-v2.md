# EXH2 — Prospective Exhaustion Validation

Status: **PRE-REGISTERED / PROSPECTIVE**

Frozen on: 2026-09-11

## Purpose

EXH2 validates the exploratory EXH1 finding that a large T-1→T0 breakout expansion followed by T+1 bearish rejection is associated with near-term post-breakout exhaustion. EXH2 is a separate diagnostic sidecar. It does **not** modify X3, X1, PORT1, FWD1, C/A, M, or production rules.

## Discovery evidence carried forward

EXH1 (`34466747136`) grouped shock by quintile and found the highest-shock quintile combined with T+1 `BEARISH_AND_BELOW_T0` rejection had materially worse X1 outcomes than high shock without rejection. The discovery sample is not reused as validation evidence.

The operational extreme-shock cutoff is frozen as the EXH1 80th-percentile boundary:

`shock_tminus1_t0 >= 0.0533333333333332` (5.33333333333332%).

This is a direct transfer of the already-defined top-quintile discovery bucket. No alternative threshold search is permitted in EXH2.

## Prospective boundary

Validation signal dates must satisfy:

`signal_date > 2026-09-11`

Therefore the earliest possible US-market validation signal is the first trading session after 2026-09-11. Historical observations through 2026-09-11 are excluded from EXH2 inference.

## Frozen definitions

For every post-boundary technical candidate from the existing frozen CAN SLIM candidate engine:

- `shock_tminus1_t0 = Close(T0) / Close(T-1) - 1`
- `extreme_shock = shock_tminus1_t0 >= 0.0533333333333332`
- `t1_bearish = Close(T+1) < Open(T+1)`
- `t1_below_t0_close = Close(T+1) < Close(T0)`
- `t1_rejection = t1_bearish AND t1_below_t0_close`
- `retest_pivot_by_t3 = min(Close(T+1), Close(T+2), Close(T+3)) <= Pivot * 1.01`
- `breakdown_below_pivot_by_t3 = min(Close(T+1), Close(T+2), Close(T+3)) < Pivot`
- `t3_close_vs_t0 = Close(T+3) / Close(T0) - 1`

A row becomes **mature** only when T+1, T+2, and T+3 bars all exist. Pending rows are retained operationally but excluded from inference.

## Primary comparison

Within `extreme_shock == true` candidates, compare:

1. `t1_rejection == true`
2. `t1_rejection == false`

Primary endpoint: `breakdown_below_pivot_by_t3` rate.

Secondary endpoints:

- `retest_pivot_by_t3` rate
- median `t3_close_vs_t0`
- sample counts by group

The directional hypothesis is that the rejected group has a higher T+3 pivot-breakdown rate than the non-rejected extreme-shock group.

## Review gate

EXH2 remains `ACCUMULATING` until both groups contain at least 50 mature extreme-shock observations:

- rejected extreme-shock mature observations >= 50
- non-rejected extreme-shock mature observations >= 50

Passing the sample gate means `REVIEW_ELIGIBLE`, not automatic strategy adoption.

## Guardrails

- No historical backfill can count as EXH2 validation evidence.
- No cutoff changes after this preregistration.
- No subgroup search may redefine the primary hypothesis.
- EXH2 findings cannot change frozen FWD1 semantics.
- Any trading rule inspired by EXH2 must be versioned and validated separately because T+1 rejection is only known after T+1 close and is therefore unavailable for the frozen T+1-open execution decision.
