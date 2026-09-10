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
| E0-SMOKE | Rolling expanded technical baseline | COMPLETE / VALIDATED SMOKE | Validate end-to-end technical candidate generation on current ready universe; not PIT performance evidence |
| E0 | Independent expanded technical baseline | INPUT AUDIT / FULL PIT PENDING | Establish baseline performance on longest defensible PIT-membership window |
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

## E0-SMOKE execution record

Workflow run: `34432960298` = **SUCCESS**.

Code runner: `scripts/run_e0_rolling_baseline.py`.

Evidence record: `results/e0-rolling-baseline-v1/README.md`.

Pinned ready data:
- `production/ready/runs/2ef1b2ca8f9f44aba62d0552884e06c6.parquet`
- SHA256 `c1ed91508642acd604e73f2cb79cf8027fd91ea644acab0bb806cf7e12f237a4`
- ready snapshot date `2026-08-28`

Pinned SPY:
- `benchmarks/SPY/runs/97aa9dd852e743da93cc611c6d58c3cb.parquet`
- SHA256 `1fb495068c5392108cde7d49d4dae8e1d842dde0b01e29af8f64e477525350d4`

Observed smoke counts:

```text
ready securities                 1,223
ready OHLCV rows               366,411
feature-evaluable rows          58,216
feature-evaluable dates             77
technical candidate rows            14
technical candidate symbols         13
technical candidate dates            7
```

Entry-quality continuous diagnostics were retained for candidate rows (`T-1->T0`, H+1 gap, T0 pivot extension, H+1 fill extension) but were not used as filters.

**Evidence class:** `ROLLING_CURRENT_MEMBERSHIP_SMOKE_NOT_FULL_PIT_BACKTEST`.

**Verdict:** PASS as implementation/data-contract smoke. Do not use this run for PF/CAGR/drawdown or strategy-selection claims. Full E0 remains pending historical membership audit and full-history reconstruction.

## Robustness metrics for later trading experiments

At minimum: trade count, PF, PF ex-top10, return, max drawdown, results by subperiod, sector concentration, symbol concentration. Entry-quality studies also include MAE, MFE, stop rate, trend-exit rate, holding period and continuous-variable distributions.

## Anti-data-mining rule

Every experiment must distinguish pre-specified rules, exploratory diagnostics, and post-hoc findings. A post-hoc finding is not a production candidate until independently specified and validated on untouched evidence.
