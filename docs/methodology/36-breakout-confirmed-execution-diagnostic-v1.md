# #36 Breakout-Confirmed Execution Diagnostic — Preregistration v1

Date: 2026-09-14
Status: **PREREGISTERED / NOT YET RUN**
Primary R0–R3 CANSLIM-eligible comparison: `BLOCKED_ON_ELIGIBLE_POPULATION`

## Purpose

Measure causal execution mechanics for the frozen `BREAKOUT_CONFIRMED` historical population without pretending those records are `CANSLIM_ELIGIBLE`.

This diagnostic exists because the frozen #35 historical pool contains zero `CANSLIM_ELIGIBLE` observations but 138 `BREAKOUT_CONFIRMED` observations. It does not replace the primary population and cannot establish CAN SLIM strategy performance.

## Frozen source

Use only `BREAKOUT_CONFIRMED` records from canonical #35 run `34763920536`.

Required invariants:

- source candidate IDs and pivots are unchanged;
- `breakout_date == asof_date` for every included record;
- no future bar may alter candidate state at T;
- OHLCV comes from frozen historical source `backtest/ohlcv/{security_id}.parquet`;
- raw daily open/high/low/close are used for execution/outcome mechanics;
- no candidate is dropped because of later return.

## Variants

Use the already preregistered fixed R0/R1/R2/R3 rules from `36-entry-variants-prereg-v1.md` with no threshold changes:

- R0: T+1 open baseline;
- R1: first valid open T+1–T+3;
- R2: full daily pivot hold on T+1/T+2, then next valid open;
- R3: +2% near-pivot retest/reclaim research proxy on T+1/T+2, then next valid open.

Traditional buy zone remains `[pivot, pivot * 1.05]`.

## Integrity gate before outcomes

Require zero findings for:

1. fill before signal information availability;
2. entry after T+3;
3. fill not equal to an observed open;
4. fill outside the 0%-5% buy zone;
5. R2/R3 confirmation not preceding fill;
6. breakout date differing from frozen as-of date;
7. future bars altering frozen candidate state.

If any finding exists, stop before reading return metrics.

## Execution diagnostics

For each variant report:

- source count;
- executed count and execution rate;
- non-entry reason counts;
- T+1/T+2/T+3 entry distribution;
- median fill extension from pivot;
- overlap and incremental fills versus R0.

## Fixed outcome metrics

Only after integrity passes, report mark-to-market close return from actual fill at:

- 5 completed sessions after entry;
- 10 completed sessions after entry;
- 20 completed sessions after entry;
- 30 completed sessions after entry.

Horizon convention is frozen before execution: the entry session itself is completed session 1. Therefore horizon `H` uses the close of the H-th trading session beginning with the entry session.

For each horizon report evaluable count, mean, median, win rate, p25, p75, and censored count.

Also report first-20-session MFE and MAE from actual fill when 20 sessions beginning with the entry session exist. MFE uses the maximum observed high and MAE uses the minimum observed low across those 20 sessions.

No CAGR, portfolio simulation, sizing, stop optimization, exit optimization, or parameter search is authorized.

## Interpretation boundary

This is an **execution diagnostic on breakout-confirmed events**, not a CAN SLIM eligible backtest. A favorable R1/R2/R3 result cannot promote that variant into production without a separate freeze and independent validation decision.
