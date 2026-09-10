# Experiment Registry

Use this file to register experiments before execution. Completed experiments must pin inputs, code/config, evidence class, and verdict.

## Registered experiments

| ID | Experiment | Status | Primary purpose |
|---|---|---|---|
| C1 | C label distribution | COMPLETE / VALIDATED | C-v1 PASS/FAIL/NOT_EVALUABLE distribution |
| A1 | A label distribution | COMPLETE / VALIDATED | A-v1 PASS/FAIL/NOT_EVALUABLE distribution |
| TB1 | Independent technical baseline | COMPLETE / FROZEN | transparent N/S/L/M proxy baseline |
| E0-SMOKE | Rolling technical smoke | COMPLETE / VALIDATED | end-to-end candidate generation |
| E0-HIST | Historical technical candidates on frozen current-compliant universe | COMPLETE | establish candidate event set |
| E1 | Signal-day shock diagnostics | COMPLETE / EXPLORATORY | T-1->T0 shock mechanism |
| E2 | H+1 execution-gap diagnostics | COMPLETE / EXPLORATORY | execution gap mechanism |
| E3 | Pivot extension 3/5/8% | COMPLETE / EXPLORATORY | pre-specified extension diagnostics |
| E4 | Actual-fill pivot extension | COMPLETE / EXPLORATORY | fill-aware chasing diagnostic |
| ET1 | X1-X4 entry timing basis test | COMPLETE / VALIDATED | choose executable daily-EOD entry baseline before fundamental ablation |
| EXH1 | Post-breakout exhaustion diagnostic | COMPLETE / EXPLORATORY | test T-1->T0 shock × T+1 rejection mechanism |
| EXH2 | Exhaustion validation | PRE-REGISTRATION REQUIRED | independently validate exhaustion interaction; no discovery-sample cutoff tuning |
| CA-PERIOD | C/A period-semantics audit | COMPLETE / PASS | latest-quarter/FY state selection |
| CA-HIST | Historical C/A attachment | COMPLETE / VALIDATED | causal C/A state at each signal with explicit SEC FY identity |
| R2-C | Preferred technical baseline + C | **COMPLETE / VALIDATED DESCRIPTIVE** | incremental value of C after validated CA-HIST |
| R2-CA | Preferred technical baseline + C+A | **COMPLETE / SPARSE** | incremental value of C+A; sample too small for strategy inference |
| PORT1 | Portfolio construction | **NEXT / PRE-REGISTRATION REQUIRED** | sizing/max positions/equity curve |
| ROB1 | Strategy robustness/holdout | BLOCKED | portfolio DD, holdout and remaining concentration/robustness |

## C1/A1

Workflow run `34431101727` = SUCCESS.

Pinned fundamentals manifest:

`fundamentals/snapshots/2026-09-09/run-34417104650/manifest.json`

```text
C-v1   PASS 69 | FAIL 520 | NOT_EVALUABLE 312
A-v1   PASS 11 | FAIL 483 | NOT_EVALUABLE 407
C+A    PASS  3 | FAIL 437 | NOT_EVALUABLE 461
```

Verdict: thresholds remain frozen; no trading metrics were used.

## TB1

Implementation: `src/canslim_research/technical.py`

CI run `34431906311` = SUCCESS.

Verdict: independent technical baseline executable and frozen.

## E0 / E1-E4

Historical technical candidate engine on research universe frozen at `universe/membership/2026-08-28.json`:

- candidate events: 10,731
- candidate securities: 860

E1-E4 workflow run `34433673545` = SUCCESS.

X1 funnel:

```text
5,777 accepted T+1 entries
501 T+1 above 5% buy zone
726 T+1 at/below pivot
3,727 skipped because security already open
```

Verdict: fill-aware 5% rule addresses a real chasing mechanism; no post-hoc shock/gap threshold adopted.

## ET1 — Entry Timing Basis Test v1

Specification: `docs/methodology/entry-timing-basis-test-v1.md`

Implementation:

