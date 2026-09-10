# C — Current Quarterly Earnings

Status: **FROZEN — C-v1**

## Rule

Evaluate the latest usable fiscal quarter known by the decision-time cutoff:

```text
C_pass = TRUE
if quarterly EPS YoY >= 25%
AND quarterly revenue YoY >= 25%
```

## Interpretation

- Both EPS YoY and revenue YoY must be numerically evaluable.
- If either is below 25%, `C_state = FAIL` only when both inputs are evaluable.
- If either is undefined/missing for a defensible data-semantic reason, `C_state = NOT_EVALUABLE`.
- Missing/undefined values must never be coerced to 0%.
- Negative-base/zero-base and turnaround cases remain explicit states/evidence, not silently converted to PASS/FAIL.
- Acceleration/consistency across several quarters may be retained as diagnostics, but is **not** a C-v1 hard gate.

### Frozen truth table

```text
EPS evaluable + Revenue missing      -> NOT_EVALUABLE
EPS missing    + Revenue evaluable    -> NOT_EVALUABLE
EPS missing    + Revenue missing      -> NOT_EVALUABLE
Both evaluable; either < 25%          -> FAIL
Both evaluable; both >= 25%           -> PASS
```

Revenue is therefore a required C-v1 input, not an optional enhancement. Missing revenue is a coverage/evaluability issue and must not cause the consumer to fall back to an EPS-only verdict.

## PIT rule

Only filing information available by the historical decision-time cutoff may be used. Availability is based on SEC `accepted_at`.

## Versioning rule

C-v1 was frozen before trading-performance testing. Any change after inspecting CAGR/PF/trade outcomes must be a new methodology version (for example `C-v2`) with an explicit rationale and independent validation protocol.
