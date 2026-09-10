# Decision Record — Robustness v1

Date: 2026-09-10

Status: COMPLETE / VALIDATED HISTORICAL ROBUSTNESS

## Scope

ROB1 evaluates the frozen X3 BASE research track and mandatory X1 BASE control after PORT1, without changing entry, exit, portfolio, C/A, or EXH2 rules. This is retrospective historical robustness evidence only. Because X3 was selected using the historical sample, these diagnostics are **not true out-of-sample evidence**.

Methodology was frozen before outcome review in `docs/methodology/robustness-v1.md`.

## Canonical workflow and evidence

Final successful workflow: `34488295631`

Code head: `6f3fc86bc1230241d5414cc195004cd29c40ebcf`

Artifact: `robustness-v1-34488295631`

Artifact SHA-256: `5e1ff152b9e0cb75ebb517e716dede8624dfac01885d6d898efd1274d02977eb`

PORT1 reference run: `34488197400`.

Censored-accounting audit is aligned with frozen PORT1 semantics: X1 has 4 and X3 has 2 boundary censored positions, all at 2026-09-09; mid-sample censored positions = 0; censored positions remain mark-to-market and phantom exit cost is removed.

## Accepted portfolio trade quality

| Metric | X1 BASE | X3 BASE |
|---|---:|---:|
| Accepted portfolio trades | 1,424 | 1,129 |
| Realized trades | 1,420 | 1,127 |
| Profit factor | 1.060 | **1.162** |
| Median realized return | -7.0% | -7.0% |
| Median pre-exit MFE | +6.66% | +6.67% |
| Median pre-exit MAE | -4.93% | -5.10% |
| Target rate | 30.20% | **32.42%** |
| Stop rate | 69.52% | **67.40%** |

X3 remains better than X1 at accepted-portfolio trade level, but the median trade is still a full stop loss because the payoff structure depends on a minority of +20%-target winners offsetting a larger number of -7% stops.

## Capital-constraint opportunity cost

| Variant | Accepted PF | Not-accepted PF |
|---|---:|---:|
| X1 | 1.060 | 1.104 |
| X3 | **1.162** | **1.164** |

The frozen RS/volume same-session portfolio priority does not show evidence of adding material selection edge. For X3, accepted and capital-constrained-not-accepted opportunities have almost identical PF. This is descriptive evidence only and does **not** authorize changing the frozen ranking rule post hoc.

## Historical subperiod robustness

X3 gross five-block results:

| Block | Period | Total return | CAGR | Max DD |
|---|---|---:|---:|---:|
| 1 | 1993-03-10 → 1999-11-19 | +63.45% | +7.62% | -14.68% |
| 2 | 1999-11-19 → 2006-08-03 | -8.30% | -1.28% | -40.66% |
| 3 | 2006-08-03 → 2013-04-16 | -9.09% | -1.41% | -43.36% |
| 4 | 2013-04-16 → 2019-12-27 | +33.74% | +4.44% | -20.30% |
| 5 | 2019-12-27 → 2026-09-09 | +49.89% | +6.22% | -25.98% |

The edge is therefore not uniform across historical regimes. Two of five coarse blocks lose money gross.

Annual robustness for X3 gross: 34 years, 21 positive / 13 negative, median annual return +2.38%, worst year -15.29%, best year +35.30%. Under 20 bps round-trip cost sensitivity: 20 positive / 14 negative years, median annual return +1.57%.

## Benchmark-relative context

SPY price-only over the comparable span produced approximately:

- CAGR: **8.80%**;
- max drawdown: **-56.47%**;
- dividends excluded.

Frozen X3 portfolio produced approximately:

- gross CAGR: **3.04%**;
- gross max drawdown: **-43.36%**;
- cost20bp CAGR: **2.40%**;
- cost20bp max drawdown: **-50.94%**.

Therefore X3 historically reduced drawdown relative to SPY price-only, but surrendered a very large amount of return. Because the benchmark excludes dividends, the return shortfall versus a total-return benchmark would be larger, not smaller.

## Interpretation

1. X3's advantage over X1 survives portfolio construction and trade-level robustness diagnostics.
2. X3 is not merely driven by a few top symbols, but its aggregate economic profile remains weak.
3. Portfolio priority does not appear to improve trade selection materially.
4. Historical performance is regime-dependent and includes two losing coarse subperiods.
5. The strategy materially underperforms passive SPY on CAGR while only moderately improving drawdown.
6. These retrospective diagnostics are not true OOS evidence.

## Decision

- Mark ROB1 historical robustness COMPLETE / VALIDATED.
- Retain X3 BASE as the primary research baseline and X1 as mandatory control.
- Do not tune X3, PORT1 ranking, max positions, sizing, stop, target, or cost assumptions from ROB1.
- Do not promote the strategy to production.
- Keep C/A as descriptors and EXH2 as a separate hypothesis.
- The next evidentiary gate is genuine forward validation using frozen rules after 2026-09-09.
- Production gate remains: at least 12 calendar months and at least 50 closed X3 portfolio trades before production inference.
