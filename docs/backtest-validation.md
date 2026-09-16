# CAN SLIM v1 Historical Validation

Status: **BT0–BT4 READINESS COMPLETE / BT1-M TERMINAL BLOCKED / BT5 HEAVY REPLAY ENGINEERING IN PROGRESS**

Date opened: 2026-09-16

## Purpose and boundary

The frozen CAN SLIM v1 production baseline remains unchanged and frozen.

Historical empirical validation is deliberately split into two evidence tracks:

1. **BT-PV — Price / Volume / Market historical validation**: replay historically tractable price-volume components and frozen O'Neil morphology where required evidence is available.
2. **BT-FAI — Fundamental / Institutional validation**: validate C/A fundamentals and I institutional sponsorship separately, with PIT/coverage limitations disclosed.

BT-PV is **not** a full CAN SLIM v1 backtest and must never be labelled as one. Production `CANSLIM_ELIGIBLE` remains unchanged and fail-closed.

## Frozen governance

Production semantics remain frozen; replay is causal; execution remains T+1 Open; O'Neil is pinned to `oneil-pattern-output-v2` SHA `c433cc1e35a5aa32a46f732cd8c5545935e36e40`; no validation result may tune frozen rules; missing evidence remains NOT_EVALUABLE; no strategy returns are authorized during replay-engine development.

## BT1-M — terminal evidence boundary

Canonical actual-index history is mechanically available, but governed historical sources do not exist for the frozen M inputs `leadership_confirming`, `weakening_confirmed`, and `correction_reset`. The terminal verdict remains:

`BLOCKED_ON_HISTORICAL_M_SEMANTIC_EVIDENCE`

No proxy M or invented historical thresholds are permitted.

## BT2 — frozen component-replay contract

The component path replays frozen O'Neil and historically defensible components independently and causally. M remains NOT_EVALUABLE. Research outputs must use a distinct `BT_PV_COMPONENT_*` namespace and must never emit or imply `CANSLIM_ELIGIBLE`. Static/current Musaffa membership remains a research-universe design rather than historical membership reconstruction.

## BT3 / BT4 readiness evidence

BT3 proved deterministic R2 component-runner wiring and provenance capture. BT4 wired the canonical SP500 benchmark for frozen L and then executed the exact frozen O'Neil dependency at SHA `c433cc1e35a5aa32a46f732cd8c5545935e36e40`. The pinned O'Neil smoke completed successfully but demonstrated that naïve historical replay is computationally expensive because every as-of invocation recomputes the canonical morphology stack over its complete causal frame.

## BT5 — heavy historical replay engineering

### BT5A — runtime profiling

External-compute profiling confirmed that the frozen engine itself is executable and that repeated canonical morphology/candidate evaluation dominates the replay workload. This phase did not change detector semantics and did not authorize strategy performance.

### BT5B — bounded-history equivalence experiment

Purpose: test whether a fixed trailing history can replace full causal history while preserving the exact frozen O'Neil output.

Frozen reference semantics are always:

`analyze_security(full causal frame through D, asof_date=D)`

A bounded suffix is acceptable only if all material frozen output fields are exactly identical to that reference. Candidate IDs, statuses, structural dates/signatures, pivots, depths, semantics, detector faults, and production identities are not allowed to drift.

#### Runner validation

The standalone Kaggle runner was corrected only for API/output compatibility, without modifying the frozen engine:

- `asof_date` is passed as `datetime.date`, matching the frozen engine's normalized frame-date comparison.
- `ProductionAssessmentRecord.to_dict()` is used as the canonical serialization path.

Two short-history oracle cases completed successfully, proving runner health, but were ineligible for the 500/750/1000 bounded test because their full histories were shorter than 500 bars.

#### Substantive counterexample

Security `BMG9460G1015`, decision date `2026-09-09`:

