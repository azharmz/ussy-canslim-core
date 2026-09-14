# #46 Market State Evidence / Classification v1 — Freeze Decision

Date: 2026-09-14
Status: **IMPLEMENTATION COMPLETE / FROZEN v1**

Contract: `46-market-state-classification-v1`

## Frozen semantics

- Rally Day 1 begins on the first qualifying major-index up-close after correction.
- Strict undercut of Day-1 low resets the rally attempt.
- Follow-through requires rally Day 4 or later, close gain >=1.25%, and volume greater than the prior session.
- Distribution evidence is a decline >=0.20% on volume greater than the prior session.
- Distribution evidence alone does not invent a universal weakening/correction count threshold.
- Leadership confirmation can promote `FOLLOW_THROUGH_CONFIRMED` to `UPTREND_HEALTHY`.
- Explicit PIT weakening evidence can produce `UPTREND_WEAKENING` and takes precedence over same-session leadership confirmation.
- Explicit correction reset produces `CORRECTION`.
- No stock-level exit or exposure percentage is generated here; frozen #45 consumes the resulting market state.
- All state changes based on daily price/volume are known after the completed session close.

## Validation

Initial run `34803646653` exposed an implementation-only rally-day off-by-one plus floating exact-boundary issue. The preregistered semantics were not changed.

Fix commit: `cc20bdfb35433b5afacf2d8a51ee56acc76b682e`.

Canonical run:
- run `34803676270`
- job `103851194650`
- result **SUCCESS**
- **13 passed in 0.02s**

## Remaining production wiring boundary

The classifier intentionally does not hard-code index tickers or data provider. A separate integration contract must declare the exact major-index OHLCV series and provenance used in production. Leadership/weakening booleans likewise require PIT provenance and may not be fabricated from future outcomes.
