# #35 Independent Historical Corpus v1

Date: 2026-09-13
Status: PREREGISTERED / IN PROGRESS

This document defines the independent historical corpus for #35 candidate-semantic validation. It is separate from performance research and must not be used to tune frozen #33 morphology or #34 candidate rules.

Primary historical source: `ussy-data/backtest/ohlcv/{security_id}.parquet`.

Core production patterns only:
- FLAT_BASE
- DOUBLE_BOTTOM
- CUP_WITHOUT_HANDLE
- CUP_WITH_HANDLE

P6 advanced patterns remain excluded.

## Independence rule

Selection must not use future returns, CAGR, PF, win rate, breakout success/failure, or later winner/loser status. Future-performance fields must not appear in the sampling table.

## Fixed as-of calendar

Use quarter-end anchors from 2021-03-31 through 2025-12-31. For each anchor, use the latest completed trading session on or before that date. The initial corpus excludes 2026.