# Experiment Registry

Use this file to register experiments before execution. Completed experiments must pin inputs, code/config, evidence class, and verdict.

## Registered experiments

| ID | Experiment | Status | Primary purpose |
|---|---|---|---|
| C1 | C label distribution | COMPLETE / VALIDATED | C-v1 distribution |
| A1 | A label distribution | COMPLETE / VALIDATED | A-v1 distribution |
| TB1 | Independent technical baseline | COMPLETE / FROZEN | transparent N/S/L/M proxy baseline |
| E0-SMOKE | Rolling technical smoke | COMPLETE / VALIDATED | end-to-end candidate generation |
| E0-HIST | Historical technical candidates | COMPLETE | establish frozen event set |
| E1-E4 | Entry-quality diagnostics | COMPLETE / EXPLORATORY | shock/gap/extension mechanisms |
| ET1 | X1-X4 entry timing basis test | COMPLETE / VALIDATED | executable daily-EOD entry baseline |
| EXH1 | Post-breakout exhaustion diagnostic | COMPLETE / EXPLORATORY | high-shock × T+1 rejection discovery |
| EXH2 | Prospective exhaustion validation | PRE-REGISTERED / LIVE | independent post-2026-09-11 validation |
| CA-PERIOD | C/A period-semantics audit | COMPLETE / PASS | PIT period selection |
| CA-HIST | Historical C/A attachment | COMPLETE / VALIDATED | causal C/A states |
| R2-C | Preferred baseline + C | COMPLETE / VALIDATED DESCRIPTIVE | incremental value of C |
| R2-CA | Preferred baseline + C+A | COMPLETE / SPARSE | incremental value of C+A |
| PORT1 | Frozen portfolio construction | COMPLETE / VALIDATED DESCRIPTIVE | capital-constrained X3 vs X1 |
| ROB1 | Historical strategy robustness | COMPLETE / VALIDATED HISTORICAL | retrospective robustness; not OOS |
| FULL-M1 | SPY+QQQ market-regime sidecar | COMPLETE / NOT PROMOTED | dual-index M test |
| I0 | SEC 13F sponsorship feasibility | COMPLETE / VALIDATED | identity/source feasibility |
| I1-DATA | SEC 13F PIT data pipeline | COMPLETE / VALIDATED | current + historical + uncertainty + R2 pointer |
| I1-ATTACH | Historical I-v1 PIT attachment | COMPLETE / VALIDATED | attach preregistered I state to candidates |
| I1-ABL | I-v1 hard-filter ablation | **COMPLETE / NOT PROMOTED** | test sponsorship-growth hard filter on X1/X3/PORT1 |
| FWD1 | Genuine forward validation | LIVE / ACCUMULATING | frozen post-2026-09-09 validation |

## Core frozen evidence

### Technical / execution baseline

Historical engine: **10,731 candidates / 860 securities**.

ET1 run `34464861119`:

| Variant | Entries | PF | PF ex-top10 |
|---|---:|---:|---:|
| X1 | 5,777 | 1.093 | 1.082 |
| X2 | 6,158 | 1.096 | 1.086 |
| **X3** | **3,604** | **1.163** | **1.146** |
| X4 | 4,216 | 1.109 | 1.093 |

X3 pivot-hold remains preferred; X1 remains mandatory control.

### C/A

CA-HIST run `34479060107`:

```text
C-v1   PASS 703 | FAIL 3,475 | NOT_EVALUABLE 6,553
A-v1   PASS  34 | FAIL   768 | NOT_EVALUABLE 9,929
C+A    PASS   2 | FAIL   650 | NOT_EVALUABLE 10,079
```

Fundamental ablation run `34481587218` showed hard C did not improve X3; C+A was too sparse. C/A remain descriptors.

### PORT1 / ROB1

PORT1 run `34488197400`:

```text
X1 portfolio entries = 1,424
X3 portfolio entries = 1,129
X3 gross CAGR ≈ 3.04%
X3 gross max DD ≈ -43.36%
X3 CAGR @20bp RT ≈ 2.40%
X3 max DD @20bp RT ≈ -50.94%
```

ROB1 run `34488295631` is retrospective historical evidence only. SPY price-only context CAGR ≈ 8.80%.

### FULL-M1

Run `34576910915` = SUCCESS. Dual SPY+QQQ M retained 7,694 of 10,731 candidates, added none, reduced X3 drawdown but reduced CAGR. It is a risk throttle, not an incremental edge source, and was not promoted. FWD1 remains SPY-only.

