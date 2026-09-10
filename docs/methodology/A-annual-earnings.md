# A — Annual Earnings Growth

Status: **WORKING SPEC / NOT FROZEN**

## Goal

Define a point-in-time, reproducible interpretation of CAN SLIM **A** using annual EPS history from `ussy-fundamentals`, without selecting the initial rule based on trading performance.

## Available data foundation

The upstream engine already provides, when supported and ready:

- annual EPS;
- annual EPS growth;
- fiscal-year identity;
- SEC provenance and `accepted_at` availability;
- production-readiness classification;
- 5Y target history with 3Y fallback.

Do not modify the extraction layer because a CAN SLIM rule appears too strict or too loose.

## Questions to freeze

1. Should A evaluate 3Y, 5Y, or both?
2. Should the primary metric be CAGR or year-by-year growth?
3. Is consistency required across individual years?
4. How should negative EPS years be treated?
5. How should turnaround companies be treated?
6. Is `PASS_3Y_FALLBACK` eligible for the same A label as `PASS_FULL`?
7. Should fallback be a separate state or confidence tier?
8. Should A be a hard filter, label, or score during initial research?

## Initial methodological constraint

Keep annual-history quality and economic interpretation separate.

Illustrative schema only — **not yet frozen**:

```text
A_growth_state
A_consistency_state
A_history_depth
A_data_state
A_pass
A_reason_codes
```

## PIT rule

Annual state at historical decision time T must only use information available by the defined cutoff according to SEC `accepted_at`.

## Freeze protocol

Before performance backtesting:

1. document source rationale for each annual-growth rule;
2. distinguish O'Neil-derived concepts from our quantitative adaptations;
3. define treatment of negative years, fallback, missing and turnaround states;
4. inspect the label distribution without consulting CAGR/PF;
5. freeze version `A-v1`;
6. only then run C+A strategy ablation.
