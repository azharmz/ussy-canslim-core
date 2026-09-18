# FA-first historical CAN SLIM backtest — contract audit v1

Date: 2026-09-18
Status: IMPLEMENTATION BOUNDARY FROZEN BEFORE PERFORMANCE

## Purpose

Define the minimal causal historical runner without requiring a full-universe historical O'Neil replay.

Canonical flow:

```text
historical PIT fundamental state
-> PASS interval / watchlist
-> causal daily chart monitoring
-> frozen #33 pattern contract
-> frozen #34 candidate semantics
-> signal T
-> frozen #36 T+1 Open execution
-> frozen lifecycle/outcome
```

Performance must not alter any upstream rule.

## Authorities audited

- Fundamental PIT: `docs/methodology/historical-ca-asof-v1.md`.
- Production baseline: `docs/decisions/2026-09-16-canslim-v1-production-baseline-freeze.md`.
- Pattern source: `azharmz/ussy-oneil-patterns@c433cc1e35a5aa32a46f732cd8c5545935e36e40`.
- Pattern schema: `oneil-pattern-output-v2`; four core families only.
- Candidate: `34-candidate-generator-v0.2` / `src/canslim_research/candidate_v2.py`.
- Entry: `36-execution-entry-v1`.
- Market consumer: `50-market-state-consumer-v1`.
- Lifecycle arbiter: `43-position-lifecycle-exit-arbiter-v2`.

## Audit findings

### Fundamental/watchlist boundary

Historical fundamental evidence is causal only when every source used satisfies:

```text
accepted_at <= 16:00 America/New_York on decision date D
```

Amendments become usable only after their own acceptance time. Missing evidence remains NOT_EVALUABLE.

A watchlist interval is therefore a maximal contiguous decision-state interval for which the frozen historical fundamental state remains PASS. The runner must consume the historical state/transition artifact as authority for its boundaries; it must not invent a fixed expiry or monitor only the first PASS date.

The existing `run_historical_ca_attachment.py` is NOT the population source for this backtest because it begins from technical candidates. It is retained as historical regression evidence.

### Pattern input/window

The backtest must execute the exact frozen #33 implementation pinned above. On decision date D, no bar with session_date > D may be passed to #33. Required warm-up is determined by the frozen engine itself; the backtest adapter may fetch older bars but may not shorten/change detector semantics.

### Breakout/volume/candidate gate

Downstream candidate semantics are exact:

- only RECOGNIZED frozen core patterns with a defined pivot can progress;
- breakout is the first daily bar after structure whose HIGH is strictly greater than pivot;
- a prior HIGH > pivot after structural_end makes a later crossing non-first;
- breakout volume confirmation requires current volume / mean(prior 50 session volumes) >= 1.40;
- full entry staging requires frozen letter-state eligibility; pattern recognition alone is never BUY;
- canonical entry candidate stage is `CANSLIM_ELIGIBLE`.

### M

Production M requires a canonical market state for the exact completed decision session. Future state is prohibited and stale state fails closed. Historical backtest may therefore use M only where a governed historical exact-date state exists. Otherwise M is NOT_EVALUABLE and cannot be synthesized from current/future M.

### Execution

Signal uses completed bar T. First execution opportunity is T+1 Open.

```text
pivot <= T1_open <= pivot * 1.05 -> EXECUTED_T1_OPEN
T1_open > pivot * 1.05          -> MISSED_EXTENDED_AT_OPEN
T1_open < pivot                 -> BELOW_PIVOT_AT_OPEN
no next session                 -> NO_NEXT_SESSION_BAR
```

Actual T+1 Open is the fill; no same-close or synthetic +5% fill. Persist T close -> T+1 open gap explicitly.

### Exit

Do not invent a simplified holding-period exit. Historical outcome work must consume the already-frozen sell/lifecycle contracts and v2 arbiter. Until those inputs are wired causally, the minimal runner stops at entry events.

## Minimal-runner gate

Phase 1 is intentionally one security x one fundamental PASS interval.

Required assertions before scaling:

1. interval boundaries come from the frozen historical fundamental state artifact;
2. every monitored decision date is inside that interval;
3. every fundamental source accepted_at <= decision cutoff;
4. every #33 OHLCV input bar <= decision date;
5. prefix replay cannot change an already-emitted assessment when future bars are appended;
6. candidate construction is the frozen #34 implementation;
7. M is exact-date governed evidence or fail-closed;
8. signal T never fills before T+1 Open;
9. T+1 gap is persisted;
10. no performance metric is computed in this phase.

After PASS, scale only to all historical PASS intervals. BT5 mass replay remains OPTIONAL REUSABLE INFRASTRUCTURE, not a prerequisite.
