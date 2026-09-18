# Historical M scope correction for FA-first backtest

Date: 2026-09-18
Status: **FROZEN INTERPRETATION / NO NEW M RULE**

## Finding

The historical major-index OHLCV is mechanically sufficient for causal replay of frozen `46-market-state-classification-v1`, but the existing #51 contract intentionally leaves `leadership_confirming` and `weakening_confirmed` unavailable when no governed broad-market leadership source exists.

That missing auxiliary evidence must **not** be converted into invented False values, and it must not be used to manufacture `UPTREND_HEALTHY` or `UPTREND_WEAKENING`.

However, frozen #46 itself already supports index-derived states without those optional auxiliary inputs. In particular, `FOLLOW_THROUGH_CONFIRMED` is an emitted frozen state and frozen #50 maps it to `ALLOW_NEW_BUYS`.

## Backtest interpretation

For historical dates:

- replay canonical NASDAQ Composite, S&P 500 and DJIA bars causally;
- initialize prior state as `NOT_EVALUABLE`;
- pass `leadership_confirming=None`;
- pass `weakening_confirmed=None`;
- do not fabricate `correction_reset`;
- preserve the exact frozen #46 state/reason;
- map the emitted state through frozen #50 entry semantics.

This does **not** claim a complete reconstruction of discretionary O'Neil market interpretation. It is the reproducible subset already implemented by frozen #46/#50.

## Important limitation

Without governed historical #51 evidence, the replay cannot produce evidence-backed promotions/demotions that require those auxiliary channels. Reports must label M provenance as:

`HISTORICAL_INDEX_ONLY_FROZEN_46_REPLAY`

and retain the missing #51 evidence limitation.

This correction supersedes the overly broad statement in `fa-first-historical-data-binding-v1.md` that all historical M must be NOT_EVALUABLE merely because auxiliary evidence is unavailable. No classifier threshold or transition is changed.
