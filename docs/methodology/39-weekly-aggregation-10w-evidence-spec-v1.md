# #39 Weekly Aggregation / 10-Week Evidence Specification v1

Date: 2026-09-14
Status: **PREREGISTERED / EVIDENCE LAYER ONLY**

Upstream frozen authority:

- `docs/methodology/oneil-theory-fidelity-audit-v1.md` (#31)
- `docs/methodology/38-technical-deterioration-evidence-spec-v1.md`
- frozen #33/#34/#35/#36/#37/#38 contracts

## 1. Purpose

Implement a completed-week aggregation contract and a faithful 10-week moving-average evidence channel without equating it to 50 daily sessions.

#31 identifies a decisive 50-day / 10-week heavy-volume break as major institutional-selling evidence. #38 deliberately kept 10-week unimplemented until a weekly aggregation specification existed. #39 closes that data-semantic gap as an **evidence layer**, not as a newly promoted mandatory sell action.

Required order:

```text
weekly calendar semantics
-> aggregation
-> 10-week evidence
-> semantic/causal validation
-> freeze
-> only later consider action promotion
```

No outcome/performance metric may tune this contract.

## 2. Weekly calendar

Use ISO calendar weeks, Monday through Friday, identified by `(ISO year, ISO week)`.

A weekly bar is considered **completed** only when the data stream has advanced into a later ISO week. Therefore the current in-progress ISO week is excluded from completed-week evidence.

This rule is intentionally conservative and fully causal: no Monday-Thursday partial week can masquerade as a completed weekly bar.

Holiday-shortened weeks are valid completed weeks if the stream advances into a later ISO week; they do not require five trading sessions.

## 3. Weekly OHLCV aggregation

For all daily bars belonging to one completed ISO week:

```text
week_open   = first observed daily open of that ISO week
week_high   = max(daily high)
week_low    = min(daily low)
week_close  = last observed daily close of that ISO week
week_volume = sum(daily volume), if all component volumes are available
```

If any component daily volume is missing, `week_volume` is `NOT_EVALUABLE` for volume-derived evidence while price aggregation remains valid.

Persist the first and last daily dates and session count for provenance.

## 4. Ten-week line

The canonical weekly evidence line is a simple moving average of the closes of the latest 10 **completed weekly bars**:

```text
ma10w = mean(week_close of latest 10 completed weeks)
```

If fewer than 10 completed weekly bars exist:

```text
ma10w = NOT_EVALUABLE
break_10w_state = NOT_EVALUABLE
```

A 10-week break is:

```text
break_10w = latest_completed_week_close < ma10w
```

Equality is not a break.

This is an explicit weekly construction. It must never be described as equivalent to MA50 daily.

## 5. Weekly heavy-volume evidence

To preserve the theory's heavy-volume deterioration concept without inventing a new universal numeric threshold, #39 computes descriptive weekly volume context:

```text
week_volume_ratio_10 = latest_completed_week_volume / mean(volume of prior 10 completed weeks)
```

The latest completed week is excluded from the denominator.

If fewer than 11 completed weeks exist, or required weekly volumes are unavailable, the ratio is `NOT_EVALUABLE`.

#39 v1 also provides a project-consistent heavy-volume proxy using the already frozen `>=1.40x` evidence boundary:

```text
heavy_volume_break_10w = break_10w and week_volume_ratio_10 >= 1.40
```

Governance classification: **quantitative evidence proxy only**. It is not promoted to a canonical O'Neil sell action by #39.

## 6. First decisive break boundary

Theory highlights the importance of a first decisive break of the 10-week line after a sustained advance. #39 v1 preserves the chronology but does not invent a numeric definition of "sustained advance".

Persist:

```text
prior_completed_week_break_10w
first_break_10w_observed = break_10w and prior_completed_week_break_10w == FALSE
```

If the prior completed week lacks evaluable 10-week history, `first_break_10w_observed` is `NOT_EVALUABLE`.

This is chronology evidence, not proof that the discretionary theory condition "after a sustained advance" has been fully implemented.

## 7. Causality

A weekly evidence state for ISO week W becomes known only after the data stream advances into a later ISO week.

Therefore:

- weekly close/volume/MA evidence cannot be acted on during W by this daily-data reconstruction;
- no Friday-close hindsight execution is fabricated;
- any future mandatory action based on #39 must define a separate causal execution clock no earlier than the first observable session after W is known complete.

#39 itself defines no sell execution.

## 8. Output contract

Version:

`39-weekly-10w-evidence-v1`

Required output:

```text
candidate_id
security_id
asof_date
latest_completed_iso_year
latest_completed_iso_week
latest_completed_week_first_date
latest_completed_week_last_date
latest_completed_week_session_count
week_open
week_high
week_low
week_close
week_volume
completed_week_count
ma10w
break_10w_state
prior_completed_week_break_10w_state
first_break_10w_observed_state
week_volume_ratio_10
heavy_volume_break_10w_state
weekly_aggregation_version
source_technical_deterioration_version
action_promotion_state
```

Evidence vocabulary:

```text
TRUE
FALSE
NOT_EVALUABLE
```

## 9. Semantic validation classes

Before any performance work:

- **W39-A Week partition** — ISO year/week partition is correct.
- **W39-B Completed-week boundary** — current ISO week is excluded.
- **W39-C OHLC aggregation** — first open, max high, min low, last close.
- **W39-D Volume aggregation** — sum only when all component volumes exist.
- **W39-E 10-week window** — latest 10 completed weekly closes only.
- **W39-F Break boundary** — strict `<`; equality is not a break.
- **W39-G Weekly volume ratio** — latest week excluded from prior-10 denominator.
- **W39-H First-break chronology** — prior weekly state must be evaluable and false.
- **W39-I Causality** — no current partial week is consumed.
- **W39-J Daily/weekly separation** — no MA50=10w identity assumption.
- **W39-K No action promotion** — output cannot itself force a new sell action.

Acceptance criterion: **zero semantic/causal findings**.

## 10. Governance

Terminal success state:

`WEEKLY AGGREGATION + 10W EVIDENCE COMPLETE / FROZEN v1`

Any promotion of a 10-week break into a mandatory sell action requires a separate, explicitly specified action workstream. #39 may not be tuned from returns.
