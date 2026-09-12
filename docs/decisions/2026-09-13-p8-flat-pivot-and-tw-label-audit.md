# P8 decision — flat-base pivot semantics and Tradeweb label audit

Date: 2026-09-13
Scope: #33 O'Neil Pattern Recognition Engine, DEVELOPMENT morphology only

## Decision

1. Withdraw `p8-label-0003` (Tradeweb/TW) from the frozen DEVELOPMENT label set.
2. Promote the flat-base persisted pivot semantic from v0.2 to `p8-v0.3-development-flat-pivot-correction`.
3. Keep NFLX `p8-label-0002` locked in VALIDATION and unread by DEVELOPMENT comparison.

## Why the TW label was withdrawn

The public IBD evidence verifies that Tradeweb formed a second-stage flat base, rebounded from its 50-day moving average on 2024-11-06, and broke out on 2024-11-20 from a 136.13 entry. The evidence inspected during the audit does not support the previously preregistered exact `2024-10-09` start. That date had been inferred by subtracting six calendar weeks rather than anchored to a published exact base boundary.

An inferred boundary must not be promoted to an authoritative DEVELOPMENT label. TW therefore returns to adjudication rather than being used to tune or score the detector.

## Flat-base pivot correction

The v0.1/v0.2 flat-base detector already used an early/left-side high to enforce containment, but persisted the maximum high over the full rolling window as `flat_left_high` and pivot. When a recognition window included a breakout session, the breakout-day new high could therefore redefine the structural pivot.

That is internally inconsistent with the frozen #27 contract: a flat-base pivot is the established prior/base high that price must clear, not the new high printed after crossing it.

v0.3 preserves the preregistered duration, depth, prior-uptrend and containment gates. It changes only the persisted flat-base pivot landmark:

- derive `flat_left_high` from the same first-third left-side zone already used by the containment gate;
- persist that earlier high as `pivot_level` / `pivot_source_date`;
- never let an optional breakout-day new high silently become the structural pivot.

This correction is theory/semantics-driven and was not selected from CAGR, profit factor, returns, or any post-event performance outcome.

## Validation contract

A regression fixture now requires that a modest breakout-day new high may remain inside the allowed recognition window without becoming the persisted flat-base pivot.

The authoritative evaluator remains raw-window-first, then maps the selected emitted window back to stable `base_id` / lineage. If a source does not provide a detector-comparable pivot anchor, the evaluator records `pivot_validation_state=SOURCE_NOT_PROVIDED` and must not imply full landmark validation.
