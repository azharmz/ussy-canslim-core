# Decision — Institutional Sponsorship I-v1 Historical Ablation

Date: 2026-09-12

## Status

**COMPLETE / NOT PROMOTED AS HARD FILTER**

Canonical ablation run: `34664388792` = SUCCESS.

Evidence class: **retrospective historical**, not OOS.

Frozen methodology: `docs/methodology/institutional-sponsorship-growth-v1.md`.

## Inputs

Canonical sponsorship pointer:

```text
institutional_sponsorship/current.json
```

Pinned manifest:

```text
institutional_sponsorship/snapshots/2026-09-12/run-34663714292/manifest.json
```

Upstream evidence:

```text
historical sponsorship state = run 34654725293
historical uncertainty mask  = run 34656995462
historical I-v1 attachment   = run 34663929577
```

Attachment distribution:

```text
PASS          1,902
FAIL          2,888
NOT_EVALUABLE 5,941
I-evaluable   4,790
```

There were zero future-availability violations.

## Frozen rule

The rule was preregistered before strategy outcomes were inspected:

```text
I_delta = manager_count_latest - manager_count_prior
PASS = I_delta > 0
FAIL = I_delta <= 0
NOT_EVALUABLE = missing / non-consecutive / unmapped / uncertain
```

No minimum manager count, percentage growth, share growth, or value-growth threshold was searched.

## Comparator correction

The initial run included the all-history BASE track beginning in 1993, while SEC 13F data only supports I from 2013 onward. That all-history baseline is retained as context but is not the primary causal comparator.

Before freezing the verdict, run `34664388792` added `I_EVALUABLE` = PASS + FAIL as a same-support control. This changed no I rule or threshold; it only made the comparison valid on the same information-availability support.

## Preferred X3 results

| Metric | I_EVALUABLE | I_PASS |
|---|---:|---:|
| Eligible candidates | 4,790 | 1,902 |
| Candidate trades | 1,596 | 671 |
| Trade PF | 1.1194 | 1.1465 |
| PF ex-top10 | 1.0856 | 1.0711 |
| Portfolio entries | 475 | 331 |
| Gross CAGR | 2.96% | 2.17% |
| Gross max DD | -28.19% | -39.02% |
| CAGR @20bp RT | 2.07% | 1.57% |
| Max DD @20bp RT | -31.97% | -43.08% |

The raw trade PF improves slightly, but the improvement disappears after the ten best trades are removed. More importantly, the frozen PORT1 implementation produces lower CAGR and materially worse drawdown under `I_PASS`.

X1 also does not provide a basis for promotion: while its trade PF rises on I_PASS, cost-adjusted CAGR remains negative and the preferred strategy for this project is X3.

## Decision

1. **Do not promote I-v1 as a hard trading filter.**
2. Keep institutional sponsorship as a CAN SLIM descriptor.
3. Do not alter frozen X3, PORT1, or FWD1.
4. FWD1 continues with `I = NOT_IMPLEMENTED` in its frozen strategy semantics.
5. Do not search post-hoc manager-count thresholds, percentage growth cutoffs, share-growth cutoffs, or reported-value cutoffs to repair the historical result.
6. Any materially different sponsorship hypothesis must be preregistered as a new version and validated independently.

This closes the currently defined I-v1 historical research track.