# E1 — Signal-Day Shock

Status: **PLANNED**

## Question

Does an unusually large T-1 -> T0 price move increase the probability of retracement, stop-out, or weak expectancy after the realistic H+1 entry?

## Motivation

Legacy walk-forward observations include several large T0 moves followed by poor outcomes. These observations define a hypothesis only; they must not be used to fit a threshold.

## Primary variable

```text
signal_day_return = close_T0 / close_T-1 - 1
```

## Analysis

Treat the variable continuously and in pre-declared descriptive buckets first. Relate it to:

- realized return;
- MAE;
- MFE;
- stop-loss rate;
- trend-exit rate;
- holding period;
- PF and PF ex-top10 when tested as a rule.

## Guardrail

Do not derive a production threshold from the small legacy walk-forward sample. Any candidate threshold requires a pre-specified research protocol and holdout validation.
