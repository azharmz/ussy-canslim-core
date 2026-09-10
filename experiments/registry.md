# Experiment Registry

Use this file to register experiments before execution. Every experiment should pin immutable inputs and record a verdict after review.

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
| E0 | Expanded exact legacy baseline | PLANNED | Measure effect of expanding beyond legacy ~199 universe without changing strategy rules |
| E1 | Signal-day shock diagnostics | PLANNED | Test relationship between T-1->T0 move and post-entry outcomes |
| E2 | H+1 execution-gap diagnostics | PLANNED | Test execution gap and retracement risk |
| E3 | Pivot extension 3/5/8% | PLANNED | Test pre-specified signal extension caps |
| E4 | Actual fill pivot extension | PLANNED | Measure executable H+1 extension from pivot |
| E5 | Entry-quality interactions | PLANNED | Separate/measure shock + gap + extension interactions |
| E6 | Entry outcome robustness | PLANNED | MAE/MFE/PF/DD/subperiod/concentration review |
| C1 | C label distribution | BLOCKED | Run after C-v1 methodology freeze; no trading-performance optimization |
| A1 | A label distribution | BLOCKED | Run after A-v1 methodology freeze |
| R2-C | Baseline + C ablation | BLOCKED | Incremental value of C |
| R2-CA | Baseline + C + A ablation | BLOCKED | Incremental value of C+A |
| R2-EC | Entry rule + C | BLOCKED | Interaction of entry discipline and C |
| R2-ECA | Entry rule + C + A | BLOCKED | Combined candidate framework |

## Primary robustness metrics

At minimum:

- trade count;
- profit factor;
- PF ex-top10;
- return;
- max drawdown;
- results by subperiod;
- sector concentration;
- symbol concentration.

For Entry Quality studies also include MAE, MFE, stop rate, trend-exit rate, holding period and relevant continuous-variable distributions.

## Rule against data-mining

An experiment specification must distinguish:

- pre-specified primary rule/threshold;
- exploratory diagnostics;
- post-hoc findings.

A post-hoc finding is not a production candidate until independently specified and validated on untouched data/forward evidence.
