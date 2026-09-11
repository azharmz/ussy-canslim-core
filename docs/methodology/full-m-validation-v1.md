# Full-M Validation v1

Status: **PRE-REGISTERED / SIDE-CAR ONLY**

Date frozen: 2026-09-11

## Purpose

Evaluate whether the already-defined dual-index CAN SLIM market-direction proxy (SPY + QQQ) changes candidate quality or portfolio outcomes relative to the frozen SPY-only baseline.

This workstream does **not** modify FWD1. FWD1 remains frozen on its SPY-only M proxy.

## Inputs

- Frozen research universe: current Musaffa-compliant snapshot frozen at 2026-08-28.
- Stock OHLCV: canonical `ussy-data` backtest histories.
- SPY benchmark pointer: `benchmarks/SPY/current.json`.
- QQQ benchmark pointer: `benchmarks/QQQ/current.json`.
- Existing technical N/S/L rules and X1/X3 execution semantics are unchanged.

## Market-state algorithm

For each benchmark independently:

1. Daily return = close / previous close - 1.
2. Distribution day = return <= -0.2% and volume > previous-session volume.
3. Distribution count = rolling 25-session count.
4. A rally attempt begins after a new 10-session low and the first subsequent positive session.
5. Follow-through proxy becomes active on rally day >=4 when daily return >= +1.0% and volume > previous-session volume.
6. An active FTD proxy is invalidated if close later falls below the rally low.

These thresholds already exist in `src/canslim_research/technical.py`; they are not tuned in this experiment.

## Comparator definitions

### M0 — frozen baseline

`M0_SPY_ONLY = spy_ftd_active AND spy_distribution_count_25 < 6`

This reproduces the current historical/FWD1 market proxy.

### M1 — dual-index full-M candidate

`M1_DUAL = (spy_ftd_active OR qqq_ftd_active) AND max(spy_distribution_count_25, qqq_distribution_count_25) < 6`

This is the exact behavior implied by the already-existing `m_label(spy_confirmed, qqq_confirmed, spy_distribution_count, qqq_distribution_count)` function.

## Primary comparison

Hold every non-M rule constant and compare M0 vs M1 on:

1. technical candidate count;
2. X3 candidate-trade count;
3. X3 trade-level profit factor and PF excluding the top 10 realized winners;
4. X3 portfolio gross CAGR and maximum drawdown under frozen PORT1 construction;
5. 20 bp round-trip cost sensitivity;
6. candidate overlap: M0-only, M1-only, both.

X1 remains a mandatory control and is reported descriptively.

## Interpretation

This is retrospective historical side-car evidence, not genuine OOS evidence. It may determine whether a future strategy version is worth preregistering, but it cannot modify the running FWD1 clock or its frozen SPY-only semantics.

No QQQ/SPY combination threshold, distribution-count threshold, or FTD threshold may be changed after outcome review within this experiment. Any such change requires a new versioned hypothesis.

## Decision rule

Do not promote M1 merely because it increases CAGR. A promotion candidate requires evidence that the dual-index definition provides a coherent improvement in candidate/trade quality without materially worsening drawdown/concentration and that the result is not driven solely by a small M1-only subset.

Any eventual forward validation of M1 must start a new independently versioned forward clock.
