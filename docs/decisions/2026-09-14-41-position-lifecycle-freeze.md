# #41 Position Lifecycle / Exit Arbiter v1 — Freeze Decision

Date: 2026-09-14
Status: **IMPLEMENTATION COMPLETE / FROZEN v1**

Contract: `41-position-lifecycle-exit-arbiter-v1`

## Decision

Freeze the lifecycle arbiter that combines already-frozen #37 capital-protection execution and #40 technical-deterioration execution without changing either upstream contract.

## Frozen arbitration semantics

- no executable #36 entry => no position and no fabricated exit;
- no executable exit candidate => position remains OPEN;
- one executable exit => close exactly once using that upstream execution fact;
- different exit dates => earliest causal executable exit wins;
- same observed-open #37 gap-through and #40 next-session-open => one `SAME_OPEN_CONVERGENCE` close;
- same date where #40 executes at the session open and #37 only later through the daily-low stop convention => #40 open executes first;
- any other same-session ordering not established by frozen source semantics remains `AMBIGUOUS_SAME_SESSION`;
- no OHLC intraday path is invented;
- no exit before entry;
- no double exit after position closure.

## Canonical validation

Workflow: `.github/workflows/41-position-lifecycle-v1.yml`

Canonical run:
- run `34790106465`
- job `103812624227`
- commit `44685b62432adf1601ae6759b5ffa00517410ddf`
- result: **SUCCESS**
- tests: **11 passed in 0.03s**

No semantic/causal finding was observed.

## Governance consequence

The theory-faithful engine now has a deterministic end-to-end trade lifecycle contract from executable #36 entry through currently frozen #37/#40 exits.

This does not create a strategy-performance claim. Primary performance validation remains blocked until a genuine frozen `CANSLIM_ELIGIBLE` population exists. #33-#40, FWD1, EXH2 and P6 boundaries remain unchanged.
