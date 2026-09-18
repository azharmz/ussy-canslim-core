# Historical backtest data binding v1

Date: 2026-09-18
Status: PARTIAL BINDING / FAIL CLOSED ON M

## Stock OHLCV — RESOLVED

Use the already-frozen #35 historical source:

`backtest/ohlcv/{security_id}.parquet`

Authority: `docs/decisions/2026-09-13-35-historical-ohlcv-source.md`.

Semantics:
- Yahoo full daily history, `auto_adjust=False`;
- raw OHLCV for #33 morphology/pivot/breakout/volume;
- `adj_close` for RS/L;
- no ad-hoc provider fetch inside the backtest runner.

This removes H1 from the 2026-09-18 readiness audit.

## Fundamental population — RESOLVED

Use artifact from workflow run `35175083156`, especially `ca_pass_by_decision_date.csv`, digest-bound to the run artifact. It yields 515 PASS security-date rows across five intervals and three securities.

## I — SOURCE CONTRACT EXISTS

Historical I is governed by the existing SEC 13F historical event-state contract. Backtest attachment must use historical availability semantics, never current live state retroactively. Until the concrete R2 historical event object is resolved and validated at runtime, I remains fail-closed.

## L — COMPUTABLE FROM FROZEN HISTORICAL INPUTS

The #35 OHLCV decision explicitly freezes `adj_close` for L/RS. The backtest may compute the already-governed RS/leadership evidence only through the existing frozen adapter and canonical S&P 500 input; it must not invent a new L threshold.

## M — STILL BLOCKING

The long-history canonical-index remediation artifact explicitly publishes `historical_replay_authorized: false`. Therefore it is not authorized as historical M input. No trade signal may be labelled full `CANSLIM_ELIGIBLE` until a governed historical-M replay contract is explicitly authorized.

## Minimal next run

The first one-interval run can now safely exercise:

`fundamental dates -> backtest/ohlcv prefix -> pinned #33 -> N/S`

and separately attach available L/I/M evidence. It must stop before #36 execution whenever any mandatory letter is NOT_EVALUABLE.

No performance metrics are authorized at this stage.
