# P8 / #33 Pattern Recognition Engine — DEVELOPMENT Design v0.1

Date: 2026-09-12
Status: PREREGISTERED DEVELOPMENT IMPLEMENTATION
Upstream contract: `docs/methodology/theory-faithful-candidate-spec-v1.md`

## Purpose

Implement the first reproducible OHLCV-only morphology layer for #33. This layer recognizes candidate base structures and persists their landmarks and pattern-specific pivots. It does **not** decide breakout confirmation, CAN SLIM eligibility, entry, exit, or trading performance.

The implementation order remains:

```text
Theory -> frozen candidate specification -> pattern implementation -> morphology validation -> performance
```

No threshold in this document may be chosen or altered by inspecting CAGR, PF, FWD1 outcomes, or downstream trade returns.

## Data and split guardrail

- Input: daily OHLCV only.
- Primary source: PIT full-history R2 through the strict `R2 -> Yahoo -> Tiingo` router.
- Current execution split: `DEVELOPMENT` only.
- Provider/QC failure is terminal; fallback is allowed only for explicit source unavailability.
- No future bar beyond the requested as-of window is consumed.

## Core named patterns in v0.1

Implemented:

```text
CUP_WITH_HANDLE
CUP_WITHOUT_HANDLE
DOUBLE_BOTTOM
FLAT_BASE
```

Deferred from this first slice:

```text
ASCENDING_BASE
BASE_ON_BASE
IPO_BASE
```

A consolidation that does not satisfy a named morphology remains unlabeled. The engine must not force a pattern name.

## Preregistered geometry assumptions

These are transparent implementation assumptions for DEVELOPMENT semantic validation, not claims that every number is a uniquely canonical O'Neil threshold.

### Prior uptrend

A named proper-base candidate requires a measurable prior advance:

```text
lookback = 40 completed sessions before base start
pre-base close / lookback-start close - 1 >= 20%
```

If 40 prior sessions are unavailable, state is `NOT_EVALUABLE` and the first v0.1 named detector does not promote the candidate.

### Flat base

```text
duration = 25..35 sessions
max depth <= 15%
prior uptrend = PASS
```

Structural pivot: highest base/left-side high, persisted as `flat_left_high`.

### Cup family

```text
cup duration = 35..130 sessions
cup depth = 12%..50%
right-side recovery >= 90% of left peak
at least 3 sessions in lower quartile of cup range
at least 5 sessions from left peak to low and low to right-side high
prior uptrend = PASS
```

The lower-quartile residence requirement is a fail-closed v0.1 guard against obvious V-shaped rebounds.

#### Cup without handle

Additional rule:

```text
right-side high >= 95% of left peak
```

Structural pivot: left peak.

#### Cup with handle

Additional rules:

```text
handle duration = 5..20 sessions
handle depth <= 15%
handle low remains in upper half of cup
handle high <= 103% of left peak
```

Structural pivot: highest price in the handle. `HANDLE_LOW_TOO_EARLY` is preserved as a warning flag rather than silently discarded.

### Double bottom

```text
duration = 35..90 sessions
first and second lows separated by >= 5 sessions
second-bottom price within +/-5% of first-bottom price
middle rebound >= 10% above first bottom
whole structure depth <= 50%
prior uptrend = PASS
```

Structural pivot: middle peak of the W. A second bottom that does not undercut the first may still be retained with fault flag `SECOND_LOW_DID_NOT_UNDERCUT_FIRST` for semantic review.

## Evidence and ambiguity

Every candidate persists:

```text
pattern_type
pattern_evidence_state
confidence
base_start_date
base_end_or_breakout_ready_date
base_duration_sessions
base_depth_pct
prior_uptrend_state
pivot_level
pivot_landmark_type
pivot_source_date
landmarks
fault_flags
ambiguity_with
pattern_engine_version
```

Confidence is a deterministic morphology-evidence score used only to order/inspect candidates during DEVELOPMENT. It is not trained on outcomes and is not a probability of future return.

If two different pattern types ending on the same session have confidence within 0.05, the engine preserves `pattern_evidence_state=AMBIGUOUS` and lists the competing type(s). It does not resolve the ambiguity using future performance.

## Search policy

- Flat bases: all 25..35-session windows.
- Cup and double-bottom families: deterministic 5-session duration grid plus the exact maximum feasible duration at each end date.
- Search breadth is fixed by this document before reviewing SNPS morphology output.

## Validation target for the first DEVELOPMENT slice

The first live example remains `SNPS`, 2023-01-01 through 2023-12-31, because the source probe already established 250 valid R2 trading sessions for that window.

The first acceptance check is **not profitability**. It is:

1. the workflow completes from R2;
2. output persists landmarks and pivots for every named candidate;
3. no candidate is created without prior-uptrend evidence in v0.1;
4. no pattern type outside the implemented vocabulary appears;
5. ambiguous/fault states are visible rather than silently coerced.

Any morphology problems discovered on SNPS must be documented as detector/definition errors. Threshold changes require a versioned decision before rerunning broader DEVELOPMENT fixtures.
