# Tasklist — Historical CAN SLIM Fundamental Screener

Status: **ACTIVE / SCOPE LOCKED**

This file is the execution authority for the current historical-fundamental workstream. Work must stay inside this boundary unless the user explicitly changes the scope.

## Objective

Produce, for each required historical decision date, the list of stocks whose **fundamental evidence available at that time** satisfies the frozen CAN SLIM fundamental criteria.

The terminal deliverable is a reusable historical screener result answering:

> On decision date T, which stocks satisfied the applicable frozen CAN SLIM fundamental criteria using only information actually available by T?

**STOP after the fundamental-qualified stock list/dataset is produced and validated.**

## Hard scope boundary

### In scope

- historical SEC/fundamental evidence;
- point-in-time reconstruction using filing availability / `accepted_at`;
- security identity / CIK mapping required for fundamental evaluation;
- frozen CAN SLIM fundamental semantics already authorized by repository governance;
- PASS / FAIL / NOT_EVALUABLE states and reasons;
- efficient preparation/cache/artifact needed to avoid repeatedly reconstructing raw fundamentals;
- final historical stock lists/dataset satisfying the fundamental criteria;
- correctness, completeness, reproducibility and anti-lookahead validation.

### Out of scope

- OHLCV historical screening;
- O'Neil pattern recognition;
- technical candidate generation;
- breakout/pivot/volume logic;
- entry/exit or lifecycle logic;
- trade simulation;
- strategy performance backtest;
- optimization/tuning based on returns;
- rebuilding or restoring deleted legacy R2 historical OHLCV;
- adding a large historical corpus to R2 merely for this workstream.

R2 is **not** to be treated as the assumed historical-data source or default destination. Existing production R2 artifacts may be read only when genuinely required by an already-authorized contract, but this workstream must not create new material R2 storage load without an explicit requirement and user approval.

## Governing invariants

- Preserve all already-frozen CAN SLIM fundamental semantics; this task is implementation/audit, not strategy redesign.
- `accepted_at` / actual information availability is the PIT boundary. No later filing or amendment may leak backward.
- Missing evidence is not zero and must not silently become FAIL if the frozen contract says NOT_EVALUABLE.
- Do not tune thresholds or extraction logic to increase the number of passing stocks.
- Do not use future prices, future returns, trade outcomes or technical signals to construct or validate fundamental qualification.
- Prefer low-cost ephemeral preparation and reusable CI artifacts/cache over persistent duplication of historical data.
- Every long-running CI phase must emit lightweight start/progress/completion logs.

## Execution checklist

- [x] **FUND-01 — Audit current implementation and handoff**
  - Existing frozen PIT C/A methodology: `docs/methodology/historical-ca-asof-v1.md`.
  - Existing implementation: `scripts/run_historical_ca_attachment.py` + `src/canslim_research/labels.py`.
  - Existing workflow: `.github/workflows/historical-ca-attachment-v1.yml`.
  - Existing validated implementation already enforces the 16:00 America/New_York decision cutoff, `accepted_at <= cutoff`, amendment causality, explicit annual FY identity/consecutiveness, and PASS/FAIL/NOT_EVALUABLE semantics.
  - **Important mismatch:** the existing runner obtains evaluation dates/securities from `generate_candidates(...)`, so its output is attached to technical candidate rows. That population source is OUT OF SCOPE for the active screener and must be replaced, not extended.
  - Historical C/A workflow currently has a narrow `push` trigger on `main`; therefore edits to its workflow/runner/labels are potential compute executions and must follow the repository Actions execution governance.
  - The BT5C landmark/pattern workstream and its R2 OHLCV inputs are unrelated to this task and are excluded.

- [ ] **FUND-02 — Establish historical evidence source path**
  - Identify how historical SEC evidence is obtained without assuming historical snapshots exist in R2.
  - Record coverage limits and source provenance.
  - Confirm identity chain from research-universe security to CIK/fundamental evidence.

- [ ] **FUND-03 — Verify PIT reconstruction**
  - For decision date T, enforce evidence availability at/before T according to the frozen decision-time contract.
  - Verify amendment handling and fiscal-period resolution.
  - Add/retain hard anti-lookahead assertions.

- [ ] **FUND-04 — Verify frozen CAN SLIM fundamental evaluator**
  - Inventory the frozen fundamental criteria/states actually supported by the repository.
  - Reuse them unchanged.
  - Confirm PASS / FAIL / NOT_EVALUABLE reasons are deterministic and auditable.

- [ ] **FUND-05 — Build/verify efficient preparation layer**
  - Prepare historical PIT fundamental states once for reuse by the screener.
  - Avoid repeated raw-SEC reconstruction where a safe reusable artifact/cache suffices.
  - Do not introduce a new large R2 historical dataset.

- [ ] **FUND-06 — Produce historical fundamental screener output**
  - Generate per-date/per-security fundamental states.
  - Produce the filtered list of stocks satisfying the applicable frozen CAN SLIM fundamental criteria.
  - Preserve enough provenance/reason fields to audit every qualification.

- [ ] **FUND-07 — Validate output**
  - Check duplicate identities/rows.
  - Check unresolved/missing CIK and fiscal-period cases.
  - Check `max(source accepted_at used) <= decision cutoff`.
  - Check state distributions and unsupported/not-evaluable cases.
  - Regression-check against previously validated fundamental evidence where comparable.

- [ ] **FUND-08 — Freeze terminal artifact and document result**
  - Record source/version/provenance, methodology version, checksums and validation summary.
  - Mark the historical fundamental screener dataset READY only after all correctness gates pass.
  - Update the project progress documentation with the terminal result.
  - **STOP. Do not continue into technical screening or trading backtest.**

## Definition of done

This workstream is DONE when we have a validated, reproducible output that can answer for every supported historical decision date:

1. which research-universe securities were evaluable;
2. their frozen CAN SLIM fundamental component states;
3. which securities passed the applicable overall fundamental qualification;
4. the PIT evidence/provenance supporting each decision;
5. explicit reasons for FAIL or NOT_EVALUABLE where applicable.

No technical or trading-performance result is required for completion.

## Execution rule

Before every implementation step, compare the proposed action against this tasklist. If an action does not advance FUND-01 through FUND-08, do not perform it. If repository history or an old workflow conflicts with this scope, preserve the historical record but follow this tasklist for the active workstream and document the conflict rather than silently expanding scope.
