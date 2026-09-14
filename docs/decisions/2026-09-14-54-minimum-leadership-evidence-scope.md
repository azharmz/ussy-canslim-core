# #54 Decision — Minimum Leadership Evidence Scope

Date: 2026-09-14

Status: **SCOPE CORRECTED / FULL-MARKET OHLCV RECONSTRUCTION DEFERRED**

## Decision

The project will **not** build or maintain a full ~7,500-security broad-market OHLCV panel merely to reproduce a project approximation of IBD's proprietary Relative Strength Rating.

The earlier Cycle 1 cross-sectional selector remains a valid frozen **research-only experiment**, but its broad-market OHLCV dependency is no longer a production prerequisite. Existing Cycle 1 files and audit evidence are retained for provenance; they are not deleted or rewritten.

## Authoritative distinction

The project now explicitly separates three concepts that must not be conflated:

1. **IBD Relative Strength Rating** — a proprietary cross-sectional rating comparing a stock's price performance with other stocks. Reproducing this requires a broad stock database and is not necessary for this project's minimum theory-fidelity production scope.
2. **Relative Strength line** — stock price performance relative to the S&P 500. IBD/O'Neil educational material uses the S&P 500 comparison and treats a rising/new-high RS line as leadership evidence. This is reproducible from the stock universe already under study plus the canonical S&P 500 benchmark.
3. **Industry-group leadership** — O'Neil/IBD treats strong industry groups as important context for leading stocks. This is more granular than broad sector classification. A sector ETF is therefore **not** adopted as a required CAN SLIM leadership input merely because sector-ETF benchmarking is useful in another project.

## Minimum viable #54 leadership evidence

For the CAN SLIM project, the next implementation/research path should use evidence already defensible without reconstructing the whole U.S. stock market:

- stock-level RS line versus the canonical `SP500` benchmark;
- RS-line direction/state and, where reproducibly defined, RS-line new-high evidence;
- existing frozen price/new-high, breakout, and technical evidence where applicable;
- institutional demand/selling only when a separate PIT-valid evidence source/calculation is defensible.

This minimum path does **not** claim equivalence to `IBD_RS_RATING`.

## Sector ETF decision

Sector ETFs are **NOT REQUIRED** for the CAN SLIM leadership contract.

They may remain useful in other frameworks (for example, sector-relative Trend Following research), but they are not inserted into CAN SLIM merely for convenience. O'Neil/IBD industry-group analysis is a distinct and more granular concept than stock-versus-sector-ETF relative strength.

If a future CAN SLIM study proposes sector ETFs, it must be a separately preregistered evidence experiment and must not be represented as a direct substitute for IBD industry-group rankings.

## What happens to #53 and Cycle 1

#53 remains useful as a prospective PIT broad-market membership archive, but it does not force the project to maintain price histories for every member.

`54-cycle1-candidate-leader-selector-v1` remains frozen as research history. Its current `BLOCKED_ON_BROAD_MARKET_OHLCV` result is preserved, but the blocker is **DEFERRED / NON-BLOCKING FOR MINIMUM CAN SLIM v1**.

The Tiingo/Yahoo broad-market provider audits remain evidence of the rejected/high-cost architecture path. No production broad-market OHLCV publisher should be built from those audits unless governance explicitly reopens that path.

## Production boundary

This decision does not modify frozen #46, #45, #51, #52, or #53 semantics.

Until institutional-demand/weakening evidence is separately approved, #50 must continue to preserve unavailable leadership booleans as `None` rather than fabricate confirmation.

## Terminal decision

**FULL-MARKET OHLCV / PROJECT RS-PERCENTILE REPLICATION: DEFERRED, NON-BLOCKING**

**SECTOR-ETF BENCHMARK FOR CAN SLIM: NOT REQUIRED**

**NEXT #54 PATH: MINIMUM REPRODUCIBLE RS-LINE EVIDENCE VS CANONICAL S&P 500 + SEPARATE PIT INSTITUTIONAL-DEMAND EVIDENCE IF DEFENSIBLE**
