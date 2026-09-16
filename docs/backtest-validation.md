# CAN SLIM v1 Historical Validation

Status: **BT0 COMPLETE / BT1-M BLOCKED ON LONG-HISTORY CANONICAL INDEX COVERAGE**

Date opened: 2026-09-16
BT1 evidence run: `35046760706` — **SUCCESS**
BT1-M inventory run: `35047685677` — **SUCCESS**
BT1-M content run: `35048973755` — **SUCCESS**

## Purpose and boundary

The frozen CAN SLIM v1 production baseline remains unchanged and frozen.

Historical empirical validation is deliberately split into two separate evidence tracks:

1. **BT-PV — Price / Volume / Market historical backtest**: replay historically tractable price-volume components, frozen O'Neil morphology, N/S/L/M, frozen T+1 Open execution, and frozen lifecycle/outcomes.
2. **BT-FAI — Fundamental / Institutional validation**: validate C/A fundamentals and I institutional sponsorship separately against candidate/trade evidence produced by BT-PV, with their PIT/coverage limitations disclosed.

BT-PV is **not** a full CAN SLIM v1 backtest and must never be labelled as one. Removing C/A/I from the retrospective gate is a research-design boundary only; it does not change production `CANSLIM_ELIGIBLE`, where frozen C/A/N/S/L/I/M requirements remain mandatory and fail-closed.

## BT0 — Governance / no-tuning lock

**COMPLETE**

1. Production CAN SLIM v1 semantics remain frozen and untouched.
2. BT-PV uses only historically causal information available through each decision date.
3. Execution remains the frozen T+1 Open contract. No close-price execution substitution.
4. Frozen N-v1 remains governed price/new-high breakout evidence. Historical catalyst data is not silently added.
5. Frozen O'Neil morphology remains `oneil-pattern-output-v2`, four production-authorized core patterns, pinned to `ussy-oneil-patterns` SHA `c433cc1e35a5aa32a46f732cd8c5545935e36e40`.
6. BT-PV does not use C/A/I as eligibility gates. Its outputs must use a distinct research label and must not emit or imply production `CANSLIM_ELIGIBLE`.
7. C/A and I are evaluated only in BT-FAI, separately from BT-PV execution/performance generation.
8. Backtest results must not tune frozen thresholds/rules in this validation cycle.
9. Missing evidence remains missing/NOT_EVALUABLE; no future/current information may be imputed backward.
10. Report coverage and attrition before performance metrics and preserve code/input/output provenance.

## Why the validation was split

BT1 run `35046760706` established substantial historical OHLCV and C/A evidence, while exact institutional availability compatible with the prospective production contract does not cover the same long window. C/A and I therefore move to separate validation tracks rather than contaminating the causal price/volume backtest.

## BT-PV readiness

| Input / layer | Evidence | Assessment |
|---|---|---|
| Historical stock OHLCV | 1,300 `backtest/ohlcv/*.parquet` objects | **READY** for long-history price/volume replay |
| Research universe | frozen contemporary/current Musaffa research-universe design | **READY** for declared static-universe research; not historical membership reconstruction |
| O'Neil patterns | pinned frozen four-core production engine, OHLCV-driven | **MECHANICALLY READY**; historical replay must use pinned code |
| N | frozen price/new-high breakout evidence | **READY** from causal price history |
| S | frozen price/volume supply-demand evidence | **READY** from causal price/volume history |
| L | frozen relative-strength/leadership evidence | **READY SUBJECT TO** exact production-compatible historical calculation |
| M | frozen #46 classifier + canonical ^IXIC/^GSPC/^DJI datasets | **VALID FOR 2024-09-16..2026-09-14 ONLY; BLOCKED for long-history BT-PV** |
| T+1 Entry | frozen production execution code exists | **READY** after BT-PV Candidate/event reconstruction |
| Lifecycle/outcomes | frozen production lifecycle semantics exists | **READY** after executable historical Entries exist |

## BT1-M — canonical market-data audit

### Result

**BLOCKED_ON_LONG_HISTORY_CANONICAL_INDEX_COVERAGE** for the intended long-history BT-PV.

The canonical market-input objects themselves are clean and usable for a bounded two-year replay. Run `35048973755` resolved the official immutable run through `market/indexes/official.json`:

