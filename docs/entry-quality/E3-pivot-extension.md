# E3 — Signal Pivot Extension

Status: **PLANNED**

## Question

Does limiting how far the T0 signal close is above the breakout pivot improve robustness?

## Primary variable

```text
signal_pivot_extension = close_T0 / pivot - 1
```

## Pre-specified variants

- <= 3%
- <= 5%
- <= 8%
- baseline with no extension cap

These thresholds were specified before the expanded-universe backtest. Do not re-label another threshold as the primary result after observing CAGR/PF.

## Metrics

Compare:

- trade count;
- profit factor;
- PF excluding top 10 trades;
- total/portfolio return as appropriate;
- max drawdown;
- MAE/MFE;
- stop rate;
- subperiod stability;
- sector and symbol concentration.

## Interpretation

This study addresses signal-time chasing. It does **not** fully solve execution-time chasing because H+1 may gap substantially after a non-extended T0 signal. That is handled separately by E4.
