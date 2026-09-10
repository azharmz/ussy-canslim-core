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
| ET1 | **X1-X4 entry timing basis test** | **COMPLETE / VALIDATED** | choose executable daily-EOD entry baseline before fundamental ablation |
| CA-PERIOD | C/A period-semantics audit | COMPLETE / PASS | latest-quarter/FY state selection |
| CA-HIST | Historical C/A attachment | NEXT | causal C/A state at each signal |
| R2-C | Preferred technical baseline + C | BLOCKED | incremental value of C after CA-HIST |
| R2-CA | Preferred technical baseline + C+A | BLOCKED | incremental value of C+A after CA-HIST |
| PORT1 | Portfolio construction | PLANNED | sizing/max positions/equity curve |
| ROB1 | Strategy robustness/holdout | BLOCKED | PF ex-top10, DD, subperiod, concentration |

## C1/A1

Workflow run `34431101727` = **SUCCESS**.

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

CI run `34431906311` = **SUCCESS**.

Verdict: independent technical baseline executable and frozen.

## E0 / E1-E4

Historical technical candidate engine on research universe frozen at `universe/membership/2026-08-28.json`:

- candidate events: **10,731**
- candidate securities: **860**

E1-E4 workflow run `34433673545` = **SUCCESS**.

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

Workflow run `34464861119` = **SUCCESS**; timing/execution tests: **13 passed**.

Research universe: frozen contemporary/current Musaffa-compliant universe at 2026-08-28. Historical Musaffa status is not a strategy input to this research question.

All variants share:

```text
stop = actual fill * 0.93
target = pivot * 1.20
same-bar ambiguity = stop-first
no time stop
```

Results:

| Variant | Entries | Fill rate | PF | PF ex-top10 | Target rate | Stop rate |
|---|---:|---:|---:|---:|---:|---:|
| X1 | 5,777 | 53.83% | 1.093 | 1.082 | 30.95% | 68.98% |
| X2 | 6,158 | 57.39% | 1.096 | 1.086 | 31.02% | 68.89% |
| **X3** | **3,604** | **33.58%** | **1.163** | **1.146** | **32.77%** | **67.18%** |
| X4 | 4,216 | 39.29% | 1.109 | 1.093 | 30.95% | 69.00% |

Subperiod robustness: X3 > X1 in 4/5 coarse periods and 22/34 years with observations for both.

Mechanism check:

- 2,775 events traded by both X1 and X3: X1 PF ~1.224; X3 PF ~1.172;
- 3,002 X1 trades not shared with X3: PF ~0.982.

Interpretation: X3's advantage is mainly **selection by pivot-hold confirmation**, not better delayed fills on the same opportunities.

**Verdict:** promote **X3 pivot-hold** to preferred research execution baseline; retain X1 as control. Do not tune X3/X4 parameters on this same evidence set.

Detailed record: `results/entry-timing-basis-test-v1/README.md`.

## CA period semantics

Audit run `34434268817` = **SUCCESS**.

At each decision cutoff:

- restrict SEC evidence to `accepted_at <= cutoff`;
- for C, select latest fiscal quarter known at cutoff, then latest accepted state within that quarter;
- older-period amendments cannot displace newer fiscal periods merely because accepted later;
- for A, select latest accepted annual state per FY and then latest three consecutive FY growth states;
- undefined growth remains NOT_EVALUABLE.

## Robustness requirements for later strategy claims

At minimum: trade count, PF, PF ex-top10, portfolio return, max drawdown, subperiod stability, sector/symbol concentration, MAE/MFE, fill rate and opportunity cost.

## Anti-data-mining rule

Every experiment must distinguish pre-specified rules, exploratory diagnostics, and post-hoc findings. A changed threshold or rule must be versioned as a new hypothesis and independently validated; it cannot be retrofitted into a completed experiment.
