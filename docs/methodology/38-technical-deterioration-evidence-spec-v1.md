# #38 Technical Deterioration Evidence Specification v1

Date: 2026-09-14
Status: **PREREGISTERED / EVIDENCE LAYER ONLY**

Upstream frozen authority:

- `docs/methodology/oneil-theory-fidelity-audit-v1.md` (#31)
- `docs/methodology/37-theory-faithful-sell-risk-spec-v1.md`
- frozen #33/#34/#35/#36/#37 contracts

## 1. Purpose

Implement the next downstream sell/risk evidence layer without changing frozen #37 action semantics.

#31 explicitly preserves failed-breakout / early-deterioration evidence and identifies a decisive 50-day / 10-week heavy-volume break as major institutional-selling evidence. #37 intentionally left exact executable technical-deterioration rules unimplemented pending a separate frozen specification.

#38 therefore begins as an **evidence computation and semantic-validation workstream**, not a performance-selected exit strategy.

Required order:

```text
authoritative frozen theory
-> evidence definitions
-> implementation
-> semantic/causal validation
-> independent evidence review
-> only then consider any action-state promotion
```

No return/CAGR/PF/win-rate result may be used to choose or tune #38 definitions.

## 2. Non-negotiable boundaries

#38 must not modify:

- #33 morphology;
- #34 candidate eligibility;
- #35 validation corpus/evidence;
- #36 entry/fill history;
- #37 practical ~7% capital-protection trigger;
- #37 +20%-25% profit-zone semantics;
- #37 eight-week exceptional-winner semantics;
- FWD1, X1-X4/X3, PORT1, or EXH2;
- P6 production exclusion.

#38 must not promote a technical-evidence condition into a mandatory sell action merely because historical returns look favorable.

## 3. Evidence channels

For every completed daily bar after entry, preserve independently:

```text
close
volume
ma10
ma21
ma50
fell_back_below_pivot
break_10d
break_21d
break_50d
volume_ratio_50
heavy_volume_break_10d
heavy_volume_break_21d
heavy_volume_break_50d
largest_down_volume_since_breakout
```

The 10-day and 21-day channels are tactical/early-warning evidence. The 50-day channel is the principal daily-data proxy for the theory's 50-day/10-week institutional-deterioration concept.

## 4. Moving-average semantics

For daily reproducibility:

```text
ma10  = arithmetic mean of closes over current completed session and prior 9 completed sessions
ma21  = arithmetic mean of closes over current completed session and prior 20 completed sessions
ma50  = arithmetic mean of closes over current completed session and prior 49 completed sessions
```

A break state is evaluated only after the current daily bar is complete:

```text
break_10d = close < ma10
break_21d = close < ma21
break_50d = close < ma50
```

Equality is not a break.

If the required completed-session history is unavailable, the corresponding state is `NOT_EVALUABLE`, never coerced to false/pass.

These daily moving-average calculations are reproducibility conventions. They do not claim that all O'Neil/IBD discretionary interpretation is reducible to one daily close comparison.

## 5. 10-week boundary

The theory references the 10-week line. A faithful weekly implementation requires an explicitly specified completed-week calendar and weekly aggregation contract.

#38 v1 therefore does **not** silently equate `10 weeks == 50 daily sessions` as an exact theory identity.

Persist:

```text
break_10w_state = NOT_IMPLEMENTED_REQUIRES_WEEKLY_AGGREGATION_SPEC
```

The daily `break_50d` channel remains available as its own evidence.

## 6. Heavy-volume evidence

The already frozen project convention for strong volume uses prior 50 completed sessions as a reference window. #38 reuses that existing volume-ratio convention only as an evidence measurement; it does not claim a new universal O'Neil sell threshold.

```text
volume_ratio_50 = current_volume / mean(volume of prior 50 completed sessions)
```

If prior 50 completed sessions are unavailable or unusable:

```text
volume_ratio_50 = NOT_EVALUABLE
```

For #38 v1, preserve heavy-volume break evidence at the already frozen `>=1.40x` volume-confirmation boundary:

```text
heavy_volume_break_10d = break_10d and volume_ratio_50 >= 1.40
heavy_volume_break_21d = break_21d and volume_ratio_50 >= 1.40
heavy_volume_break_50d = break_50d and volume_ratio_50 >= 1.40
```

**Governance classification:** this is a project-consistent quantitative evidence proxy, not a newly asserted authoritative universal sell threshold. It may not be promoted to a canonical mandatory exit without separate authoritative/action validation.

## 7. Largest down-volume evidence

Preserve whether the current completed session is a down session and whether its volume is the largest observed down-session volume since breakout:

```text
down_session = close < prior_close
largest_down_volume_since_breakout =
    down_session and current_volume >= max(volume of prior down sessions since breakout)
```

If there is no prior completed down session since breakout, the first down session may be marked as the current largest observation, with observation count preserved.

This field is descriptive evidence; it is not independently a mandatory exit.

## 8. Failed-breakout evidence

Preserve independently:

```text
fell_back_below_pivot = close < pivot_level
loss_from_fill_pct
```

A fall below pivot does not replace the frozen #37 capital-protection rule. It is an additional technical-warning channel.

## 9. Causality

All close/volume/MA-based #38 evidence for session D is known only after D closes.

Therefore:

- it may update evidence state at D close;
- it may not fabricate an intraday sell before the evidence existed;
- any future action contract based on this evidence must execute no earlier than a separately specified causal clock after D close.

#38 v1 does not define that action clock because it does not yet promote evidence to mandatory sell actions.

## 10. Output contract

Version:

`38-technical-deterioration-evidence-v1`

Required fields:

```text
candidate_id
security_id
breakout_date
entry_date
fill_price
pivot_level
asof_date
close
volume
ma10
ma21
ma50
break_10d_state
break_21d_state
break_50d_state
break_10w_state
volume_ratio_50
heavy_volume_break_10d_state
heavy_volume_break_21d_state
heavy_volume_break_50d_state
down_session
largest_down_volume_since_breakout
down_session_observation_count
fell_back_below_pivot
loss_from_fill_pct
technical_deterioration_version
source_sell_risk_version
```

Tri-state evidence vocabulary where history/data can be missing:

```text
TRUE
FALSE
NOT_EVALUABLE
```

## 11. Semantic validation classes

Before any outcome/performance research:

- **T38-A Contract** — required fields/version/source lineage.
- **T38-B MA windows** — exact completed-session 10/21/50 close windows.
- **T38-C Break boundaries** — `< MA` is break; equality is not.
- **T38-D Volume chronology** — current volume excluded from prior-50 denominator.
- **T38-E Heavy-volume proxy** — only break + evaluable ratio >=1.40 may classify TRUE.
- **T38-F Missing history** — insufficient history yields NOT_EVALUABLE.
- **T38-G Down-volume chronology** — only information through current completed session.
- **T38-H Pivot/fill references** — pivot evidence uses pivot; loss evidence uses actual fill.
- **T38-I Weekly boundary** — 10-week remains explicitly unimplemented until weekly spec exists.
- **T38-J No action promotion** — #38 output cannot itself force a new canonical sell action.

Acceptance criterion: **zero semantic/causal findings**.

## 12. Terminal possibilities

After implementation and semantic validation, #38 may terminate as:

```text
EVIDENCE LAYER COMPLETE / FROZEN
```

A later mandatory technical-deterioration sell action requires a separate workstream and explicit authoritative/action specification. It must not be inferred from favorable historical outcomes.
