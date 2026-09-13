# #41 Position Lifecycle / Exit Arbiter Specification v1

Date: 2026-09-14
Status: **FROZEN FOR IMPLEMENTATION**

Contract: `41-position-lifecycle-exit-arbiter-v1`

Upstream frozen authority:
- `36-execution-entry-v1`
- `37-sell-risk-v1`
- `40-technical-deterioration-action-v1`

## 1. Purpose

Create one deterministic position lifecycle from the frozen entry fill and the two currently canonical executable exit channels. #41 does not invent a sell rule. It only resolves competing already-frozen executable exits by chronology.

```text
#36 executable fill
-> OPEN POSITION
-> #37 defensive capital-protection exit candidate
   OR #40 technical-deterioration exit candidate
-> earliest causal executable exit
-> CLOSED POSITION
```

## 2. Non-negotiable boundaries

#41 must not change #33-#40 semantics, thresholds, evidence, clocks, or source records. In particular:
- #37 practical ~7% stop remains referenced to actual fill;
- #37 gap-through and stop-convention prices remain unchanged;
- #40 action remains completed 10-week break + above-average weekly volume, executed at the first later daily open;
- no performance result may alter arbitration;
- no second exit may occur after the position is closed.

## 3. Source eligibility

A lifecycle can be opened only from an actually executed #36 entry. Required entry facts:

```text
entry_date
fill_price
source_entry_version
```

If there is no executable entry/fill, lifecycle state is `NOT_OPENED` and downstream exit candidates must not fabricate a trade.

## 4. Exit candidate normalization

Normalize each upstream executable exit into:

```text
exit_channel
execution_date
execution_price
execution_source
source_version
```

Canonical channels in v1:
- `CAPITAL_PROTECTION_37`
- `TECHNICAL_DETERIORATION_40`

Only exit candidates with a concrete execution date and price are executable.

## 5. Earliest causal exit

For an open position, choose the executable exit with the earliest `execution_date` strictly on or after `entry_date`.

```text
selected_exit = min(executable_exit_candidates, key=execution_date)
```

If no executable candidate exists, lifecycle remains `OPEN`.

## 6. Same-session collision

If #37 and #40 have the same execution date, #41 must not infer an unsupported intraday ordering from daily OHLCV.

For the currently frozen contracts:
- #40 executes at that session's observed open;
- #37 may execute at the same observed open when the session opens through the stop, or later via the daily low stop convention.

Therefore same-session arbitration is:
1. if both upstream candidates execute at the same observed open price, classify `SAME_OPEN_CONVERGENCE` and close once at that price;
2. if #40 is at the session open while #37 is a later stop-convention fill, select #40 because the open is causally earlier;
3. any other same-date ordering that cannot be established from frozen source semantics is `AMBIGUOUS_SAME_SESSION` and must not be resolved optimistically.

No close/high/low ordering may be invented.

## 7. Terminal lifecycle states

```text
NOT_OPENED
OPEN
CLOSED_CAPITAL_PROTECTION
CLOSED_TECHNICAL_DETERIORATION
CLOSED_SAME_OPEN_CONVERGENCE
AMBIGUOUS_SAME_SESSION
NOT_EVALUABLE
```

## 8. Output contract

Required fields:

```text
candidate_id
security_id
entry_date
fill_price
source_entry_version
capital_exit_date
capital_exit_price
capital_exit_source
source_sell_risk_version
technical_exit_date
technical_exit_price
technical_exit_source
source_technical_action_version
lifecycle_state
selected_exit_channel
selected_exit_date
selected_exit_price
selected_exit_source
arbitration_reason
lifecycle_version
```

## 9. Validation classes

- **L41-A Contract/version lineage**
- **L41-B No trade without executable entry**
- **L41-C Earliest-date selection**
- **L41-D Same-open convergence closes once**
- **L41-E Open-before-stop same-day ordering**
- **L41-F Ambiguous same-session ordering remains explicit**
- **L41-G No exit before entry**
- **L41-H No double exit**
- **L41-I No upstream mutation**

Acceptance: zero semantic/causal findings.

## 10. Performance boundary

#41 is lifecycle semantics only. It must not calculate or optimize CAGR, profit factor, win rate, expectancy, or exit thresholds. Primary strategy-performance validation remains blocked until a genuine frozen `CANSLIM_ELIGIBLE` population exists.
