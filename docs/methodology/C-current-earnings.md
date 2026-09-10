# C — Current Quarterly Earnings

Status: **WORKING SPEC / NOT FROZEN**

## Goal

Define a point-in-time, reproducible interpretation of CAN SLIM **C** using the production outputs of `ussy-fundamentals`, without tuning the initial rule against trading performance.

## Available data foundation

The upstream engine already provides, when supported and ready:

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

## Questions to freeze

1. Which quarter is the primary evaluation quarter?
2. Is EPS YoY the primary rule?
3. Is revenue YoY mandatory, confirmatory, or separately scored?
4. Is one strong quarter enough?
5. Should recent acceleration/consistency across multiple quarters matter?
6. How should prior-year EPS <= 0 be interpreted?
7. How should turnaround cases be represented?
8. How should zero-base / intentionally undefined growth be represented?
9. What constitutes stale C evidence?
10. Is C a hard filter, label, score, or multiple component labels during research?

## Initial methodological constraint

During the first research phase, prefer retaining transparent component labels rather than collapsing everything into one opaque score.

Illustrative schema only — **not yet frozen**:

```text
C_eps_growth_state
C_revenue_growth_state
C_recent_consistency_state
C_data_state
C_pass
C_reason_codes
```

## Missing semantics

Never coerce these into 0% growth:

- intentionally undefined negative/zero-base comparisons;
- unsupported issuer state;
- unresolved identity;
- insufficient history;
- structurally unavailable evidence.

These need explicit downstream handling.

## PIT rule

At decision time T, only filing information available by the defined cutoff may be used. Availability is governed by SEC `accepted_at`, not fiscal-period end.

## Freeze protocol

Before performance backtesting:

1. document source rationale for each rule;
2. distinguish O'Neil-derived concepts from quantitative adaptations;
3. define all edge-case semantics;
4. inspect pass/fail/data-state distribution on the production-ready universe;
5. freeze version `C-v1`;
6. only then run trading ablation.
