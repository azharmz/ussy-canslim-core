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
| E1 | Signal-day shock diagnostics | COMPLETE / EXPLORATORY | T-1→T0 shock mechanism |
| E2 | H+1 execution-gap diagnostics | COMPLETE / EXPLORATORY | execution gap mechanism |
| E3 | Pivot extension 3/5/8% | COMPLETE / EXPLORATORY | pre-specified extension diagnostics |
| E4 | Actual-fill pivot extension | COMPLETE / EXPLORATORY | fill-aware chasing diagnostic |
| ET1 | X1-X4 entry timing basis test | COMPLETE / VALIDATED | executable daily-EOD entry baseline |
| EXH1 | Post-breakout exhaustion diagnostic | COMPLETE / EXPLORATORY | T-1→T0 shock × T+1 rejection discovery |
| EXH2 | Prospective exhaustion validation | **PRE-REGISTERED / LIVE** | independently validate EXH1 mechanism on post-2026-09-11 evidence |
| CA-PERIOD | C/A period-semantics audit | COMPLETE / PASS | latest-quarter/FY state selection |
| CA-HIST | Historical C/A attachment | COMPLETE / VALIDATED | causal C/A state with SEC FY identity |
| R2-C | Preferred baseline + C | COMPLETE / VALIDATED DESCRIPTIVE | incremental value of C |
| R2-CA | Preferred baseline + C+A | COMPLETE / SPARSE | incremental value of C+A |
| PORT1 | Frozen portfolio construction | COMPLETE / VALIDATED DESCRIPTIVE | capital-constrained X3 vs X1 |
| ROB1 | Historical strategy robustness | COMPLETE / VALIDATED HISTORICAL | retrospective robustness; not true OOS |
| FWD1 | Genuine forward validation | **LIVE / ACCUMULATING** | frozen post-2026-09-09 validation; data gate passed |

## Core frozen evidence

### C1 / A1

Workflow `34431101727` = SUCCESS. Pinned manifest: `fundamentals/snapshots/2026-09-09/run-34417104650/manifest.json`.

```text
C-v1   PASS 69 | FAIL 520 | NOT_EVALUABLE 312
A-v1   PASS 11 | FAIL 483 | NOT_EVALUABLE 407
C+A    PASS  3 | FAIL 437 | NOT_EVALUABLE 461
```

Thresholds remain frozen.

### TB1 / E0

Historical engine produced 10,731 technical candidates across 860 securities on the frozen current-compliant research universe.

### ET1 — Entry Timing Basis Test v1

Workflow `34464861119` = SUCCESS.

| Variant | Entries | PF | PF ex-top10 |
|---|---:|---:|---:|
| X1 | 5,777 | 1.093 | 1.082 |
| X2 | 6,158 | 1.096 | 1.086 |
| **X3** | **3,604** | **1.163** | **1.146** |
| X4 | 4,216 | 1.109 | 1.093 |

X3 pivot-hold is the preferred frozen research execution baseline; X1 remains mandatory control.

### EXH1 — Post-breakout exhaustion discovery

Workflow `34466747136` = SUCCESS. Highest shock quintile plus T+1 bearish-and-below-T0 rejection had X1 PF about 0.56 and stop rate about 80.8%. High-shock observations without that rejection were materially stronger. This remains exploratory discovery evidence.

The EXH1 80th-percentile shock boundary is `0.0533333333333332` (+5.3333%). It is transferred once into EXH2 as the frozen operational definition of “extreme shock”; EXH2 does not search alternative cutoffs.

### EXH2 — Prospective exhaustion validation

Pre-registration: `docs/methodology/exhaustion-validation-v2.md`.

Collector: `scripts/run_exhaustion_validation_v2.py`.

Workflow: `.github/workflows/exhaustion-validation-v2.yml`.

Prospective signal boundary:

```text
signal_date > 2026-09-11
```

Frozen hypothesis:

```text
extreme_shock = T0/T-1 - 1 >= 0.0533333333333332
T+1 rejection = Close(T+1) < Open(T+1) AND Close(T+1) < Close(T0)
primary endpoint = breakdown below pivot by T+3
expected direction = rejected rate > non-rejected rate
```

A row is mature only when T+1, T+2, and T+3 exist. Review eligibility requires >=50 mature extreme-shock rejected observations and >=50 mature extreme-shock non-rejected controls.

EXH2 is diagnostic only. Because T+1 rejection is not observable at T+1 Open, it cannot alter frozen FWD1 execution. Any trading rule inspired by EXH2 requires a new versioned validation track.

### CA-PERIOD / CA-HIST

CA period-semantics audit `34434268817` = SUCCESS. Historical attachment `34479060107` = SUCCESS.

```text
C-v1   PASS 703 | FAIL 3,475 | NOT_EVALUABLE 6,553
A-v1   PASS  34 | FAIL   768 | NOT_EVALUABLE 9,929
C+A    PASS   2 | FAIL   650 | NOT_EVALUABLE 10,079
```

### R2-C / R2-CA — Fundamental Ablation v1

Workflow `34481587218` = SUCCESS.

| Execution | Filter | Entries | PF | PF ex-top10 |
|---|---|---:|---:|---:|
| X1 | BASE | 5,777 | 1.093 | 1.082 |
| X1 | C | 382 | 1.056 | 0.949 |
| X1 | C+A | 2 | 0.000 | n/a |
| X3 | BASE | 3,604 | 1.163 | 1.146 |
| X3 | C | 238 | 1.020 | 0.861 |
| X3 | C+A | 2 | 0.000 | n/a |

C/A remain descriptors, not hard performance filters.

## PORT1 — Portfolio Construction v1

Canonical workflow `34488197400` = SUCCESS.

```text
X1 portfolio entries = 1,424
X3 portfolio entries = 1,129
X3 gross CAGR ≈ 3.04%
X3 gross max DD ≈ -43.36%
X3 CAGR @20bp RT ≈ 2.40%
X3 max DD @20bp RT ≈ -50.94%
```

Absolute historical economics remain weak.

## ROB1 — Historical Robustness v1

Workflow `34488295631` = SUCCESS. ROB1 is retrospective historical evidence only, not OOS.

```text
X1 accepted PF ≈ 1.060
X3 accepted PF ≈ 1.162
SPY price-only CAGR ≈ 8.80%
X3 gross CAGR ≈ 3.04%
```

No historical tuning is reopened from ROB1.

## FWD1 — Genuine forward validation

Methodology: `docs/methodology/forward-validation-v1.md`.

Canonical current run `34568992370` = SUCCESS.

```text
forward boundary exclusive = 2026-09-09
first forward session = 2026-09-10
market_data_asof = 2026-09-10
data_gate_pass = true
status = ACCUMULATING
forward_candidate_count = 0
closed_x3_portfolio_trades = 0
completed_calendar_months = 0
```

The zero candidate observation for 2026-09-10 is interpretable because the source-freshness gate passed.

Formal review requires both:

```text
>= 12 completed calendar months
>= 50 closed X3 portfolio trades
```

Passing the gate means `REVIEW_ELIGIBLE`, never automatic production promotion.

## Anti-data-mining rule

Every experiment must distinguish pre-specified rules, exploratory diagnostics, and post-hoc findings. A changed threshold or rule must be versioned as a new hypothesis and independently validated. EXH2 cannot modify FWD1, and FWD1 interim outcomes cannot change frozen FWD1 rules.
