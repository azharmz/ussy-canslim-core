# Decision — I1 PIT ingestion validation

Date: 2026-09-12

Status: **CURRENT/LIVE DATA GATE PASS; FULL HISTORICAL BUILD RUNNING**

## Decision

The previous SEC/GitHub-runner blocker is closed. Institutional sponsorship remains a separate sidecar research track and does not modify frozen FWD1.

Current/live 13F filing-level ingestion is accepted as technically valid for I1 data-quality purposes based on canonical workflow run `34603142916`.

```text
Q3-2026 index filings = 9,731
filing success count = 9,731
filing failure count = 0
fetch success rate = 1.0
accepted_at complete rate = 1.0
period_of_report complete rate = 1.0
amendment count = 383
amendment classified count = 383
amendment classified rate = 1.0
ambiguous lineage events = 0
latest period_of_report = 2026-06-30
latest-period mapped securities = 996
data_gate_pass = true
strategy returns inspected = false
FWD1 modified = false
```

The historical engine uses official SEC Form 13F bulk datasets as as-filed source material and reconstructs manager-period state event-by-event. Historical I-v1 availability is frozen before performance inspection as:

```text
historical_available_on = SEC filing_date + 1 calendar day
```

This is deliberately conservative. Quarter-end is never treated as availability, and historical rows are never attached earlier than the filing date.

Frozen amendment lineage semantics:

```text
BASE                    -> REPLACE manager-period state
AMENDMENT_RESTATEMENT   -> REPLACE manager-period state
AMENDMENT_NEW_HOLDINGS  -> ADD only when a valid base exists
unclassified amendment  -> manager-period NOT_EVALUABLE
new-holdings without base -> manager-period NOT_EVALUABLE
```

The first three official SEC datasets passed the historical event-state smoke test in run `34604836077`.

A full build across all 53 official SEC datasets is running in workflow `34624132399`. No I performance rule may be evaluated until the full-build artifact is audited for coverage, unresolved lineage, and usable QoQ manager-count deltas.

## Guardrails

- No strategy returns/PF/CAGR are used to choose the I threshold.
- No fuzzy issuer-name mapping.
- Non-US-ISIN securities remain NOT_EVALUABLE unless a separately audited identifier crosswalk exists.
- Put/call rows are excluded from common-share sponsorship.
- FWD1 remains unchanged.
- Any I-enabled strategy will be separately versioned with a new validation clock.
