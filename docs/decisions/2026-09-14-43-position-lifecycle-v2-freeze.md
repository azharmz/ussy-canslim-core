# #43 Position Lifecycle / Exit Arbiter v2 — Freeze Decision

Date: 2026-09-14
Status: **IMPLEMENTATION COMPLETE / FROZEN v2**

Contract: `43-position-lifecycle-exit-arbiter-v2`

## Decision

Freeze the lifecycle arbiter that combines the already-frozen executable exits from #37 capital protection, #40 technical deterioration, and #42 round-trip behavior.

## Frozen semantics

- no executable #36 entry => no opened position;
- no executable exit => position remains OPEN;
- one executable exit => close once using that exact upstream execution fact;
- different dates => earliest causal executable exit wins;
- same-date session-open exits occur before #37 daily-low stop-convention execution;
- multiple session-open exits at the same observed open and same price converge into one close;
- same-date open exits with conflicting prices are `NOT_EVALUABLE_SOURCE_CONFLICT` because one daily bar has one observed open;
- same-session ordering unsupported by frozen source semantics remains `AMBIGUOUS_SAME_SESSION`;
- no OHLC intraday path is invented;
- no exit may precede entry;
- no later exit may close an already closed position.

## Canonical validation

Workflow: `.github/workflows/43-position-lifecycle-v2.yml`

Canonical run:
- run `34796938374`
- job `103831748596`
- commit `879c50109f90a73d5ea7cd9f42988b3542d00e90`
- result: **SUCCESS**
- tests: **11 passed in 0.03s**

No semantic/causal findings were observed.

## Governance consequence

The current theory-faithful lifecycle now has three frozen executable sell channels:

```text
#37 capital protection
#40 technical deterioration
#42 round-trip
        ↓
#43 lifecycle v2 arbitration
```

#41 v1 remains frozen as historical contract and is not rewritten. #43 supersedes it only for integrations that explicitly opt into #42.

This is semantic completeness for the current three-channel action set, not a strategy-performance claim. Primary performance validation remains blocked until a genuine frozen `CANSLIM_ELIGIBLE` population exists.
