# CAN SLIM v1 Historical Validation

Status: **BT0 COMPLETE / BT1-M NEXT — PRICE/VOLUME BACKTEST PATH AUTHORIZED**

Date opened: 2026-09-16
BT1 evidence run: `35046760706` — **SUCCESS**

## Purpose and boundary

The frozen CAN SLIM v1 production baseline remains unchanged and frozen.

Historical empirical validation is now deliberately split into two separate evidence tracks rather than forcing all production evidence into one retrospective replay:

1. **BT-PV — Price / Volume / Market historical backtest**: replay the historically tractable price-volume components, frozen O'Neil morphology, N/S/L/M, frozen T+1 Open execution, and frozen lifecycle/outcomes.
2. **BT-FAI — Fundamental / Institutional validation**: validate C/A fundamentals and I institutional sponsorship separately against the candidate/trade evidence produced by BT-PV, with their own PIT/coverage limitations disclosed.

BT-PV is **not** a full CAN SLIM v1 backtest and must never be labelled as one. Removing C/A/I from the retrospective gate is a research-design boundary only; it does not change production `CANSLIM_ELIGIBLE`, where the frozen C/A/N/S/L/I/M requirements remain mandatory and fail-closed.

This split avoids manufacturing historical timestamps, weakening production semantics, or expanding R2 merely to make a monolithic backtest possible.

## BT0 — Governance / no-tuning lock

**COMPLETE**

Rules:

1. Production CAN SLIM v1 semantics remain frozen and untouched.
2. BT-PV uses only historically causal information available through each decision date.
3. Execution remains the frozen T+1 Open contract. No close-price execution substitution.
4. Frozen N-v1 remains governed price/new-high breakout evidence. Historical catalyst data is not silently added.
5. Frozen O'Neil morphology remains `oneil-pattern-output-v2`, four production-authorized core patterns, pinned to `ussy-oneil-patterns` SHA `c433cc1e35a5aa32a46f732cd8c5545935e36e40`.
6. BT-PV does not use C/A/I as eligibility gates. Its outputs must use a distinct research label and must not emit or imply production `CANSLIM_ELIGIBLE`.
7. C/A and I are evaluated only in BT-FAI, separately from BT-PV execution/performance generation.
8. Backtest results must not be used to tune frozen thresholds/rules in this validation cycle.
9. Missing evidence remains missing/NOT_EVALUABLE; no future/current information may be imputed backward.
10. Report coverage and attrition before performance metrics and preserve code/input/output provenance.

## Why the validation was split

Fresh Actions audit `35046760706` established that historical OHLCV and C/A evidence are substantial, but exact institutional availability compatible with the prospective production contract is not available over the same long window. Historical institutional state events use date-level `available_on`, while the exact live EDGAR `accepted_at` layer begins only in 2026. Forcing that older stream into the exact production-I contract would create an unjustified PIT assumption.

C/A is therefore not discarded. It moves to a separate fundamental validation track. I likewise moves to a separate institutional validation track. This allows their empirical contribution to be studied without contaminating the causal price/volume backtest.

## BT-PV readiness

| Input / layer | Evidence | Assessment |
|---|---|---|
| Historical OHLCV | 1,300 `backtest/ohlcv/*.parquet` objects | **READY** for long-history price/volume replay |
| Research universe | frozen contemporary/current Musaffa research-universe design | **READY** for declared static-universe research; not historical membership reconstruction |
| O'Neil patterns | pinned frozen four-core production engine, OHLCV-driven | **MECHANICALLY READY**; historical replay must use pinned code |
| N | frozen price/new-high breakout evidence | **READY** from causal price history |
| S | frozen price/volume supply-demand evidence | **READY** from causal price/volume history |
| L | frozen relative-strength/leadership evidence | **READY SUBJECT TO** exact production-compatible historical calculation |
| M | frozen #46 causal market classifier exists, but R2 canonical-state history is only recent | **NEXT READINESS TASK:** reconstruct/audit historical M causally from governed major-index inputs |
| T+1 Entry | frozen production execution code exists | **READY** after BT-PV Candidate/event reconstruction |
| Lifecycle/outcomes | frozen production lifecycle semantics exist | **READY** after executable historical Entries exist |

