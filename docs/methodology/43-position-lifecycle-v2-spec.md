# #43 Position Lifecycle / Exit Arbiter v2 Specification

Date: 2026-09-14
Status: **FROZEN FOR IMPLEMENTATION**

Contract: `43-position-lifecycle-exit-arbiter-v2`

Upstream frozen authority:
- `36-execution-entry-v1`
- `37-sell-risk-v1`
- `40-technical-deterioration-action-v1`
- `42-round-trip-sell-action-v1`
- `41-position-lifecycle-exit-arbiter-v1`

## 1. Purpose

Extend the frozen #41 lifecycle arbiter by adding the separately frozen #42 round-trip executable exit channel. No upstream threshold, trigger, evidence definition, execution clock, or fill convention may change.

```text
#36 executable entry
-> OPEN POSITION
-> #37 capital-protection exit candidate
   OR #40 technical-deterioration exit candidate
   OR #42 round-trip exit candidate
-> earliest causal executable exit
-> CLOSED POSITION
```

## 2. Non-negotiable governance

#43 is integration only.

- #37 practical ~7% defensive rule is unchanged.
- #40 completed-week 10-week deterioration trigger and next-session-open execution are unchanged.
- #42 prior double-digit gain, subsequent completed-close return to/below pivot, ambiguity handling, and next-session-open execution are unchanged.
- No historical return may choose arbitration precedence.
- No exit may occur before the #36 executable entry.
- Once a position closes, later exits are ignored as non-executable for that lifecycle.

## 3. Normalized channels

Canonical v2 channels:

```text
CAPITAL_PROTECTION_37
TECHNICAL_DETERIORATION_40
ROUND_TRIP_42
```

Each executable candidate must contain:

```text
execution_date
execution_price
execution_source
source_version
```

## 4. Earliest causal date

For candidates on different dates, the earliest executable date on/after `entry_date` wins.

## 5. Same-session ordering

#43 may use only ordering already implied by the frozen execution sources.

Known session-open sources:
- #37 `DAILY_OHLCV_OPEN_GAP_THROUGH`
- #40 `DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_WEEK`
- #42 `DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_CLOSE`

Known later intraday convention:
- #37 `DAILY_OHLCV_STOP_CONVENTION`

Therefore:
1. one or more open-execution candidates on the same date occur before a same-date #37 stop-convention candidate;
2. if multiple open-execution candidates share the same observed open price, close once and classify convergence;
3. multiple open-execution candidates with different prices on the same date are inconsistent with one observed daily open and therefore `NOT_EVALUABLE_SOURCE_CONFLICT`;
4. any same-session combination whose ordering is not established by frozen source semantics remains `AMBIGUOUS_SAME_SESSION`;
5. no OHLC intraday path may be invented.

## 6. Terminal states

```text
NOT_OPENED
OPEN
CLOSED_CAPITAL_PROTECTION
CLOSED_TECHNICAL_DETERIORATION
CLOSED_ROUND_TRIP
CLOSED_OPEN_CONVERGENCE
AMBIGUOUS_SAME_SESSION
NOT_EVALUABLE
NOT_EVALUABLE_SOURCE_CONFLICT
```

## 7. Output contract

Persist all three upstream candidate facts plus:

```text
lifecycle_state
selected_exit_channel
selected_exit_date
selected_exit_price
selected_exit_source
converged_channels
arbitration_reason
lifecycle_version
```

## 8. Validation classes

- **L43-A lineage/version integrity**
- **L43-B no trade without executable entry**
- **L43-C earliest-date selection across three channels**
- **L43-D open-source precedence over same-date stop convention**
- **L43-E open convergence closes once**
- **L43-F conflicting open prices remain not evaluable**
- **L43-G unsupported same-session ordering remains ambiguous**
- **L43-H no exit before entry**
- **L43-I no double exit**
- **L43-J no mutation of #37/#40/#42**

Acceptance: zero semantic/causal findings.

## 9. Performance boundary

#43 makes no CAGR, expectancy, win-rate, profit-factor, or superiority claim. Primary lifecycle performance validation remains blocked until a genuine frozen `CANSLIM_ELIGIBLE` population exists.
