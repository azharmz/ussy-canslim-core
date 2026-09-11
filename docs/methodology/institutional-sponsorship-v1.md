# Institutional Sponsorship v1 — SEC 13F Research Contract

Status: **PRE-REGISTERED / PIT INGESTION VALIDATED, HISTORICAL FULL BUILD RUNNING**

Date: 2026-09-11

## Purpose

Implement the missing CAN SLIM `I` component without contaminating frozen FWD1. `I` remains `NOT_IMPLEMENTED` in the frozen technical baseline until this separate research track proves that point-in-time institutional ownership can be reconstructed with adequate identifier coverage and amendment semantics.

This track is independent of TrendFoll and cannot modify X3, PORT1, FWD1, EXH2, C/A, or M.

## Primary source

Use SEC Form 13F filings / official SEC Form 13F data sets only for the first implementation. Form 13F reports holdings of institutional investment managers subject to Rule 13f-1. Holdings are reported quarterly and filings are generally due within 45 days after quarter-end.

Bulk SEC data are treated as as-filed source records, not as a ready-made PIT signal table.

## Point-in-time rule

The economic holding period (`period_of_report`) is **not** the date at which the information becomes usable.

For current/live filing-level data:

```text
usable filing state requires accepted_at <= decision_cutoff(T0)
```

Exact EDGAR `<ACCEPTANCE-DATETIME>` is the canonical live availability timestamp.

For historical bulk data, I-v1 freezes a deliberately conservative availability approximation **before any I performance ablation**:

```text
historical_available_on = SEC filing_date + 1 calendar day
```

Rationale: the official bulk datasets preserve filing date/accession but not the exact acceptance timestamp needed for intraday same-day use. Waiting until the next calendar day cannot make historical information available earlier than the filing date and therefore avoids quarter-end or same-day look-ahead. This historical approximation is explicitly versioned as `filing_date_plus_1_calendar_day_conservative_v1`.

Historical I-v1 may use this conservative approximation for daily T0 attachment. Exact accession-level acceptance-time reconstruction remains a possible later refinement, but it is **not required to retroactively alter I-v1 after performance is observed**. Any such refinement must be a separately versioned methodology.

Quarter-end must never be substituted as availability time.

## Amendments

Submission types `13F-HR` and `13F-HR/A` must be preserved. Amendments may restate or add holdings. No rule may simply "take the latest row" without resolving the amendment type and accession lineage.

Frozen lineage semantics:

```text
BASE                    -> replace manager-period state
AMENDMENT_RESTATEMENT   -> replace manager-period state
AMENDMENT_NEW_HOLDINGS  -> add to an already-valid manager-period state
unclassified amendment  -> manager-period becomes NOT_EVALUABLE until a later valid replacement restores it
new-holdings without valid base -> NOT_EVALUABLE
```

Records affected by unresolved amendments are never implicit zero or PASS.

## Security identity

13F information tables are keyed primarily by CUSIP; FIGI may be present but is not guaranteed.

Frozen universe identity remains `security_id`.

Deterministic mapping allowed in v1:

```text
if security_id is a valid US ISIN:
    derived_cusip9 = security_id[2:11]
```

No fuzzy issuer-name matching is allowed for production research attachment.

Foreign/ADR listings whose frozen `security_id` is not a US ISIN are `NOT_EVALUABLE` until a separately audited CUSIP/FIGI mapping is available.

## Validated ingestion evidence

Current/live filing-level canonical validation:

```text
workflow run = 34603142916
Q3-2026 index filings = 9,731
fetch success rate = 100%
accepted_at complete rate = 100%
period_of_report complete rate = 100%
amendments = 383
amendments classified = 383 (100%)
ambiguous lineage events = 0
data_gate_pass = true
latest period_of_report = 2026-06-30
latest-period mapped securities = 996
strategy returns inspected = false
FWD1 modified = false
```

Historical event-state smoke run `34604836077` = SUCCESS for the first three official SEC bulk datasets. Full official-history build is separately versioned and must complete its data-quality gate before I ablation.

## I-v1 candidate descriptors

Once full historical PIT reconstruction validates, each security-date state may expose:

```text
I_manager_count
I_manager_count_qoq_delta
I_reported_share_total
I_reported_share_total_qoq_delta
I_reported_value_total
I_period_of_report
I_available_at
I_mapping_method
I_amendment_state
I_state = EVALUABLE | NOT_EVALUABLE
```

The first core proxy will emphasize **change in the number of reporting managers**. Reported shares/value remain descriptors and are not used for the first hard rule because split/class handling can contaminate raw share deltas.

## No hard PASS rule yet

This document deliberately does **not** freeze an `I_pass` threshold yet. The historical full-build gate must first quantify evaluable coverage, unresolved lineage, and usable quarter-over-quarter manager-count deltas.

A later `I1` methodology may freeze a simple sponsorship-growth rule only after:

1. identifier mapping coverage is quantified;
2. current/live EDGAR accepted-time availability is reproducible;
3. historical conservative availability semantics are validated;
4. 13F-HR/A amendment semantics are resolved or quarantined;
5. stock vs put/call rows are separated;
6. duplicate manager/accession handling is audited;
7. usable QoQ manager-count coverage is quantified.

The I1 threshold must be preregistered **before** any performance ablation. No PF/CAGR/return inspection may be used to choose the threshold.

## Live-data limitation

Official bulk 13F datasets are published quarterly and can lag individual EDGAR filings. They are suitable for historical reconstruction but are not sufficient as the sole live source. Live/current collection therefore uses filing-level EDGAR metadata and preserves accession + exact acceptance timestamp.

## Guardrails

- `I_state` remains `NOT_IMPLEMENTED` in frozen FWD1.
- Missing/unmapped ownership is never implicit PASS or zero sponsorship.
- Options are excluded from common-share sponsorship counts.
- No fuzzy issuer-name matching.
- No quarter-end look-ahead.
- No same-day historical use from bulk filing date; historical I-v1 waits until filing date + 1 calendar day.
- No post-hoc threshold search against PF/CAGR.
- Any future I-enabled strategy is a new versioned validation track with a new forward clock.
