# #54 — Minimum RS-Line Evidence v1

Date: 2026-09-14
Status: **PREREGISTERED / EVIDENCE-ONLY / NO PRODUCTION BOOLEAN**
Contract: `54-rs-line-evidence-v1`

## Purpose

Implement the minimum reproducible relative-strength evidence authorized by the #54 scope correction without reconstructing a ~7,500-security market database and without pretending to reproduce IBD's proprietary Relative Strength Rating.

## Authoritative anchor

IBD educational material distinguishes the Relative Strength line from the Relative Strength Rating. The RS line compares a stock's price performance with the S&P 500; a rising line means the stock is outperforming the benchmark, and an RS line reaching a new high is treated as bullish leadership evidence.

This contract implements only that transparent ratio relationship. It does not implement or approximate `IBD_RS_RATING`.

## Benchmark

The benchmark identity is the frozen canonical `SP500` from #47. An ETF identity such as `SPY` is not accepted as the canonical benchmark for this contract.

## Input contract

The caller supplies an already point-in-time-safe, date-aligned sequence through `asof_date` containing:

- session date;
- stock price;
- canonical S&P 500 price;
- stock source/provenance identity;
- benchmark source/provenance identity;
- declared input-window identity.

All prices must be positive. Dates must be unique, strictly increasing, and the final date must equal `asof_date`. The module does not fetch or align data itself.

The price basis must be internally consistent and declared by the caller. This evidence layer does not silently mix adjusted stock prices with a differently interpreted benchmark series.

## RS-line calculation

For each aligned session `t`:

`rs_line[t] = stock_price[t] / sp500_price[t]`

The absolute scale is arbitrary; only its evolution matters.

The v1 evidence packet reports:

- latest RS-line value;
- previous RS-line value;
- `direction_vs_prior`: `RISING`, `FALLING`, or `FLAT` using exact arithmetic comparison with no invented tolerance threshold;
- `at_input_window_high`: whether the latest RS-line value equals or exceeds every earlier value in the supplied declared window;
- `new_input_window_high`: whether the latest RS-line value is strictly greater than every earlier value in that window.

No fixed 52-week/252-session RS-line-high lookback is claimed by this contract. The caller must declare the supplied window identity. A later study may preregister a fixed lookback if authoritative evidence or a separately governed research convention justifies it.

## Missing-data behavior

Fewer than two aligned observations, invalid/nonpositive prices, duplicate/nonmonotonic dates, a final date different from `asof_date`, missing provenance, a noncanonical benchmark identity, or an undeclared input window produce `NOT_EVALUABLE` with explicit reason codes. They are not converted to weak/negative leadership.

## Governance boundary

This contract is stock-level evidence only.

It does **not**:

- change frozen #34 L semantics;
- replace #34's frozen RS-percentile adapter;
- change #51 broad-market leadership/weakening semantics;
- set #46 `leadership_confirming` or `weakening_confirmed`;
- infer institutional accumulation or selling;
- require sector ETFs;
- require #53 broad-market OHLCV;
- change FWD1/X3/EXH2;
- use future returns.

The restricted USSY/Musaffa universe may be evaluated stock-by-stock with this RS line because the calculation is stock versus canonical S&P 500, but observations from that restricted universe may not be promoted into a broad-market #51 boolean without a separately valid contract.

## Promotion boundary

Passing RS-line evidence is supportive leadership evidence, not a complete CAN SLIM `L` or general-market `M` decision by itself. Institutional-demand/selling evidence remains separate validation debt.

Terminal preregistration status:

**MINIMUM RS-LINE EVIDENCE DEFINED / NO FULL-MARKET PANEL REQUIRED / NO SECTOR ETF REQUIRED / NO #51 BOOLEAN AUTHORIZED**