### EXH2

Pre-registration: `docs/methodology/exhaustion-validation-v2.md`.

```text
signal_date > 2026-09-11
extreme shock >= +5.3333%
T+1 rejection = Close(T+1) < Open(T+1) AND Close(T+1) < Close(T0)
primary endpoint = breakdown below pivot by T+3
```

EXH2 is diagnostic only and cannot alter frozen T+1 Open execution/FWD1.

## Institutional Sponsorship I-v1

### I0 feasibility

Run `34593720220` = SUCCESS. Deterministic mapping coverage:

```text
universe = 1,327
US-ISIN -> CUSIP9 = 1,010 (76.1%)
non-US deferred = 317
```

The earlier SEC/GitHub-runner blocker was resolved; do not treat it as current.

### I1 data pipeline

Current/live filing-level validation `34603142916` = SUCCESS:

```text
9,731 filings
100% fetch success
100% accepted_at coverage
100% period_of_report coverage
383/383 amendments classified
0 ambiguous lineage events
```

Historical event-state run `34654725293` = SUCCESS:

```text
53 / 53 official SEC datasets
313,055 filings
14,529,166 state-change events
53 unclassified amendment filings
0 new-holdings-without-valid-base
```

Uncertainty run `34656995462` = SUCCESS. Affected CUSIP-period states are quarantined rather than interpreted as zero.

Canonical R2 publish run `34663714292` = SUCCESS:

```text
pointer = institutional_sponsorship/current.json
manifest = institutional_sponsorship/snapshots/2026-09-12/run-34663714292/manifest.json
history source = 34654725293
uncertainty source = 34656995462
```

Historical information availability is conservatively `filing_date + 1 calendar day`; live uses exact EDGAR `accepted_at`.

### I-v1 frozen rule

Preregistered in `docs/methodology/institutional-sponsorship-growth-v1.md` before performance review:

```text
I_delta = latest manager count - prior manager count
PASS = I_delta > 0
FAIL = I_delta <= 0
NOT_EVALUABLE = missing / non-consecutive / unmapped / uncertain
```

No manager-count minimum, percentage-growth, shares, or value threshold was searched.

### I1-ATTACH

Run `34663929577` = SUCCESS:

```text
candidate count = 10,731
PASS = 1,902
FAIL = 2,888
NOT_EVALUABLE = 5,941
I-evaluable = 4,790
future-availability violations = 0
```

### I1-ABL

Canonical run `34664388792` = SUCCESS. Evidence is retrospective historical, not OOS.

Because SEC 13F history begins in 2013, the primary comparison is I_PASS against the **I_EVALUABLE control** (PASS+FAIL), not against the 1993–2026 all-history baseline.

Preferred X3:

| Metric | I_EVALUABLE | I_PASS |
|---|---:|---:|
| Candidates | 4,790 | 1,902 |
| X3 candidate trades | 1,596 | 671 |
| PF | 1.1194 | 1.1465 |
| PF ex-top10 | **1.0856** | **1.0711** |
| Portfolio entries | 475 | 331 |
| Gross CAGR | **2.96%** | **2.17%** |
| Gross max DD | **-28.19%** | **-39.02%** |
| CAGR @20bp RT | **2.07%** | **1.57%** |
| Max DD @20bp RT | **-31.97%** | **-43.08%** |

Verdict: **NOT PROMOTED as a hard filter**. Raw PF rises slightly, but PF ex-top10 declines and preferred X3 portfolio CAGR/drawdown both worsen. Institutional sponsorship remains a descriptor. No post-hoc I threshold search is opened.

Decision: `docs/decisions/2026-09-12-i1-historical-ablation.md`.

## FWD1

FWD1 remains frozen and unchanged:

```text
forward boundary exclusive = 2026-09-09
first forward session = 2026-09-10
status = ACCUMULATING
data_gate_pass = true
```

Formal review requires both >=12 completed calendar months AND >=50 closed X3 portfolio trades. Review eligibility is not automatic production promotion.

## Anti-data-mining rule

Every changed threshold/rule is a new hypothesis and requires preregistration plus independent validation. Historical C/A, FULL-M1, and I1 results cannot alter FWD1. Interim FWD1 outcomes cannot change frozen FWD1 rules. No retrospective tuning is reopened merely to improve benchmark-relative performance.
