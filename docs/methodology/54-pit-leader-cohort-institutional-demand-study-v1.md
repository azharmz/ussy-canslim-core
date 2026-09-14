# 54 — PIT Leader-Cohort / Institutional-Demand Evidence Study v1

Status: **PREREGISTERED EVIDENCE STUDY / DETERMINISTIC PRODUCTION SELECTOR NOT YET AUTHORIZED**

Study: `54-pit-leader-cohort-institutional-demand-study-v1`

## Purpose

Close the remaining evidence gap between #53 prospective broad-market membership and the frozen #51 leadership/weakening evidence contract without inventing a leader algorithm from future returns or performance optimization.

#53 answers **which securities were in the broad exchange-listed membership as of T**. It does not answer **which of those securities were O'Neil-style market leaders as of T**, nor whether institutional demand/selling in those leaders was confirming or weakening the general market.

This study therefore preregisters the admissible evidence families and the unresolved translation problem. It does not modify #46, #45, #51, #52, or #53.

## Authoritative findings

William J. O'Neil's general-market framework explicitly distinguishes market-leading-stock evidence from major-index price/volume evidence.

For an up-trending market, O'Neil describes:

- new market-leading stocks as the first stocks to move to new price highs while the market is also rising on strong volume; and
- institutional money moving into those new leaders.

For a down-trending market, O'Neil describes:

- a majority of new leaders stopping making new highs; and
- institutional selling of new leaders.

O'Neil/AAII CAN SLIM material also supports stock-level leader characteristics including strong relative strength, price near/new highs, strong volume demand, and institutional sponsorship. Contemporary IBD educational material likewise treats a bullish RS line/new-high behavior and accumulation/distribution information as useful leader/institutional-demand evidence.

These sources establish admissible evidence families, but they do **not** establish one public universal formula that converts every exchange-listed security into a market-leader cohort for #51.

## Frozen evidence families for the study

A candidate PIT leader observation may carry the following evidence channels. Each channel must be computed or observed using information available no later than `asof_date`.

### 1. Relative-strength evidence

Permitted evidence:

- stock price performance relative to a broad benchmark;
- RS line direction/state;
- RS line at/new high where source or separately frozen calculation supports it;
- an authoritative PIT RS rating when a licensed/auditable source is available.

No new RS cutoff is authorized by this study. Existing stock-selection guidance such as RS rank 80+ may be recorded as authoritative stock-level evidence, but it must not be silently promoted into a universal general-market leader-cohort cutoff without separate validation.

### 2. Price leadership / new-high evidence

Permitted evidence:

- stock at or near a price high using a preregistered lookback;
- stock making a new price high;
- constructive breakout/new-high behavior from an already frozen morphology/breakout contract where applicable.

This study does not choose a new lookback, distance-to-high threshold, or breakout-success horizon.

### 3. Demand / accumulation evidence

Permitted evidence:

- strong volume accompanying upward price action;
- authoritative accumulation/distribution evidence when PIT-accessible;
- other separately frozen price-volume evidence that explicitly represents demand rather than future performance.

Daily dollar volume may be useful as a liquidity/institutional-capacity descriptor but is not, by itself, proof of institutional accumulation.

### 4. Institutional sponsorship evidence

Permitted evidence:

- PIT institutional-owner count;
- PIT change in institutional sponsorship;
- authoritative fund-ownership/sponsorship fields with an availability timestamp.

Quarterly ownership data must use its actual public availability timestamp, not the quarter-end date as though it were known then.

### 5. Breakdown / weakening evidence

Permitted evidence:

- a previously valid PIT leader ceasing to make new highs;
- breakdown/deterioration evidence from a separately frozen technical contract;
- explicit institutional selling/distribution evidence.

#51's `majority` rule remains ordinary >50% of a **valid observed leadership cohort**. #54 does not redefine it.

## Cohort construction problem

A production leader cohort must be selected from a valid PIT broad-market membership such as #53, but membership alone is insufficient.

A future selector must specify, before outcome evaluation:

1. eligible security types and exclusions;
2. minimum history/data-quality requirements;
3. the exact RS evidence and benchmark;
4. the exact price/new-high evidence;
5. the exact demand/accumulation evidence;
6. whether institutional sponsorship is required for cohort membership or retained as a separate #51 channel;
7. tie/duplicate/share-class handling;
8. missing-data behavior;
9. cohort refresh clock;
10. provenance/versioning.

Any numeric choices not directly fixed by authoritative evidence must be preregistered as research conventions and validated out-of-sample. They may not be chosen by maximizing future returns or by making #46/#45 produce a preferred exposure history.

## PIT / anti-leakage contract

For every security observation, preserve at least:

- `asof_date`
- #53 membership run/manifest identity
- security identifier and source symbol
- evidence timestamps
- benchmark identity
- RS evidence and calculation version/source
- new-high/price-leadership evidence and lookback version
- price-volume demand evidence and version/source
- institutional sponsorship evidence and actual availability timestamp when used
- prior-leader state if weakening is evaluated
- selector/study version

Forbidden:

- defining leaders from subsequent returns;
- using today's membership for historical dates before #53 snapshots existed unless a separately validated historical membership source is adopted;
- backdating institutional ownership to quarter end before it became public;
- selecting thresholds after viewing #46 state transitions, #45 exposure performance, strategy returns, CAGR, win rate, profit factor, or future breakout success;
- using the restricted USSY/Musaffa universe as the broad-market cohort.

## What can be implemented now

The project can safely implement a **PIT evidence packet/schema and research dataset builder** that joins #53 membership with raw, timestamped candidate evidence channels.

The project must not yet implement a production boolean selector that claims to emit an authoritative leader cohort unless the exact selector is separately frozen after preregistration and untouched validation.

## Validation path

Recommended next experimental cycle inside this study, not a new production contract:

`authoritative evidence inventory → preregister candidate selector(s) → development on development period → freeze → untouched validation → one-shot validation → terminal decision`

Acceptance is semantic/reproducibility first. Future-return performance must not be the criterion for whether a selector is called theory-faithful.

## Terminal boundary

#54 resolves **what evidence may legitimately be studied** and freezes the anti-leakage requirements. It does not resolve the final numeric leader-selector algorithm.

Until such a selector passes a separately frozen validation cycle:

- #53 remains membership-only;
- #51 remains the governing boolean evidence contract;
- #50 continues passing `leadership_confirming=None` and `weakening_confirmed=None` when no approved #51 evidence packet exists.

Status: **PREREGISTERED EVIDENCE STUDY / DETERMINISTIC PRODUCTION SELECTOR NOT YET AUTHORIZED**