- full causal history: **1,345 bars**, 2021-05-03..2026-09-09;
- full-history frozen oracle: **29,465 assessments**;
- elapsed: **28.01 s**;
- canonical SHA256: `088b93508900edec854e07409456b6fb944fa8c4873502b6999fa9d549843f80`.

Exact bounded comparisons:

| History | Assessments | Missing vs full | Extra | Changed same candidate ID | Exact |
|---|---:|---:|---:|---:|---|
| 500 bars | 1,132 | 28,333 | 0 | 0 | NO |
| 750 bars | 3,174 | 26,291 | 0 | 0 | NO |
| 1,000 bars | 11,256 | 18,209 | 0 | 47 | NO |

The 1,000-bar case is especially decisive: truncation not only removes historical candidates but changes material output for 47 candidate IDs that exist in both runs. Therefore older causal history can affect frozen outputs observed inside the retained suffix.

**BT5B terminal verdict:**

`BOUNDED_HORIZON_NOT_SUPPORTED_IN_TESTED_CASE`

`bounded_replay_authorized = false`

This counterexample falsifies the proposed universal replacement of full causal history by any of the tested 500/750/1000-bar suffixes. Further repetitions cannot authorize those fixed horizons as an exact general replacement. The frozen O'Neil engine remains unchanged.

### BT5C — exact-computation acceleration

**CURRENT / OPEN.** Optimization must preserve full-history semantics exactly. Simple input truncation is closed.

Inspection of the pinned canonical adapter shows that each call sorts/copies the frame, extracts excursion and confirmed-window landmarks, fuses landmarks, builds atomic and multiturn segments, assembles double-bottom/cup/handle structures, evaluates open-right-edge observations, constructs predictions, and only then deduplicates by candidate ID. The production wrapper then converts every prediction to `ProductionAssessmentRecord` and deduplicates by assessment ID.

The next engineering target is therefore **reuse of exact computation across successive as-of dates**, not a second detector and not a bounded approximation. Any cache/incremental implementation is research infrastructure only and must be validated against untouched calls to the pinned frozen engine before it can be used for replay.

BT5C acceptance criteria:

1. Full causal history remains the semantic reference; no `tail(N)` approximation.
2. Frozen O'Neil repository/SHA and detector code remain untouched.
3. Cached/incremental results must match untouched `analyze_security` output exactly across all material fields.
4. Validation must cover multiple securities and multiple as-of dates, including a long-history case.
5. Any mismatch fails closed; no post-validation tuning to make the oracle match.
6. No production eligibility, M qualification, strategy returns, or performance optimization during this phase.
7. Runtime and memory improvement must be measured separately from semantic equivalence.

## Current checklist

| Phase | Scope | Status |
|---|---|---|
| BT0 | Scope + no-tuning governance | COMPLETE |
| BT1 | Historical input readiness | COMPLETE |
| BT1-M | Frozen M reconstruction | TERMINAL BLOCKED — historical semantic evidence unavailable |
| BT2 | Component-replay contract | COMPLETE / FROZEN |
| BT3 | Reproducible component runner | COMPLETE |
| BT4 | Canonical L wiring + exact pinned O'Neil execution smoke | COMPLETE |
| BT5A | External runtime profiling | COMPLETE |
| BT5B | Fixed bounded-history equivalence | TERMINAL — NOT SUPPORTED IN TESTED CASE / NOT AUTHORIZED |
| BT5C | Exact-computation acceleration | CURRENT / OPEN |
| BT6 | Execution/outcome mechanical reconstruction | PENDING; no M-qualified performance |
| BT7+ | Complete BT-PV/performance | BLOCKED ON required semantic evidence |
| BT-FAI | C/A and I validation overlays | SEPARATE |

## Immediate next step

**BT5C:** build a research-only exact replay accelerator around the pinned frozen engine. Start with a cache/incremental prototype and an equivalence harness that compares its output against untouched full-history `analyze_security` calls. Do not alter the frozen detector or authorize replay acceleration until exact equivalence is demonstrated.