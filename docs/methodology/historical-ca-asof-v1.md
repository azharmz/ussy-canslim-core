# Historical C/A As-of Join v1 — FROZEN

Date: 2026-09-10

Status: **FROZEN BEFORE C/A TRADING ABLATION**

## Purpose

Attach C-v1 and A-v1 labels to a historical technical signal using only SEC information available by the signal decision time.

## Identity chain

Fundamental PIT rows are keyed by `symbol + cik`; they do not contain `security_id`. The pinned fundamentals snapshot also contains `current_universe.csv`, which exposes a unique `security_id` and `symbol/ticker` bridge.

For the current static-history research track, the join chain is:

```text
security_id
  -> pinned current_universe.csv symbol
  -> pinned fundamentals_final_production_report.csv CIK
  -> PIT fundamentals rows
```

The bridge must be pinned to the same fundamentals manifest used by the experiment. Joining ad-hoc current ticker strings is not allowed.

Because historical Musaffa membership exists only from 2026-08-28, a pre-2026-08-28 static-history experiment still has eligibility/survivorship bias even when its SEC C/A join is temporally correct.

## Decision-time cutoff

A T0 signal is known after the U.S. regular-market close. For every trading date:

```text
cutoff = 16:00 America/New_York on T0
```

converted to UTC with timezone/DST awareness.

Only fundamental evidence with:

```text
accepted_at <= cutoff
```

may contribute to C or A.

This is stricter and more precise than using fiscal-period end, filing date alone, or UTC end-of-day.

## C-v1 historical state

At each signal cutoff:

1. keep SEC PIT rows for the mapped issuer with `accepted_at <= cutoff`;
2. identify the latest known quarterly fundamental state;
3. evaluate the frozen C-v1 rule:

```text
quarterly EPS YoY >= 25%
AND
quarterly revenue YoY >= 25%
```

If the latest quarter has undefined/missing growth, C is `NOT_EVALUABLE`; do not skip backward to an older quarter merely to obtain a numeric value.

## A-v1 historical state

At each signal cutoff:

1. keep annual SEC evidence known by cutoff;
2. for each fiscal year, retain the latest evidence known by cutoff;
3. order fiscal years chronologically;
4. take the latest three consecutive annual EPS-growth observations;
5. evaluate A-v1: all three must be evaluable and each >=25%.

Undefined/negative/zero-base growth remains `NOT_EVALUABLE`, never zero.

## Pre-SEC coverage

The current PIT dataset begins in 2009. Signals before the first issuer evidence are `NOT_EVALUABLE`, not FAIL.

## Amendment handling

Later amendments can affect only decision times after their own `accepted_at`. Historical states before amendment acceptance remain unchanged.

## Readiness

Current production readiness is not retroactively interpreted as historical economic quality. For static exploratory joins, readiness metadata is retained as provenance; historical C/A labels derive from available PIT evidence at each signal cutoff.

## Output contract

Every labeled signal must retain at least:

```text
signal_date
signal_cutoff_utc
security_id
symbol
cik
C_state
C_reason
C_source_accepted_at
C_source_fiscal_period_end
A_state
A_reason
A_latest_source_accepted_at
fundamentals_manifest_key
identity_bridge_snapshot_date
```

## Anti-look-ahead invariant

For every emitted label:

```text
max(source accepted_at used) <= signal_cutoff_utc
```

Any violation is a hard failure of the experiment.
