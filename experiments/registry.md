# Experiment Registry

Use this file to register experiments before execution. Completed experiments must pin immutable inputs and record a verdict.

## Required fields

```text
experiment_id
status
hypothesis
strategy_baseline
universe_snapshot
fundamentals_snapshot
fundamentals_manifest_checksum
code_commit
config_path
date_range
holdout_protocol
trade_log
result_artifacts
primary_metrics
verdict
notes
```

## Registered experiments

| ID | Experiment | Status | Primary purpose |
|---|---|---|---|
| C1 | C label distribution | COMPLETE / VALIDATED | Measure C-v1 PASS/FAIL/NOT_EVALUABLE without trading metrics |
| A1 | A label distribution | COMPLETE / VALIDATED | Measure A-v1 PASS/FAIL/NOT_EVALUABLE without trading metrics |
| TB1 | Independent technical baseline specification + rule engine | COMPLETE / FROZEN | Freeze transparent N/S/L/M proxies before performance testing |
| E0 | Independent expanded technical baseline | READY TO IMPLEMENT | Establish baseline performance on expanded PIT universe |
| E1 | Signal-day shock diagnostics | PLANNED | T-1->T0 move vs post-entry outcomes |
| E2 | H+1 execution-gap diagnostics | PLANNED | execution gap vs retracement/outcomes |
| E3 | Pivot extension 3/5/8% | PLANNED | pre-specified signal extension caps |
| E4 | Actual fill pivot extension | PLANNED | executable H+1 extension from pivot |
| E5 | Entry-quality interactions | PLANNED | shock + gap + extension interactions |
| E6 | Entry outcome robustness | PLANNED | MAE/MFE/PF/DD/subperiod/concentration |
| R2-C | Technical baseline + C | BLOCKED | incremental value of C; requires E0 + historical PIT C labels |
| R2-CA | Technical baseline + C + A | BLOCKED | incremental value of C+A; requires E0 + historical PIT C/A |
| R2-EC | Entry rule + C | BLOCKED | interaction of entry discipline and C |
| R2-ECA | Entry rule + C + A | BLOCKED | combined candidate framework |

## C1/A1 execution record

- Workflow run: `34431101727`
- Result: **SUCCESS**
- Fundamentals manifest: `fundamentals/snapshots/2026-09-09/run-34417104650/manifest.json`
- Fundamentals source run: `34417104650`
- Production-ready denominator: `901`
- Trading metrics used: `false`

Distribution:

```text
C-v1   PASS 69 | FAIL 520 | NOT_EVALUABLE 312
A-v1   PASS 11 | FAIL 483 | NOT_EVALUABLE 407
C+A    PASS  3 | FAIL 437 | NOT_EVALUABLE 461
```

C+A PASS: `FIX`, `NBIX`, `NVDA`.

**Verdict:** distribution study is operationally valid; do not tune frozen C-v1/A-v1 thresholds from these counts.

## TB1 execution record

Specification: `docs/methodology/technical-baseline-v1.md`

Implementation: `src/canslim_research/technical.py`

Unit tests: `tests/test_technical.py`

CI workflow: `Technical baseline v1 tests`

- first CI run `34431864161`: failed on exact 5% floating-point boundary;
- implementation corrected to compare `close > pivot * 1.05` directly;
- validation run `34431906311`: **SUCCESS**.

**Verdict:** technical baseline v1 rule semantics are frozen and executable. This is an independent CAN SLIM baseline, not TrendFoll production logic.

## Robustness metrics for later trading experiments

At minimum: trade count, PF, PF ex-top10, return, max drawdown, results by subperiod, sector concentration, symbol concentration. Entry-quality studies also include MAE, MFE, stop rate, trend-exit rate, holding period and continuous-variable distributions.

## Anti-data-mining rule

Every experiment must distinguish pre-specified rules, exploratory diagnostics, and post-hoc findings. A post-hoc finding is not a production candidate until independently specified and validated on untouched evidence.
