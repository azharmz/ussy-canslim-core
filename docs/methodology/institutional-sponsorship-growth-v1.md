# Institutional Sponsorship Growth v1 — Pre-registration

Status: **PRE-REGISTERED / NO PERFORMANCE INSPECTED**

Date: 2026-09-12

## Purpose

Freeze the first executable CAN SLIM `I` proxy before any strategy-performance ablation. This is a separate research track and does not modify frozen X3, PORT1, FWD1, EXH2, C/A, or M.

## Data source and availability

Primary source: SEC Form 13F.

Historical source: official SEC bulk Form 13F data sets, reconstructed as event-based manager/period states.

Historical availability rule:

```text
available_on = filing_date + 1 calendar day
```

This is intentionally conservative because SEC bulk data do not expose exact acceptance timestamps for every historical row.

Live/current availability rule:

```text
accepted_at <= decision_cutoff(T0)
```

using exact EDGAR `<ACCEPTANCE-DATETIME>`.

Quarter-end / `period_of_report` is never an availability timestamp.

## Identity

V1 is evaluable only for securities with deterministic US-ISIN → CUSIP9 mapping:

```text
cusip9 = security_id[2:11]
```

Non-US ISIN securities remain `NOT_EVALUABLE`. Fuzzy issuer-name matching is prohibited.

## Amendment lineage

- `13F-HR` base filing: replace manager-period state.
- `13F-HR/A` restatement: replace manager-period state.
- `13F-HR/A` new holdings: add to an already-valid manager-period base.
- new-holdings amendment without a valid base: ambiguous / `NOT_EVALUABLE`.
- unclassified amendment: ambiguous / `NOT_EVALUABLE`.

Ambiguity is not interpreted as zero ownership. Historical ingestion must preserve an uncertainty mask for CUSIP/period combinations that may be affected by unresolved manager-period lineage. Only affected security-period states are `NOT_EVALUABLE`; unaffected states remain usable.

Put/call rows are excluded from common-share sponsorship counts.

## Frozen I-v1 signal definition

For a decision at T0, select the latest two **consecutive report periods** for the security whose reconstructed states are available by the decision cutoff.

Let:

```text
M0 = number of reporting managers owning the security in latest usable report period
M1 = number of reporting managers owning the security in immediately preceding report period
I_delta = M0 - M1
```

Classification:

```text
I-v1 PASS = I_delta > 0
I-v1 FAIL = I_delta <= 0
I-v1 NOT_EVALUABLE = either period unavailable, non-consecutive, identifier unmapped,
                      or either period/CUSIP affected by unresolved lineage uncertainty
```

There is deliberately **no minimum manager-count threshold**, no percentage-growth cutoff, and no reported-value/share threshold in v1. This avoids adding arbitrary degrees of freedom before the first ablation.

Descriptors retained:

```text
I_manager_count_latest
I_manager_count_prior
I_manager_count_qoq_delta
I_latest_period_of_report
I_prior_period_of_report
I_latest_available_on / accepted_at
I_mapping_method
I_state
I_v1_label
```

Reported share/value totals remain descriptors only and are not used in `I_v1_label` because corporate actions and share-class effects can distort raw share changes.

## Ablation plan

After historical PIT reconstruction plus uncertainty masking pass data-quality review, compare frozen baseline vs baseline+I-v1 using the existing frozen X1 control and X3 preferred execution.

Primary readouts:

```text
entries
PF
PF ex-top10
stop/target rates
PORT1 gross CAGR
PORT1 max drawdown
20bp round-trip sensitivity
```

The experiment is retrospective historical evidence, not OOS.

No threshold may be changed after inspecting these outcomes. If I-v1 is weak, it remains a descriptor rather than being tuned. Any alternative I rule is a new versioned hypothesis with a separate validation track.

## Guardrails

- FWD1 remains unchanged and continues with `I = NOT_IMPLEMENTED`.
- Missing/unmapped/uncertain sponsorship is never implicit PASS or zero.
- No quarter-end look-ahead.
- No fuzzy identity mapping.
- No post-hoc threshold search.
- No production promotion from historical ablation alone.
