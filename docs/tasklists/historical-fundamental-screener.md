# Tasklist — Historical CAN SLIM Fundamental Screener

Status: **COMPLETE / VALIDATED / FROZEN**

## Objective

Produce historical NYSE decision-date lists of stocks whose point-in-time fundamental evidence satisfies the frozen CAN SLIM C/A criteria. **STOP after the validated fundamental-qualified dataset.**

## Frozen boundary

In scope: SEC/fundamental PIT evidence, identity/CIK, frozen C/A evaluation, PASS/FAIL/NOT_EVALUABLE, provenance, decision-date output, correctness and anti-lookahead validation.

Out of scope: OHLCV screening, O'Neil patterns, technical candidates, breakout/pivot/volume, entries/exits, trade simulation, performance backtest, optimization, legacy OHLCV restoration, and creation of a large historical R2 corpus.

## Governing invariants

- `accepted_at <= decision cutoff`; no filing/amendment leakage backward.
- Missing evidence is not zero and retains NOT_EVALUABLE semantics where required.
- Frozen thresholds/extraction semantics are not tuned to increase PASS count.
- No future price, return, trade outcome, or technical signal participates in qualification.
- Historical Musaffa membership is not reconstructed; static frozen/current-universe eligibility/survivorship bias remains documented.

## Execution checklist

- [x] **FUND-01 — Audit current implementation and handoff.** Existing candidate-attached implementation was audited; `generate_candidates(...)` was rejected as the screener population source.
- [x] **FUND-02 — Establish historical evidence source path.** Pinned SEC/PIT fundamentals snapshot from `ussy-fundamentals`; manifest `fundamentals/snapshots/2026-09-16/run-35091300858/manifest.json`; 1,327-security frozen/current research universe; 44 missing CIK.
- [x] **FUND-03 — Verify PIT reconstruction.** Event-driven states; frozen decision cutoff; 0 future C-source and 0 future A-source violations.
- [x] **FUND-04 — Verify frozen evaluator.** Reused `src/canslim_research/labels.py`: C requires EPS YoY >=25% and revenue YoY >=25%; A requires latest three consecutive annual EPS growth observations all >=25%; PASS/FAIL/NOT_EVALUABLE preserved.
- [x] **FUND-05 — Build/verify efficient preparation layer.** Reusable event-driven PIT transitions; no new material historical R2 dataset.
- [x] **FUND-06 — Produce output.** `fundamental_state_transitions.csv`, `ca_pass_intervals.csv`, `ca_pass_by_decision_date.csv`, `latest_ca_pass.csv`, summaries and pinned provenance.
- [x] **FUND-07 — Validate output.** Run `35175083156`, commit `25288c3844d9800b8465525952b427a882464976`, SUCCESS. 47,817 transitions; 0 duplicates; 8 C+A PASS transitions; 5 intervals; 392 PASS decision dates; 515 date×security PASS rows; PASS symbols `BCC`, `CRUS`, `MEDP`; 303 securities without transitions.
- [x] **FUND-08 — Freeze terminal artifact and document result.** Decision: `docs/decisions/2026-09-17-historical-fundamental-screener-v1.md`. Artifact `historical-fundamental-screener-v1-35175083156`, ID `10478028865`, 1,827,934 bytes, archive SHA256 `15f126b7f7adb1be233ef3e9353b9b761bdb7bf5c198e6f465dacf506024293b`. Workflow restored to manual-only.

## Terminal result

The direct historical answer is `ca_pass_by_decision_date.csv`. Across the pinned evidence and frozen/current research universe, only **BCC, CRUS, and MEDP** ever satisfy C+A simultaneously. There are 392 NYSE decision dates with at least one PASS and 515 date×security PASS rows. Latest C+A PASS count is 0.

## Definition of done

**DONE.** Validated reproducible PIT output exists with component states, qualification, provenance, explicit unsupported states, and decision-date PASS lists.

## STOP

This workstream is **FROZEN**. Do not continue into technical screening or trading research unless the user explicitly opens a separate scope.
