# CAN SLIM Progress Board

Last updated: 2026-09-12

Frozen quantitative v1 remains research-complete but not production-ready. FWD1 and EXH2 continue unchanged. The post-v1 Theory Fidelity Audit (#25-#31) is complete; #32 Theory-Faithful Candidate Specification v1 is now frozen and must not alter frozen v1/FWD1 semantics.

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

Historical v1 reference remains approximately X3 PF 1.163, PF ex-top10 1.145, PORT1 gross CAGR 3.02–3.04%, gross max DD -43.36%, and SPY price-only CAGR context ~8.80%. These figures must not be used to tune the theory-faithful path.

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
| 32 | **Theory-faithful candidate specification** | **COMPLETE / FROZEN v1** |
| 33 | **O'Neil Pattern Recognition Engine** | **IN PROGRESS — P8 v0.1 merged** |
| 34 | Theory-faithful candidate generator | NOT STARTED |
| 35 | New-candidate validation | NOT STARTED |
| 36 | Execution / entry research | **PARKED** |

## #32 Theory-Faithful Candidate Specification v1

Canonical specification: `docs/methodology/theory-faithful-candidate-spec-v1.md`.

Decision record: `docs/decisions/2026-09-12-theory-faithful-candidate-spec-v1.md`.

The spec deliberately avoids a single universal Boolean candidate flag. It preserves staged semantics:

```text
BASE_RECOGNIZED
PIVOT_DEFINED
PIVOT_CROSSED
BREAKOUT_CONFIRMED
CANSLIM_ELIGIBLE
```

The initial `CANSLIM_ELIGIBLE` contract requires:

```text
valid named proper base
+ pattern-specific pivot
+ pivot crossing
+ breakout-day volume >=1.40x prior-50-session average
+ C primary screen PASS
+ A primary screen PASS
+ individual L screen PASS (transparent RS proxy >=80)
+ M permits new buys
```

Attached evidence that is intentionally not promoted to a universal additional hard gate in this first theory-faithful candidate contract includes broader S supply descriptors, I sponsorship state, RS-line confirmation/divergence, industry-group leadership, non-price N catalyst state, close-above-pivot quality and 5% extension/buy-zone state.

Important fundamental distinction:

- C freezes recent quarterly EPS growth around >=25% as the core screen; revenue growth/acceleration remains required quality evidence, not a universal mandatory `revenue>=25%` conjunction.
- A freezes sustained multi-year annual EPS growth around >=25% as the theory requirement; the exact reproducible aggregation/consistency adapter must be versioned before #35 and cannot be chosen from return optimization. The old v1 rule requiring each of three annual YoY observations individually >=25% is not treated as canonical O'Neil identity.

Missing/stale evidence remains `NOT_EVALUABLE/NOT_IMPLEMENTED`, never coerced to PASS or FAIL.

## #33 — O'Neil Pattern Recognition Engine

#33 is active against frozen #32. The first DEVELOPMENT implementation slice is merged as P8 pattern engine v0.1.

Implemented in v0.1:

- strict R2 -> Yahoo -> Tiingo OHLCV routing, with fallback only on explicit `UNAVAILABLE`;
- DEVELOPMENT-only execution guardrail;
- preregistered geometry policy before broader validation;
- `CUP_WITH_HANDLE` detector;
- `CUP_WITHOUT_HANDLE` detector;
- `DOUBLE_BOTTOM` detector;
- `FLAT_BASE` detector;
- prior-uptrend state;
- pattern-specific landmark persistence and pivot derivation;
- fault flags and ambiguity state;
- synthetic morphology regression fixtures;
- live SNPS 2023 workflow from R2.

First live DEVELOPMENT result for SNPS 2023: 250 R2 sessions consumed successfully. v0.1 emitted 47 raw morphology windows: 38 flat-base windows and 9 double-bottom windows, with 5 ambiguity states. This result is **not** a candidate count and is **not** performance evidence; overlapping windows still require stable base-identity clustering/deduplication.

Current #33 next slice:

1. consolidate overlapping raw windows into stable `base_id` identities;
2. define recognition chronology / earliest valid recognition date explicitly;
3. add candidate-base segmentation around stable landmark sets rather than window multiplicity;
4. expand labelled DEVELOPMENT fixtures and inspect false positives/false negatives;
5. then implement secondary `ASCENDING_BASE` and `BASE_ON_BASE` relationships;
6. only after morphology validation may #34 consume #33 output.

Design contract: `docs/methodology/p8-pattern-engine-design-v0.md`.

#33 must not optimize detector definitions against CAGR/PF. The acceptance target remains morphology/landmark fidelity and reproducibility, not trading performance.

## Frozen theory summary (#26-#31)

- Proper base: v1 generic 35-session/depth<=40% is a weak proxy; named morphology is required.
- Pivot: pattern-specific landmark, not arbitrary rolling high.
- Breakout: pivot crossing event is distinct from close/hold quality; breakout-day volume >=1.40x prior 50 completed sessions is the canonical strong daily confirmation.
- Leadership: RS>=80 is a useful leader screen but RS line and industry context are separate evidence.
- Component roles: C/A screens; S/I evidence/confirmation; M timing/context/risk gate.
- Sell/risk: downstream state machine; v1 does not contain a canonical O'Neil sell engine.

Canonical audit detail: `docs/methodology/oneil-theory-fidelity-audit-v1.md`.

## Forward tracks remain frozen

FWD1 boundary remains exclusive 2026-09-09 with formal review only after both >=12 completed calendar months and >=50 closed X3 portfolio trades. EXH2 remains separate and prospective. Theory-fidelity/specification findings must not be retrofitted into either track.

## Active work from here

1. **Continue #33** with stable base identity / `base_id` clustering and recognition chronology.
2. Validate morphology and landmarks before using returns as evidence.
3. Then implement #34 theory-faithful candidate generator.
4. Run #35 semantic/morphology/candidate validation before performance research.
5. Keep #36 execution/entry research parked and keep FWD1/EXH2 accumulating unchanged.
6. Any material change to #32 hard eligibility or evidence-vs-gate semantics requires a new spec version and decision record.
