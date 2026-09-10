# C/A PIT Labels v1 — Implementation Contract

Status: **IMPLEMENTATION READY**

This layer interprets frozen C-v1 and A-v1 specifications. It must not modify `ussy-fundamentals` extraction semantics.

## C-v1

For the latest usable fiscal quarter known at decision cutoff:

- EPS YoY >= 25%; and
- revenue YoY >= 25%.

Both must be evaluable. Missing/undefined is `NOT_EVALUABLE`, never 0%.

## A-v1

Use the latest three consecutive evaluable annual EPS YoY observations known at decision cutoff. Each must be >=25%.

`PASS_3Y_FALLBACK` remains evaluable but carries a separate history tier. Missing/undefined annual growth is `NOT_EVALUABLE`.

## PIT contract

Only facts with `accepted_at <= decision_cutoff` may contribute. The consumer must resolve `fundamentals/current.json` to an immutable snapshot and record snapshot identity + manifest checksum for reproducibility.

## Distribution gate before backtest

First run is descriptive only. Report C/A PASS/FAIL/NOT_EVALUABLE counts, reason codes, readiness cross-tabs, sector distribution, and history-depth distribution. Do not compute CAGR, PF, return, drawdown, or trade-conditioned outcomes in this stage.

## Freeze boundary

Any semantic change after this point becomes a new version (C-v2/A-v2 or label-contract v2). Do not silently alter v1 after seeing trading performance.
