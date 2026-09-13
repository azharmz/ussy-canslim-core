# #37 Theory-Faithful Sell / Risk Execution Specification v1

Date: 2026-09-14
Status: **FROZEN FOR IMPLEMENTATION**

Upstream frozen authority:

- `docs/methodology/oneil-theory-fidelity-audit-v1.md` (#31)
- `docs/methodology/36-execution-entry-spec-v1.md`
- `docs/decisions/2026-09-14-36-theory-vs-execution-boundary-clarification.md`
- frozen #33/#34/#35 contracts

## 1. Purpose

Define a downstream sell/risk state machine for positions created by a frozen entry contract without rewriting candidate identity, entry semantics, or prior validation evidence.

Required order:

```text
frozen theory semantics
-> explicit sell/risk specification
-> implementation
-> semantic/causal validation
-> only then performance research
```

Legacy `execution-exit-v1.md`, X1-X4/X3, PORT1 and EXH2 remain historical/prospective evidence. They are not automatically promoted into this theory-faithful #37 contract.

## 2. Three-layer boundary

### A. O'Neil / CAN SLIM sell-risk semantics

Theory-derived concepts:

- maximum-loss discipline measured from actual purchase/fill price;
- current practical defensive trigger around -7%;
- historical/legacy absolute-loss language around -7% to -8%;
- failed-breakout / early deterioration evidence;
- 50-day / 10-week heavy-volume deterioration as major institutional-selling evidence;
- normal +20% to +25% profit-management zone measured from the proper buy point;
- eight-week hold exception for unusually fast winners reaching about +20% within the first 1-3 weeks after breakout;
- round-trip behavior after a meaningful gain;
- climax/exhaustion as contextual late-stage evidence rather than a single fixed threshold;
- market-level exposure reduction separate from stock-level sell state.

### B. Information boundary

Daily bars are only complete after the session closes. Any sell state depending on completed daily close/volume/MA evidence becomes actionable no earlier than the next causal execution clock unless an intraday price rule is independently observable from OHLC (for example a stop/gap condition).

### C. Backtest execution convention

Execution clocks such as next-session open, same-bar stop handling, or gap-through handling are implementation conventions. They must never be labelled as O'Neil terminology.

## 3. Core position inputs

#37 consumes an already executed position and must preserve:

```text
candidate_id
security_id
pattern
pivot_level
breakout_date
entry_date
fill_price
entry_execution_version
source_candidate_version
```

#37 must not mutate #33 morphology, #34 eligibility, #35 evidence, or #36 fill history.

## 4. Capital-protection state

Reference is actual fill price.

Persist:

```text
practical_loss_trigger_price = fill_price * 0.93
legacy_hard_loss_ceiling_price = fill_price * 0.92
loss_from_fill_pct
```

Classification:

```text
LOSS_OK
PRACTICAL_7PCT_TRIGGER_REACHED
LEGACY_8PCT_CEILING_BREACHED
```

The ~7% practical trigger is the canonical defensive action threshold for v1 implementation. The 8% level is preserved as historical/legacy ceiling evidence, not as permission to wait past a triggered 7% exit.

Gap-through handling must never fabricate a fill at the stop level: if the next observable market open is below the defensive threshold, execution uses the observed open.

## 5. Failed-breakout / deterioration evidence

Preserve independently:

```text
fell_back_below_pivot
loss_from_fill_pct
break_10d
break_21d
break_50d
break_10w_proxy
heavy_volume_break
largest_down_volume_since_breakout
```

These are evidence channels, not substitutes for the universal maximum-loss discipline.

A decisive 50d/10w heavy-volume break may become a major sell state only if its exact daily-EOD semantics are implemented and validated separately from the hard-loss rule.

## 6. Normal profit zone

Reference is proper buy point / pivot, not actual fill.

```text
normal_profit_zone_low = pivot_level * 1.20
normal_profit_zone_high = pivot_level * 1.25
profit_from_buy_point_pct
profit_from_fill_pct
```

State vocabulary:

```text
BELOW_NORMAL_PROFIT_ZONE
IN_NORMAL_PROFIT_ZONE
ABOVE_NORMAL_PROFIT_ZONE
```

Entering the +20% to +25% zone is **profit-management evidence**, not an automatic full liquidation rule in #37 v1.

Legacy `execution-exit-v1.md` used a deterministic `pivot * 1.20` full target for an old research baseline. That behavior is explicitly **not** canonical #37 theory semantics.

## 7. Eight-week exceptional-winner state

Preserve chronology from breakout, not from arbitrary backtest labels.

```text
reached_20pct_within_first_3_weeks
eight_week_hold_exception_active
eight_week_assessment_date
```

For daily data, "first 3 weeks" is represented as the first 15 completed market sessions after breakout. "Eight weeks" is represented as 40 completed market sessions after breakout for the mechanical assessment clock.

These session counts are implementation calendar conventions for daily-data reproducibility, not claims that O'Neil theory is expressed as T+15/T+40 terminology.

The exceptional-winner state does not override the practical maximum-loss discipline or severe technical deterioration.

## 8. Round-trip state

Preserve:

```text
max_gain_from_fill_pct
max_gain_from_buy_point_pct
round_trip_to_buy_point
```

A round-trip condition requires that the position first achieved a meaningful gain and subsequently returned to or below the proper buy point. #37 v1 records the state but does not invent a new numeric "meaningful gain" threshold beyond theory-supported evidence. Until authoritative numeric semantics are frozen, the round-trip sell trigger remains `EVIDENCE_ONLY / NOT_FULLY_IMPLEMENTED`.

## 9. Climax / exhaustion boundary

Climax-top behavior is contextual and late-stage. #37 v1 does **not** convert EXH2 or any single percentage threshold into canonical O'Neil climax detection.

Preserve available evidence fields where computable, but classify canonical climax detection as:

`NOT_IMPLEMENTED / REQUIRES SEPARATE AUTHORITATIVE SPECIFICATION`

EXH2 remains separate prospective research and cannot be relabelled as #37.

## 10. Market-level risk boundary

Stock-level state and market exposure remain separate:

```text
stock_sell_state
market_exposure_state
```

A weakening M state may justify reduced exposure, fewer new buys, or tighter risk, but #37 v1 does not force automatic liquidation of every open stock merely from a market-state change without a separately frozen exposure contract.

## 11. Position sizing and event risk

Position sizing, portfolio risk budget, earnings-event handling, options mechanics, slippage and transaction costs are distinct contracts. #37 must not silently optimize them through sell-state logic.

## 12. Canonical v1 action hierarchy

For the initial implementation target:

```text
1. PRACTICAL_7PCT_TRIGGER_REACHED -> defensive exit required
2. LEGACY_8PCT_CEILING_BREACHED -> integrity/severity evidence; should never be the planned first trigger
3. normal profit-zone state -> management evidence, not mandatory full exit
4. eight-week exceptional-winner state -> hold/assessment context
5. technical deterioration -> evidence channel until exact executable rule is frozen
6. round-trip -> evidence-only until exact numeric precondition is frozen
7. climax/exhaustion -> not implemented in canonical #37 v1
8. market exposure -> separate portfolio-level state
```

## 13. Daily-OHLC execution conventions

For the v1 defensive stop only:

- if session open is already below the practical 7% trigger, exit at observed open;
- otherwise if session low reaches/crosses the practical trigger, a stop-level fill may be represented at the trigger price as a mechanical daily-OHLC stop convention;
- this same-bar convention must be labelled `BACKTEST_EXECUTION_CONVENTION`, not theory semantics;
- no synthetic profit-target fill is created because +20%-25% is not a mandatory full-exit rule.

Any ambiguity involving multiple sell conditions on the same daily bar must be preserved explicitly rather than resolved optimistically.

## 14. Required output contract

Version:

`37-sell-risk-v1`

Required fields include:

```text
candidate_id
security_id
entry_date
fill_price
pivot_level
asof_date
loss_from_fill_pct
practical_loss_trigger_price
legacy_hard_loss_ceiling_price
capital_protection_state
fell_back_below_pivot
profit_from_buy_point_pct
profit_from_fill_pct
normal_profit_zone_state
reached_20pct_within_first_3_weeks
eight_week_hold_exception_active
eight_week_assessment_date
max_gain_from_fill_pct
max_gain_from_buy_point_pct
round_trip_to_buy_point
technical_deterioration_state
climax_state
market_exposure_state
sell_action_state
sell_execution_date
sell_execution_price
sell_execution_source
sell_risk_version
source_entry_version
```

## 15. Semantic validation classes

```text
S37-A contract/schema
S37-B actual-fill loss-reference
S37-C gap-through defensive execution
S37-D pivot-reference profit zone
S37-E exceptional-winner chronology
S37-F theory-vs-execution terminology boundary
S37-G no upstream mutation / no EXH2 relabelling
```

Acceptance criterion before any performance study: zero semantic findings.

## 16. Explicitly deferred

- automatic full exit at +20% or +25%;
- optimization between 7% and 8%;
- arbitrary time stop;
- exact tactical 10d/21d sell trigger;
- exact 50d/10w heavy-volume execution trigger until separately frozen;
- numeric round-trip precondition not supported by frozen authoritative evidence;
- canonical climax detector;
- market-wide forced liquidation rule;
- earnings/options execution;
- position sizing optimization;
- performance-selected sell thresholds.

## 17. Governance freeze

This specification freezes the initial #37 implementation target as a **sell/risk state machine**, not a simplistic stop-and-target strategy.

The only mandatory v1 stock-level executable action is the practical ~7% capital-protection trigger referenced to actual fill, with causal gap-through handling. Other theory-derived states are preserved without silently converting them into unsupported deterministic exits.