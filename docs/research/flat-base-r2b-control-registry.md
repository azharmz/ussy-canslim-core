# Flat Base vNext R2-B — negative/control development registry

Status: **CONTROL ORACLES FROZEN BEFORE DESCRIPTOR REPLAY**

Freeze date: 2026-09-20

Purpose: provide source-backed counterexamples for development of local weekly tight/sideways descriptors. These controls are not a new Flat Base validation set and are not used to relabel other pattern families as Flat Bases.

## Anti-leakage

No Golden, R1-E, or R2-A case is used here. Controls were selected from IBD descriptions of explicitly wide/loose or erratic basing action before descriptor values were measured.

## Frozen controls

| ID | Symbol | Source window/as-of | Source-backed role | Pivot |
| --- | --- | --- | --- | ---: |
| C01 | FICO | five-week Flat Base ending at 2019-09-09 breakout episode | IBD explicitly calls the short five-week Flat Base / late-stage action wide, loose and erratic; daily swings routinely >=1%, including a 5.6% drop | 371.91 |
| C02 | VZIO | IPO base from 2021-03-25 through 2021-04-28 breakout | IBD explicitly calls the basing action fast/wide/loose; some daily swings >=12%; base lasted only three weeks | 25.90 |

Sources:
- FICO: IBD Top Stocks 2019, article adapted from 2019-09-09 IBD coverage.
- VZIO: IBD Investors Corner, originally published 2021-09-03 and later updated.

## Interpretation boundary

C01 is the key morphology-quality control because the source itself calls the structure a five-week Flat Base while describing its action as wide/loose/erratic.

C02 is a volatility control, not a duration-eligible Flat Base: its three-week IPO base intentionally tests whether local weekly descriptors respond strongly to source-labelled loose action. It must never be used to infer the Flat Base minimum-duration rule.

R2-B may be expanded only with additional source-backed controls selected without looking at candidate descriptor values. No production threshold is authorized from this small cohort.


## First control replay

Actions run: `35514727718`.

FICO produced 25 sessions / 6 trading weeks on the frozen operational window. Descriptor evidence:
- weekly_close_span_pct = 6.28%
- weekly_median_range_pct = 6.61%
- weekly_close_change_abs_median = 4.12%
- weekly_direction_changes = 2
- late_base_contraction_ratio = 1.012

VZIO returned zero Yahoo rows because the historical/delisted ticker is unavailable through this adapter. It is **DATA_UNAVAILABLE / NOT SCORED**; no substitute case is selected after seeing descriptor results.

### Development implication

The currently preregistered H2 descriptors do **not** show a clean separation on the tiny source-backed development comparison. In particular, FICO's source-labelled wide/loose Flat Base overlaps materially with ANET and HUBS on weekly median range and median absolute weekly close change. Therefore no numeric vNext tightness cutoff is selected from R2-A/R2-B.

This is evidence against prematurely converting any one H2 descriptor into a recognition threshold. The next research step must expand source-backed controls/positives or revisit the morphology representation itself, while preserving the untouched validation boundary.
