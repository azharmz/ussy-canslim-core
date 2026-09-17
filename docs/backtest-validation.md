# CAN SLIM v1 Historical Validation

Status: **BT0–BT4 READINESS COMPLETE / BT1-M TERMINAL BLOCKED / BT5C CLOSED / HISTORICAL COMPONENT REPLAY NEXT**

Date opened: 2026-09-16
BT5C exit gate closed: 2026-09-17

## Purpose and boundary

The frozen CAN SLIM v1 production baseline remains unchanged and frozen. Historical empirical validation is split into evidence tracks. Technical historical replay is component/research evidence unless and until every required historical semantic input is available. It must never silently become production `CANSLIM_ELIGIBLE`.

## Frozen governance

Production semantics remain frozen; replay is causal; execution remains T+1 Open; O'Neil is pinned to `oneil-pattern-output-v2` SHA `c433cc1e35a5aa32a46f732cd8c5545935e36e40`; no validation result may tune frozen rules; missing evidence remains NOT_EVALUABLE. Canonical OHLCV source is `ussy-data` prefix `history/ohlcv/`.

## BT1-M — terminal evidence boundary

Canonical actual-index history is mechanically available, but governed historical sources do not exist for the frozen M inputs `leadership_confirming`, `weakening_confirmed`, and `correction_reset`. Terminal verdict:

`BLOCKED_ON_HISTORICAL_M_SEMANTIC_EVIDENCE`

No proxy M or invented historical thresholds are permitted.

## BT2–BT4 — component replay readiness

BT2 froze the component-replay contract. BT3 proved deterministic R2 runner wiring and provenance capture. BT4 wired canonical SP500 benchmark evidence for frozen L and executed the exact frozen O'Neil dependency. Naive cross-asof O'Neil replay was computationally expensive because every as-of invocation recomputed the complete causal morphology stack.

## BT5A — runtime profiling

Profiling confirmed repeated canonical morphology/candidate evaluation dominates replay workload. This did not change detector semantics or authorize strategy performance.

## BT5B — bounded-history experiment — TERMINAL NOT AUTHORIZED

Frozen reference semantics are always:

`analyze_security(full causal frame through D, asof_date=D)`

A fixed trailing suffix was tested as a possible replacement. Security `BMG9460G1015`, decision date `2026-09-09`, full causal history 1,345 bars produced 29,465 assessments. H=500 produced 1,132; H=750 produced 3,174; H=1000 produced 11,256, with 47 materially changed same-candidate outputs at H=1000.

Terminal verdict:

`BOUNDED_HORIZON_NOT_SUPPORTED_IN_TESTED_CASE`

`bounded_replay_authorized = false`

Fixed 500/750/1000-bar suffixes are not exact replacements for full causal history.

## BT5C — exact-computation acceleration — CLOSED

BT5C pursued reuse of exact computation across successive as-of dates while leaving the frozen O'Neil detector untouched.

### Evidence sequence

- **BT5C-1:** standard raw excursion and confirmed-window landmark reuse matched earlier-frame raw extraction in tested cases.
- **BT5C-2:** latest-frame fused landmarks were shown to be frame-relative and therefore cannot simply be filtered backward. Fusion must be recomputed per as-of. With raw reuse + frame-relative fusion/segmentation recomputation, tested cases were exact.
- **BT5C-3:** local-turn raw landmark reuse isolated; run #13 produced 32/32 exact comparisons across 8 deterministic securities × 4 earlier as-of offsets. Structural geometry was intentionally excluded.
- **BT5C-4:** frame-relative boundary evidence and downstream local-turn DB structural assembly were recomputed. Run #14 produced 8/8 exact comparisons. Structural reuse performance was modest/near-neutral, so this path is not relied upon for operational acceleration.
- **BT5C-5:** an initial final-output run was exact but did not exercise the local-turn fallback, so it was not accepted as substantive accelerator evidence. Run #17 instead integrated standard raw excursion + confirmed-window reuse into full frozen `analyze_security`; 8/8 final `ProductionAssessmentRecord` comparisons were exact and both accelerated paths were exercised in every comparison. Observed speedup was approximately 1.04x–1.22x.
- **BT5C-6:** run #18 repeated final-output exactness while measuring runtime, Python peak allocation, and fail-closed behavior. All 8 comparisons were exact; both accelerated paths were exercised; deliberately corrupted prefixes were rejected for all four securities with `BT5C_REUSE_GUARD_NOT_PREFIX`. Observed speedup was approximately 1.045x–1.186x. Peak memory was approximately neutral with small case-level increases/decreases; no material memory-improvement claim is made.

### BT5C exit decision

`BT5C_EXIT_GATE = CLOSED`

Authorized research scope is deliberately narrow:

1. Precompute exact raw **excursion** and **confirmed-window** landmarks from one complete canonical security history.
2. Reuse those raw landmarks only for an earlier frame proven to be an exact causal prefix of that same source history.
3. Filter reusable raw landmarks causally by frame membership and `confirmed_date <= asof`.
4. Recompute **fusion and every downstream frozen O'Neil operation per as-of**.
5. If source/prefix identity or any accelerator invariant fails, fail closed to the untouched frozen oracle; never approximate.
6. Frozen O'Neil source/SHA remains untouched.

This is empirical tested-case equivalence, **not mathematical/global proof**. `global_reuse_authorized = false` remains appropriate. Fixed suffixes remain unauthorized. Local-turn structural reuse is not required for the operational accelerator.

The speedup is consistent but modest. BT5C is closed because further optimization is not justified before actual historical workload evidence. Correctness remains more important than acceleration.

## Historical fundamental track

Historical C/A fundamental screening is a separate frozen workstream. Its output may later be joined by historical decision date to technical qualification, but technical logic must not be mixed into or used to retune the frozen C/A screener.

## Current checklist

| Phase | Scope | Status |
|---|---|---|
| BT0 | Scope + no-tuning governance | COMPLETE |
| BT1 | Historical input readiness | COMPLETE |
| BT1-M | Frozen M reconstruction | TERMINAL BLOCKED — historical semantic evidence unavailable |
| BT2 | Component-replay contract | COMPLETE / FROZEN |
| BT3 | Reproducible component runner | COMPLETE |
| BT4 | Canonical L wiring + exact pinned O'Neil execution smoke | COMPLETE |
| BT5A | Runtime profiling | COMPLETE |
| BT5B | Fixed bounded-history equivalence | TERMINAL — NOT AUTHORIZED |
| BT5C | Exact-computation acceleration | COMPLETE / EXIT GATE CLOSED |
| Historical BT5 | Actual causal technical/component replay | NEXT |
| BT6 | Mechanical T+1 Open execution/outcome | PENDING after replay output |
| Full M-qualified historical performance | Required M semantics | BLOCKED on historical M semantic evidence |

## Immediate next step

Build/run the **actual historical component replay** with checkpoint/resume and sparse progress logging. Use canonical `history/ohlcv/`, exact frozen O'Neil SHA, and only the narrowly authorized BT5C raw-landmark reuse boundary. Preserve research/component namespace and provenance. Do not emit full production CAN SLIM eligibility where required historical semantic evidence is unavailable. After replay output exists, proceed to mechanical T+1 Open execution/outcome reconstruction under the frozen execution rules.
