# CAN SLIM Progress Board

Last updated: 2026-09-13

Frozen quantitative v1 remains research-complete but not production-ready. FWD1 and EXH2 continue unchanged. The post-v1 Theory Fidelity Audit (#25-#31) is complete; #32 Theory-Faithful Candidate Specification v1 is frozen and must not alter frozen v1/FWD1 semantics.

## Canonical v1 state

| Area | Status | Note |
|---|---|---|
| Independent CAN SLIM project | COMPLETE | separate from TrendFoll |
| Frozen Musaffa universe | COMPLETE / FROZEN | 1,327 current-compliant securities |
| Production OHLCV / data infrastructure | COMPLETE | existing R2 daily OHLCV is the technical-data basis |
| SEC/PIT fundamentals | COMPLETE / FROZEN | upstream `ussy-fundamentals` |
| C / A | COMPLETE | PIT-safe historical attachment validated |
| N / S / L proxies | COMPLETE | v1 proxy semantics frozen |
| I institutional sponsorship | COMPLETE / NOT PROMOTED as hard filter | descriptor retained |
| M / SPY+QQQ ablation | COMPLETE / NOT PROMOTED | v1 evidence frozen |
| Historical candidates v1 | COMPLETE | 10,731 / 860 securities; proxy candidates, not O'Neil ground truth |
| X1-X4 / X3 | COMPLETE / PARKED | historical v1 work complete; no current entry optimization |
| PORT1 / costs / robustness | COMPLETE | retrospective evidence frozen |
| CAN SLIM quantitative v1 | **RESEARCH COMPLETE** | historical economics weak vs passive SPY |
| FWD1 | LIVE / ACCUMULATING | frozen forward validation |
| EXH2 | LIVE / PROSPECTIVE | separate exhaustion sidecar |
| Production integration | BLOCKED | FWD1 review gate not met |

## Theory Fidelity / v2 path — #25 onward

| # | Workstream | Status |
|---:|---|---|
| 25 | Theory Fidelity Audit — O'Neil vs engine v1 | **COMPLETE** |
| 26 | Proper-base definitions | **COMPLETE** |
| 27 | Pivot / buy-point definition | **COMPLETE** |
| 28 | Breakout + volume confirmation | **COMPLETE** |
| 29 | RS / leadership fidelity | **COMPLETE** |
| 30 | C/A/S/I/M role fidelity | **COMPLETE** |
| 31 | Sell / risk-management fidelity | **COMPLETE** |
| 32 | Theory-faithful candidate specification | **COMPLETE / FROZEN v1** |
| 33 | O'Neil Pattern Recognition Engine | **IN PROGRESS — P8 v0.3 detector / v0.6 authoritative DEVELOPMENT evaluator** |
| 34 | Theory-faithful candidate generator | NOT STARTED |
| 35 | New-candidate validation | NOT STARTED |
| 36 | Execution / entry research | **PARKED** |

## #32 Theory-Faithful Candidate Specification v1

Canonical specification: `docs/methodology/theory-faithful-candidate-spec-v1.md`.

The staged contract remains:

```text
BASE_RECOGNIZED
PIVOT_DEFINED
PIVOT_CROSSED
BREAKOUT_CONFIRMED
CANSLIM_ELIGIBLE
```

Initial `CANSLIM_ELIGIBLE` requires a valid named proper base, pattern-specific pivot, pivot crossing, breakout-day volume >=1.40x prior-50-session average, C PASS, A PASS, individual L screen PASS (transparent RS proxy >=80), and M permitting new buys. S/I and other quality descriptors remain attached evidence unless separately promoted by a versioned specification decision.

## #33 — O'Neil Pattern Recognition Engine

Core morphology infrastructure is implemented for `CUP_WITH_HANDLE`, `CUP_WITHOUT_HANDLE`, `DOUBLE_BOTTOM`, and `FLAT_BASE`, with strict R2 -> Yahoo -> Tiingo routing, DEVELOPMENT/VALIDATION separation, v0.3 prior-uptrend semantics, v0.3 established-left-high flat pivot semantics, raw-window persistence, deterministic structural identities, PIT/prefix-stable lineages, and explicit conflicts/ambiguity.

The authoritative evaluator is now **v0.6**. It scores raw emitted windows and maps the selected raw candidate back to stable identity/lineage. Source dimensions are never invented: an authoritative example may omit exact `window_end`, in which case end fidelity is not scored and `boundary_validation_state=START_ONLY_SOURCE_ANCHOR`. At least a source-anchored start is still required in v0.6.

CI for the v0.6 partial-boundary semantics passed on branch run `34705192430` at commit `ce7b68378b7bf2e3147a176843ac307497fd726c`.

### Authoritative validation status

| Example | Split | Pattern | Status | Evidence |
|---|---|---|---|---|
| SNPS (`p8-label-0001`) | DEVELOPMENT | FLAT_BASE | **MATCH / FROZEN** | start error 0d; end error 1d; pivot date error 0d; pivot price error ~0; pivot VALIDATED |
| NFLX (`p8-label-0002`) | VALIDATION | CUP_WITH_HANDLE | **LOCKED / UNTOUCHED** | do not inspect for tuning |
| TW candidate | ADJUDICATION | FLAT_BASE | **WITHDRAWN** | source supports breakout/entry but not previously inferred exact start |
| TSM late-2024 candidate | ADJUDICATION | CUP_WITH_HANDLE | **NOT PROMOTED** | IBD supports named CWH and 205.63 buy point; inspected text does not explicitly publish exact base start |
| OLED 2019 candidate | ADJUDICATION | CUP_WITH_HANDLE | **NOT PROMOTED** | IBD supports second-stage CWH, Jun. 18 breakout and 177.05 buy point; inspected text does not explicitly publish exact base start |

Source adjudication record: `docs/p8-next-cwh-source-adjudication-v0.md`.

SNPS emitted detector window remains `2023-04-04 -> 2023-05-17` with pivot `2023-04-04 @ ~392.79000854`, matching the authoritative IBD anchor `2023-04-04 -> 2023-05-18` and pivot `392.79`. Validation record: `docs/p8-snps-development-validation-v0.md`.

### v0.3 structural-identity audit

The v0.3 correction was audited against the same 1,387 raw SNPS 2023 candidate windows. Candidate membership was unchanged. Of 975 flat-base windows, 615 receive a corrected persisted pivot. Structural identities changed 104 -> 111 overall (flat 60 -> 67), while lineages changed 39 -> 38 overall (flat 26 -> 25). Split/merge assignment churn is material, so v0.3 is retained but BaseIdentity/Lineage is not yet frozen. Decision record: `docs/decisions/2026-09-13-p8-v03-structural-identity-audit.md`.

This remains morphology evidence, not trading-performance evidence.

### Current #33 next slice

1. continue source-first search for a non-FLAT authoritative DEVELOPMENT example with an explicitly published detector-comparable start anchor;
2. do not promote TSM/OLED by inferring a start from their charts or record highs;
3. if high-quality authoritative sources repeatedly publish pattern/pivot but not exact boundaries, consider a separately documented evaluator v0.7 allowing independently optional source dimensions; this must be a semantic evidence-model decision, not an accommodation for a desired detector result;
4. repeat raw-window plus identity/lineage audits across multiple symbols and pattern families once additional DEVELOPMENT labels are defensible;
5. freeze detector semantics only after broader DEVELOPMENT agreement/disagreement evidence;
6. keep NFLX VALIDATION locked until DEVELOPMENT semantics are frozen;
7. after freeze, open untouched VALIDATION once and issue final P8 verdict;
8. only after defensible P8 validation may #34 consume #33 output.

Secondary `ASCENDING_BASE`, `BASE_ON_BASE`, and `IPO_BASE` remain deferred.

Design contract: `docs/methodology/p8-pattern-engine-design-v0.md`.

#33 must not optimize detector definitions against CAGR/PF. Acceptance remains morphology/landmark fidelity and reproducibility, not trading performance.

## Frozen theory summary (#26-#31)

- Proper base: v1 generic 35-session/depth<=40% is a weak proxy; named morphology is required.
- Pivot: pattern-specific landmark, not arbitrary rolling high.
- Breakout: pivot crossing event is distinct from close/hold quality; breakout-day volume >=1.40x prior 50 completed sessions is the canonical strong daily confirmation.
- Leadership: RS>=80 is a useful leader screen but RS line and industry context are separate evidence.
- Component roles: C/A screens; S/I evidence/confirmation; M timing/context/risk gate.
- Sell/risk: downstream state machine; v1 does not contain a canonical O'Neil sell engine.

## Forward tracks remain frozen

FWD1 boundary remains exclusive 2026-09-09 with formal review only after both >=12 completed calendar months and >=50 closed X3 portfolio trades. EXH2 remains separate and prospective. Theory-fidelity/specification findings must not be retrofitted into either track.

## Active work from here

1. Continue #33 source-first DEVELOPMENT corpus expansion without weakening evidence provenance.
2. Decide v0.7 evidence-dimension semantics only if source coverage demonstrates the need independently of detector outcomes.
3. Freeze detector semantics after broader DEVELOPMENT evidence, then open VALIDATION once.
4. Then implement #34 and run #35 before performance research.
5. Keep #36 parked and FWD1/EXH2 accumulating unchanged.
