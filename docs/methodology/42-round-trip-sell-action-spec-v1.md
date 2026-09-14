# #42 Round-Trip Sell Action Specification v1

Date: 2026-09-14
Status: **FROZEN FOR IMPLEMENTATION**

Contract: `42-round-trip-sell-action-v1`

Upstream frozen authority:
- `docs/methodology/37-theory-faithful-sell-risk-spec-v1.md`
- frozen #36 entry facts
- authoritative IBD round-trip sell-rule evidence identifying a double-digit gain from the ideal buy point followed by a return to/below the buy point as a sell condition

## 1. Purpose

Resolve the #37 round-trip boundary without using historical-return optimization.

#42 promotes only the minimum reproducible rule supported by the authoritative evidence:

```text
position first achieves a double-digit gain from the proper buy point
AND
later completed daily close returns to or below the proper buy point
-> round-trip sell action
```

## 2. Numeric precondition

"Double-digit gain" is operationalized at its lower bound:

```text
prior_max_high >= pivot_level * 1.10
```

The reference is the proper buy point / pivot, not actual fill.

This is not a performance-selected threshold. It is the minimum numeric interpretation of authoritative "double-digit gain" language.

## 3. Return-to-buy-point condition

Canonical v1 uses completed daily close:

```text
current_close <= pivot_level
```

This is intentionally conservative. Authoritative examples describe a return below the buy point, while some guidance says to act before all gains are fully erased. Because "near the buy point" lacks a frozen quantitative distance, #42 v1 does **not** invent a near-pivot band.

Thus #42 v1 claims only a reproducible minimum sell trigger, not the earliest discretionary O'Neil execution.

## 4. Chronology

The double-digit gain must occur strictly before the trigger session.

```text
prior_max_high = max(high of completed sessions before trigger session)
```

A session that both first reaches +10% intraday and closes back at/below pivot on the same daily bar is `AMBIGUOUS_SAME_SESSION` in v1 because daily OHLCV cannot establish whether the gain occurred before the return-to-pivot condition.

No high/low intraday path may be invented.

## 5. Causal execution

The round-trip condition depends on completed-session close, so it is known only after that close.

Canonical execution convention:

```text
first observed trading-session open after the trigger session
```

If no later daily bar exists, state is `NO_NEXT_SESSION_BAR`.

This next-session-open clock is a backtest/data convention, not O'Neil terminology.

## 6. Interaction with #37

#42 does not change:
- practical ~7% capital protection from actual fill;
- gap-through handling;
- +20%-25% management evidence;
- eight-week exceptional-winner state.

If #37 capital protection executes before #42, the position is already closed. Final multi-exit arbitration belongs to a later lifecycle version; frozen #41 v1 is not mutated.

## 7. States

```text
NOT_EVALUABLE
NO_ACTION
ROUND_TRIP_EXIT_REQUIRED
NO_NEXT_SESSION_BAR
AMBIGUOUS_SAME_SESSION
```

## 8. Required output

```text
candidate_id
security_id
entry_date
fill_price
pivot_level
prior_max_high
prior_max_gain_from_buy_point_pct
trigger_date
trigger_close
round_trip_state
execution_date
execution_price
execution_source
source_sell_risk_version
source_entry_version
action_version
```

## 9. Validation classes

- R42-A version/lineage
- R42-B proper-buy-point reference
- R42-C prior double-digit-gain chronology
- R42-D completed-close return-to-pivot
- R42-E same-session ambiguity preserved
- R42-F next-session causal execution
- R42-G no synthetic near-pivot threshold
- R42-H no upstream mutation

Acceptance: zero semantic/causal findings.

## 10. Performance boundary

No CAGR, profit factor, win-rate, expectancy or threshold optimization may be used to validate or tune #42.
