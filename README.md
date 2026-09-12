# USSY CAN SLIM Research HQ

Independent CAN SLIM research program for USSY.

This repository is **not** an upgrade branch of `ussy-trendfoll` and is not a production trading application. It owns CAN SLIM methodology, experiment specifications, evidence, roadmap/progress, and research decisions.

> ## START HERE — continuation / context recovery
>
> For overall CAN SLIM state, read `docs/progress-board.md` on the active branch.
>
> For workstream **#33 — O'Neil Pattern Recognition Engine / P8 morphology validation**, do **not** continue from local pattern-engine code in this repository. The canonical implementation/source of truth is `azharmz/ussy-oneil-patterns`. Start from that repository's `README.md`, then `docs/progress-board.md` and latest #33/P8 decision records.
>
> Local #33/P8 implementation history in this repository is retained as research/migration evidence until a separate cleanup is completed; it is superseded as the implementation source of truth. #34 remains blocked until canonical #33/P8 is defensible.

## Project boundaries

| Repository | Ownership |
|---|---|
| `ussy-data` | Canonical universe and OHLCV data contracts |
| `ussy-fundamentals` | SEC facts, PIT normalization, readiness, immutable R2 production snapshots |
| `ussy-oneil-patterns` | **Canonical #33 O'Neil pattern engine**, morphology/fault/ambiguity implementation, P8 labelled morphology validation, versioned #33 output |
| `ussy-trendfoll` | Independent legacy TrendFoll strategy and paper-trading implementation |
| `ussy-canslim-research` | CAN SLIM parent/HQ: theory/specification, roadmap, integration evidence, #32 contract, later #34+ research |

TrendFoll is a comparator/reference source only. CAN SLIM may adopt, modify, or reject any TrendFoll rule without changing TrendFoll production.

## Current theory-fidelity boundary — 13 Sep 2026

- #25–#31 Theory Fidelity Audit: **COMPLETE**
- #32 Theory-Faithful Candidate Specification v1: **COMPLETE / FROZEN**
- #33 O'Neil Pattern Recognition Engine: **IN PROGRESS in `ussy-oneil-patterns`**
- #33/P8 current phase: canonical DEVELOPMENT reconciliation / morphology validation
- canonical P8 corpus: five DEVELOPMENT examples spanning all four core pattern families plus locked NFLX VALIDATION
- parent-side `5 MATCH / 5 AMBIGUOUS` result is preserved as migration evidence only until canonical oneil re-execution
- #34 Theory-Faithful Candidate Generator: **NOT STARTED / BLOCKED on #33**
- FWD1 and EXH2 remain separate frozen/prospective tracks and must not influence #33 tuning

Canonical #33 reconciliation landed in `ussy-oneil-patterns` at merge `261d667eecf8525b27e8a15b6980ba698e609848`.

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

1. Finish canonical #33/P8 DEVELOPMENT morphology validation in `ussy-oneil-patterns`.
2. Freeze #33 only after morphology disagreements/ambiguities have defensible `KEEP` / `REVISE` / `UNRESOLVED` treatment and untouched validation is evaluated.
3. Only then begin #34 in this parent program using frozen/versioned #33 output.
4. Keep FWD1/EXH2 accumulating unchanged and keep execution/entry research parked during #33 validation.
