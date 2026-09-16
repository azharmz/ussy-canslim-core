# CAN SLIM v1 Historical Backtest Validation

Status: **BT0 COMPLETE / BT1 IN PROGRESS — READINESS BOUNDARY IDENTIFIED**

Date opened: 2026-09-16

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

**IN PROGRESS — full historical performance backtest is NOT YET AUTHORIZED.**

Repository evidence already establishes the following:

| Input / layer | Current evidence | BT1 assessment |
|---|---|---|
| Historical OHLCV | `backtest/ohlcv/{security_id}.parquet`, 1,300 objects in E0 audit | Long-history technical replay feasible |
| Research universe | Project README explicitly defines primary historical research as a frozen contemporary/current Musaffa-compliant universe; historical Musaffa compliance is not a strategy input for that design | Static-universe research is allowed by project contract, but must not be mislabeled as historical eligibility reconstruction |
| Historical membership alternative | E0 audit found only one membership snapshot, 2026-08-28 | True historical Musaffa-membership reconstruction before 2026-08-28 unavailable under current data contract |
| Technical candidate reconstruction | E0 static study reconstructed 6,095,031 evaluable rows and 10,731 technical candidate rows using frozen 2026-08-28 membership | Mechanism replay feasible; existing study is explicitly exploratory, not full CAN SLIM performance evidence |
| Fundamentals C/A | Production contract is accepted-at PIT; historical backtest must prove historical C/A source coverage and exact decision-time join before authorization | **TO VERIFY** |
| Institutional I | Production code has exact accepted-at live semantics plus historical state events and fail-closed lineage handling | PIT mechanism exists; **historical coverage window/completeness still TO VERIFY** |
| Market M | Earlier E0 evidence had SPY objects but no QQQ contract and explicitly treated SPY-only as incomplete relative to then-frozen SPY-or-QQQ specification | **RE-AUDIT against current canonical frozen M contract required** |
| O'Neil patterns | Production #33 is external/frozen four-core contract | Need historical replay feasibility at pinned implementation/input history; **TO VERIFY** |
| T+1 Entry | Frozen production execution code exists | Mechanically replayable once Candidate history is valid |
| Lifecycle/outcomes | Frozen production lifecycle semantics exist | Mechanically replayable once historical executable Entries are valid |

### Existing evidence that must not be mistaken for the final backtest

- E0 rolling baseline was explicitly `ROLLING_CURRENT_MEMBERSHIP_SMOKE_NOT_FULL_PIT_BACKTEST` and prohibited PF/CAGR/drawdown claims.
- E0 static-history candidate study was explicitly `STATIC_2026_08_28_UNIVERSE_EXPLORATORY_NOT_PIT_UNIVERSE`; it generated a large historical technical event set but prohibited performance/production claims.
- Those artifacts are useful readiness evidence, not a substitute for the frozen full C/A/N/S/L/I/M replay.

## Backtest validation checklist

| Phase | Scope | Status |
|---|---|---|
| BT0 | Scope + no-tuning governance | **COMPLETE** |
| BT1 | Historical/PIT data readiness audit | **IN PROGRESS** |
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

BT1 may close only when the repo has evidence for the actual historical availability window and join semantics of C/A, I, current canonical M, frozen #33 pattern replay, OHLCV, and the declared research-universe design. The audit must state the intersection date window in which all mandatory frozen eligibility components can be evaluated without future leakage.

If no useful full-component intersection exists, BT1 must report `BLOCKED_ON_HISTORICAL_INPUT_COVERAGE`; it must not weaken eligibility to make a backtest run.

## Intended compute architecture after BT1

GitHub remains source of truth for frozen code/governance. R2 remains the data/evidence source. Google Colab may be used as the compute runner for the heavy historical replay, but the notebook must pin repository code and input contracts and must emit reproducible artifacts/results rather than becoming an alternate strategy implementation.