- `src/canslim_research/entry_timing.py`
- `scripts/run_entry_timing_basis_test.py`
- `tests/test_entry_timing.py`

Workflow run `34464861119` = SUCCESS; timing/execution tests: 13 passed.

All variants share the same 7% stop from actual fill and 20% target from pivot.

| Variant | Entries | Fill rate | PF | PF ex-top10 | Target rate | Stop rate |
|---|---:|---:|---:|---:|---:|---:|
| X1 | 5,777 | 53.83% | 1.093 | 1.082 | 30.95% | 68.98% |
| X2 | 6,158 | 57.39% | 1.096 | 1.086 | 31.02% | 68.89% |
| **X3** | **3,604** | **33.58%** | **1.163** | **1.146** | **32.77%** | **67.18%** |
| X4 | 4,216 | 39.29% | 1.109 | 1.093 | 30.95% | 69.00% |

Verdict: X3 pivot-hold is the current preferred research execution baseline; X1 remains mandatory control. This does not end entry-quality research.

## EXH1 — Post-breakout exhaustion diagnostic

Implementation: `scripts/run_post_breakout_exhaustion_diagnostics.py`

Workflow: `.github/workflows/post-breakout-exhaustion-v1.yml`

Workflow run `34466747136` = SUCCESS.

Research question: does an extreme T-1->T0 expansion become especially vulnerable when T+1 confirms rejection?

Discovery-sample findings:

- top shock decile median move ~8.70%, X1 PF ~1.05;
- bottom shock decile median move ~0.78%, X1 PF ~1.36;
- raw return-to-pivot frequency is not monotonic with shock because low-shock breakouts begin mechanically closer to pivot;
- the interaction with T+1 rejection is much stronger than shock alone.

Highest shock quintile interaction:

| T+1 state | Candidates | X1 PF | Stop rate | Retest pivot by T+3 | Breakdown below pivot by T+3 |
|---|---:|---:|---:|---:|---:|
| Bearish + Close < T0 Close | 962 | 0.560 | 80.84% | 74.32% | 60.60% |
| Bearish only | 171 | 0.675 | 76.40% | 34.50% | 25.15% |
| Close < T0 only | 120 | 1.601 | 61.25% | 61.67% | 43.33% |
| No rejection | 893 | 1.573 | 59.63% | 21.61% | 14.22% |

Verdict: support the mechanism hypothesis `large T0 expansion × T+1 rejection -> exhaustion risk`. Do not derive or adopt a hard momentum cutoff from EXH1. Any rule based on this finding must be separately versioned and validated on independent/forward evidence.

Artifacts: workflow artifact `post-breakout-exhaustion-v1-34466747136` (`candidate_exhaustion_features.csv`, `shock_deciles.csv`, `shock_x_t1_rejection.csv`).

## CA period semantics

Audit run `34434268817` = SUCCESS.

At each decision cutoff:

- restrict SEC evidence to `accepted_at <= cutoff`;
- for C, select latest fiscal quarter known at cutoff, then latest accepted state within that quarter;
- older-period amendments cannot displace newer fiscal periods merely because accepted later;
- for A, select latest accepted annual state per FY and then latest three consecutive FY growth states;
- undefined growth remains NOT_EVALUABLE.

## CA-HIST — Historical C/A attachment v1

Workflow run `34479060107` = SUCCESS.

Code commit:

`26892121cb4a650b5fe9e00491a557963b9f49c1`

Pinned fundamentals manifest:

`fundamentals/snapshots/2026-09-10/run-34470910341/manifest.json`

The wide PIT table carries annual state but not SEC FY. CA-HIST resolves `annual_eps_source_accession -> SEC fy` through the immutable long PIT artifact, then selects the latest accepted state per FY and requires the latest three resolved FY to be consecutive. Unresolved FY identity is `NOT_EVALUABLE`; no calendar-year inference is allowed.

Structural validation:

```text
candidate rows                         10,731
candidate securities                      860
duplicate candidate attachment rows         0
future accepted_at violations               0
identity-missing-CIK rows                   56
annual states                           11,703
annual FY resolved                     10,307
annual FY unresolved                    1,396
```

