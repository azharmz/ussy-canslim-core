# #36 Theory-Faithful Execution / Entry Specification v1

Date: 2026-09-14
Status: FROZEN FOR IMPLEMENTATION

Upstream frozen authority:

- `docs/methodology/oneil-theory-fidelity-audit-v1.md` (#27/#28/#31)
- `docs/methodology/theory-faithful-candidate-spec-v1.md` (#32)
- #33 pattern contract `oneil-pattern-output-v2`
- #34 candidate generator `34-candidate-generator-v0.2`
- #35 terminal validation decision

## 1. Purpose

Define how a frozen theory-faithful candidate becomes an executable daily-EOD trading entry without rewriting pattern identity, pivot identity, breakout identity, CAN SLIM eligibility, or the frozen #35 validation corpus.

Required order remains:

```text
frozen candidate semantics
-> execution specification
-> implementation
-> validation
-> only then performance research
```

No rule in this document was selected from CAGR, profit factor, win rate, future return, or the frozen #35 validation corpus.

## 2. Hard architectural boundary

#36 consumes #34 output. It does not modify it.

```text
#33 morphology/pivot          FROZEN
#34 qualification/staging     FROZEN
#35 validation                FROZEN
            |
            v
#36 execution / entry
```

The following remain upstream facts and must not be recomputed by #36:

```text
candidate_id
base_id / lineage
pattern
pattern_status
pivot_level
structural_end
breakout_date / first crossing chronology
volume confirmation
C / A / L / M states
candidate_stage
```

P6 advanced patterns remain outside production.

## 3. Causal daily-EOD boundary

The canonical #34 candidate is evaluated using the completed daily bar at signal date `T`.

Therefore information such as:

- T close;
- T volume;
- T strong-volume confirmation;
- final C/A/L/M eligibility state at T;

is not available for a causal fill earlier during the same session.

Canonical #36 rule:

```text
signal_date = T
information_available_after = T close
first_executable_session = next completed market session after T
canonical_entry_clock = T+1 OPEN
```

Same-day/T fills based on a completed T bar are prohibited in this daily-EOD contract because they would be hindsight fills.

This does not claim that discretionary O'Neil traders cannot buy during a breakout session. It is a data/causality rule for this implementation.

## 4. Entry opening gate

#36 may open an entry only when the frozen candidate state at T is:

```text
candidate_stage == CANSLIM_ELIGIBLE
```

For the current #34 contract this already requires:

```text
BREAKOUT_CONFIRMED
C == PASS
A == PASS
L == PASS/STRONG
M == ALLOW_NEW_BUYS
```

#36 must not relax those gates.

A candidate below `CANSLIM_ELIGIBLE` may still be retained as evidence but receives:

```text
execution_state = NOT_ENTRY_ELIGIBLE
```

## 5. Traditional buy-zone contract

The structural pivot remains the upstream #33/#34 pivot.

Canonical traditional buy zone:

```text
buy_zone_floor = pivot_level
buy_zone_ceiling = pivot_level * 1.05
```

The 5% ceiling is execution/anti-chasing semantics, not breakout identity.

At T+1 open:

```text
open_extension_pct = (T1_open / pivot_level) - 1
```

Canonical T+1 decision:

```text
if pivot_level <= T1_open <= pivot_level * 1.05:
    EXECUTED_T1_OPEN
elif T1_open > pivot_level * 1.05:
    MISSED_EXTENDED_AT_OPEN
elif T1_open < pivot_level:
    BELOW_PIVOT_AT_OPEN
```

A breakout is not invalidated merely because execution is missed.

## 6. Gap handling

Preserve gap state explicitly.

```text
T1_open > prior_close
T1_open > pivot_level
```

A gap that opens above the pivot but remains at or below +5% may still be executed at the actual T+1 open under the canonical baseline.

A T+1 open above +5% is not chased:

```text
execution_state = MISSED_EXTENDED_AT_OPEN
fill_price = NULL
```

Do not fabricate a fill at the +5% boundary when the market opens above it.

## 7. Below-pivot / retrace handling

If T+1 opens below the pivot, the canonical T+1-open baseline does not fabricate an entry:

```text
execution_state = BELOW_PIVOT_AT_OPEN
fill_price = NULL
```

A later pivot reclaim, pullback/retest entry, buy-stop entry, or delayed entry is a legitimate separate research question, but it is **not** silently folded into the canonical baseline.

Any delayed/retest variant must be preregistered with:

- allowed delay window;
- order type;
- exact trigger;
- fill assumptions;
- gap behavior;
- cancellation rule;
- handling of ambiguous daily-bar order chronology.

Those variants must be compared as execution variants, not used to rewrite #33/#34 candidate quality.

## 8. Fill-price contract

For canonical baseline executions:

```text
fill_date = T+1 session date
fill_price = observed T+1 open
fill_source = DAILY_OHLCV_OPEN
slippage_model = NONE_IN_SEMANTIC_VALIDATION
```

No synthetic intraday price is allowed in the semantic-validation phase.

Transaction costs/slippage belong to later performance research and must be versioned separately.

## 9. Initial risk semantics from frozen #31

Capital protection references the **actual fill price**, not the chart pivot.

Persist:

```text
initial_stop_reference = fill_price
practical_loss_trigger_price = fill_price * 0.93
legacy_hard_loss_ceiling_price = fill_price * 0.92
```

Interpretation:

- ~7% is the current practical defensive trigger carried from #31;
- 7%-8% is preserved as the historical/legacy absolute-loss language;
- #36 v1 records these levels but does not yet claim a complete sell-engine implementation.

A later sell engine must preserve actual-fill chronology, gaps through stops, and technical sell evidence separately.

## 10. Profit-reference semantics from frozen #31

The normal offensive profit zone is referenced to the proper buy point/pivot, not silently to the actual fill:

```text
normal_profit_zone_low = pivot_level * 1.20
normal_profit_zone_high = pivot_level * 1.25
```

Persist separately:

```text
profit_from_buy_point
profit_from_actual_fill
```

The +20%-25% zone is profit-management guidance, not a mandatory full liquidation rule.

The eight-week exceptional-winner hold rule, round-trip behavior, 50d/10w deterioration, climax behavior, and market-level exposure reduction remain downstream sell/risk states. They are not entry-selection variables.

## 11. Required output contract

Version:

```text
36-execution-entry-v1
```

Required fields:

```text
candidate_id
security_id
signal_date
candidate_stage
pivot_level
next_session_date
next_open
buy_zone_floor
buy_zone_ceiling
open_extension_pct
gap_above_pivot
execution_state
fill_date
fill_price
fill_source
initial_stop_reference
practical_loss_trigger_price
legacy_hard_loss_ceiling_price
normal_profit_zone_low
normal_profit_zone_high
execution_version
source_candidate_version
```

Canonical execution-state vocabulary:

```text
NOT_ENTRY_ELIGIBLE
NO_NEXT_SESSION_BAR
EXECUTED_T1_OPEN
MISSED_EXTENDED_AT_OPEN
BELOW_PIVOT_AT_OPEN
NOT_EVALUABLE
```

## 12. Semantic invariants

The validator must reject records violating any of these:

1. `EXECUTED_T1_OPEN` without upstream `CANSLIM_ELIGIBLE`.
2. fill date not strictly after signal date.
3. fill price different from observed T+1 open for canonical baseline.
4. fill below pivot or above +5% for `EXECUTED_T1_OPEN`.
5. non-null fill for `MISSED_EXTENDED_AT_OPEN` or `BELOW_PIVOT_AT_OPEN`.
6. stop reference based on pivot instead of actual fill.
7. profit-zone reference based on fill instead of proper buy point/pivot.
8. P6 advanced pattern consumption.
9. any use of future bars to alter T execution eligibility.
10. any mutation/reclassification of #33/#34 fields.

## 13. Validation protocol before performance testing

#36 implementation validation must be semantic/causal first.

Required test classes:

```text
E36-A contract/schema validation
E36-B causality/date validation
E36-C buy-zone boundary validation
E36-D gap/extended/below-pivot validation
E36-E actual-fill stop-reference validation
E36-F pivot-reference profit-zone validation
```

Boundary fixtures must include at least:

- open exactly at pivot;
- open just above pivot;
- open exactly +5%;
- open above +5%;
- gap within buy zone;
- open below pivot;
- no T+1 bar;
- non-eligible upstream candidate.

Acceptance criterion is zero semantic findings. Trading returns are explicitly excluded from implementation acceptance.

## 14. Explicitly deferred from v1

Not authorized as silent defaults:

- same-day hindsight fills;
- T+2/T+3 arbitrary waiting windows;
- retest bands such as +1%, +2%, etc.;
- limit-order fills inferred from daily bars without order assumptions;
- intraday breakaway-gap protocols;
- performance-selected entry timing;
- position sizing percentages;
- full sell-engine implementation;
- earnings/options mechanics.

Existing X1-X4/X3 work remains frozen historical execution research and must not be relabeled as this theory-faithful #36 contract.

## 15. Governance freeze

This specification freezes the first #36 implementation target:

`CANSLIM_ELIGIBLE at T -> causal T+1-open execution if and only if the observed open is within the structural pivot through +5% traditional buy zone.`

Any extension must be versioned and preregistered before outcome inspection.
