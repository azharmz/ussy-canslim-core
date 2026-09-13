# #33 Canonical P8 Final Verdict

Date: 2026-09-13

Canonical repository: `azharmz/ussy-oneil-patterns`.

The canonical #33 core morphology engine completed P8 with a **CONDITIONAL PASS / FROZEN WITH VALIDATION DEBT**, and P9 production output is now aligned to that exact frozen P8 stack.

Frozen DEVELOPMENT evidence in the canonical repo:

- 20 authoritative positives;
- five each for FLAT_BASE, CUP_WITH_HANDLE, DOUBLE_BOTTOM, CUP_WITHOUT_HANDLE;
- 20/20 source-dimension MATCH;
- zero true candidate identity STATUS_CONFLICT.

Freeze evidence commit: `2ed3dadcc354f56f4cb27401248daef60b1627fa`.

The previously locked NFLX CUP_WITH_HANDLE VALIDATION example was opened once after freeze and returned MATCH on the preregistered comparable source dimensions with a unique candidate and exact 2023-02-03 start. The frozen detector state remained `CUP_WITH_HANDLE_AMBIGUOUS` because of `BELOW_CUP_MIDPOINT`; that is retained as validation debt rather than tuned away.

Canonical final decision: `ussy-oneil-patterns/docs/decisions/p8-final-verdict.md`.
Canonical downstream contract: `ussy-oneil-patterns/docs/production-output-contract-v2.md`.

## Frozen production handoff

#34 must consume:

- output schema `oneil-pattern-output-v2`;
- engine `33-core-p8-frozen-v1`;
- validation status `P8_CONDITIONAL_PASS_FROZEN`;
- canonical `candidate_id`;
- stable exact-structure `base_id` (`core-base-id-v1`);
- conservative exact-anchor `lineage_id` (`core-lineage-v1`);
- `RECOGNIZED` / `AMBIGUOUS` / `REJECTED` state;
- candidate semantics and structural signature;
- structural start/end;
- pivot source date/level and depth when available;
- detector faults and versioned detector contract.

Production v2 no longer rebuilds a separate first-pass detector path; it directly consumes the canonical P8 prediction adapter frozen by validation. Its regression suite passed 224 tests before documentation freeze.

Parent consequence:

- local #33/P8 implementation remains superseded migration evidence;
- #33 core implementation is complete/frozen for the four validated families;
- advanced pattern families do not inherit the core P8 evidence level automatically;
- #34 may start from the frozen production v2 contract;
- #34 must not silently coerce `AMBIGUOUS`, and must not reopen P8 using returns, CAGR, PF, FWD1, breakout outcomes or entry optimization.
