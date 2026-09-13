# #35 Theory-Faithful New-Candidate Validation Protocol v1

Date: 2026-09-13
Status: **PREREGISTERED / IN PROGRESS**
Upstream frozen contracts:

- #32 `theory-faithful-candidate-spec-v1`
- #33 `oneil-pattern-output-v2` core production contract
- #34 `34-candidate-generator-v0.2`

## 1. Purpose

Validate that the frozen #33 + #34 chain produces chronologically correct, explainable CAN SLIM candidate states on data not used to tune the frozen contracts.

This phase is **candidate validation before performance research**.

It must answer whether the system correctly preserves and composes:

```text
BASE_RECOGNIZED
→ PIVOT_DEFINED
→ PIVOT_CROSSED
→ BREAKOUT_CONFIRMED
→ CANSLIM_ELIGIBLE
```

It must not answer whether buying those candidates is profitable.

## 2. Prohibited tuning

During #35 do not alter #33 morphology or #34 thresholds based on:

- forward returns;
- win rate;
- CAGR;
- PF;
- Sharpe;
- drawdown;
- breakout success/failure;
- entry optimization.

A validation defect may justify a code/schema/PIT correction only when the frozen specification is being implemented incorrectly. A theory change requires a new explicit parent decision and must not be inferred from trading outcomes.

## 3. Data separation

### Production

Daily production scanning may continue to use the compact R2 ready contract (~300 bars/security).

### #35 validation

Historical validation is not constrained by production R2 retention. Acquire purpose-built historical OHLCV with enough prehistory for every evaluated as-of date.

The historical source must be recorded with:

```text
provider
retrieval timestamp
symbol/security mapping
raw price fields
corporate-action adjustment semantics
first/last date
row count
checksum/version
```

Do not mix adjusted and unadjusted OHLC fields silently. The historical adapter must document how split/dividend adjustments compare with the production technical-data semantics before the validation corpus is opened.

## 4. Minimum warm-up

For an evaluated date T, retain enough history for all frozen inputs. At minimum:

- #33 morphology context: production detector-compatible history;
- breakout volume: >=50 completed sessions before T;
- L/RS proxy: >=252 completed sessions before T;
- M proxy: sufficient benchmark history for the frozen market-state implementation.

Use a safety buffer rather than constructing validation rows exactly at the mathematical minimum.

## 5. Validation layers

### V35-A — Contract / schema validation

For every row verify:

- only four frozen core pattern families enter the production candidate consumer;
- exact #33 engine/schema/detector versions are accepted;
- `candidate_id`, `base_id`, `lineage_id` are preserved;
- `RECOGNIZED / AMBIGUOUS / REJECTED` is preserved;
- detector faults and structural provenance survive #34 unchanged;
- missing evidence remains explicit.

### V35-B — Chronology / PIT validation

Verify on selected cases:

- no bar after as-of T affects state at T;
- pivot crossing is the first crossing after `structural_end`;
- historical prior crossings are not recounted;
- breakout day is excluded from prior-50 volume average;
- fundamental evidence is available on/before T;
- annual and quarterly evidence does not use later filings;
- RS is cross-sectional as-of T and uses only completed data through T;
- M state uses only benchmark information available through T.

### V35-C — Stage-transition validation

Construct positive and negative examples for each transition:

```text
RECOGNIZED but no pivot -> BASE_RECOGNIZED
pivot defined, no cross -> PIVOT_DEFINED
first cross, low volume -> PIVOT_CROSSED
first cross + >=1.40x volume -> BREAKOUT_CONFIRMED
confirmed + C/A/L PASS + M ALLOW -> CANSLIM_ELIGIBLE
confirmed + any core gate not pass -> BREAKOUT_CONFIRMED
AMBIGUOUS/REJECTED -> NOT_ELIGIBLE
```

### V35-D — Independent real-chart candidate audit

Use historical cases not selected from downstream profitability. For each case, inspect the chart/data and independently audit:

- pattern status from frozen #33;
- pivot and pivot source;
- structural end;
- first crossing date;
- volume baseline and ratio;
- C state;
- A state;
- L percentile/state;
- M state;
- final candidate stage;
- reason codes.

The audit target is semantic agreement, not future return.

## 6. Sampling discipline

The real-chart validation set must contain both positive and negative/near-miss cases.

At minimum include cases spanning:

- all four core pattern families where available;
- RECOGNIZED, AMBIGUOUS and REJECTED #33 states;
- no-cross, first-cross and already-crossed chronology;
- volume below and above 1.40x;
- C/A/L/M pass and non-pass states;
- missing/not-evaluable fundamental evidence;
- gaps through pivot where present.

Do not select the corpus because the stocks later became large winners or losers.

## 7. Required evidence table

For each audited event persist at least:

```text
validation_case_id
security_id
symbol
asof_date
source_dataset_version
pattern
pattern_status
candidate_id
base_id
lineage_id
structural_end
pivot_level
pivot_source_date
expected_first_cross_state
observed_first_cross_state
expected_volume_ratio
observed_volume_ratio
expected_C_state
observed_C_state
expected_A_state
observed_A_state
expected_L_state
observed_L_state
expected_M_state
observed_M_state
expected_candidate_stage
observed_candidate_stage
field_match_state
mismatch_reason
reviewer_notes
```

## 8. Acceptance logic

Separate defects into:

```text
IMPLEMENTATION_DEFECT
DATA_SEMANTICS_DEFECT
PIT_DEFECT
UPSTREAM_33_VALIDATION_DEBT
EXPECTED_AMBIGUITY
NOT_EVALUABLE
```

Do not collapse these into one accuracy score.

A #35 PASS requires:

1. contract/schema checks green;
2. no unresolved look-ahead/PIT defects;
3. stage transitions match frozen #32/#34 semantics;
4. real-chart audit has no unexplained systematic semantic mismatch;
5. known #33 P8 validation debt remains explicit rather than hidden downstream;
6. no parameter was changed from trading outcomes.

## 9. Historical OHLCV source decision gate

Before downloading the full validation corpus, freeze the research OHLCV source/adjustment adapter. Candidate providers may be evaluated for data semantics and coverage, but not selected by resulting strategy performance.

The provider decision should prioritize:

- reproducible historical daily OHLCV;
- corporate-action consistency with production semantics;
- adequate history;
- stable symbol/security mapping;
- practical retrieval/versioning.

This gate does **not** require changing the production R2 contract.

## 10. Next implementation task

1. inspect/document production OHLCV adjustment semantics;
2. select and freeze the #35 historical OHLCV research adapter;
3. build a versioned historical dataset with >=252-session warm-up plus buffer;
4. run V35-A/B/C before opening the independent real-chart audit set;
5. only after #35 is closed may the project discuss downstream execution/performance work.
