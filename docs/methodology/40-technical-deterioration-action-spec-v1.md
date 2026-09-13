# #40 Technical Deterioration Action Specification v1

Date: 2026-09-14
Status: **FROZEN FOR IMPLEMENTATION**

Upstream frozen authority:

- `docs/methodology/oneil-theory-fidelity-audit-v1.md` (#31)
- `docs/methodology/37-theory-faithful-sell-risk-spec-v1.md`
- `docs/methodology/38-technical-deterioration-evidence-spec-v1.md`
- `docs/methodology/39-weekly-10w-evidence-spec-v1.md`
- frozen #33/#34/#35/#36/#37/#38/#39 contracts

Authoritative interpretation used for this action contract:

- a weekly close below the 10-week line on above-average/heavy volume is a major sell signal / evidence of institutional selling;
- a low-volume first close below the 10-week line is not automatically a mandatory sell;
- therefore the action rule must combine a 10-week break with a volume condition rather than converting every weekly break into an exit.

## 1. Purpose

Promote one narrowly specified technical-deterioration condition from frozen weekly evidence into a canonical stock-level sell action, without modifying the universal #37 capital-protection rule.

Required order:

```text
frozen evidence
-> explicit action semantics
-> causal execution convention
-> semantic validation
-> freeze
-> only then any performance research
```

No historical return metric may alter the rule after freeze.

## 2. Action trigger

Canonical v1 deterioration trigger:

```text
completed_week.break_10w_state == TRUE
AND completed_week.weekly_volume_ratio_prior10 > 1.00
```

Interpretation:

- price condition: completed weekly close is strictly below the frozen 10-week moving average;
- volume condition: completed weekly volume is strictly above the mean volume of the prior 10 completed weeks;
- equality to the MA is not a break;
- equality to average weekly volume is not "above-average volume" and therefore does not trigger the canonical action.

This is the only #40 v1 mandatory deterioration trigger.

## 3. Why `> 1.00`, not the #38 `>=1.40` proxy

#38's `>=1.40x` daily volume boundary is preserved as a project-consistent evidence proxy inherited from breakout-volume work. It is not promoted into the weekly O'Neil sell rule.

The authoritative weekly sell wording is above-average / huge-volume deterioration. For the reproducible canonical v1 weekly action, "above average" is represented literally as:

```text
weekly_volume > mean(prior 10 completed weekly volumes)
```

No optimization against returns is used.

## 4. Non-trigger states

No mandatory #40 deterioration action when any of the following applies:

```text
close >= ma10w
weekly_volume_ratio_prior10 <= 1.00
break_10w_state == NOT_EVALUABLE
weekly_volume_ratio_prior10 == NOT_EVALUABLE
```

A low-volume close below the 10-week line remains deterioration evidence but does not force the #40 canonical action.

## 5. First-break / repeated-break semantics

#40 v1 acts on the first completed week after entry that satisfies the full combined trigger.

Persist:

```text
first_actionable_10w_break_week
```

A prior low-volume break does not consume the action opportunity. If a later completed week again closes below the 10-week line and volume is above average, that later week can become the first actionable deterioration week.

Once the canonical #40 sell action has executed, later deterioration states are not additional exits for the same position.

## 6. Interaction with #37 capital protection

#37 practical ~7% capital protection remains independent and has priority whenever it produces an earlier causal exit.

#40 must never delay or override an already-triggered #37 defensive exit.

For a complete position lifecycle, the earliest causal exit among frozen action contracts governs. #40 itself does not rewrite #37 execution history.

## 7. Information boundary

The weekly close, weekly volume, and completed 10-week MA for week W are known only after W's final trading session completes.

Therefore the #40 deterioration action becomes known after week W closes.

No fill may be backdated into W.

## 8. Canonical execution clock

The canonical daily-OHLC backtest execution convention is:

```text
signal_week = completed actionable week W
execution_date = first observed trading session after W
fill_price = that session's observed open
```

This next-session-open convention is an implementation/causality rule, not O'Neil terminology.

If no later trading-session bar exists:

```text
NO_NEXT_SESSION_BAR
```

No synthetic weekend, Friday-close, MA-level, or intraday fill is created.

## 9. Action vocabulary

```text
NO_ACTION
TECHNICAL_DETERIORATION_EXIT_REQUIRED
NO_NEXT_SESSION_BAR
NOT_EVALUABLE
```

Execution source when filled:

```text
DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_WEEK
```

## 10. Required output contract

Version:

`40-technical-deterioration-action-v1`

Required fields:

```text
candidate_id
security_id
entry_date
fill_price
source_sell_risk_version
source_daily_deterioration_version
source_weekly_evidence_version
signal_week_start
signal_week_end
signal_week_close
signal_week_ma10w
signal_week_volume
signal_week_volume_ratio_prior10
action_state
execution_date
execution_price
execution_source
action_version
```

## 11. Semantic validation classes

Before performance inspection:

- **A40-A Contract/lineage** — exact frozen source versions preserved.
- **A40-B Trigger price boundary** — only `close < ma10w` qualifies.
- **A40-C Trigger volume boundary** — only ratio strictly `>1.00` qualifies.
- **A40-D Missing evidence** — missing MA/volume history never coerced into action.
- **A40-E Low-volume break** — break with ratio `<=1.00` remains no mandatory action.
- **A40-F First actionable chronology** — earlier non-actionable break does not block later actionable break.
- **A40-G Causality** — execution strictly after signal week completion.
- **A40-H Observed fill** — fill equals observed next-session open.
- **A40-I No synthetic fill** — missing next bar remains explicit.
- **A40-J #37 independence** — no change to hard-stop thresholds or fill history.

Acceptance: zero semantic/causal findings.

## 12. Performance boundary

#40 semantic validation is not evidence that the exit improves returns. Historical performance remains closed until separately preregistered, and any such result cannot retroactively tune this frozen action rule.
