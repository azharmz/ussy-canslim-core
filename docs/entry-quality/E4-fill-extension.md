# E4 — Actual Fill Pivot Extension

Status: **PLANNED**

## Question

How far above the breakout pivot is the price the strategy can actually buy at H+1 open, and does excessive fill-time extension degrade expectancy?

## Primary variable

```text
fill_pivot_extension = open_H1 / pivot - 1
```

## Why it is separate from E3

A T0 signal can be close to the pivot and still become badly extended because H+1 gaps up. Conversely, a T0 signal can look extended and H+1 can open lower.

Therefore signal-time extension and executable-fill extension must be measured separately.

## Analysis

Relate fill extension to:

- realized return;
- MAE/MFE;
- stop-loss rate;
- trend-exit rate;
- holding period;
- T-1 -> T0 move;
- T0 -> H+1 gap;
- PF and PF ex-top10 for any tested rule.

## Guardrail

Do not assume the E3 3/5/8% thresholds automatically apply to E4. First characterize the distribution and interaction. Any fill-time threshold must be specified under a separate protocol and validated out-of-sample.
