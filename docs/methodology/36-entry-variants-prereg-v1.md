# #36 Entry Timing Variants — Preregistration v1

Date: 2026-09-14
Status: **PREREGISTERED / NOT YET RUN**
Upstream frozen baseline: `36-execution-entry-v1`

## Purpose

Compare a small set of causal daily-EOD execution variants **without changing** the frozen #33 pattern contract, #34 qualification contract, #35 validation corpus, or canonical #36 T+1-open baseline.

This is execution research, not detector/classifier tuning and not an O'Neil-theory redefinition.

## Non-negotiable causal rule

For every variant, a fill may use only information available before that fill.

```text
candidate known after close T
→ no same-day hindsight fill
→ confirmation using close of day D can only be acted on at D+1 open or later
```

No synthetic intraday limit fill, no assumed touch fill, and no backdating.

## Frozen reference boundary

Traditional buy-zone upper boundary remains:

```text
pivot * 1.05
```

It is not tunable in this research.

A valid executable open is:

```text
pivot <= open <= pivot * 1.05
```

## Variants

### E36-R0 — canonical baseline

```text
T+1 open only
```

Enter at T+1 open iff the open is inside the frozen buy zone. Otherwise record the appropriate non-entry state. This is the frozen `36-execution-entry-v1` baseline and is never rewritten based on comparison results.

### E36-R1 — first valid open through T+3

```text
inspect opens T+1, T+2, T+3 sequentially
→ enter on the first open inside the frozen buy zone
```

No close/low confirmation is required. The maximum delay is fixed at three sessions before any result is inspected.

Purpose: quantify whether a short causal waiting window recovers otherwise missed entries without inventing fills.

### E36-R2 — full daily pivot hold, then next open

Confirmation can occur on T+1 or T+2 only.

A confirmation session requires:

```text
session low > pivot
AND pivot < session close <= pivot * 1.05
```

Because the close is known only after that session ends, execution occurs at the next session open and only if that open is still inside the frozen buy zone. Maximum executable entry remains T+3.

Purpose: test a stricter post-breakout-hold confirmation while preserving causal chronology.

### E36-R3 — near-pivot retest/reclaim research proxy, then next open

This is explicitly a **research proxy**, not an authoritative O'Neil threshold.

Confirmation can occur on T+1 or T+2 only and uses the already pre-existing research band from legacy entry-timing work:

```text
session low <= pivot * 1.02
AND pivot < session close <= pivot * 1.05
```

Execution is at the following session open only if still inside the frozen buy zone, no later than T+3.

The +2% proximity band is fixed before this analysis and must not be tuned from outcomes. A result favorable to R3 does not promote +2% into theory or production identity.

## Input population

Use only records satisfying the frozen upstream #34/#35 contract required for actionable entry research. Preserve candidate IDs and signal dates exactly.

The research dataset must not alter candidate eligibility using future bars.

## Pre-performance integrity checks

Before any return metric is inspected, require:

1. zero fill before information availability;
2. no fill after T+3 for R1/R2/R3;
3. every executed fill equals an observed daily open;
4. every executed fill lies inside the frozen 0%-5% pivot buy zone;
5. R2/R3 confirmation-date chronology precedes fill date;
6. no future bar changes signal-T candidate state;
7. no #33/#34/#35 code or frozen 60-case evidence is modified.

A failure here is an implementation/causality finding, not a performance result.

## Descriptive execution metrics

Report for each variant before outcome returns:

- source candidate count;
- executed count and execution rate;
- non-entry reason counts;
- entry offset distribution (T+1/T+2/T+3);
- gap-through-pivot entry count;
- median and distribution of fill extension from pivot;
- overlap / incremental fills relative to R0.

These are execution diagnostics, not strategy selection metrics.

## Performance metrics — fixed before inspection

If and only if integrity checks pass, report the same fixed post-entry mark-to-market horizons for all variants:

```text
5 completed sessions
10 completed sessions
20 completed sessions
30 completed sessions
```

For each horizon report:

- number evaluable;
- mean return;
- median return;
- win rate (`return > 0`);
- 25th / 75th percentiles;
- missing/censored count.

Also report maximum adverse excursion and maximum favorable excursion over the first 20 completed sessions when the required bars exist.

No CAGR, portfolio sizing, stop optimization, or exit optimization is part of this comparison.

## Interpretation rule

This run is comparative/descriptive. No variant becomes canonical merely because it has the best mean return, win rate, or MFE/MAE profile.

Any production promotion requires a separate governance decision considering:

- causal correctness;
- execution coverage;
- robustness across time/security/pattern strata;
- whether the rule is theory-backed or only a research proxy;
- independent validation after a rule is frozen.

## Prohibited actions

- Do not tune +5%, +2%, T+3, or confirmation windows after seeing results.
- Do not drop losing cases or strata.
- Do not change frozen #33/#34/#35 semantics.
- Do not use the frozen #35 60-case corpus to optimize execution thresholds.
- Do not relabel R1/R2/R3 as O'Neil-authoritative rules solely from performance.
- Do not retrofit results into frozen FWD1/X3 or EXH2.
