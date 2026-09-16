# CAN SLIM v1 Historical Validation

Status: **BT0 COMPLETE / BT1 COMPLETE / BT1-M BLOCKED ON HISTORICAL SEMANTIC EVIDENCE / BT2 OPEN**

Date opened: 2026-09-16
BT1 evidence run: `35046760706` — **SUCCESS**
BT1-M inventory run: `35047685677` — **SUCCESS**
BT1-M original content run: `35048973755` — **SUCCESS**
BT1-M long-history publisher run: `35052740492` — **SUCCESS**
BT1-M post-publish verification run: `35052773417` — **SUCCESS**
BT1-M causal replay run: `35053132268` — **SUCCESS MECHANICALLY / SEMANTICALLY BLOCKED**

## Purpose and boundary

The frozen CAN SLIM v1 production baseline remains unchanged and frozen.

Historical empirical validation is deliberately split into two evidence tracks:

1. **BT-PV — Price / Volume / Market historical validation**: replay historically tractable price-volume components, frozen O'Neil morphology, N/S/L/M, frozen T+1 Open execution, and frozen lifecycle/outcomes where the required upstream evidence is available.
2. **BT-FAI — Fundamental / Institutional validation**: validate C/A fundamentals and I institutional sponsorship separately, with PIT/coverage limitations disclosed.

BT-PV is **not** a full CAN SLIM v1 backtest and must never be labelled as one. Removing C/A/I from the retrospective gate is a research-design boundary only; production `CANSLIM_ELIGIBLE` remains unchanged and fail-closed.

## BT0 — Governance / no-tuning lock

**COMPLETE.** Production semantics remain frozen; replay is causal; execution remains T+1 Open; O'Neil is pinned to `oneil-pattern-output-v2` SHA `c433cc1e35a5aa32a46f732cd8c5545935e36e40`; no validation result may tune frozen rules; missing evidence remains NOT_EVALUABLE; provenance and attrition precede performance reporting.

## BT1 — Historical input readiness

**COMPLETE.** Historical stock OHLCV, the declared static/current Musaffa research-universe design, O'Neil OHLCV morphology, and causal N/S/L inputs are mechanically available. C/A and I remain separate BT-FAI overlays.

## BT1-M — canonical market evidence

### Data remediation result

The original 500-bar limitation was remediated without ETF substitution or M-rule changes. Official long-history run `35052740492` provides canonical actual-index identities:

- `NASDAQ_COMPOSITE` / `^IXIC`: 14,019 rows, 1971-02-05..2026-09-15;
- `SP500` / `^GSPC`: 24,793 rows, 1927-12-30..2026-09-15;
- `DJIA` / `^DJI`: 8,737 rows, 1992-01-02..2026-09-15;
- common causal coverage: **8,737 sessions, 1992-01-02..2026-09-15**.

Post-publish verification `35052773417` passed required columns, null, duplicate-date, monotonic-date, and long-history coverage checks. Thus **canonical M price/volume data is mechanically READY**.

### Causal replay finding

Run `35053132268` replayed the exact frozen `46-market-state-classification-v1` with no future bars and no fabricated unsupported inputs. Historical governed sources do not exist for `leadership_confirming`, `weakening_confirmed`, or `correction_reset`, so replay correctly supplied `None`, `None`, and `False` respectively.

Observed result: 4 `RALLY_ATTEMPT` sessions followed by 8,733 `FOLLOW_THROUGH_CONFIRMED` sessions; only one state transition occurred. This demonstrates that long index history alone is insufficient to reconstruct representative historical production M semantics. The previous mechanical authorization criterion based on session count was therefore rejected and corrected fail-closed in commit `7d623c4c5dfdebc46fc9019df218d2dbac2cc56c`.

**Terminal BT1-M verdict:** `BLOCKED_ON_HISTORICAL_M_SEMANTIC_EVIDENCE`.

This is an evidence boundary, not a classifier failure and not permission to invent historical leadership/weakening/correction thresholds. No strategy returns were inspected.

## BT2 — frozen component-replay contract

**OPEN.** BT1-M no longer blocks validation of components that do not require historical M. It **does block** calling a long-history result a complete N/S/L/M BT-PV strategy backtest and blocks M-gated Entry/Lifecycle performance claims.

The BT2 contract is:

1. Replay frozen O'Neil four-core morphology, N, S, and L independently and causally from historical OHLCV.
2. Preserve M as `NOT_EVALUABLE / BLOCKED_ON_HISTORICAL_M_SEMANTIC_EVIDENCE` for long-history component validation; never substitute a proxy M.
3. Emit research-only labels under a distinct `BT_PV_COMPONENT_*` namespace. Never emit or imply `CANSLIM_ELIGIBLE`.
4. Reconstruct candidate/event dates for component validation, but do not promote them to M-qualified strategy entries.
5. T+1 Entry and Lifecycle code may be regression-tested mechanically against reconstructed events, but long-history performance is not authorized until its required gating evidence is defensible.
6. No thresholds or morphology rules may be tuned from retrospective results.
7. The static/current Musaffa research universe remains explicitly a research-universe design, not historical membership reconstruction.
8. Every output must pin repository commit, O'Neil SHA, input manifests, decision date, and evidence availability.

## BT-FAI — separate C/A/I validation

C/A immutable PIT evidence has 47,267 wide rows / 85,519 long rows with `accepted_at` evidence extending back to 2009. Historical C/A attachment was previously validated against 10,731 technical candidates with zero future `accepted_at` violations. C/A remains a separate empirical overlay and cannot retroactively alter BT-PV component events.

I contains 14,529,166 historical state-event rows / 993 CUSIPs, while exact live EDGAR `accepted_at` coverage begins only in 2026. Historical `available_on` limitations must remain explicit and unsupported periods NOT_EVALUABLE.

## Validation checklist

| Phase | Scope | Status |
|---|---|---|
| BT0 | Scope + no-tuning governance | **COMPLETE** |
| BT1 | Historical input readiness discovery | **COMPLETE** |
| BT1-M | Frozen #46 M reconstruction/readiness | **TERMINAL BLOCKED — historical semantic evidence unavailable** |
| BT2 | Freeze component-replay contract and research labels | **COMPLETE — contract frozen here** |
| BT3 | Reproducible component runner | **NEXT** |
| BT4 | Historical N/S/L + O'Neil component event reconstruction | PENDING |
| BT5 | T+1 Entry mechanical reconstruction/regression | PENDING; no M-qualified performance |
| BT6 | Lifecycle mechanical reconstruction/regression | PENDING; no M-qualified performance |
| BT7 | Complete BT-PV execution | **BLOCKED ON BT1-M semantic evidence** |
| BT8 | Complete BT-PV performance + robustness | **BLOCKED ON BT7** |
| BT-FAI-C/A | Separate frozen C/A empirical validation | PENDING |
| BT-FAI-I | Separate institutional empirical validation | PENDING |
| BT9 | Independent leakage/reproducibility audit | PENDING |
| BT10 | Final empirical evidence freeze | PENDING |

## Compute architecture

GitHub remains source of truth for code, frozen contracts, governance, and reproducibility metadata. R2 supplies governed historical inputs. Google Colab remains the intended heavy-compute environment for large replay execution; the runner must pin repository code and frozen O'Neil dependency and must not become an alternate strategy implementation.

## Immediate next step

**BT3:** build a reproducible research-only component runner that inventories/pins inputs and reconstructs frozen O'Neil + N/S/L evidence without M qualification, strategy returns, or threshold tuning. First execution should be a bounded smoke/regression sample before scaling heavy compute.
