# Robustness / Holdout Protocol v1 — Pre-registration

Date frozen: 2026-09-10

Status: FROZEN BEFORE ROB1 OUTCOME REVIEW

## Purpose

Evaluate whether the already-frozen X3 BASE portfolio result is robust enough to justify further development, without altering entry, exit, sizing, allocation, C/A, or exhaustion rules after seeing PORT1 outcomes.

Primary track: X3 BASE. Mandatory control: X1 BASE.

PORT1 rules remain exactly as frozen in `docs/methodology/portfolio-construction-v1.md`.

## Important evidence boundary

A retrospective split created now cannot be called a true untouched holdout because X3 was selected using the historical sample and PORT1 has already been observed on that sample. Therefore ROB1 historical subperiod work is **robustness evidence only**, not out-of-sample evidence.

True forward validation begins with data after the frozen research boundary of 2026-09-09. No strategy-rule change may be justified by calling a newly carved historical segment 'OOS'.

## Historical robustness diagnostics

For X3 BASE and X1 BASE:

1. Portfolio outcome diagnostics already frozen in PORT1:
   - gross and COST20BP_RT return/CAGR/max drawdown;
   - accepted entry count, capacity/cash skips, exposure and position count;
   - contribution concentration.
2. Accepted-portfolio trade quality:
   - median pre-exit MFE;
   - median pre-exit MAE;
   - target/stop/censored counts.
3. Opportunity-cost diagnostic:
   - compare accepted portfolio trades with trade candidates rejected only by portfolio capacity/cash;
   - report descriptive independent-trade PF/median return/target/stop for accepted vs non-accepted candidate trades;
   - never label skipped-candidate independent returns as realizable portfolio performance.
4. Calendar robustness:
   - divide each portfolio track's observed date span into five equal-duration calendar blocks using dates only, not outcomes;
   - report block return, CAGR and max drawdown for gross and COST20BP_RT curves.
5. Annual robustness:
   - count positive/negative years and median/worst/best annual return from the frozen equity curve.
6. Benchmark-relative context:
   - compare against SPY **price-only** close series over the exact same first/last dates;
   - report SPY price total return, CAGR and max drawdown;
   - dividends are not available in this benchmark contract, so do not describe it as total-return index performance.

## Forward-validation protocol

Forward validation starts with the first eligible US session after 2026-09-09 using the frozen X3 BASE + PORT1 rules.

Checkpoints may be reported at 25 and 50 closed portfolio trades, but no production verdict is allowed before both:

- at least 12 calendar months have elapsed from the forward start; and
- at least 50 X3 portfolio trades have closed.

During forward validation:

- no threshold/rule/sizing/priority/cost change may be back-applied to the frozen track;
- any new idea becomes a separately versioned experimental branch;
- EXH2 remains separate and cannot be inserted into X3 BASE retrospectively;
- C/A remain descriptors unless a separately pre-registered experiment tests another role.

## Decision standard

ROB1 may reject or downgrade the current baseline if robustness is poor. It may not promote the strategy to production on retrospective evidence alone. Production still requires the forward-validation gate above.
