# Decision — I1 historical PIT reconstruction and I-v1 growth preregistration

Date: 2026-09-12

## Status

**HISTORICAL PIT RECONSTRUCTION COMPLETE / I-v1 RULE PRE-REGISTERED / PERFORMANCE NOT YET INSPECTED**

Canonical upstream historical run: `azharmz/ussy-fundamentals` run `34654725293` = SUCCESS.

Superseded partial run: `34624132399` (failed on a later SEC ZIP layout change and is not canonical).

## Canonical historical evidence

```text
official SEC 13F datasets = 53 / 53
total filings processed = 313,055
state-change events = 14,529,166
unclassified amendment filings = 53
ambiguous filing events = 53
new-holdings without valid base = 0
deterministic US-ISIN -> CUSIP9 = 1,010
non-US ISIN NOT_EVALUABLE = 317
historical availability = filing_date + 1 calendar day
quarter-end used as availability = false
strategy returns inspected = false
FWD1 modified = false
```

The 53 unresolved amendments are a tiny exception set and do not justify discarding the entire historical 13F reconstruction. Equally, they must not be interpreted as zero ownership. A dedicated CUSIP/period uncertainty mask is therefore required so only states that could be affected by unresolved manager-period lineage become `NOT_EVALUABLE`.

Uncertainty-mask workflow: `34656995462` (started after this decision; audit before any performance ablation).

## Frozen I-v1 rule

Methodology: `docs/methodology/institutional-sponsorship-growth-v1.md`.

For decision date T0, use the latest two consecutive report periods whose reconstructed states are available by the decision cutoff.

```text
I_delta = manager_count_latest - manager_count_prior
PASS = I_delta > 0
FAIL = I_delta <= 0
NOT_EVALUABLE = missing/non-consecutive/unmapped/uncertain period
```

No minimum manager count, percentage-growth threshold, share threshold, or reported-value threshold is permitted in v1.

This definition was frozen before any I-v1 PF, CAGR, drawdown, stop rate, or target rate was inspected.

## Forward separation

Frozen FWD1 remains unchanged with `I = NOT_IMPLEMENTED`. Historical I-v1 results cannot be retrofitted into the current forward clock. If I-v1 later merits promotion, it requires a separately versioned strategy and validation track.