- official run: `34905626834`;
- publisher: `49-market-index-publisher-v1`;
- source contract: `47-market-input-data-contract-v1`;
- `NASDAQ_COMPOSITE` / source `^IXIC`: 500 rows;
- `SP500` / source `^GSPC`: 500 rows;
- `DJIA` / source `^DJI`: 500 rows;
- common coverage: **2024-09-16 through 2026-09-14**;
- required OHLCV columns present on all three;
- zero required-OHLCV nulls;
- zero duplicate dates;
- dates monotonically increasing.

The audit therefore returned `content_ready_for_causal_replay_contract=true`, but this means the **available 500-bar dataset is mechanically valid**, not that it is long enough for the intended historical backtest.

### Why we stop rather than silently replay two years

The stock-history research layer extends much farther back than September 2024. Running M only from 2024-09-16 and presenting the result as the intended long-history BT-PV would materially shrink the experiment and change its evidence population. That is not authorized by BT0.

ETF proxies remain forbidden. SPY/QQQ/DIA cannot replace the frozen major-index identities.

### Frozen #46 replay semantics

`46-market-state-classification-v1` is causal from completed-session index price/volume, but its full state machine also accepts explicit PIT inputs `leadership_confirming`, `weakening_confirmed`, and `correction_reset`. The frozen methodology explicitly says these must carry their own provenance and that #46 must not invent universal distribution-count, moving-average, breadth, or leadership thresholds.

Accordingly, a long-history M replay must not fabricate those booleans. Unsupported evidence remains unavailable. Any replay implementation must preserve this boundary and document initialization/prior-state semantics before execution.

### Required remediation

Extend the **same canonical index contract** (`NASDAQ_COMPOSITE`, `SP500`, `DJIA`; actual index identities, not ETF proxies) backward far enough to support the intended BT-PV period, with immutable provenance/manifest evidence. This is a data-coverage remediation, not a CAN SLIM rule change.

No strategy returns were inspected in BT1-M.

## BT-FAI — separate C/A/I validation

### C/A fundamentals

The immutable PIT snapshot has 47,267 wide rows / 85,519 long rows with `accepted_at` evidence extending back to 2009. Historical C/A attachment was previously validated against the 10,731 technical candidates with zero future `accepted_at` violations. BT-FAI will use C/A as a separate empirical overlay; it will not retroactively change BT-PV entries.

### I institutional sponsorship

BT1 found 14,529,166 historical state-event rows / 993 CUSIPs, but exact live EDGAR `accepted_at` coverage begins only in 2026. Long-history I validation must disclose its historical `available_on` evidence boundary and report NOT_EVALUABLE where production-compatible evidence is unavailable.

## Existing historical evidence

- E0 rolling baseline remains `ROLLING_CURRENT_MEMBERSHIP_SMOKE_NOT_FULL_PIT_BACKTEST` and is not performance evidence for BT-PV.
- E0 static-history study produced 6,095,031 evaluable rows and 10,731 technical candidate rows under the frozen 2026-08-28 research universe. It remains exploratory readiness evidence, not final BT-PV execution evidence.
- BT1 run `35046760706` and BT1-M runs inspected input coverage only; `strategy_returns_inspected=false`.

## Validation checklist

| Phase | Scope | Status |
|---|---|---|
| BT0 | Scope + no-tuning governance | **COMPLETE** |
| BT1 | Historical input readiness discovery | **COMPLETE — evidence boundary identified** |
| BT1-M | Causal historical frozen-#46 M reconstruction/readiness | **BLOCKED — canonical index history currently only 2024-09-16..2026-09-14** |
| BT2 | Freeze BT-PV replay contract and distinct research output labels | PENDING ON BT1-M |
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

GitHub remains source of truth for code, frozen contracts, governance, and reproducibility metadata. R2 supplies governed historical inputs. Google Colab remains the intended heavy-compute runner after historical M coverage is sufficient. The Colab runner must pin repository code and the frozen O'Neil dependency and must not become an alternate strategy implementation.

## Immediate next step

**BT1-M data remediation:** inspect the canonical index publisher/data-source path and extend `^IXIC`, `^GSPC`, and `^DJI` history under the existing `47-market-input-data-contract-v1`, without changing M semantics or substituting ETFs. Then rerun the same content/coverage audit before authorizing BT2.
