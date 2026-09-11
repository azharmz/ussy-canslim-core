# Institutional Sponsorship v1 — SEC 13F Research Contract

Status: **PRE-REGISTERED / COVERAGE AUDIT FIRST**

Date: 2026-09-11

## Purpose

Implement the missing CAN SLIM `I` component without contaminating frozen FWD1. `I` remains `NOT_IMPLEMENTED` in the frozen technical baseline until this separate research track proves that point-in-time institutional ownership can be reconstructed with adequate identifier coverage and amendment semantics.

This track is independent of TrendFoll and cannot modify X3, PORT1, FWD1, EXH2, C/A, or M.

## Primary source

Use SEC Form 13F filings / official SEC Form 13F data sets only for the first implementation. Form 13F reports holdings of institutional investment managers subject to Rule 13f-1. Holdings are reported quarterly and filings are generally due within 45 days after quarter-end.

Bulk SEC data are treated as as-filed source records, not as a ready-made PIT signal table.

## Point-in-time rule

The economic holding period (`period_of_report`) is **not** the date at which the information becomes usable.

For any strategy decision at signal date T0:

```text
usable filing state requires accepted_at <= decision_cutoff(T0)
```

If exact EDGAR `accepted_at` is unavailable for a filing, that filing cannot be used for same-day T0 decisions. A conservative later availability date may be used only if explicitly versioned and documented; quarter-end must never be substituted as availability time.

For historical bulk data, filing metadata must ultimately be reconciled back to the EDGAR accession and acceptance timestamp before strategy attachment.

## Amendments

Submission types `13F-HR` and `13F-HR/A` must be preserved. Amendments may restate or add holdings. No rule may simply "take the latest row" without resolving the amendment type and accession lineage.

Until amendment semantics are audited, records affected by unresolved amendments are `NOT_EVALUABLE` for I-v1.

## Security identity

13F information tables are keyed primarily by CUSIP; FIGI may be present but is not guaranteed.

Frozen universe identity remains `security_id`.

Deterministic mapping allowed in v1 coverage audit:

```text
if security_id is a valid US ISIN:
    derived_cusip9 = security_id[2:11]
```

No fuzzy issuer-name matching is allowed for production research attachment.

Foreign/ADR listings whose frozen `security_id` is not a US ISIN are `NOT_EVALUABLE` until a separately audited CUSIP/FIGI mapping is available.

## I-v1 candidate descriptors

Once PIT reconstruction is validated, each security-date state may expose:

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

The first core proxy will emphasize **change in the number of reporting managers**, because IBD educational material describes institutional sponsorship using the number of funds owning a stock over recent quarters and whether sponsorship is increasing. Reported shares/value are descriptors and require split/class handling before any hard rule.

## No hard PASS rule yet

This document deliberately does **not** freeze an `I_pass` threshold before the data-quality/coverage audit. The first experiment (`I0`) is feasibility only and may not inspect strategy returns.

A later `I1` methodology may freeze a simple sponsorship-growth rule only after:

1. identifier mapping coverage is quantified;
2. EDGAR accepted-time availability is reproducible;
3. 13F-HR/A amendment semantics are resolved;
4. stock vs put/call rows are separated;
5. duplicate manager/accession handling is audited;
6. corporate-action sensitivity of reported share changes is understood.

The I1 threshold must be preregistered **before** any performance ablation.

## Live-data limitation

Official bulk 13F datasets are published quarterly and can lag individual EDGAR filings. They are suitable for historical reconstruction but are not sufficient as the sole live source. A future live collector must use filing-level EDGAR metadata and preserve accession + acceptance timestamps.

## Guardrails

- `I_state` remains `NOT_IMPLEMENTED` in frozen FWD1.
- Missing/unmapped ownership is never implicit PASS or zero sponsorship.
- Options must not be counted as common-share sponsorship.
- No fuzzy issuer-name matching.
- No quarter-end look-ahead.
- No post-hoc threshold search against PF/CAGR.
- Any future I-enabled strategy is a new versioned validation track with a new forward clock.
