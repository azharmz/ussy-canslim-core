# #36 Clarification — O'Neil Entry Semantics vs Backtest Execution Clock

Date: 2026-09-14
Status: **GOVERNANCE CLARIFICATION / NO SEMANTIC CHANGE**

## Purpose

Clarify terminology in frozen `36-execution-entry-v1` so implementation conventions are not misrepresented as CAN SLIM / O'Neil theory.

This clarification does **not** reopen, retune, or alter #33, #34, #35, frozen #36 v1 behavior, the frozen 60-case corpus, or any numeric threshold.

## Layer A — O'Neil / CAN SLIM theory semantics

Theory-derived concepts used by #36 include:

- proper buy point / structural pivot;
- breakout through the pivot;
- breakout volume confirmation;
- CAN SLIM qualification inherited from #34;
- traditional buy zone from the proper buy point through approximately +5%;
- avoiding/chasing an entry beyond that traditional buy zone;
- defensive loss management referenced to the actual purchase price;
- normal +20%-25% profit-management zone referenced to the proper buy point.

These are the theory-semantic layer.

## Layer B — Daily-EOD information boundary

`T`, `close T`, and `information available after close T` are dataset/backtest chronology labels, not O'Neil terminology.

In the current system, #34 uses the completed daily bar at T, including T close and T volume, to finalize breakout confirmation and candidate eligibility. Therefore a simulation that waits for that completed information cannot causally claim an earlier fill during T.

This is an information-availability constraint, not a claim that an O'Neil trader must wait until the market closes.

## Layer C — Execution convention

`T+1 OPEN` is the frozen canonical **backtest execution convention** for `36-execution-entry-v1`.

It means:

```text
candidate finalized from completed T data
-> information known after T close
-> first mechanically observable causal fill convention = next session open
```

It is **not** an O'Neil/CAN SLIM rule.

Likewise, `T+1 through T+3`, delayed pivot-hold entries, and retest/reclaim variants are research execution conventions. They must never be labelled as canonical O'Neil timing rules.

## Naming rule going forward

Documentation and future outputs should distinguish:

```text
THEORY SEMANTICS
  pivot / proper buy point
  breakout + volume confirmation
  CAN SLIM eligibility
  traditional +5% buy zone

INFORMATION BOUNDARY
  signal date T
  completed T bar
  information available after close T

EXECUTION CLOCK
  T+1 OPEN baseline
  T+1..T+3 or delayed/retest variants
```

Preferred wording:

- `O'Neil/CAN SLIM entry semantics` for the theory-derived price/state rules;
- `daily-EOD information boundary` for when the system knows the completed signal;
- `backtest execution convention` for T+1/T+2/T+3 clocks.

Avoid wording that implies `T+1 Open` or `T+3` is itself an O'Neil rule.

## Governance effect

Frozen #36 v1 remains unchanged and valid as a causal implementation baseline. Its T+1-open rule is now explicitly classified as an implementation/execution-clock convention layered beneath theory-derived entry semantics.

The completed BREAKOUT_CONFIRMED-only diagnostic remains diagnostic-only. No R1/R2/R3 promotion follows from this clarification.

Any future execution research must report theory semantics and execution-clock assumptions separately.