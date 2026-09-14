# #46 Market State Evidence / Classification — Specification v1

Date: 2026-09-14
Status: PREREGISTERED BEFORE IMPLEMENTATION
Contract: `46-market-state-classification-v1`

## Purpose

Produce a point-in-time, reproducible general-market state that can feed frozen #45 market-exposure action without changing #45.

This module classifies market evidence. It does not place trades, liquidate stock positions, or optimize exposure from returns.

## Authoritative semantics frozen for v1

1. `CORRECTION` is the defensive/downtrend state.
2. A rally attempt begins only after correction when a major index posts the first qualifying up-close session. That session is rally Day 1.
3. The rally attempt remains intact only while the Day-1 low is not undercut. An undercut resets the attempt and returns the index to correction.
4. A follow-through day can confirm an uptrend only on rally Day 4 or later.
5. For reproducibility, v1 uses the current IBD quantitative follow-through floor: index close gain >= 1.25% versus the prior close and current volume > prior-session volume.
6. A distribution day during an uptrend is an index decline >= 0.20% versus prior close on volume > prior-session volume.
7. Distribution is evidence of institutional selling and weakening, but distribution count alone is not treated as a complete market classifier because authoritative guidance also considers leadership and index action around key moving averages.
8. After follow-through, market strength must be confirmed incrementally. v1 therefore separates `FOLLOW_THROUGH_CONFIRMED` from later `UPTREND_HEALTHY`.
9. `UPTREND_WEAKENING` requires explicit weakening evidence supplied to the classifier; v1 does not invent a universal distribution-count threshold.

## Major-index aggregation

Each tracked major index maintains its own rally chronology and follow-through state. The portfolio market state is based on available major-index evidence:

- any index with a valid current follow-through can establish `FOLLOW_THROUGH_CONFIRMED` unless explicit weakening evidence overrides it;
- correction/rally-attempt chronology remains per-index;
- missing one index must not fabricate its state;
- if no index has sufficient evaluable evidence, output `NOT_EVALUABLE`.

The canonical index set is an input contract, not hard-coded ticker symbols in this module. Production wiring must declare the exact index series and data source separately.

## Leadership / weakening inputs

Because authoritative market assessment uses more than distribution count, v1 accepts explicit PIT booleans:

- `leadership_confirming`: leading CAN SLIM stocks are providing confirming breakouts/strength;
- `weakening_confirmed`: upstream evidence has established material weakening from distribution/index/leadership evidence.

These inputs must carry their own provenance in production. #46 does not derive arbitrary thresholds for them.

State transition semantics:

```text
CORRECTION
  -> RALLY_ATTEMPT on valid Day 1
RALLY_ATTEMPT
  -> CORRECTION if Day-1 low is undercut
  -> FOLLOW_THROUGH_CONFIRMED on valid Day >=4 FTD
FOLLOW_THROUGH_CONFIRMED
  -> UPTREND_HEALTHY when leadership_confirming == TRUE
  -> UPTREND_WEAKENING when weakening_confirmed == TRUE
UPTREND_HEALTHY
  -> UPTREND_WEAKENING when weakening_confirmed == TRUE
UPTREND_WEAKENING
  -> CORRECTION only when an explicit correction reset is supplied
```

`weakening_confirmed` has precedence over `leadership_confirming` on the same completed session.

## Causality

All price/volume classifications for date D are known only after D close. #46 may update the market state after D close; it must not backdate the state into D intraday.

## Explicit non-claims

- No return/CAGR/win-rate tuning.
- No fixed distribution-day count is invented as an automatic correction threshold.
- No moving-average threshold is invented here.
- No breadth threshold is invented here.
- No stock-level exit is created.
- #45 remains frozen and consumes the resulting state only after it exists.
