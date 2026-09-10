# Execution & Exit Baseline v1 — Validation Record

Date: 2026-09-10

Methodology: `docs/methodology/execution-exit-v1.md`

Implementation: `src/canslim_research/execution.py`

Tests: `tests/test_execution.py`

CI run: `34433458116` — **SUCCESS**

## Frozen primary baseline

`X1_7PCT_STOP_20PCT_PIVOT_TARGET`

- candidate determined after T0 close;
- earliest execution H+1 open;
- H+1 fill accepted only when `pivot < Open_H+1 <= 1.05 * pivot`;
- one active position per security;
- hard stop = 7% below actual fill;
- primary target = 20% above pivot;
- gap-through exits use the session open;
- same-bar stop/target ambiguity resolves stop-first;
- no arbitrary time stop;
- sample-end open positions are censored, not forced closed for realized PF.

This is independent CAN SLIM research logic and does not inherit TrendFoll's ATR stop, EMA20 exit, or 45-session time stop.
