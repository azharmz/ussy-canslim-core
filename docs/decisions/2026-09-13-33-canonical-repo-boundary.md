# Decision — canonical repository boundary for #33 O'Neil Pattern Recognition Engine

Date: 2026-09-13
Status: FROZEN REPOSITORY BOUNDARY

## Decision

`azharmz/ussy-oneil-patterns` is the canonical implementation repository and source of truth for workstream **#33 — O'Neil Pattern Recognition Engine**, including P8 labelled morphology validation.

`azharmz/ussy-canslim-research` remains the parent/HQ repository. It owns the frozen #32 theory-faithful candidate specification, CAN SLIM roadmap, cross-workstream integration, and later #34+ research. It does not own a second #33 detector/evaluator implementation.

Canonical reconciliation was merged into `ussy-oneil-patterns` at:

`261d667eecf8525b27e8a15b6980ba698e609848`

## Background

During P8 development, substantial pattern-engine and morphology-validation work also accumulated inside this parent repository, including OHLCV routing, detector iterations, structural identity/lineage, conflict handling, labelled evaluation, and authoritative DEVELOPMENT examples.

That work produced useful evidence, but maintaining both repositories as active #33 implementations would create two competing definitions of the same engine.

## Treatment of existing parent #33/P8 work

Existing parent commits remain preserved as historical research/migration evidence. They are not deleted or rewritten as part of this boundary decision.

Useful evidence-model concepts and authoritative corpus rows were reconciled into the canonical oneil repository. The parent-specific detector stack, base identity/lineage implementation, duplicate conflict machinery, and workflow runners are not promoted as a parallel canonical implementation.

The parent result `5 MATCH / 5 AMBIGUOUS` is retained as migration evidence only. It does not become the final #33/P8 verdict until canonical oneil re-execution confirms or contradicts it.

## Continuation rule

Any future session working on #33/P8 must begin in `ussy-oneil-patterns`:

1. read its `README.md`;
2. read its `docs/progress-board.md`;
3. inspect latest #33/P8 decision records and commits;
4. continue only from the canonical active slice.

Do not resume #33 implementation from `feat/p8-labelled-development-v0` or other P8 branches in this parent repository.

## Validation lock

NFLX remains the untouched VALIDATION example. It must not be inspected or used for DEVELOPMENT tuning before canonical detector semantics freeze.

## Downstream rule

#34 Theory-Faithful Candidate Generator remains blocked until canonical #33/P8 has a defensible final morphology-validation verdict and frozen/versioned output contract.

## Cleanup rule

Removal, archival, or consolidation of duplicate parent workflow/code is a separate housekeeping task. It must occur only after unique evidence has been verified preserved and must not rewrite research history.
