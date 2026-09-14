# CAN SLIM v1 — Post-Audit Remediation Register

Status: **ACTIVE — REMEDIATION REQUIRED**
Target: **CAN SLIM v1 — PRODUCTION BASELINE FROZEN**

## Scope lock

This remediation cycle fixes integration and correctness only.

**No strategy expansion, tuning, optimization, or new theory workstream is permitted during remediation.**

### Frozen / preserved components

The following remain frozen and must not be redesigned merely to satisfy remediation:

- production OHLCV / R2 infrastructure
- #33 four-core O'Neil pattern engine
- `oneil-pattern-output-v2`
- `33-core-p8-frozen-v1`
- P6 advanced-pattern exclusion
- upstream SEC PIT infrastructure
- existing entry, risk, sell, and lifecycle semantics

### Finding disposition

- **F01–F11:** active remediation scope; must be resolved or explicitly accepted by the independent re-audit before production freeze.
- **F12–F15:** controlled/freezeable debt unless remediation uncovers production-critical impact.

### Explicit prohibitions

- Do not reopen/tune frozen #33/#34/#36/#45/#46 strategy semantics.
- Do not invent missing CAN SLIM evidence or proprietary IBD-like proxies merely to force evaluability.
- Do not create a #55/new research workstream as part of this remediation.
- Do not optimize backtest/performance metrics during remediation.

## Remediation phases

| Phase | Work | Finding | Status |
|---:|---|---|---|
| 0 | Governance & remediation scope lock | all | **COMPLETE** |
| 1 | SEC decision-time PIT fix | F02 / P0 | **NEXT** |
| 2 | Freeze C/A/N/S/L/I/M semantics | F03/F05 | PENDING |
| 3 | Prospective I wiring | F04/F06 | PENDING |
| 4 | Canonical M + dependency pinning | F07/F08 | PENDING |
| 5 | Correct `CANSLIM_ELIGIBLE` | F03 / P0 | PENDING |
| 6 | Production candidate publisher | F10 | PENDING |
| 7 | Candidate → entry | F01/F11 | PENDING |
| 8 | Entry → lifecycle | F01/F11 | PENDING |
| 9 | E2E production orchestrator | F01 / P0 | PENDING |
| 10 | E2E integration CI | F09 | PENDING |
| 11 | Manifest / reproducibility | F01/F09 | PENDING |
| 12 | Clean prospective dry-run | acceptance | PENDING |
| 13 | Independent re-audit | acceptance | PENDING |
| 14 | Production Baseline Freeze | final | LOCKED UNTIL GO |

## Phase 0 acceptance checklist

- [x] Independent audit findings are adopted as the remediation authority.
- [x] F01–F11 are the active remediation scope.
- [x] F12–F15 are controlled debt unless production-critical evidence emerges.
- [x] Existing frozen production/research contracts remain frozen.
- [x] Strategy/performance tuning is prohibited during remediation.
- [x] No #55/new research workstream will be opened.
- [x] A single freeze acceptance path is established: remediation → E2E CI → prospective dry-run → independent re-audit → freeze.

**Phase 0 verdict: COMPLETE / SCOPE LOCKED.**

## Phase 1 — F02 / SEC decision-time PIT

This is the first technical remediation because a filing accepted after the relevant decision cutoff must not influence the same decision.

Required contract:

- introduce an explicit `decision_asof_timestamp`
- define `market_session` and `information_cutoff`
- preserve full SEC `accepted_at` timestamp until availability is decided
- require `accepted_at <= information_cutoff`
- filings after cutoff become eligible only for the appropriate later session
- amendments obey the same cutoff
- remove end-of-calendar-day UTC as a proxy for decision-time information availability

Required negative/regression tests:

- before cutoff → available
- exactly at cutoff → handled according to the frozen contract
- after cutoff / after market close → unavailable to the same-close decision
- later filing cannot leak backward
- amendments cannot leak backward
- timezone conversion preserves semantics
- existing C, A, PIT, and candidate tests remain green

Phase 1 exit criterion: **no fundamental information with `accepted_at > information_cutoff` can influence that decision.**

## Controlled debt

- F12 — silent missing-price accounting: may be closed while production manifest/accounting is implemented.
- F13 — #33 conditional validation debt: remains frozen/disclosed.
- F14 — stale documentation risk: clean up before final freeze.
- F15 — historical/deprecated artifacts: no cleanup requirement during blocker remediation.
