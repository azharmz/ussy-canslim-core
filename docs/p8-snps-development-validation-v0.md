# P8 SNPS Authoritative DEVELOPMENT Validation v0

Date: 2026-09-12

Status: **DEVELOPMENT CASE PASSED / FROZEN**

This note records the first authoritative morphology-validation case for #33 O'Neil Pattern Recognition Engine. It is morphology evidence only; no post-breakout return, CAGR, PF, FWD1, or other outcome evidence was inspected or used.

## Frozen authoritative label

- example: `p8-label-0001`
- security: SNPS / Synopsys
- source: Investor's Business Daily
- named pattern: `FLAT_BASE`
- source base anchor: 2023-04-04
- source breakout date: 2023-05-18
- expected structural pivot source date: 2023-04-04
- expected structural pivot level: 392.79
- split: `DEVELOPMENT`

The authoritative source label and anchors were recorded before detector comparison.

## Data route

- selected source: R2
- security_id: `US8716071076`
- R2 object: `backtest/ohlcv/US8716071076.parquet`
- external fallback: not used
- detector input is truncated at the label `asof_date`; future bars are not supplied.

## Final v0.4 agreement

The frozen detector emitted a raw Flat Base window with:

- detected start: 2023-04-04
- detected end / breakout-ready date: 2023-05-17
- detected pivot source date: 2023-04-04
- detected pivot: approximately 392.79000854

Agreement:

- named pattern: MATCH
- start error: 0 calendar days
- end error: 1 calendar day
- pivot-date error: 0 calendar days
- pivot-price error: approximately 0.000002%
- final state: `MATCH`

The matched emitted window maps to stable `base_id = base_f4e321a93cf8dce2` and `lineage_id = lineage_dead150a96867922`.

## Evaluator semantics learned from this case

`BaseIdentity` and `BaseLineage` are intentionally many-to-one summaries of rolling detector windows. Their representatives can discard the exact start/end boundaries of another member window even when that raw window was correctly emitted by the detector.

Therefore P8 evaluator v0.4 scores **raw windows actually emitted by the frozen detector**, then maps the selected window back to its stable base identity and lineage for auditability. It does not synthesize a new base, change detector output, relax preregistered tolerances, or use outcome data.

This is an evaluator/data-model correction, not a morphology-rule optimization.

## Freeze decision

SNPS is now frozen as the first successful authoritative DEVELOPMENT case. Do not tune it further unless a later cross-example contradiction demonstrates that the detector/evaluator semantics are internally inconsistent.

`p8-label-0002` NFLX remains `VALIDATION` and must remain untouched until DEVELOPMENT work is frozen.
