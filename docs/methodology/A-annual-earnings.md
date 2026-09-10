# A — Annual Earnings Growth

Status: **A-v1 FROZEN — PRE-PERFORMANCE**

## Goal

Define a point-in-time, reproducible interpretation of CAN SLIM **A** using annual EPS history from `ussy-fundamentals`, before consulting trading performance.

## Source basis

O'Neil/IBD educational material states that candidate stocks should generally show each of the last three years' earnings up 25% or more, and also describes an average profit-growth target of at least 25% over the past three years. The same material highlights ROE of 17% or more as a desirable characteristic.

William O'Neil + Company's current EPS Rank separately uses a five-year earnings growth rate, falling back to a three-year growth rate when five-year growth is unavailable, alongside recent-quarter growth and earnings stability.

Therefore A-v1 deliberately distinguishes:

- the core annual EPS-growth gate that our SEC/PIT dataset can reproduce defensibly;
- history depth / fallback state;
- additional O'Neil quality evidence that is not yet available in the frozen upstream contract.

## A-v1 primary rule

For the latest annual state known by the decision-time cutoff:

```text
A_pass = TRUE
if:
  three consecutive annual EPS YoY growth observations are evaluable
  AND each annual EPS YoY growth >= +25%
```

This is the frozen primary A-v1 gate.

### Why three annual growth observations?

A-v1 operationalizes the O'Neil/IBD wording that each of the last three years' earnings should be up roughly 25% or more. It is intentionally stricter and more transparent than selecting a CAGR threshold after observing trading results.

## Five-year history

Five-year history is retained as evidence when available, but **is not an additional hard gate in A-v1**.

Record:

```text
A_history_depth
A_five_year_growth_state
```

This preserves the O'Neil EPS-Rank concept of preferring a five-year growth rate when available without pretending that our simple A-v1 gate reproduces the proprietary EPS Rank.

## PASS_3Y_FALLBACK

`PASS_3Y_FALLBACK` is **eligible for A-v1 evaluation** when the required three consecutive annual growth observations are actually evaluable.

It must remain explicitly identifiable:

```text
A_history_tier = FULL | 3Y_FALLBACK
```

A fallback security is not silently promoted to FULL history. Whether FULL and 3Y_FALLBACK have different predictive value is a later research question, not a reason to change A-v1.

## Negative, zero-base and turnaround treatment

Never coerce undefined annual growth into 0%.

If any of the three required annual comparisons is intentionally undefined because the prior/base EPS is nonpositive or otherwise cannot produce a meaningful percentage under the upstream policy:

```text
A_pass = NULL
A_growth_state = TURNAROUND_OR_UNDEFINED_BASE
```

This is not an automatic economic FAIL. It means the strict A-v1 growth gate cannot evaluate the company defensibly.

Turnaround companies may later be studied as a separately pre-specified variant. They are not silently folded into A-v1 PASS.

## Missing / readiness semantics

Data states such as unsupported issuer, unresolved CIK, insufficient history, structurally unavailable evidence, or other non-evaluable annual states must remain explicit.

```text
A_pass = NULL
```

where A cannot be evaluated. Missing is not zero, unsupported is not failed, and insufficient history is not a judgment about company quality.

## ROE

O'Neil/IBD material also highlights ROE around 17% or higher. However, the current frozen `ussy-fundamentals` handoff guarantees annual EPS/growth but does not establish ROE as part of the production C/A contract.

Therefore:

- ROE is documented as an **O'Neil-derived A quality dimension**;
- ROE is **not part of A-v1**;
- the SEC extraction layer must not be reopened merely to make A-v1 look more literal;
- a future `A-v2` or separate quality study may add ROE only through an approved data-contract extension and pre-specified methodology.

## Recommended output schema

```text
A_pass: TRUE | FALSE | NULL
A_growth_state
A_history_tier: FULL | 3Y_FALLBACK | OTHER
A_history_depth
A_year1_eps_yoy
A_year2_eps_yoy
A_year3_eps_yoy
A_five_year_growth_state
A_reason_codes
A_spec_version = "A-v1"
```

`FALSE` means the required annual observations are evaluable but at least one is below +25%.

`NULL` means A-v1 cannot make a defensible classification.

## PIT rule

At historical decision time T, use only annual evidence available by the defined cutoff according to SEC `accepted_at`. Fiscal-year end is not an information-availability timestamp.

## Research discipline

A-v1 is frozen **before trading-performance testing**.

The following are prohibited during the initial test:

- changing 25% because another threshold improves CAGR/PF;
- replacing the three-year consistency gate with CAGR after seeing performance;
- treating negative/undefined bases as zero to increase sample size;
- changing `PASS_3Y_FALLBACK` semantics after seeing its returns;
- modifying SEC extraction/tag vocabulary to improve A pass-rate.

Any material methodological change after performance inspection must receive a new version (`A-v2`, etc.) and an explicit rationale.

## First downstream validation

Before trading ablation:

1. compute A-v1 labels point-in-time;
2. report TRUE / FALSE / NULL distribution;
3. split by FULL vs 3Y_FALLBACK;
4. report reason-code distribution for NULL;
5. inspect sector/symbol concentration;
6. do not use CAGR/PF to revise A-v1.

Only after this distribution sanity check should A-v1 enter C+A strategy experiments.
