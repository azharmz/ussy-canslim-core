# Decision — Theory-Faithful Candidate Specification v1

Date: 2026-09-12
Status: FROZEN

## Decision

Freeze `docs/methodology/theory-faithful-candidate-spec-v1.md` as the implementation contract for the post-v1 O'Neil/CAN SLIM research path.

## Rationale

The completed #25-#31 Theory Fidelity Audit showed that frozen quantitative v1 is a transparent CAN SLIM-inspired proxy rather than a faithful reconstruction. In particular, proper-base morphology, pattern-specific pivots, breakout event-vs-quality semantics, full leadership context, component-role semantics and canonical sell/risk logic were incompletely represented.

The new specification therefore separates:

```text
BASE_RECOGNIZED
PIVOT_DEFINED
PIVOT_CROSSED
BREAKOUT_CONFIRMED
CANSLIM_ELIGIBLE
```

instead of using one universal Boolean candidate flag.

## Core candidate eligibility

The initial theory-faithful candidate path requires:

```text
valid named proper base
+ pattern-specific pivot
+ pivot crossing
+ breakout-day volume >=1.40x prior-50-session average
+ C primary screen PASS
+ A primary screen PASS
+ individual L screen PASS (transparent RS proxy >=80)
+ M permits new buys
```

S broader supply evidence, I sponsorship, RS-line confirmation/divergence, industry leadership and non-price N catalyst state are retained as explicit evidence layers rather than universal additional hard gates in this first theory-faithful candidate contract.

## Fundamental semantics

For C, the core theory-supported hard screen is recent quarterly EPS growth around >=25%. Revenue growth/acceleration is retained as quality evidence; the old v1 conjunction `EPS YoY >=25% AND Revenue YoY >=25%` is not frozen as the only canonical definition of C.

For A, the theory-supported requirement is sustained multi-year annual earnings growth around >=25%. The old v1 rule requiring each of the latest three annual YoY observations individually to exceed 25% is not frozen as canonical identity. A reproducible aggregation/consistency adapter must be versioned before #35 and must not be chosen using return optimization.

## Implementation boundaries

- #33 implements pattern/base segmentation, landmarks, named morphology and pattern-specific pivots from existing daily R2 OHLCV.
- #34 later composes pattern output with breakout, volume, C/A/L/S/I/M evidence into candidate records.
- #35 validates morphology, landmark/pivot accuracy, chronology, PIT safety and state semantics before performance testing.
- #36 remains the downstream execution/entry track.
- Detailed #31 sell/risk rules are downstream and do not define whether a pre-entry candidate exists.

## Guardrails

- Do not retrofit v2 semantics into frozen v1/FWD1/EXH2.
- Do not optimize pattern or eligibility rules against historical CAGR/PF before semantic validation.
- Preserve `NOT_EVALUABLE`, `NOT_IMPLEMENTED`, `AMBIGUOUS`, warning and confirmation states explicitly.
- Do not fabricate proprietary IBD ratings/taxonomies.

## Consequence

#32 is complete. #33 O'Neil Pattern Recognition Engine may now begin against the frozen specification.
