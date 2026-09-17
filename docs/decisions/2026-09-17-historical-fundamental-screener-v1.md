# Historical Fundamental Screener v1 — Terminal Decision

Date: 2026-09-17
Status: **READY / VALIDATED / FROZEN**

## Scope

This decision closes the historical CAN SLIM fundamental-only screener. It does not authorize OHLCV screening, O'Neil pattern recognition, technical candidate generation, trade simulation, strategy backtesting, or return-based tuning.

## Frozen contract

Population is the pinned frozen/current research universe. Fundamental evidence is point-in-time SEC-derived evidence from the pinned `ussy-fundamentals` snapshot. Decision dates are NYSE sessions with cutoff 16:00 America/New_York. Only evidence with `accepted_at <= cutoff` is available.

C-v1 PASS requires quarterly EPS YoY >=25% and revenue YoY >=25%. A-v1 PASS requires the latest three consecutive annual EPS growth observations all >=25%. Missing or unsupported evidence retains NOT_EVALUABLE semantics. Current production status is provenance only and is not applied retroactively as a historical economic-quality gate.

Historical Musaffa membership is not reconstructed; use of the frozen/current research universe therefore retains the documented static-history eligibility/survivorship limitation.

## Reproducibility

Validated code commit: `25288c3844d9800b8465525952b427a882464976`

Validated Actions run: `35175083156` — SUCCESS.

Pinned fundamentals manifest: `fundamentals/snapshots/2026-09-16/run-35091300858/manifest.json` (source run `35091300858`).

Actions artifact: `historical-fundamental-screener-v1-35175083156`, artifact ID `10478028865`, size `1,827,934` bytes, archive SHA256 `15f126b7f7adb1be233ef3e9353b9b761bdb7bf5c198e6f465dacf506024293b`.

Core transition artifact SHA256: `75804e75fd1d7be8641a21a2fda193aaf0fdc331ef2f197c5169b73dcd6ebe03`.

## Validation result

Universe: 1,327 securities. Securities with PIT transitions: 1,024. Missing CIK: 44. Securities without transitions: 303. Total state transitions: 47,817. Duplicate transitions: 0. Future C-source violations: 0. Future A-source violations: 0.

C+A produced 8 PASS transitions forming 5 PASS intervals. Materialization to NYSE decision dates produced 515 date×security PASS rows across 392 decision dates. The only securities that ever satisfy C+A simultaneously are `BCC`, `CRUS`, and `MEDP`. Latest C+A PASS count is 0.

## Terminal artifacts

`fundamental_state_transitions.csv` preserves event-driven PIT component states and evidence. `ca_pass_intervals.csv` is the compact PASS interval representation. `ca_pass_by_decision_date.csv` is the direct historical screener answer by NYSE decision date. `latest_ca_pass.csv`, `summary.json`, `validation.json`, and pinned source pointer/manifest files provide terminal audit provenance.

## Verdict

Historical Fundamental Screener v1 is **READY / VALIDATED / FROZEN** for the stated research contract. The workstream stops here. Any technical screening or trading study is a separate scope.
