# Decision — #34 starts only as frozen #33 production consumer

Date: 2026-09-13
Status: ACTIVE / IMPLEMENTATION STARTED

## Decision

#34 Theory-Faithful Candidate Generator consumes only `azharmz/ussy-oneil-patterns` schema `oneil-pattern-output-v2`.

Production pattern scope is frozen to:

- `FLAT_BASE`
- `DOUBLE_BOTTOM`
- `CUP_WITHOUT_HANDLE`
- `CUP_WITH_HANDLE`

`ASCENDING_BASE` and `BASE_ON_BASE` remain outside production under the #33 P6 terminal verdict `DEFERRED / NOT PRODUCTION-VALIDATED / FROZEN UNTIL NEW AUTHORITATIVE MORPHOLOGY EVIDENCE EXISTS`.

#34 must not import, copy, extend, or tune the historical pattern detector/evaluator implementation that remains in the CAN SLIM parent repository. Pattern recognition authority is exclusively `ussy-oneil-patterns`.

## Preservation rule

The consumer preserves without reinterpretation:

- `normalized_status` (`RECOGNIZED`, `AMBIGUOUS`, `REJECTED`);
- `candidate_id`;
- `base_id`;
- `lineage_id`;
- `candidate_semantics`;
- detector faults;
- pattern-engine/contract provenance.

`AMBIGUOUS` is retained as explicit evidence and is not silently promoted to `BASE_RECOGNIZED` or collapsed to no-pattern.

## Candidate stages

The frozen #32 boundary remains:

```text
BASE_RECOGNIZED
-> PIVOT_DEFINED
-> PIVOT_CROSSED
-> BREAKOUT_CONFIRMED
-> CANSLIM_ELIGIBLE
```

A pattern assessment, breakout event, confirmed breakout, and CAN SLIM eligibility are distinct facts. A failure at a later stage must not erase an earlier valid state.

## Initial implementation

`src/canslim_research/candidate_v2.py` is the new #34 consumer boundary. It:

1. validates `oneil-pattern-output-v2` and rejects patterns outside the four-core production contract;
2. preserves identity, ambiguity, detector faults, and provenance;
3. derives pivot-cross facts from daily OHLCV without changing the upstream pivot;
4. computes the frozen breakout-volume benchmark from the prior 50 completed sessions, excluding the breakout session;
5. attaches C/A/L/M eligibility states supplied by versioned upstream adapters;
6. preserves N/S/I/industry states as evidence rather than silently making them universal hard gates.

This is intentionally separate from legacy `pattern_engine.py`, `pattern_identity.py`, `pattern_lineage.py`, and related historical #33 code in the parent repository.

## Open #34 work

Before #34 can be frozen/closed:

- connect the production pattern stream/runner output to the consumer rather than relying on hand-built mappings;
- connect PIT daily R2 OHLCV to breakout evaluation;
- freeze the exact theory-supported A annual-growth adapter required by #32;
- connect C PIT evidence;
- connect/version L individual RS proxy and M entry-state adapters;
- attach N/S/I/industry evidence with explicit evaluability semantics;
- add chronology/PIT tests and end-to-end fixtures;
- run CI and document the final #34 output contract.

No return, CAGR, PF, FWD1, breakout-success, or execution outcome may be used to alter frozen #33 morphology or choose #34 theory parameters.
