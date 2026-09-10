# Entry Timing Basis Test v1

Status: **PRE-SPECIFIED BEFORE COMPARATIVE PERFORMANCE REVIEW**

Purpose: determine how a completed daily-EOD breakout signal should be translated into an executable CAN SLIM-style entry without look-ahead.

## Information timing

The T0 breakout and full-session T0 volume are only known after the T0 close in the daily-EOD pipeline. Therefore T0-close fills are not treated as executable. The earliest clean executable fill is T+1 Open.

This is a quantitative data-availability constraint, not a claim that discretionary O'Neil CAN SLIM requires waiting until T+1.

## Frozen comparison variants

### X1 — Immediate T+1 control

Enter at T+1 Open only when:

```text
pivot < Open_T+1 <= 1.05 * pivot
```

### X2 — First valid Open through T+3

Check T+1, T+2, T+3 Opens in order. Enter the first Open inside the same buy zone. No close-based confirmation is required.

### X3 — Pivot-hold confirmation

A confirmation may occur on T+1 or T+2. The daily bar must hold fully above the pivot:

```text
Low_day > pivot
AND pivot < Close_day <= 1.05 * pivot
```

Because the Close is only known after that session ends, entry occurs at the following Open, which must itself remain in the buy zone. Latest possible entry is T+3.

### X4 — Retest-and-hold proxy

A confirmation may occur on T+1 or T+2. The session must revisit the pivot neighborhood and close back above it:

```text
Low_day <= 1.02 * pivot
AND pivot < Close_day <= 1.05 * pivot
```

Entry occurs at the following Open and that Open must remain within the 5% buy zone. Latest possible entry is T+3.

The +2% retest neighborhood is a pre-specified quantitative proxy for this basis test. It must not be tuned using the result of this test.

## Common exit/risk rules

To isolate entry timing, all variants use identical trade management:

```text
hard stop = actual fill * 0.93
profit target = pivot * 1.20
gap-through = actual session Open
same-bar stop+target ambiguity = stop first
no arbitrary time stop
```

One active position per security is retained independently within each variant.

## Primary diagnostics

- candidate count;
- fill count and fill rate;
- entry delay distribution;
- actual fill extension from pivot;
- missed-opportunity count;
- MFE/MAE;
- stop rate;
- target rate;
- trade-level expectancy/median return;
- descriptive trade-level PF.

Portfolio return and max drawdown are not computed in this basis test.

## Research-universe interpretation

The research universe is the set of securities **currently/frozen compliant at the selected Musaffa snapshot**. Historical Musaffa compliance is not an input to the strategy question being tested. Historical OHLCV and decision inputs remain causal; SEC fundamentals, when attached later, must obey `accepted_at` point-in-time constraints.

The result should therefore be described as historical behavior of the frozen current-compliant research universe, not as a reconstruction of historical Musaffa eligibility.
