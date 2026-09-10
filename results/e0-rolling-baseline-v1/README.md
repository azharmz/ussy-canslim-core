# E0 Rolling Baseline v1 — Validated Smoke Evidence

Date: 2026-09-10

Workflow run: `34432960298`
Artifact: `e0-rolling-baseline-v1-34432960298`

## Evidence class

**ROLLING_CURRENT_MEMBERSHIP_SMOKE_NOT_FULL_PIT_BACKTEST**

This run validates that the frozen independent CAN SLIM technical baseline can be executed end-to-end against the expanded `ussy-data` R2 contract. It is **not** a historical performance backtest and must not be used for PF/CAGR/drawdown claims.

## Pinned inputs

- Ready pointer: `production/ready/current.json`
- Ready snapshot date: `2026-08-28`
- Ready parquet: `production/ready/runs/2ef1b2ca8f9f44aba62d0552884e06c6.parquet`
- Ready SHA256: `c1ed91508642acd604e73f2cb79cf8027fd91ea644acab0bb806cf7e12f237a4`
- SPY pointer: `benchmarks/SPY/current.json`
- SPY parquet: `benchmarks/SPY/runs/97aa9dd852e743da93cc611c6d58c3cb.parquet`
- SPY SHA256: `1fb495068c5392108cde7d49d4dae8e1d842dde0b01e29af8f64e477525350d4`

## Results

- ready securities: **1,223**
- ready rows: **366,411**
- rolling price span: **2025-05-16 to 2026-09-08**
- feature-evaluable rows after 252-day RS warm-up: **58,216**
- feature-evaluable dates: **77**
- exact technical candidate rows: **14**
- candidate symbols: **13**
- candidate dates: **7**

Component PASS rows among feature-evaluable rows:

| Component | PASS rows |
|---|---:|
| Price >= $15 | 37,071 |
| N-price | 1,878 |
| S-volume | 6,236 |
| L-RS | 11,691 |
| M (SPY-only smoke proxy) | 12,183 |

## Entry-quality diagnostics retained

Candidate evidence records, without filtering on them:

- T-1 -> T0 move
- T0 close -> H+1 open gap
- T0 extension from pivot
- H+1 actual-fill extension from pivot

These feed E1-E4 later. They are not tuned thresholds in E0.

## Limitations / non-claims

1. The ready export uses current active compliant membership and then exposes rolling historical bars. Retroactive membership is therefore not PIT-historical.
2. Ready OHLCV is capped at 300 bars per security; 252-day RS leaves only 77 evaluable dates in this snapshot.
3. M is SPY-only because `ussy-data` currently exposes no QQQ benchmark R2 contract.
4. No PnL, PF, CAGR, max drawdown, or strategy verdict is permitted from this run.

## Verdict

**PASS as implementation/data-contract smoke evidence. NOT sufficient as E0 historical strategy evidence.**

Next dependency: audit `universe/membership/*` coverage and use full `backtest/ohlcv/{security_id}.parquet` objects for the longest defensible PIT-universe window.
