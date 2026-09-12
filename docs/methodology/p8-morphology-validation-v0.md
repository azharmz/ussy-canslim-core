# P8 / #33 Morphology Validation Protocol v0.1

Date: 2026-09-13  
Status: PREREGISTERED DEVELOPMENT VALIDATION  
Upstream design: `docs/methodology/p8-pattern-engine-design-v0.md`

## Purpose

Validate the #33 pattern engine against **independently adjudicated morphology labels** before #34 consumes detector output. The target is pattern/landmark fidelity, not trading performance.

No return, CAGR, profit factor, forward-trade result, or downstream CAN SLIM eligibility outcome may be used to create labels or resolve detector disagreements.

## Unit of comparison

Validation is performed on **base lineages**, not rolling candidate windows. This prevents one evolving economic base from being counted many times solely because it appears in multiple overlapping detector windows.

Implemented label vocabulary remains limited to:

```text
CUP_WITH_HANDLE
CUP_WITHOUT_HANDLE
DOUBLE_BOTTOM
FLAT_BASE
```

`ASCENDING_BASE`, `BASE_ON_BASE`, and `IPO_BASE` remain outside this validation version until their detectors are implemented.

## Label schema

Each adjudicated label must contain:

```text
label_id
security_id
ticker
pattern_type
start_date_min
start_date_max
end_date_min
end_date_max
adjudication = POSITIVE | NEGATIVE
notes
```

Date ranges are intentional. Human morphology review often cannot justify one exact base-start or completion date. The range must be fixed during adjudication and must not be widened after inspecting detector output merely to convert a miss into a hit.

### POSITIVE

The reviewer states that the named morphology is present within the stated date envelope.

- detector match -> TP
- no detector match -> FN

### NEGATIVE

The reviewer states that the named morphology must **not** be recognized within the stated date envelope.

- detector match -> FP
- no detector match -> TN

## Critical guardrail: unadjudicated output

A detector lineage that is not covered by any positive or negative label is `UNADJUDICATED`.

It is **not** automatically a false positive. Counting every unlabelled detector output as FP would confound incomplete human coverage with detector error.

Therefore precision is reported only on explicitly adjudicated windows, while the count and IDs of unadjudicated detector lineages are reported separately for review.

## Matching rule v0.1

A detector lineage matches a label only when all are true:

1. `security_id` matches;
2. `pattern_type` matches exactly;
3. detector `base_start_date` falls inside the adjudicated start-date range;
4. detector `last_supported_date` falls inside the adjudicated end-date range.

Cross-pattern conflict records remain separate evidence. This validator does not silently reinterpret `FLAT_BASE` as `DOUBLE_BOTTOM`, nor `CUP_WITH_HANDLE` as `CUP_WITHOUT_HANDLE`.

## Metrics

The validator reports:

```text
TP / FN on POSITIVE labels
FP / TN on NEGATIVE labels
recall_on_positive_labels
precision_on_adjudicated_windows
unadjudicated_lineage_count
unadjudicated_lineage_ids
per-label matched lineage IDs
```

These are morphology diagnostics only. No minimum precision/recall promotion threshold is frozen yet because the first purpose is to expose the error taxonomy and review detector semantics on a broader labelled DEVELOPMENT set.

## Workflow

1. Run `scripts/run_p8_pattern_engine.py` on a preregistered DEVELOPMENT symbol/window.
2. Independently adjudicate labels without consulting returns.
3. Save labels as JSON under a versioned evidence/fixture path.
4. Run:

```text
python scripts/validate_p8_morphology.py \
  --report results/<pattern-report>.json \
  --labels <labels>.json \
  --output results/<validation-report>.json
```

5. Review FN, adjudicated FP, conflicts, and unadjudicated lineages.
6. Any detector-threshold change requires a versioned methodology decision before rerunning the labelled set.

## Next DEVELOPMENT work

The next data task is to build a labelled set spanning multiple securities and all four implemented core pattern types, including explicit negative windows. The current SNPS 2023 live run remains useful detector evidence but is not by itself sufficient morphology validation.
