# A — Annual Earnings Growth

Status: **FROZEN — A-v1**

## Rule

Evaluate the latest three consecutive annual EPS YoY observations known by the decision-time cutoff:

```text
A_pass = TRUE
if latest 3 annual EPS YoY observations
are all evaluable
AND each >= 25%
```

## Interpretation

- Three consecutive evaluable annual growth observations are required.
- If any of the three is below 25%, `A_state = FAIL`.
- If fewer than three are available, `A_state = NOT_EVALUABLE`.
- If one or more required growth observations are intentionally undefined/missing, `A_state = NOT_EVALUABLE`.
- Negative/zero-base annual comparisons are not coerced to 0%.
- Turnaround histories remain explicit evidence states, not silently forced into PASS/FAIL.
- `PASS_3Y_FALLBACK` is eligible for evaluation but remains a separate provenance tier from `PASS_FULL`.
- Five-year history may be retained as evidence/diagnostic context, but is not an A-v1 hard gate.
- ROE is not part of A-v1 because it is not part of the frozen production C/A input contract.

## PIT rule

Annual state at historical decision time T may only use information available by the explicit cutoff according to SEC `accepted_at`.

## Versioning rule

A-v1 was frozen before trading-performance testing. Any later change motivated by performance must become a new methodology version with an explicit rationale and untouched validation evidence.
