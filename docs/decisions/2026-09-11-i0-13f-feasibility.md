# Decision — I0 SEC 13F Sponsorship Feasibility

Date: 2026-09-11

## Status

**COMPLETE / DATA BLOCKED — I-v1 remains NOT_IMPLEMENTED**

Canonical confirmation workflow: `34593720220` = SUCCESS.

Evidence class: data-quality feasibility only. Strategy PF/CAGR/returns were not inspected. FWD1 was not modified.

Methodology: `docs/methodology/institutional-sponsorship-v1.md`.

## Coverage findings

Frozen compliant universe: 1,327 securities.

Deterministic identifier rule:

```text
if security_id is a valid US ISIN:
    CUSIP9 = security_id[2:11]
```

Coverage:

```text
US-ISIN deterministic CUSIP9 mapping = 1,010 / 1,327 = 76.1%
non-US ISIN deferred                 = 317
```

The 317 non-US-ISIN securities remain `NOT_EVALUABLE` for I-v1 until a separately validated CUSIP/FIGI crosswalk exists. Fuzzy issuer-name matching is prohibited.

## SEC ingestion finding

The intended primary source is official SEC Form 13F data / EDGAR filings. The GitHub-hosted runner received HTTP 403 when attempting to fetch the official bulk 13F ZIP. I0 was patched to preserve mapping evidence and explicitly record this condition rather than substituting an unverified mirror.

Canonical evidence records:

```text
sec_bulk_download.status = BLOCKED_HTTP
sec_bulk_download.http_status = 403
strategy_returns_inspected = false
fwd1_modified = false
```

This is an ingestion/access blocker, not evidence that Form 13F is unsuitable conceptually.

## PIT guardrail

`period_of_report` is not information availability. Any future I-v1 attachment must use a reproducible filing availability timestamp, with the target rule:

```text
accepted_at <= decision_cutoff(T0)
```

`13F-HR` and `13F-HR/A` amendments must be preserved and resolved by accession lineage. Unresolved amendment states are `NOT_EVALUABLE`.

## Decision

1. Keep `I_state = NOT_IMPLEMENTED` in the frozen baseline and FWD1.
2. Do not interpret missing/unmapped ownership as zero sponsorship or PASS.
3. Do not use quarter-end as the PIT availability date.
4. Do not use fuzzy issuer-name matching for the 317 deferred securities.
5. Do not promote an I hard filter from I0; I0 intentionally inspected no performance evidence.
6. A future I1 may proceed only after first-party SEC ingestion is reproducible, accepted-at/amendment semantics are audited, and the I1 rule is preregistered before performance ablation.

This closes I0 while leaving I-v1 explicitly unimplemented.