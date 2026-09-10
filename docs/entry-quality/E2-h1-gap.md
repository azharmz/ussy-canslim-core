# E2 — H+1 Execution Gap

Status: **PLANNED**

## Question

How much does the gap from the T0 signal close to the realistic H+1 open affect subsequent expectancy and drawdown?

## Motivation

The strategy can only act after the T0 close. A valid signal can therefore become materially more expensive by the H+1 open even when T0 itself was not unusually extended.

## Primary variable

```text
h1_gap = open_H1 / close_T0 - 1
```

## Analysis

Relate H+1 gap size to:

- realized return;
- MAE and MFE;
- stop-loss probability;
- trend-exit probability;
- holding period;
- actual extension from pivot at fill;
- PF and PF ex-top10 for any tested rule.

## Guardrail

Do not substitute Trigger/T0 close for executable price when evaluating realized entry quality. The purpose of this study is to preserve execution realism.
