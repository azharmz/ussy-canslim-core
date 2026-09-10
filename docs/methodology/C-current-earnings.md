# C — Current Quarterly Earnings

Status: **C-v1 FROZEN — 2026-09-10**

## Goal

Define a point-in-time, reproducible interpretation of CAN SLIM **C** using production outputs from `ussy-fundamentals`, without tuning the initial rule against trading performance.

## Source rationale

Primary O'Neil/IBD guidance used for C-v1:

- IBD's published investment rules state that recent quarterly **earnings and sales should be up 25% or preferably much more**.
- The same guidance prefers recent earnings and sales to be accelerating.
- William O'Neil + Co.'s EPS Rank explicitly uses the percentage increase in the most recent quarter versus a year ago and the prior quarter versus its year-ago comparison.

C-v1 therefore uses **25% YoY** as the pre-performance threshold for both latest-quarter EPS and revenue, while keeping acceleration as a diagnostic rather than an initial hard gate.

## Available data foundation

The upstream engine provides, when supported and ready:

- quarterly EPS;
- quarterly revenue;
- quarterly EPS YoY;
- quarterly revenue YoY;
- fiscal-period identity;
- SEC filing provenance;
- `accepted_at` availability;
- missing/readiness reason codes;
- direct-quarter / valid Q4 reconstruction provenance.

Do not change upstream extraction rules to improve C pass-rate.

## C-v1 point-in-time evaluation

At each strategy decision timestamp `T`:

1. use only facts with `accepted_at <= decision_cutoff(T)`;
2. identify the latest usable fiscal quarter known at that time;
3. respect the upstream staleness/readiness contract;
4. evaluate latest-quarter EPS YoY and revenue YoY against their same-quarter prior-year bases.

### Frozen threshold

```text
EPS YoY >= +25%
AND
Revenue YoY >= +25%
```

Both are required for `C_pass = TRUE` in C-v1.

This is intentionally strict and transparent. We do not relax either threshold based on the first backtest result.

## Frozen output states

Recommended downstream fields:

```text
C_version = "C-v1"
C_data_state
C_eps_yoy
C_revenue_yoy
C_eps_pass
C_revenue_pass
C_eps_acceleration_state
C_revenue_acceleration_state
C_turnaround_state
C_pass
C_reason_codes
C_source_accepted_at
C_fiscal_period
```

### `C_pass`

Use nullable three-state semantics:

- `TRUE`: both numeric latest-quarter EPS YoY and revenue YoY are defined and >= 25%;
- `FALSE`: required values are defined, but at least one is < 25%;
- `NULL`: C cannot be evaluated defensibly because a required comparison is unavailable/undefined or the issuer is not C-ready under the data contract.

`NULL` is not economic FAIL.

## Acceleration

C-v1 records acceleration but **does not use it as a hard gate**.

Where the latest and prior evaluable YoY observations exist:

```text
C_eps_acceleration = latest_eps_yoy - prior_eps_yoy
C_revenue_acceleration = latest_revenue_yoy - prior_revenue_yoy
```

Store categorical states such as `ACCELERATING`, `DECELERATING`, `FLAT`, or `UNAVAILABLE` using a separately documented comparison tolerance if needed. Do not introduce a trading-performance-selected acceleration threshold into C-v1.

Reason: O'Neil guidance favors acceleration, but making it an additional hard gate in the first specification would combine multiple hypotheses and reduce interpretability of the first ablation.

## Negative-base, zero-base and turnaround treatment

Upstream policy intentionally leaves some percentage growth undefined when the prior-year/base value is nonpositive or otherwise not meaningful as a percentage comparison. C-v1 preserves that semantic.

### Prior EPS <= 0 with current EPS > 0

Label as a **turnaround state** rather than inventing an EPS growth percentage.

```text
C_turnaround_state = TURNAROUND_FROM_NONPOSITIVE_BASE
C_eps_yoy = NULL
C_eps_pass = NULL
C_pass = NULL
```

A later explicitly versioned turnaround variant may test whether such cases deserve separate treatment. C-v1 does not silently pass them.

### Zero/nonpositive revenue base or other intentionally undefined comparison

Preserve upstream undefined/missing reason and set the affected component plus `C_pass` to `NULL` when a required numeric comparison cannot be made.

Never coerce undefined growth to `0%`.

## Missing/readiness treatment

These are data states, not automatic economic verdicts:

- `UNSUPPORTED_FPI`
- `UNRESOLVED_CIK`
- `INSUFFICIENT_HISTORY`
- `STRUCTURALLY_UNAVAILABLE_OR_UNSUPPORTED`
- other explicit upstream readiness/missing states

For C-v1 they produce `C_pass = NULL` unless enough defensible C evidence exists under the upstream contract.

## PIT and filing timing

The availability timestamp is SEC `accepted_at`, not fiscal-period end.

The CAN SLIM implementation must define a market decision cutoff. If a filing is accepted after that cutoff, it becomes eligible only at the next decision point. The cutoff convention must be stored in every experiment config.

## Research protocol after freeze

C-v1 is frozen **before trading-performance testing**.

Next steps:

1. implement the C-v1 labeler without look-ahead;
2. resolve and pin the exact fundamental snapshot/manifest used;
3. inspect `TRUE/FALSE/NULL` distribution and reason-code distribution on the production-ready universe;
4. inspect sector/symbol concentration of C-pass for obvious pathological behavior;
5. do not change the 25% thresholds merely because the distribution looks inconvenient;
6. then run C ablation against the independent CAN SLIM technical baseline.

Any later change becomes `C-v2` with a written rationale and must not overwrite C-v1 history.
