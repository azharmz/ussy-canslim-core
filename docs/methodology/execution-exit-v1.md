# CAN SLIM Execution & Exit Baseline v1 — FROZEN

Status: **FROZEN BEFORE TRADING-PERFORMANCE TESTING**

Date: 2026-09-10

This document defines a deterministic execution/exit baseline for the independent CAN SLIM research track. It does **not** inherit TrendFoll's ATR stop, EMA20 exit, or 45-session time stop.

## 1. Entry timing

A technical candidate is identified after the T0 close. With daily data, the earliest non-look-ahead executable price is **H+1 open**.

However, H+1 open is **not automatically filled**.

### H+1 executable buy-zone rule

Entry is allowed only when:

```text
pivot < Open_H+1 <= pivot * 1.05
```

If `Open_H+1 > pivot * 1.05`, the candidate is skipped as `ABOVE_BUY_ZONE_AT_FILL`.

If `Open_H+1 <= pivot`, the candidate is skipped as `BELOW_PIVOT_AT_FILL`.

This makes actual execution respect the same 5% CAN SLIM buy zone used at signal construction and directly prevents an H+1 gap from turning a valid T0 breakout into an overextended chase.

No intraday wait/re-entry logic is assumed in v1 because only daily OHLCV is available.

## 2. Purchase price

For an accepted entry:

```text
entry_price = Open_H+1
```

This is the actual price from which loss risk is measured.

## 3. Hard loss rule

Primary v1 defensive exit:

```text
hard_stop = entry_price * 0.93
```

That is a **7% maximum loss from the actual purchase price**. IBD commonly describes the classic rule as 7%-8% and current educational material often operationalizes it at 7%.

No ATR-based widening is allowed in v1.

## 4. Primary profit-taking rule

IBD describes the normal profit-taking zone as roughly 20%-25% above the ideal buy point. For a deterministic primary baseline, v1 uses the **lower edge** of that pre-existing zone:

```text
profit_target = pivot * 1.20
```

The target is measured from the ideal buy point/pivot, not from the actual H+1 fill.

This choice is pre-specified before performance testing and must not be moved within the 20%-25% zone based on observed PF/CAGR.

## 5. Intraday execution from daily OHLC

For every session after entry, including the entry session:

1. if `Low <= hard_stop`, exit at `hard_stop`;
2. else if `High >= profit_target`, exit at `profit_target`;
3. otherwise remain open.

If a daily bar touches both stop and target, OHLC does not reveal intraday ordering. **v1 resolves the ambiguity stop-first**, which is deliberately conservative and avoids optimistic sequencing.

Gap-through handling:

- if the session opens below the hard stop, exit at the session open rather than at the higher stop price;
- if the session opens above the profit target, exit at the session open rather than at the lower target price.

## 6. No arbitrary time stop in v1

The independent CAN SLIM primary baseline does **not** inherit TrendFoll's 45-session exit.

A position that reaches neither hard stop nor profit target remains open. At the research sample boundary it is marked `CENSORED_OPEN`, with mark-to-market reported separately from realized-trade PF.

## 7. Eight-week hold rule

The O'Neil/IBD eight-week hold rule is a real part of the method: a stock that gains about 20% within the first three weeks after breakout may deserve at least an eight-week hold.

It is **not silently approximated in primary v1** because 'assess the chart after eight weeks' requires an additional deterministic sell proxy. It is registered as a pre-specified follow-up exit variant, not a post-hoc rescue if v1 performance is weak.

Planned variant:

```text
X2_EIGHT_WEEK_HOLD
```

Primary v1 remains `X1_7PCT_STOP_20PCT_PIVOT_TARGET`.

## 8. Market direction

M-v1 gates new entries. A later change in M does not automatically liquidate an existing position in execution v1. Market-triggered liquidation may be tested only as a separately specified variant.

## 9. Relationship to Entry Quality E1-E4

Execution v1 explicitly records:

- T-1 -> T0 move;
- T0 close -> H+1 open gap;
- T0 extension from pivot;
- H+1 fill extension from pivot;
- skip reason when H+1 is outside the buy zone.

Thus the legacy H+1 chasing problem becomes an observable execution mechanism rather than an implicit assumption.

## 10. Anti-data-mining boundary

The following are frozen before trading-performance evaluation:

- actual H+1 fill must remain inside the 0%-5% buy zone;
- 7% hard stop from actual fill;
- 20% primary target from pivot;
- stop-first resolution for same-bar ambiguity;
- no arbitrary time stop.

Any change after results are observed must receive a new version/experiment ID.
