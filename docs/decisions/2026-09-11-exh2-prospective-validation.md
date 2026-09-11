# Decision — EXH2 prospective exhaustion validation

Date: 2026-09-11

Status: **PRE-REGISTERED / LIVE / ACCUMULATING**

## Decision

EXH2 is launched as a prospective diagnostic sidecar to validate the EXH1 exhaustion mechanism. It does not modify frozen X3, X1, PORT1, FWD1, C/A, or M semantics.

## Discovery basis

EXH1 run `34466747136` found that the highest T-1→T0 shock quintile combined with T+1 bearish-and-below-T0 rejection was associated with materially weaker X1 outcomes. This remains exploratory discovery evidence.

The exact EXH1 80th-percentile shock boundary, `0.0533333333333332`, is transferred once as the frozen EXH2 definition of extreme shock. No alternative cutoff search is permitted.

## Prospective protocol

Methodology: `docs/methodology/exhaustion-validation-v2.md`.

Validation signal dates must satisfy `signal_date > 2026-09-11`.

Primary hypothesis:

- extreme shock: `T0/T-1 - 1 >= 0.0533333333333332`
- T+1 rejection: `Close(T+1) < Open(T+1)` AND `Close(T+1) < Close(T0)`
- primary endpoint: rate of closing below pivot by T+3
- expected direction: extreme-shock rejected group has a higher breakdown rate than extreme-shock non-rejected group

A row becomes mature only after T+1, T+2, and T+3 bars exist. Review eligibility requires at least 50 mature observations in each extreme-shock comparison group.

## Infrastructure validation

Initial workflow run `34574192537` = SUCCESS, but audit found that an empty `observations.csv` had no schema header. This was an evidence-contract issue only; strategy semantics and summary counts were correct.

Patch commit `da0c144ed08807e432745369b1be87f11c3a8d48` preserves the observation schema even when no post-boundary rows exist.

Confirmation run `34574410482` = SUCCESS.

Confirmed initial evidence:

```text
status = ACCUMULATING
candidate_count_post_boundary = 0
mature_candidate_count = 0
mature_extreme_shock_count = 0
rejected_extreme_mature_n = 0
non_rejected_extreme_mature_n = 0
review_eligible = false
fwd1_modified = false
```

The confirmation artifact contains a valid header-only `observations.csv`, so zero-row evidence remains machine-readable.

## Guardrail

T+1 rejection is only observable after T+1 close. Therefore it cannot be retrofitted into the frozen T+1 Open execution decision. If EXH2 validates the mechanism and motivates a tradable rule, that rule must start a separate versioned validation track with its own executable timing semantics.
