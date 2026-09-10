# Decision Record — Fundamental Ablation v1

Date: 2026-09-10

Status: COMPLETE / VALIDATED DESCRIPTIVE

## Scope

Test the incremental effect of the frozen CAN SLIM fundamental filters after the validated historical C/A attachment, without changing technical/execution rules.

Primary execution baseline: X3 pivot-hold.

Mandatory control: X1 immediate executable entry.

Comparisons:

```text
BASE
vs BASE + C-v1
vs BASE + C-v1 + A-v1
```

EXH2/post-breakout-exhaustion was intentionally not applied.

## Frozen inputs

- research universe: `CURRENT_COMPLIANT_UNIVERSE_FROZEN_AT_2026_08_28`;
- technical candidates: 10,731 across 860 securities;
- CA-HIST validation workflow: `34479060107`;
- fundamentals source run: `34470910341`;
- C-v1: latest usable quarterly EPS YoY >=25% AND revenue YoY >=25%;
- A-v1: latest three consecutive annual EPS YoY each >=25%;
- X1/X3 execution semantics unchanged;
- stop: 7% from actual fill;
- target: 20% from pivot;
- same-bar ambiguity: stop first;
- no arbitrary time stop.

## Workflow and implementation

Implementation: `scripts/run_fundamental_ablation_v1.py`

Workflow: `.github/workflows/fundamental-ablation-v1.yml`

Successful workflow run: `34481587218`

Code head: `0f711bf7561bfe7da901905083bc7582983026c8`

Artifact: `fundamental-ablation-v1-34481587218`

Artifact SHA-256: `9a4018cad0f8dc35439633065520d2e4d829fc835c6bfd099cdbbf4e9c1f154a`

Frozen semantic tests: 23 passed.

## Main results

| Execution | Filter | Eligible candidates | Entries | PF | PF ex-top10 | Target | Stop |
|---|---|---:|---:|---:|---:|---:|---:|
| X1 | BASE | 10,731 | 5,777 | 1.093 | 1.082 | 30.95% | 68.98% |
| X1 | C-v1 | 703 | 382 | 1.056 | 0.949 | 30.37% | 69.63% |
| X1 | C+A | 2 | 2 | 0.000 | n/a | 0.00% | 100.00% |
| X3 | BASE | 10,731 | 3,604 | 1.163 | 1.146 | 32.77% | 67.18% |
| X3 | C-v1 | 703 | 238 | 1.020 | 0.861 | 30.25% | 69.75% |
| X3 | C+A | 2 | 2 | 0.000 | n/a | 0.00% | 100.00% |

Trade-level PF is descriptive evidence only, not portfolio return.

## Robustness observations

For X3+C, coarse subperiod PFs with trades were approximately:

```text
period 2: 1.49
period 3: 1.41
period 4: 0.44
period 5: 1.74
```

However PF ex-top10 was below 1 in every X3+C subperiod with trades:

```text
period 2: ~0.72
period 3: ~0.74
period 4: ~0.11
period 5: ~0.45
```

This indicates that the apparently positive raw PF in several periods depends materially on the strongest winners.

Symbol concentration rises under C filtering but is not dominated by one ticker:

```text
X3 BASE top symbol share ~0.4%; top five ~2.0%
X3 + C top symbol share ~2.5%; top five ~9.7%
```

## Interpretation

### R2-C

The hard C-v1 filter does not improve the preferred X3 baseline in this sample.

```text
X3 BASE PF        1.163
X3 + C PF         1.020
X3 BASE ex-top10  1.146
X3 + C ex-top10   0.861
```

The same direction is visible under X1. Therefore there is no evidence here to promote C-v1 as an additive hard trading filter.

This does **not** invalidate C as a CAN SLIM fundamental descriptor. It means the frozen C-v1 hard threshold, when intersected with this technical/execution baseline and this research universe, is not supported as incremental trading edge by this historical evidence.

Do not alter the 25% EPS/revenue thresholds based on these results.

### R2-CA

Only two C+A candidate events exist: CRUS 2022-08-03 and MEDP 2023-07-25. Both stop under both X1 and X3.

Two observations cannot establish whether A adds or destroys edge. The valid conclusion is **sample insufficiency**, not economic rejection of A.

## Decision

1. Keep C-v1 and A-v1 frozen as research descriptors.
2. Do not promote hard C or C+A filtering into the preferred trading baseline based on this result.
3. Retain X3 as the preferred research execution baseline and X1 as mandatory control.
4. Do not tune C/A thresholds post hoc.
5. Move to portfolio-construction pre-registration using X3 BASE as the primary strategy track.
6. Keep C/C+A results as secondary descriptive comparisons.
7. Keep EXH2 separate until independently validated.

## Guardrails

No portfolio CAGR, return or maximum drawdown is claimed here because portfolio construction and position sizing have not yet been frozen.
