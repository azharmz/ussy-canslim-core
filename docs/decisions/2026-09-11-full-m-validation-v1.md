# Decision — Full-M Validation v1

Date: 2026-09-11

## Status

**COMPLETE / VALIDATED HISTORICAL — DO NOT PROMOTE TO FWD1**

Canonical confirmation workflow: `34576910915` = SUCCESS.

Evidence class: retrospective historical sidecar, not out-of-sample evidence.

Methodology: `docs/methodology/full-m-validation-v1.md`.

## Compared definitions

```text
M0_SPY_ONLY = SPY FTD active AND SPY distribution_count_25 < 6

M1_DUAL = (SPY OR QQQ FTD active)
          AND max(SPY distribution_count_25, QQQ distribution_count_25) < 6
```

All non-M candidate rules, X1/X3 execution semantics, and PORT1 construction remained frozen. FWD1 was not modified.

## Canonical evidence

Candidate overlap:

```text
both    = 7,694
M0 only = 3,037
M1 only = 0
```

Thus M1 did not discover any candidate absent from M0. In this historical sample it only removed M0 candidates.

Preferred X3 comparison:

| Metric | M0 SPY-only | M1 dual |
|---|---:|---:|
| Candidates | 10,731 | 7,694 |
| X3 candidate trades | 3,604 | 2,664 |
| X3 trade PF | 1.1627 | 1.1701 |
| X3 PF ex-top10 | 1.1454 | 1.1468 |
| Portfolio entries | 1,129 | 779 |
| Gross CAGR | 3.02% | 2.40% |
| Gross max drawdown | -43.36% | -37.76% |
| CAGR @20bp RT | 2.38% | 1.74% |
| Max DD @20bp RT | -50.94% | -42.44% |

X1 deteriorated under M1: gross CAGR moved from about +0.81% to -1.64%, while drawdown improved from about -66.89% to -61.44%.

The confirmation artifact correctly reports final censored positions (X1=4, X3=1 for both tracks); the earlier evidence-field naming bug affected metadata only, not PF/CAGR/drawdown calculations.

Pinned benchmark pointers in the confirmation artifact:

```text
SPY last_date = 2026-09-10
QQQ last_date = 2026-09-10
```

## Verdict

M1 is best interpreted as a **risk throttle**, not an incremental edge source. It reduces participation and historical drawdown, but the preferred X3 PF improvement is negligible after top-10 removal and absolute CAGR falls materially.

Therefore:

1. Keep frozen FWD1 on the existing SPY-only M definition.
2. Do not retrofit QQQ/full-M into the live FWD1 clock.
3. Do not open a new M1 forward-validation clock on the basis of this result alone.
4. Preserve QQQ as validated benchmark infrastructure for future separately preregistered research.
5. Do not search alternative SPY/QQQ thresholds or Boolean combinations post hoc to improve historical results.

This closes Full-M Validation v1.