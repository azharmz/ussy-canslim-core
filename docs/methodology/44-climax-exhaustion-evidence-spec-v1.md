# #44 Climax / Exhaustion Evidence Specification v1

Date: 2026-09-14
Status: **FROZEN FOR IMPLEMENTATION**

Contract: `44-climax-exhaustion-evidence-v1`

Upstream frozen authority:
- #37 sell/risk theory boundary
- #39 completed-week aggregation semantics
- #43 lifecycle v2 remains unchanged
- EXH2 remains separate prospective research and is not canonical O'Neil climax logic

## 1. Purpose

Represent reproducible O'Neil climax/exhaustion evidence without prematurely promoting a new sell action.

Authoritative material describes climax tops as occurring after a substantial prior advance and identifies several observable signatures: largest daily price run-up of the move, heaviest daily volume of the move, exhaustion gaps after a long advance, rapid runs such as 7 of 8 or 8 of 10 up days, and unusually large weekly price spreads. The evidence is contextual and multi-signal, so #44 freezes evidence only.

## 2. Governance boundary

- No EXH1/EXH2 threshold is imported into #44.
- No historical return metric may choose thresholds.
- No mandatory sell action is emitted.
- #37/#40/#42/#43 remain frozen and unchanged.
- A later action module must explicitly specify which evidence combinations are sufficient and causal.

## 3. Daily evidence

For each completed daily session after breakout, persist:

```text
daily_point_change = close - prior_close
is_up_day = close > prior_close
largest_up_day_point_gain_since_breakout
heaviest_daily_volume_since_breakout
up_days_last_8
up_days_last_10
seven_of_eight_up_days
 eight_of_ten_up_days
exhaustion_gap_raw = low > prior_high
```

`largest_up_day_point_gain_since_breakout` is TRUE only on an up day whose close-to-close point gain is strictly greater than every prior up-day point gain since breakout.

`heaviest_daily_volume_since_breakout` is TRUE only when current volume is strictly greater than every prior evaluable daily volume since breakout.

`seven_of_eight_up_days` requires 8 completed sessions and at least 7 up days.

`eight_of_ten_up_days` requires 10 completed sessions and at least 8 up days.

`exhaustion_gap_raw` is a structural gap evidence field only. It does not by itself assert that the prior-advance maturity condition is satisfied.

## 4. Weekly evidence

Using the frozen #39 completed-week concept, persist when weekly bars are supplied:

```text
weekly_range = week_high - week_low
largest_weekly_range_since_breakout
```

This is descriptive evidence. No percentage normalization or extra threshold is invented in v1.

## 5. Prior-advance context

Authoritative sources describe climax/exhaustion as occurring after a long/substantial advance. Some exhaustion-gap examples distinguish roughly 18+ weeks from first/second-stage bases versus 12+ weeks from later-stage bases.

Because the current frozen production pattern contract does not provide a canonical base-stage lineage sufficient to apply that distinction universally, #44 persists:

```text
completed_sessions_since_breakout
completed_weeks_since_breakout
prior_advance_context_state = CONTEXT_RECORDED_NOT_ACTIONABLE
```

No universal 12- or 18-week action gate is created in #44.

## 6. Evidence-only state

Canonical action promotion field:

`action_promotion_state = EVIDENCE_ONLY_NO_CANONICAL_SELL_ACTION`

EXH2 remains a separate prospective diagnostic with its own extreme-shock and T+1 rejection definitions. It must not be relabelled as #44.

## 7. Validation classes

- C44-A contract/version integrity
- C44-B strict largest-up-day boundary
- C44-C strict heaviest-volume boundary
- C44-D 7-of-8 chronology
- C44-E 8-of-10 chronology
- C44-F raw exhaustion-gap definition
- C44-G weekly-range evidence
- C44-H insufficient-history handling
- C44-I no action promotion
- C44-J EXH2 independence

Acceptance: zero semantic findings.
