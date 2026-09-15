# CAN SLIM v1 — Production Baseline Freeze

Date: 2026-09-16
Freeze declaration commit base: `e26e1785f69e27e4be3d007db9fc4d638338cb01`

## Declaration

**CAN SLIM v1 — PRODUCTION BASELINE FROZEN**

The post-audit remediation engineering path is complete through Phase 13 independent re-audit. This freeze records the integrated production baseline without converting legitimately blocked production-population validation into PASS.

## Production contracts and frozen semantics

### Pattern / candidate

Canonical pattern dependency: `azharmz/ussy-oneil-patterns` pinned at:

`c433cc1e35a5aa32a46f732cd8c5545935e36e40`

Frozen production contract: `oneil-pattern-output-v2`.

Only these four core pattern families are production-authorized:

- `FLAT_BASE`
- `DOUBLE_BOTTOM`
- `CUP_WITHOUT_HANDLE`
- `CUP_WITH_HANDLE`

P6 `ASCENDING_BASE` / `BASE_ON_BASE` remain excluded, deferred and frozen outside the production contract.

Candidate eligibility remains full fail-closed CAN SLIM eligibility. Zero `CANSLIM_ELIGIBLE` is a legitimate outcome and must never trigger threshold tuning.

### Entry

Frozen entry semantics:

- candidate must be `CANSLIM_ELIGIBLE`;
- execution is T+1 Open;
- Open from pivot through +5% inclusive → buy;
- Open above +5% → missed/extended;
- Open below pivot → no fill;
- no next-session bar → `NO_NEXT_SESSION_BAR`;
- actual fill is the stop reference;
- normal profit zone remains pivot-based.

Canonical executable serialization state is `EXECUTED_T1_OPEN`.

### Lifecycle

Existing frozen risk, sell and lifecycle semantics remain unchanged. Entry → Lifecycle engineering compatibility is accepted; production-observed executable-entry population validation is still blocked until a natural executable entry exists.

### Cross-session production ordering

The frozen orchestrator order is:

1. consume PRIOR Candidate after T+1 becomes available;
2. produce Entry;
3. advance Lifecycle;
4. publish current-session Candidate LAST;
5. compact immutable Candidate/Pattern artifacts;
6. apply protected rolling retention;
7. audit whole-bucket R2 storage.

Do not reorder current Candidate publication ahead of prior Candidate → Entry/Lifecycle processing.

## Decision-time / evidence contracts

- SEC fundamentals use explicit decision-time PIT availability; later `accepted_at` information cannot leak backward into an earlier decision.
- Stock-level institutional sponsorship uses the canonical prospective SEC 13F source and remains PIT/fail-closed.
- Canonical production M is consumed from the frozen market-state production path.
- Unsupported market-level leadership/weakening evidence remains unavailable rather than being fabricated.

## Reproducibility / storage

Production candidate snapshots are immutable and carry manifests/hashes. Candidate and pattern JSONL may be losslessly gzip-compacted while preserving logical SHA-256 and recording stored SHA-256. Mutable pointers are advanced LAST.

Retention baseline:

- rolling 7 days;
- keep newest 2;
- protect snapshots referenced by live pointers/handoff;
- whole-bucket preflight/post-retention guard;
- warning 7 GiB;
- hard stop 9 GiB.

The hard stop is an operational ceiling, not a guarantee of enough temporary headroom for an arbitrary future raw publication. Revisit only on demonstrated production evidence, not speculative redesign.

## Terminal acceptance evidence

- Phase 9/10 E2E run `34967865047`: **SUCCESS**.
- Phase 12 clean prospective dry-run `34967947364`: **SUCCESS**.
- Frozen remediation regressions in Phase 12: **62 passed**.
- Phase 13 independent re-audit: **PASS / CLEAN FOR PRODUCTION BASELINE FREEZE**.
- Phase 12 post-run R2 state: ~2.06 GiB, guard `OK`.

## Explicit blocked validation

This freeze intentionally carries the following status:

`PRODUCTION ENTRY→LIFECYCLE OBSERVATION: BLOCKED_ON_PRODUCTION_ENTRY_POPULATION`

Reason: the prospective production path has not yet observed a natural executable production entry. Engineering plumbing and contract compatibility are accepted, but production-population validation cannot be honestly claimed until such evidence exists.

This blocked state does **not** reopen frozen strategy semantics and does **not** block the engineering baseline freeze.

## Controlled debt preserved

- #33 conditional morphology validation debt remains disclosed/frozen.
- Market-level leadership/weakening boolean remains `NOT_EVALUABLE` without new authorized evidence.
- Historical/deprecated research artifacts may remain in the repository.
- No new strategy expansion, optimization or threshold tuning is authorized by this freeze.

## Change control after freeze

Any future change to frozen CAN SLIM semantics, O'Neil morphology, entry thresholds, market-state semantics, or eligibility gates requires a separately governed evidence/research decision. Integration/correctness fixes may be made with regression evidence, but must not silently alter frozen strategy meaning.

**FINAL STATUS: CAN SLIM v1 — PRODUCTION BASELINE FROZEN.**
