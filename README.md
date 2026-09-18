# USSY CAN SLIM Research HQ

Independent CAN SLIM research program for USSY.

This repository is **not** an upgrade branch of `ussy-trendfoll` and is not a production trading application. It owns CAN SLIM methodology, experiment specifications, evidence, roadmap/progress, and research decisions.

> ## START HERE — continuation / context recovery
>
> For overall CAN SLIM state, read `docs/progress-board.md` on the active branch.
>
> Workstream **#33 — O'Neil Pattern Recognition Engine** is canonical in `azharmz/ussy-oneil-patterns` and is now closed at the defensible production boundary. The frozen production contract is `oneil-pattern-output-v2` and emits only `FLAT_BASE`, `DOUBLE_BOTTOM`, `CUP_WITHOUT_HANDLE`, and `CUP_WITH_HANDLE` while preserving `RECOGNIZED / AMBIGUOUS / REJECTED`, identities, faults, semantics, and provenance.
>
> Local #33/P8 implementation history in this repository is retained only as research/migration evidence and is superseded as implementation source of truth. **#34 is complete/frozen and production integration must consume the frozen #33 contract rather than rebuilding morphology here.**

## Project boundaries

| Repository | Ownership |
|---|---|
| `ussy-data` | Canonical universe and OHLCV data contracts |
| `ussy-fundamentals` | SEC facts, PIT normalization, readiness, immutable R2 production snapshots |
| `ussy-oneil-patterns` | **Canonical #33 O'Neil pattern engine**, frozen four-core production contract, morphology/fault/ambiguity implementation and validation evidence |
| `ussy-trendfoll` | Independent legacy TrendFoll strategy and paper-trading implementation |
| `ussy-canslim-research` | CAN SLIM parent/HQ: theory/specification, roadmap/status, #32 contract and #34+ integration research |

TrendFoll is a comparator/reference source only. CAN SLIM may adopt, modify, or reject any TrendFoll rule without changing TrendFoll production.

## Current production/research boundary — 18 Sep 2026

- CAN SLIM v1 production baseline: **FROZEN**.
- #32 Theory-Faithful Candidate Specification v1: **COMPLETE / FROZEN**.
- #33 O'Neil Pattern Recognition Engine: **CORE COMPLETE / FROZEN — P8 CONDITIONAL PASS**; production contract remains `oneil-pattern-output-v2` with four core families only.
- P6 `ASCENDING_BASE` / `BASE_ON_BASE`: **DEFERRED / NOT PRODUCTION-VALIDATED**, outside production.
- #34 Theory-Faithful Candidate Generator: **COMPLETE / FROZEN v1**.
- #35 Candidate Validation: **COMPLETE / FROZEN — CONDITIONAL PASS**.
- Production Candidate → eligibility → T+1 Open Entry → Lifecycle contracts are implemented/frozen; the remaining lifecycle observation boundary is **`BLOCKED_ON_PRODUCTION_ENTRY_POPULATION`** and must close only from natural production evidence.
- Production compute ordering is currently pattern-first before full CAN SLIM evidence assembly. The conceptual decision ordering is quality/watchlist-first then pattern/timing. This is formally tracked in `docs/progress-board.md` as **`IDENTIFIED / NOT_YET_REMEDIATED`** and does not authorize a production refactor.
- Successor architecture is now governed by `docs/decisions/2026-09-18-original-canslim-production-v2-contract.md`: **v1 remains frozen**, while v2 is a separate methodology-first path using C/A fundamental screening before expensive stock-level #33 work, role-aware evidence semantics, separate periodic full-universe Pattern Intelligence, and explicit `ORIGINAL / OPERATIONALIZATION / DATA_ADAPTATION / PROXY / UNAVAILABLE` labels. Exact v2 C/A machine formulas remain source-lock blockers before implementation.
- FWD1 and EXH2 remain separate frozen/prospective tracks and must not alter frozen production semantics.

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

1. Preserve the frozen CAN SLIM v1 production baseline and fail-closed PIT contracts.
2. Accumulate natural Candidate → T+1 Entry → Lifecycle production evidence; do not synthesize an entry merely to close the observation boundary.
3. Keep the production-ordering observation documented but **HOLD** any watchlist-first refactor until there is a concrete operational/research requirement and a semantic-equivalence validation plan.
4. Keep backtest architecture independent: FA-first/event-driven historical research does not require full-universe pattern replay and does not dictate production compute order.
5. Keep FWD1/EXH2 separate; resolve their operational freshness/evidence debt without changing frozen production strategy semantics.
