# #45 Market Exposure Action Semantics v1

Date: 2026-09-14
Status: **FROZEN FOR IMPLEMENTATION**

Contract: `45-market-exposure-action-v1`

## Purpose

Formalize the CAN SLIM `M` / general-market layer as a portfolio-exposure action contract. This is intentionally separate from stock-level exits (#37/#40/#42) and lifecycle arbitration (#43).

## Authoritative boundary

O'Neil/IBD market-direction guidance supports:
- most stocks tend to follow the general market;
- corrections call for defensive posture / cash and avoiding new buys;
- a follow-through day is the green light to begin buying leading stocks again;
- re-entry should be gradual rather than an immediate jump to full exposure;
- modern IBD guidance expresses market risk with five exposure bands: 0-20%, 20-40%, 40-60%, 60-80%, 80-100%;
- distribution, index behavior, leadership and trade feedback can reduce exposure.

The exact current IBD exposure recommendation is editorial/dynamic. #45 therefore freezes the **exposure vocabulary and action semantics**, not a reverse-engineered proprietary classifier.

## Exposure bands

```text
E0 = 0-20
E1 = 20-40
E2 = 40-60
E3 = 60-80
E4 = 80-100
```

These are portfolio target ranges, not per-position sizing rules.

## Market states

```text
CORRECTION
RALLY_ATTEMPT
FOLLOW_THROUGH_CONFIRMED
UPTREND_HEALTHY
UPTREND_WEAKENING
NOT_EVALUABLE
```

## Canonical actions

```text
HOLD_EXPOSURE
RAISE_ONE_BAND
REDUCE_ONE_BAND
RESET_TO_E0
NOT_EVALUABLE
```

### Correction

`CORRECTION` maps to `RESET_TO_E0`. It blocks new CAN SLIM entries at the portfolio gate while preserving independent stock-level sell rules. #45 does not fabricate immediate liquidation of every holding.

### Rally attempt

`RALLY_ATTEMPT` keeps exposure at E0. A rally attempt by itself is not permission to resume normal buying.

### Follow-through

`FOLLOW_THROUGH_CONFIRMED` permits a single-band increase from E0 to E1. This captures gradual re-engagement after a follow-through rather than jumping from cash to full exposure.

### Healthy uptrend

`UPTREND_HEALTHY` may raise exposure by at most one band per evaluated market observation, capped at E4. This is an exposure-management action, not a stock-selection signal.

### Weakening uptrend

`UPTREND_WEAKENING` reduces exposure by one band, floored at E0. The state may be informed upstream by distribution, index technical damage, weakening leaders or poor trade feedback, but #45 does not invent a proprietary numeric classifier for those inputs.

## Separation from stock lifecycle

#45 does not:
- rewrite #36 entry prices;
- rewrite #37/#40/#42 exits;
- enter #43 as a fourth stock-level exit;
- automatically liquidate all positions when exposure is reduced;
- specify which individual holding must be sold to reach a lower target band.

A later portfolio executor may translate target exposure into position-level actions under a separately frozen contract.

## Causality

A market-state observation is actionable only after the evidence defining that state is available. #45 accepts an already-causal market-state observation and emits the next target band. It does not backdate exposure changes.

## Output

```text
asof_date
market_state
prior_exposure_band
action
target_exposure_band
new_entries_allowed
reason
market_action_version
```

## Semantic validation

- M45-A version/vocabulary
- M45-B correction resets to E0
- M45-C rally attempt stays E0
- M45-D follow-through re-enters only to E1 from E0
- M45-E healthy uptrend rises at most one band and caps E4
- M45-F weakening uptrend falls one band and floors E0
- M45-G correction/rally attempt block new entries
- M45-H no stock-level exit is emitted
- M45-I NOT_EVALUABLE remains explicit

Acceptance: zero semantic findings.

## Performance boundary

No historical return metric may select or tune the exposure bands, transitions, or market-state definitions in #45. The contract operationalizes authoritative exposure-management semantics only.