Historical distribution:

```text
C-v1   PASS 703 | FAIL 3,475 | NOT_EVALUABLE 6,553
A-v1   PASS  34 | FAIL   768 | NOT_EVALUABLE 9,929
C+A    PASS   2 | FAIL   650 | NOT_EVALUABLE 10,079
```

Hard validation: every A-PASS row has exactly three resolved consecutive FY, zero unresolved FY identity, and no source accepted after T0 cutoff. The two C+A PASS events are CRUS `2022-08-03` and MEDP `2023-07-25`.

Evidence artifact: `historical-ca-attachment-v1-34479060107`, GitHub artifact SHA-256 `be23394a14b3096a491b67fb4836edb2656739e30ad7cefd31c52492e5f9afeb`.

Verdict: CA-HIST COMPLETE / VALIDATED. C/A thresholds remain frozen. No trading performance was consulted. R2-C and R2-CA were unblocked. EXH2 remains a separate hypothesis and must not be folded into the ablation.

Detailed decision record: `docs/decisions/2026-09-10-historical-ca-attachment-v1.md`.

## R2-C / R2-CA — Fundamental ablation v1

Implementation: `scripts/run_fundamental_ablation_v1.py`.

Workflow: `.github/workflows/fundamental-ablation-v1.yml`.

Workflow run `34481587218` = SUCCESS; 23 frozen label/timing/execution tests passed. Pinned CA-HIST validation run `34479060107` and fundamentals source run `34470910341`. No C/A thresholds changed and EXH2 was not applied.

| Execution | Filter | Eligible | Entries | PF | PF ex-top10 | Target | Stop |
|---|---|---:|---:|---:|---:|---:|---:|
| X1 | BASE | 10,731 | 5,777 | 1.093 | 1.082 | 30.95% | 68.98% |
| X1 | C | 703 | 382 | 1.056 | 0.949 | 30.37% | 69.63% |
| X1 | C+A | 2 | 2 | 0.000 | n/a | 0.00% | 100.00% |
| X3 | BASE | 10,731 | 3,604 | 1.163 | 1.146 | 32.77% | 67.18% |
| X3 | C | 703 | 238 | 1.020 | 0.861 | 30.25% | 69.75% |
| X3 | C+A | 2 | 2 | 0.000 | n/a | 0.00% | 100.00% |

X3+C coarse-subperiod PFs with trades were approximately 1.49, 1.41, 0.44 and 1.74, but PF ex-top10 was below 1 in every such subperiod (~0.72, ~0.74, ~0.11, ~0.45). X3+C top-symbol trade share was ~2.5% and top-five share ~9.7%, versus ~0.4% and ~2.0% for baseline.

Verdict for R2-C: **hard C-v1 filtering is not supported as an additive trading edge in this evidence.** It lowers both raw PF and PF ex-top10 under X3, with the same direction under X1. C-v1 remains a frozen CAN SLIM descriptor and its threshold must not be tuned post hoc.

Verdict for R2-CA: **insufficient sample.** Only two C+A candidate events exist and both stop under both controls. This cannot establish that A is harmful or useful; it establishes that the strict C+A intersection is too sparse for a reliable historical strategy claim in this dataset.

Evidence artifact: `fundamental-ablation-v1-34481587218`, artifact SHA-256 `9a4018cad0f8dc35439633065520d2e4d829fc835c6bfd099cdbbf4e9c1f154a`.

Detailed decision record: `docs/decisions/2026-09-10-fundamental-ablation-v1.md`.

## Robustness requirements for later strategy claims

At minimum: trade count, PF, PF ex-top10, portfolio return, max drawdown, subperiod stability, sector/symbol concentration, MAE/MFE, fill rate and opportunity cost.

## Anti-data-mining rule

Every experiment must distinguish pre-specified rules, exploratory diagnostics, and post-hoc findings. A changed threshold or rule must be versioned as a new hypothesis and independently validated; it cannot be retrofitted into a completed experiment.
