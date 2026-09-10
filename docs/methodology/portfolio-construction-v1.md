# Portfolio Construction v1 — Pre-registration

Date frozen: 2026-09-10

Status: FROZEN BEFORE PORTFOLIO OUTCOME REVIEW

## Purpose

Convert the already-frozen trade/execution rules into a capital-constrained portfolio so CAGR/return and maximum drawdown can be computed without conflating trade-level PF with portfolio performance.

This specification is independent of `ussy-trendfoll` portfolio rules.

## Strategy tracks

Primary: **X3 BASE** (pivot-hold execution, no C/A hard filter).

Mandatory control: **X1 BASE**.

C and C+A are not promoted to primary portfolio tracks because Fundamental Ablation v1 did not support C as additive hard-filter edge and C+A is too sparse. They may be retained only as descriptive secondary evidence.

EXH2 is not part of PORT1.

## Capital model

- initial equity: 100,000 arbitrary currency units;
- long-only;
- no leverage;
- no shorting;
- maximum concurrent positions: **7**;
- target notional per new position: **1/7 of prior-session closing equity**;
- because the frozen hard stop is 7% from fill, a fully-sized new position has approximately 1% initial equity risk before costs/gaps;
- if available cash at the entry open is less than the full target notional, the trade is skipped rather than partially filled;
- no pyramiding/add-on positions;
- one open position per security.

The 7-position cap is mechanical: 1/7 notional × 7% stop ≈ 1% equity risk per position and seven fully-sized positions use approximately 100% gross capital. It is not optimized from historical portfolio outcomes.

## Entry priority when capacity is scarce

All entry eligibility remains governed by the frozen X1/X3 execution rules.

If more valid entries occur at the same session Open than available slots, rank using information already known from T0:

1. higher `rs_percentile`;
2. higher `volume_ratio`;
3. ticker ascending as deterministic final tie-break.

No future return/exit information may influence allocation priority.

## Event timing

- entries execute at the already-defined entry Open;
- positions that are scheduled to exit later on a session still occupy a slot at that session's Open;
- therefore morning entries are allocated **before** intraday exits on the same date;
- same-bar stop/target ambiguity remains stop-first as frozen in the execution engine;
- gap-through exit semantics remain those of the frozen execution engine;
- no time stop is introduced.

## Equity and drawdown

Daily end-of-day equity:

```text
cash
+ closing market value of positions still open after that day's exits
```

On an exit day, realized exit proceeds replace the position's market value.

Maximum drawdown is computed from this daily portfolio equity curve, never from cumulative unallocated trade returns.

Final still-open/censored positions are marked to the final available close and are not invented as forced exits.

## Costs

Report two curves using identical allocations:

- **GROSS**: no explicit commission/slippage deduction;
- **COST20BP_RT**: 10 bps deducted on entry notional and 10 bps on exit proceeds (approximately 20 bps round trip).

The cost sensitivity is a robustness view, not a tuned parameter and does not alter trade eligibility.

## Required outputs

For X3 BASE and X1 BASE separately:

- accepted portfolio entries;
- capacity/cash skips;
- daily equity curve;
- total return;
- CAGR where calendar span permits;
- maximum drawdown;
- annual returns;
- gross exposure / position count over time;
- trade contribution concentration;
- GROSS and COST20BP_RT results.

Trade-level PF may be repeated for linkage but must not be labeled portfolio return.

## Guardrails

Do not change max positions, sizing, ranking, costs, or event timing after seeing PORT1 outcomes. Any alternative becomes a separately versioned experiment and requires independent validation.