### Historical M boundary

The frozen #46 classifier is causal and versioned (`46-market-state-classification-v1`). The #50 production consumer intentionally requires an exact same-session canonical state and rejects future/stale states. R2 retains only recent canonical market-state runs, so BT-PV must not use the current pointer retrospectively.

The next task is therefore to build and audit a **causal historical replay of the frozen #46 classifier** from governed historical major-index OHLCV. This is reconstruction using frozen logic, not strategy tuning.

## BT-FAI — separate C/A/I validation

### C/A fundamentals

Existing repository evidence is already strong enough to make this a separate validation dataset rather than a blocker for BT-PV. The immutable PIT snapshot has 47,267 wide rows / 85,519 long rows with `accepted_at` evidence extending back to 2009. Historical C/A attachment was previously validated against the 10,731 technical candidates with zero future `accepted_at` violations.

BT-FAI will use C/A to ask questions such as whether candidate/trade outcome distributions differ across frozen C/A states. It will not retroactively change BT-PV entries.

### I institutional sponsorship

Fresh audit evidence found 14,529,166 historical state-event rows / 993 CUSIPs, but exact live EDGAR `accepted_at` coverage begins only in 2026. Therefore long-history I validation must disclose its historical `available_on` evidence boundary rather than pretending it is identical to the production exact-timestamp contract.

BT-FAI may evaluate I only within defensible coverage and must report NOT_EVALUABLE where the production-compatible evidence is unavailable.

## Existing historical evidence

- E0 rolling baseline remains `ROLLING_CURRENT_MEMBERSHIP_SMOKE_NOT_FULL_PIT_BACKTEST` and is not performance evidence for BT-PV.
- E0 static-history study produced 6,095,031 evaluable rows and 10,731 technical candidate rows under the frozen 2026-08-28 research universe. It remains exploratory readiness evidence, not the final BT-PV execution backtest.
- Fresh BT1 audit run `35046760706` inspected historical input coverage only; `strategy_returns_inspected=false`.

## Validation checklist

| Phase | Scope | Status |
|---|---|---|
| BT0 | Scope + no-tuning governance | **COMPLETE** |
| BT1 | Historical input readiness discovery | **COMPLETE — evidence boundary identified** |
| BT1-M | Causal historical frozen-#46 M reconstruction/readiness | **NEXT** |
| BT2 | Freeze BT-PV replay contract and distinct research output labels | PENDING |
| BT3 | Reproducible Colab runner | PENDING |
| BT4 | Historical N/S/L/M + O'Neil event reconstruction | PENDING |
| BT5 | Frozen T+1 Entry reconstruction | PENDING |
| BT6 | Frozen Lifecycle/outcome reconstruction | PENDING |
| BT7 | BT-PV execution | PENDING |
| BT8 | BT-PV performance + robustness analysis | PENDING |
| BT-FAI-C/A | Separate frozen C/A empirical validation | PENDING |
| BT-FAI-I | Separate institutional empirical validation within defensible PIT coverage | PENDING |
| BT9 | Independent leakage/reproducibility audit | PENDING |
| BT10 | Final empirical evidence freeze | PENDING |

## Compute architecture

GitHub remains source of truth for code, frozen contracts, governance, and reproducibility metadata. R2 supplies the already-available historical market/evidence data required by each track. Google Colab is the intended heavy-compute runner for BT-PV once historical M readiness is closed.

The Colab runner must pin repository code and the frozen O'Neil dependency, consume governed inputs, and emit reproducible artifacts/results. It must not become an alternate implementation of the strategy.

## Immediate next step

**BT1-M:** identify the governed major-index historical OHLCV already available, then prove that the frozen #46 state machine can be replayed chronologically without future leakage. If the required index inputs are unavailable, stop with an explicit M data-coverage blocker rather than substituting a different market rule.
