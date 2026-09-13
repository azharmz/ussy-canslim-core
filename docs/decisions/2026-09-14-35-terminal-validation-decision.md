# #35 New-Candidate Validation — Terminal Governance Decision

Date: 2026-09-14

## Verdict

`CONDITIONAL PASS / VALIDATION COMPLETE WITH UPSTREAM #33 MORPHOLOGY DEBT PRESERVED`

#35 is complete and frozen. This verdict does not reopen or retune #33 or #34.

## Frozen inputs and governance

- #33 O'Neil Pattern Recognition Engine remains frozen in `azharmz/ussy-oneil-patterns`.
- #34 Theory-Faithful Candidate Generator remains frozen in this repository.
- Production pattern contract remains `oneil-pattern-output-v2` with only `FLAT_BASE`, `DOUBLE_BOTTOM`, `CUP_WITHOUT_HANDLE`, and `CUP_WITH_HANDLE`.
- P6 advanced patterns remain excluded from production.
- Validation discipline remained: authoritative development → freeze → untouched validation → one-shot validation → no post-validation tuning.
- Frozen 60-case corpus was not changed.

## Canonical historical validation

Canonical GitHub Actions run `34763920536` completed successfully.

- Historical observation pool: 265,642 observations.
- V35-A contract/schema validation: GREEN.
- V35-B chronology/PIT validation: GREEN.
- V35-C stage-transition validation: GREEN.
- Automated findings across the canonical pool: 0.
- Frozen corpus: 60 cases = 20 RECOGNIZED / 20 AMBIGUOUS / 20 REJECTED.

## V35-D identity and raw-bar audit

The final review packet reproduced all 60 frozen candidate identities with exactly one corresponding candidate per case.

- missing candidates: 0
- pattern mismatches: 0
- status mismatches: 0
- future bars: none
- first-cross chronology: 60/60 MATCH
- volume ratio: 60/60 MATCH
- final candidate stage: 60/60 MATCH

## Independent source-evidence audit

GitHub Actions run `34765922653` on commit `c89555efddc4224509f49e68abb0dd56d0ed8cef` completed **SUCCESS**.

The audit recomputed frozen-case source evidence from underlying historical sources rather than comparing #34 output with itself.

Workflow evidence:

- frozen cases audited: 60
- historical RS cross-section objects: 1,300
- future-performance fields used: false
- PIT availability violations: 0
- source-evidence artifact: `v35d-source-evidence-34765922653`
- artifact SHA-256: `06a1eabc12a48a6c4585b6fc4a5b4b8a4cc3f00719a194398c687a93661b1074`

Independent per-case comparison against the frozen manifest strata produced:

- C: 60/60 MATCH
- A: 60/60 MATCH
- L: 60/60 MATCH
- M entry state: 60/60 MATCH

Additional availability/data-through checks found no date later than frozen `asof_date` for quarterly fundamentals, annual fundamentals, RS data-through, or M/SPY data-through.

No implementation bug, PIT leakage, data/evidence issue, contract-interpretation issue, or genuine validation failure was identified in V35-D.

## Preserved upstream morphology debt

Two morphology observations remain explicit upstream #33 validation debt:

1. Some `CUP_WITH_HANDLE` cases can exhibit temporally long handles.
2. Some recognized `DOUBLE_BOTTOM` cases can exhibit a relatively large second-trough undercut.

The current authoritative theory contract does not provide sufficiently universal numeric upper bounds to justify new thresholds. Therefore no threshold is derived from the #35 corpus and no post-validation tuning is authorized.

These observations do not invalidate the O'Neil patterns and do not constitute a #34 qualification failure. They remain evidence debt in #33 until new authoritative morphology evidence becomes available.

## Governance effect

- #35 is now **COMPLETE / FROZEN**.
- #33 remains frozen; no detector retuning is authorized from #35 evidence.
- #34 remains frozen; no classifier/qualification retuning is authorized from #35 evidence.
- Frozen 60-case corpus remains immutable validation evidence.
- P6 remains `DEFERRED / NOT PRODUCTION-VALIDATED / FROZEN UNTIL NEW AUTHORITATIVE MORPHOLOGY EVIDENCE EXISTS`.
- FWD1 and EXH2 remain unchanged.
- #36 Execution / Entry is now authorized to open as a separate downstream workstream, without modifying the frozen #35 validation record.
