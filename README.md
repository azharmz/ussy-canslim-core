# USSY CAN SLIM Research HQ

Independent CAN SLIM research program for USSY.

This repository is **not** an upgrade branch of `ussy-trendfoll` and is not a production trading application. It owns CAN SLIM methodology, experiment specifications, evidence, roadmap/progress, and research decisions.

> ## START HERE — continuation / context recovery
>
> For overall CAN SLIM state, read `docs/progress-board.md` on the active branch.
>
> Workstream **#33 — O'Neil Pattern Recognition Engine** is canonical in `azharmz/ussy-oneil-patterns` and is now closed at the defensible production boundary. The frozen production contract is `oneil-pattern-output-v2` and emits only `FLAT_BASE`, `DOUBLE_BOTTOM`, `CUP_WITHOUT_HANDLE`, and `CUP_WITH_HANDLE` while preserving `RECOGNIZED / AMBIGUOUS / REJECTED`, identities, faults, semantics, and provenance.
>
> Local #33/P8 implementation history in this repository is retained only as research/migration evidence and is superseded as implementation source of truth. **#34 is active and must consume the frozen #33 contract rather than rebuilding morphology here.**

## Project boundaries

| Repository | Ownership |
|---|---|
| `ussy-data` | Canonical universe and OHLCV data contracts |
| `ussy-fundamentals` | SEC facts, PIT normalization, readiness, immutable R2 production snapshots |
| `ussy-oneil-patterns` | **Canonical #33 O'Neil pattern engine**, frozen four-core production contract, morphology/fault/ambiguity implementation and validation evidence |
| `ussy-trendfoll` | Independent legacy TrendFoll strategy and paper-trading implementation |
| `ussy-canslim-research` | CAN SLIM parent/HQ: theory/specification, roadmap/status, #32 contract and #34+ integration research |

TrendFoll is a comparator/reference source only. CAN SLIM may adopt, modify, or reject any TrendFoll rule without changing TrendFoll production.

## Current theory-fidelity boundary — 13 Sep 2026

- #25–#31 Theory Fidelity Audit: **COMPLETE**
- #32 Theory-Faithful Candidate Specification v1: **COMPLETE / FROZEN**
- #33 O'Neil Pattern Recognition Engine: **CORE COMPLETE / FROZEN — P8 CONDITIONAL PASS**
- #33 production contract: **`oneil-pattern-output-v2`**, four core families only
- P6 `ASCENDING_BASE` / `BASE_ON_BASE`: **DEFERRED / NOT PRODUCTION-VALIDATED**, outside production contract
- #34 Theory-Faithful Candidate Generator: **IN PROGRESS**
- current #34 implementation consumes frozen #33 output, evaluates pivot crossing and breakout volume from R2, and attaches PIT C/A plus L/M evidence adapters
- FWD1 and EXH2 remain separate frozen/prospective tracks and must not influence #33 morphology or #34 theory semantics

## Research-universe definition

The primary historical research question uses a **frozen contemporary/current Musaffa-compliant universe**. We ask how CAN SLIM rules behave historically on the securities that are in the selected compliant research universe now.

Historical Musaffa compliance is therefore **not** a strategy input and is not required for this research design. We do not claim that the resulting historical sample reconstructs which securities were known compliant in each historical year.

Point-in-time discipline remains mandatory for information actually used to make historical strategy decisions, especially:

- OHLCV and market-state data through the decision date only;
- SEC fundamental evidence only after `accepted_at`;
- no future filings, future prices, or later amendments before their acceptance time.

## Research principles

- Preserve facts; version interpretations.
- Freeze methodology before performance testing.
- Never optimize extraction or pattern-recognition semantics for pass-rate, CAGR, PF, win rate, FWD1, or later returns.
- `accepted_at` is the fundamental information-availability boundary.
- Define the research universe explicitly and do not confuse current-universe historical research with historical-eligibility reconstruction.
- Completed experiments must pin immutable universe/fundamental inputs and checksums.
- Missing is not zero. Unsupported is not failed. Insufficient history is not a bad-company verdict.
- Source precision is not invented; absent authoritative morphology dimensions remain unscored.
- Daily-EOD signals may only use completed daily information; close-based conditions are filled no earlier than the next session Open.

## Active path

1. Complete #34 as a consumer of frozen `oneil-pattern-output-v2` only.
2. Verify end-to-end R2 smoke: canonical #33 production output -> pivot/breakout/volume -> PIT C/A -> L/M -> candidate stage.
3. Preserve I, broader S, RS-line and industry context as evidence states until defensible PIT sources/contracts are attached.
4. Only after #34 is technically frozen, begin #35 candidate validation.
5. Keep FWD1/EXH2 accumulating unchanged and keep #36 execution/entry research parked.
