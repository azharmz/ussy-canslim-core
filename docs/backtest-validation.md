# CAN SLIM v1 Historical Backtest Validation

Status: **BT0 COMPLETE / BT1 BLOCKED_ON_HISTORICAL_INPUT_COVERAGE**

Date opened: 2026-09-16
BT1 evidence run: `35046760706` — **SUCCESS**

## Purpose

Empirically evaluate the already-frozen CAN SLIM v1 production baseline by historical replay. This workstream is evidence/validation only. It does not reopen, tune, optimize, or redefine frozen CAN SLIM semantics.

Engineering/integration freeze remains valid independently of backtest outcome. Phase 8B natural populated Entry→Lifecycle production observation also remains a separate prospective acceptance boundary.

## BT0 — Governance / no-tuning lock

**COMPLETE**

Rules:

1. Replay the frozen CAN SLIM v1 contract as-is.
2. Daily decision information is limited to information available by the governed decision cutoff; SEC evidence must obey `accepted_at` availability.
3. Execution remains T+1 Open under the frozen Entry contract. No close-price execution substitution.
4. Frozen N-v1 remains the governed price/new-high breakout evidence. Historical catalyst data must not be silently added and called CAN SLIM v1.
5. Frozen S/L/I/M eligibility states remain mandatory and fail-closed exactly as production specifies.
6. O'Neil morphology must consume the frozen `oneil-pattern-output-v2` four-core production contract pinned by the production baseline; do not rebuild or tune morphology in the backtest.
7. Backtest results must not be used to alter thresholds/rules inside this validation cycle. Any later hypothesis or v2 development must be separately governed and tested on untouched evidence.
8. Missing historical inputs remain missing/NOT_EVALUABLE; they must not be imputed from future/current information.
9. Report data coverage and attrition before performance metrics.
10. Preserve reproducibility: code ref, input object keys/versions, hashes where available, date window, and output artifacts.

## BT1 — Historical / PIT data readiness audit

**BLOCKED_ON_HISTORICAL_INPUT_COVERAGE — full historical performance backtest is NOT authorized yet.**

A fresh read-only R2 audit was executed in Actions run `35046760706`. No strategy returns were inspected.

| Input / layer | Fresh evidence | BT1 assessment |
|---|---|---|
| Historical OHLCV | 1,300 `backtest/ohlcv/*.parquet` objects | Long-history technical replay feasible |
| Research universe | Frozen contemporary/current Musaffa research-universe design remains the declared historical research contract | Allowed for the declared research question; not historical eligibility reconstruction |
| Historical membership alternative | only `universe/membership/2026-08-28.json` exists | True historical Musaffa-membership reconstruction unavailable before 2026-08-28 |
| Fundamentals C/A | current immutable PIT snapshot has 47,267 wide rows / 85,519 long rows; accepted-at evidence spans 2009-04-15 through 2026-09-14; annual accepted-at begins 2009-10-27 | **PIT source coverage exists. Historical C/A attachment was already separately validated with zero future accepted-at violations.** |
| Institutional I | 19,636 live rows with exact EDGAR `accepted_at`, but live accepted-at spans only 2026-07-01 through 2026-09-10. Historical state events: 14,529,166 rows / 993 CUSIPs, `available_on` spans 2013-05-21 through 2026-05-30 | **BLOCKER for frozen-fidelity long backtest.** Production resolver requires exact accepted-at live state for the latest period; old history exposes date-level `available_on`, not the same exact accepted-at contract. Do not silently substitute it. |
| Market M | `market/state/` currently has only four JSON objects: canonical states for 2026-09-11 and 2026-09-14 plus official pointer | **BLOCKER for direct canonical-state historical replay.** Frozen classifier code exists and is causal, so a separately audited historical reconstruction may be possible, but current canonical R2 state history is not a long backtest dataset. |
| O'Neil patterns | production code pins `ussy-oneil-patterns` SHA `c433cc1e35a5aa32a46f732cd8c5545935e36e40`; pattern engine is OHLCV-driven | Code-pinned historical replay mechanically feasible once full mandatory evidence intersection is valid |
| T+1 Entry | frozen production execution code exists | Replayable once Candidate history is valid |
| Lifecycle/outcomes | frozen production lifecycle semantics exist | Replayable once executable Entry history is valid |

