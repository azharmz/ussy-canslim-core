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
| R2-C | Preferred technical baseline + C | COMPLETE / VALIDATED DESCRIPTIVE | incremental value of C after validated CA-HIST |
| R2-CA | Preferred technical baseline + C+A | COMPLETE / SPARSE | incremental value of C+A; sample too small for strategy inference |
| PORT1 | Frozen portfolio construction | **COMPLETE / VALIDATED DESCRIPTIVE** | capital-constrained X3 BASE vs X1 BASE; portfolio return/DD/cost sensitivity |
| ROB1 | Strategy robustness / holdout | **NEXT / PRE-REGISTRATION REQUIRED** | accepted-portfolio robustness, benchmark context, holdout/forward validation |

## Core frozen evidence

### C1 / A1

Workflow `34431101727` = SUCCESS. Pinned manifest: `fundamentals/snapshots/2026-09-09/run-34417104650/manifest.json`.

```text
C-v1   PASS 69 | FAIL 520 | NOT_EVALUABLE 312
A-v1   PASS 11 | FAIL 483 | NOT_EVALUABLE 407
C+A    PASS  3 | FAIL 437 | NOT_EVALUABLE 461
```

Thresholds remain frozen; no trading metrics were used.

### TB1 / E0

Independent technical baseline is implemented in `src/canslim_research/technical.py`; CI `34431906311` = SUCCESS. Historical engine produced 10,731 technical candidates across 860 securities on the frozen current-compliant research universe.

### ET1 — Entry Timing Basis Test v1

Workflow `34464861119` = SUCCESS; 13 timing/execution tests passed.

| Variant | Entries | PF | PF ex-top10 | Target | Stop |
|---|---:|---:|---:|---:|---:|
| X1 | 5,777 | 1.093 | 1.082 | 30.95% | 68.98% |
| X2 | 6,158 | 1.096 | 1.086 | 31.02% | 68.89% |
| **X3** | **3,604** | **1.163** | **1.146** | **32.77%** | **67.18%** |
| X4 | 4,216 | 1.109 | 1.093 | 30.95% | 69.00% |

Verdict: X3 pivot-hold is the preferred research execution baseline; X1 remains mandatory control. Mechanism evidence indicates X3 mainly filters weak breakout attempts rather than improving fill on the same events.

### EXH1 — Post-breakout exhaustion diagnostic

Workflow `34466747136` = SUCCESS. Highest shock quintile + T+1 bearish rejection had X1 PF ~0.56 and ~80.8% stop rate, while high shock without rejection had PF ~1.57. Verdict: `large T0 expansion × T+1 rejection` is an exploratory exhaustion mechanism. No hard cutoff is adopted from this discovery sample.

### CA-PERIOD / CA-HIST

CA period-semantics audit `34434268817` = SUCCESS. Historical attachment `34479060107` = SUCCESS using explicit SEC FY identity and `accepted_at <= T0 cutoff`.

```text
C-v1   PASS 703 | FAIL 3,475 | NOT_EVALUABLE 6,553
A-v1   PASS  34 | FAIL   768 | NOT_EVALUABLE 9,929
C+A    PASS   2 | FAIL   650 | NOT_EVALUABLE 10,079
```

Every A-PASS row has exactly three resolved consecutive FY; future accepted-at violations = 0. Detailed decision record: `docs/decisions/2026-09-10-historical-ca-attachment-v1.md`.

### R2-C / R2-CA — Fundamental Ablation v1

Workflow `34481587218` = SUCCESS; artifact SHA-256 `9a4018cad0f8dc35439633065520d2e4d829fc835c6bfd099cdbbf4e9c1f154a`.

| Execution | Filter | Entries | PF | PF ex-top10 |
|---|---|---:|---:|---:|
| X1 | BASE | 5,777 | 1.093 | 1.082 |
| X1 | C | 382 | 1.056 | 0.949 |
| X1 | C+A | 2 | 0.000 | n/a |
| X3 | BASE | 3,604 | 1.163 | 1.146 |
| X3 | C | 238 | 1.020 | 0.861 |
| X3 | C+A | 2 | 0.000 | n/a |

Verdict: hard C-v1 filtering is not supported as additive trading edge; C+A is too sparse for inference. C/A remain frozen descriptors and thresholds must not be tuned post hoc. Detailed decision record: `docs/decisions/2026-09-10-fundamental-ablation-v1.md`.

## PORT1 — Portfolio Construction v1

Pre-registration: `docs/methodology/portfolio-construction-v1.md`, frozen before outcome review.

Specification: initial equity 100,000; long-only/no leverage; max 7 positions; each new target notional = 1/7 prior-session closing equity; no partial fills; priority `rs_percentile DESC`, `volume_ratio DESC`, ticker ASC; morning entries allocated before same-day exits; X3 BASE primary, X1 BASE control; C/A and EXH2 excluded.

Final validated workflow `34485765478` = SUCCESS. Code head `c51b7b6644aec91767b5bd2767d0b11e6ac45077`. Artifact `portfolio-construction-v1-34485765478`, SHA-256 `a0a019b666ba3cd18d23cd78366a3c645053d5f051c69b0e83a9f3e0b033fa40`.

Censored-accounting invariant passed: X1 has 4 and X3 has 2 final censored positions, all exactly at 2026-09-09; mid-sample censored positions = 0; final censored positions are mark-to-market, not forced exits, and no phantom exit cost is charged.

| Metric | X1 BASE | X3 BASE |
|---|---:|---:|
| Candidate trades | 5,777 | 3,604 |
| Portfolio entries | 1,424 | 1,129 |
| Capacity skips | 1,010 | 564 |
| Cash skips | 3,343 | 1,911 |
| Gross total return | +30.70% | **+172.90%** |
| Gross CAGR | +0.83% | **+3.04%** |
| Gross max DD | -66.89% | **-43.36%** |
| Cost20bp total return | -20.86% | **+121.37%** |
| Cost20bp CAGR | -0.70% | **+2.40%** |
| Cost20bp max DD | -85.78% | **-50.94%** |
| Median positions | 5 | 4 |
| Median gross exposure | 70.5% | 59.1% |
| Top-1 abs PnL contribution | 1.04% | 1.46% |
| Top-5 abs PnL contribution | 4.56% | 5.21% |

Entry accounting reconciles exactly: accepted + capacity skips + cash skips = candidate trade count for both X1 and X3.

Verdict: X3 retains a clear relative advantage under capital constraints, but the absolute risk-adjusted profile remains weak. About 3.0% gross CAGR with ~43% max DD, and ~2.4% CAGR with ~51% max DD under 20 bps round-trip cost sensitivity, is not production-ready evidence. X1 becomes negative-CAGR after costs.

Detailed decision record: `docs/decisions/2026-09-10-portfolio-construction-v1.md`.

## ROB1 — Next gate

Before interpreting holdout evidence, pre-register the split/protocol and keep all PORT1 rules unchanged. Required remaining work includes accepted-portfolio MAE/MFE, opportunity cost from skipped candidates, annual/subperiod stability, benchmark-relative context, and genuine holdout/forward validation. EXH2 remains a separate hypothesis.

## Anti-data-mining rule

Every experiment must distinguish pre-specified rules, exploratory diagnostics, and post-hoc findings. A changed threshold or rule must be versioned as a new hypothesis and independently validated; it cannot be retrofitted into a completed experiment.
