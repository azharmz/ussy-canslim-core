# P8 DEVELOPMENT batch 02 — four-family authoritative morphology audit

Date: 2026-09-13
Status: DEVELOPMENT EVIDENCE — NOT A P8 FREEZE

## Scope

This record summarizes the first source-grounded DEVELOPMENT batch spanning all four currently implemented core pattern families. It uses morphology/source agreement only. No return, CAGR, PF, FWD1, breakout-performance, or downstream CAN SLIM outcome is inspected.

The untouched NFLX VALIDATION example remains locked.

## Authoritative DEVELOPMENT corpus in this batch

| Example | Symbol | Pattern | Source precision used | Source pivot | Result |
|---|---|---|---|---:|---|
| p8-label-0001 | SNPS | FLAT_BASE | DAY start + DAY end | 392.79 | MATCH |
| p8-label-0003 | CTSH | CUP_WITH_HANDLE | MONTH start; no exact end | 26.74, explicit comparison factor 4 | MATCH |
| p8-label-0004 | FOUR | CUP_WITH_HANDLE | MONTH start; no exact end | 84.26 | MATCH |
| p8-label-0005 | SEI | DOUBLE_BOTTOM | MONTH start; no exact end | 12.74 | MATCH |
| p8-label-0006 | AMZN | CUP_WITHOUT_HANDLE | MONTH start; no exact end | 145.86 | MATCH |

Evaluator v0.8 continues to mean that `MATCH` is agreement on every detector-comparable dimension actually published by the source. Missing source dimensions remain unscored rather than invented.

## CI evidence

- CTSH split-normalization slice: run `34706454574` — SUCCESS; CTSH changed from landmark disagreement to MATCH without detector modification.
- FOUR source-grounded CWH label: run `34723528184` — SUCCESS; source dimensions MATCH.
- ambiguity-summary reporting: run `34723621488` — SUCCESS.
- SEI authoritative Double Bottom label: run `34723693242` — SUCCESS; source dimensions MATCH.
- AMZN authoritative Cup-without-Handle label: run `34723765592` — SUCCESS; source dimensions MATCH.

## Critical result: source agreement is not clean detector confirmation

The current report separates authoritative `agreement_state` from the selected raw candidate's `pattern_evidence_state`.

Current batch summary:

```text
agreement_counts:
  MATCH = 5

matched_detector_evidence_state_counts:
  AMBIGUOUS = 5

agreement_by_detector_evidence_state:
  MATCH:AMBIGUOUS = 5
```

Therefore **5/5 MATCH must not be interpreted as 5 clean detector confirmations**. The authoritative pattern is present among the frozen detector's emitted structures with source-faithful landmarks/pivots, but cross-pattern/fault semantics remain unresolved in every selected case.

Selected-candidate ambiguity:

- SNPS Flat Base: ambiguity with `DOUBLE_BOTTOM`.
- CTSH Cup With Handle: ambiguity with `CUP_WITHOUT_HANDLE` and `DOUBLE_BOTTOM`.
- FOUR Cup With Handle: ambiguity with `CUP_WITHOUT_HANDLE`; fault `HANDLE_LOW_TOO_EARLY`.
- SEI Double Bottom: ambiguity with `CUP_WITHOUT_HANDLE`; fault `SECOND_LOW_DID_NOT_UNDERCUT_FIRST`.
- AMZN Cup Without Handle: ambiguity with `CUP_WITH_HANDLE`.

## SEI undercut evidence

The authoritative IBD example calls SEI a Double Bottom with a 12.74 buy point. The detector-selected source-matching window has approximately:

```text
first bottom  = 11.10
second bottom = 11.15
relative difference ≈ +0.45%
```

The engine therefore persists `SECOND_LOW_DID_NOT_UNDERCUT_FIRST` even though the authoritative source names the pattern Double Bottom.

This is useful morphology evidence against treating a strict second-low undercut as already validated. One case is insufficient to revise the research band, so the undercut rule verdict remains **UNRESOLVED**, not REVISE and not KEEP.

## FOUR handle evidence

FOUR source dimensions match strongly, including an 84.26 source entry and detector pivot ~84.260002. The selected candidate nevertheless carries `HANDLE_LOW_TOO_EARLY` and CWH/Cup-without-handle ambiguity. This remains morphology evidence for later fault-band review; it is not a reason to remove the fault ad hoc.

## AMZN cup-family evidence

AMZN is explicitly labelled by IBD as Cup Without Handle. The selected raw candidate matches the source month and 145.86 pivot exactly on the comparison basis, but the detector simultaneously records Cup With Handle ambiguity. This is direct DEVELOPMENT evidence that cup-family hierarchy/conflict semantics need dedicated audit before P8 can be frozen.

## Verdict

1. Keep pattern detector v0.3 unchanged for this batch.
2. Keep evaluator v0.8 semantics: source agreement and detector ambiguity are separate axes.
3. Do not treat `MATCH:AMBIGUOUS` as clean validation success.
4. Keep Double Bottom undercut magnitude, CWH handle fault semantics, and cup-family conflict resolution `UNRESOLVED` pending broader authoritative DEVELOPMENT evidence.
5. BaseIdentity/Lineage remain unfrozen because the prior v0.3 structural audit showed material assignment churn.
6. NFLX VALIDATION remains locked and untouched.
7. #34 remains blocked.

## Next

- add more authoritative DEVELOPMENT examples, prioritizing independent examples that challenge the unresolved ambiguity/fault bands;
- acquire explicit negative/fault examples when source-grounded enough to support FP/TN analysis;
- audit cross-pattern ambiguity rate and whether the conflict layer is conservatively over-broad without silently choosing a winner;
- only after detector/conflict semantics are frozen should the untouched VALIDATION case be opened once.