### C/A reconciliation

BT1 initially listed C/A as TO VERIFY. Repository history shows this was already solved before the production remediation cycle: historical C/A attachment workflow run `34479060107` validated the 10,731 historical technical candidates using immutable SEC PIT evidence. It reported zero future `accepted_at` violations, explicit SEC FY identity, and fail-closed unresolved FY handling. Therefore C/A is not the current BT1 blocker.

### Institutional boundary

The canonical production I resolver deliberately distinguishes exact live filing availability from historical state events. It filters the latest live state using timezone-aware `I_available_at <= decision_cutoff`; historical prior-period events are resolved from `available_on`. The fresh audit proves the exact-live layer begins only on 2026-07-01. A long historical backtest cannot relabel the older date-level event stream as exact accepted-at without a new evidence reconstruction/audit.

### Market boundary

The frozen #46 classifier is causal and versioned (`46-market-state-classification-v1`), while the #50 production consumer requires an exact same-session canonical state and rejects future or stale state. R2 currently retains only 2026-09-11 and 2026-09-14 canonical market-state runs. Therefore historical M needs a governed causal replay that reproduces #46 from historical major-index inputs; the current production pointer/history alone cannot supply long-history M.

### Existing evidence that must not be mistaken for the final backtest

- E0 rolling baseline was explicitly `ROLLING_CURRENT_MEMBERSHIP_SMOKE_NOT_FULL_PIT_BACKTEST` and prohibited PF/CAGR/drawdown claims.
- E0 static-history candidate study was explicitly `STATIC_2026_08_28_UNIVERSE_EXPLORATORY_NOT_PIT_UNIVERSE`; it generated 6,095,031 evaluable rows and 10,731 technical candidate rows but prohibited full strategy-performance claims.
- Those artifacts remain useful readiness/mechanism evidence, not a substitute for frozen full C/A/N/S/L/I/M replay.

## Backtest validation checklist

| Phase | Scope | Status |
|---|---|---|
| BT0 | Scope + no-tuning governance | **COMPLETE** |
| BT1 | Historical/PIT data readiness audit | **BLOCKED_ON_HISTORICAL_INPUT_COVERAGE** |
| BT1-I | Reconstruct/audit exact historical institutional availability compatible with frozen I | **NEXT BLOCKER** |
| BT1-M | Reconstruct/audit causal historical #46 M state from governed index inputs | PENDING |
| BT2 | Frozen historical replay contract | PENDING |
| BT3 | Reproducible Colab runner | PENDING |
| BT4 | Historical Candidate reconstruction | PENDING |
| BT5 | T+1 Entry reconstruction | PENDING |
| BT6 | Lifecycle/outcome reconstruction | PENDING |
| BT7 | Backtest execution | PENDING |
| BT8 | Performance + robustness analysis | PENDING |
| BT9 | Independent leakage/reproducibility audit | PENDING |
| BT10 | Final empirical evidence freeze | PENDING |

## BT1 exit criteria

BT1 closes only after C/A, I, canonical M reconstruction, frozen #33 pattern replay, OHLCV and the declared research-universe design have a defensible common historical window with no future leakage.

Current verdict is deliberately fail-closed: `BLOCKED_ON_HISTORICAL_INPUT_COVERAGE`. Eligibility rules will not be weakened merely to produce backtest metrics.

## Intended compute architecture after BT1

GitHub remains source of truth for frozen code/governance. R2 remains the data/evidence source. Google Colab is the intended compute runner for the heavy historical replay after BT1 clears. The notebook must pin repository code and input contracts and emit reproducible artifacts/results rather than becoming an alternate strategy implementation.
