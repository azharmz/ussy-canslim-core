# CUP_WITH_HANDLE vNext — R1 morphology diagnosis

Status: **R1-A DIAGNOSIS FROZEN — NO ENGINE CHANGE**

Golden evidence baseline: `acd326676dd001316aecdc23669f77eabc2ac326`
Frozen engine audited by Golden 40: `c433cc1e35a5aa32a46f732cd8c5545935e36e40`

## Scope

This workstream follows the closed 10/10 CUP_WITH_HANDLE Golden audit. The Golden cases are diagnosis evidence only and MUST NOT be used to tune detector thresholds. Any candidate semantics must be frozen before independent development/control replay and untouched validation.

## Golden 10 diagnosis

Cases: LRCX, EW, NVO, OLED, TSLA, TOL, URBN, SHOP, RBLX, DUOL.

The family detector is operational, but source-target fidelity is not robust. The disagreement is not one universal terminal fault.

Observed mechanisms:
- `BELOW_CUP_MIDPOINT`: explicit in LRCX and source-near/alternate lineages such as SHOP and DUOL.
- `DEEP_HANDLE_EXCEPTIONAL`: repeated in NVO, TSLA, TOL, URBN, RBLX, DUOL and other source-near candidates.
- Cup/body morphology interactions: `SHARP_V` and `FRAGMENTED_BOTTOM` occur on some source-near lineages.
- Assembly/boundary selection: EW contains a source-faithful cup body (16.25897% vs source 16.3%) but no source-target CWH assembly; RBLX demonstrates family recognition on the same security while selecting a different structure.
- Pivot reconstruction is often not the primary defect: LRCX and DUOL reconstruct the source pivot practically exactly; TSLA is also practical-exact/near-exact on a source-near lineage.

## Frozen-engine handle semantics

Current production ancestry uses:
- minimum handle duration: 5 sessions;
- handle low must remain above the cup midpoint; otherwise `REJECTED / BELOW_CUP_MIDPOINT`;
- handle depth >12% becomes `AMBIGUOUS / DEEP_HANDLE_EXCEPTIONAL`;
- only a recognized Cup body plus recognized handle becomes clean CUP_WITH_HANDLE;
- open-right-edge handle applies the same midpoint and 12% rules.

The 12% band and cup-midpoint rule must be treated as hypotheses requiring source support. They must not be relaxed merely because Golden cases fail them.

## Layered diagnosis

1. **Landmark / boundary / pivot generation**
   - not a blanket failure;
   - still material for EW/RBLX and other source-target boundary mismatches.

2. **Cup-body morphology**
   - source-near bodies can exist while carrying research ambiguity (`SHARP_V`, `FRAGMENTED_BOTTOM`);
   - must remain separate from handle semantics.

3. **Handle assembly**
   - recurring disagreement around which post-rim pullback/recovery belongs to the source setup.

4. **Handle morphology/final gate**
   - repeated `BELOW_CUP_MIDPOINT` and `DEEP_HANDLE_EXCEPTIONAL` indicate the next source-semantics audit target.

5. **Breakout / execution**
   - separate from morphology; Golden evidence contains both confirmed and unconfirmed volume examples and must not be used to redefine the pattern.

6. **Price basis / corporate actions**
   - separate diagnostic layer; split-normalized cases must not be mislabeled as morphology failures.

## R1 next gates

R1-B: source-semantics audit for handle depth, upper-half/midpoint semantics, minimum duration, and handle placement.

R1-C: inspect assembly/boundary mechanics independently of numeric handle gates.

R1-D: preregister candidate semantics, if source evidence supports a change.

Only after R1-D may a new development cohort and untouched holdout be selected. Golden 10 remains locked against tuning.


## R1-B — source-semantics audit

Status: **SOURCE SEMANTICS REVIEWED / IMPLEMENTATION MISMATCH IDENTIFIED / NO THRESHOLD TUNING**

Authoritative/near-primary evidence reviewed after R1-A:

- IBD educational material defines Cup-with-Handle as a seven-week-minimum base with typical base depth 15–30%.
- An Investor's Business Daily review of Cup-with-Handle anatomy states that handles are at least five days and usually more than one or two weeks, and that the **handle's midpoint** should be in the upper half of the entire base.
- IBD's proper-handle discussion likewise states that the handle should form in the upper half of the overall base and emphasizes a downward drift with quieter volume.
- O'Neil book excerpts describe proper-handle declines around 8–12% in normal bull markets, while explicitly allowing deeper exceptional handles in unusual market/bear-market conditions.

### Contract comparison

Current engine semantics are not identical to those source statements:

1. **Duration**
   - Engine: >=5 sessions.
   - Source: at least five days / commonly 1–2+ weeks.
   - Finding: broadly source-aligned; no R1 evidence supports changing this gate.

2. **Upper-half rule**
   - Engine: `handle_low >= cup_midpoint`; if the absolute handle low crosses below the midpoint, hard `REJECTED`.
   - Source wording located in IBD: the **handle's midpoint** should be in the upper half / handle should form in the upper half.
   - Finding: the engine operationalization is stricter than the located wording. It equates one extreme low with the placement of the handle as a whole. This is a concrete semantics mismatch and is a candidate explanation for `BELOW_CUP_MIDPOINT` Golden disagreements.

3. **Handle depth**
   - Engine: >12% => `AMBIGUOUS / DEEP_HANDLE_EXCEPTIONAL`.
   - Source: 8–12% is a normal-bull-market guideline, but deeper exceptions are explicitly described.
   - Finding: 12% is defensible as a quality/evidence band, but the source does not support treating every >12% handle as universally non-recognizable. Market/base context matters. Therefore the current universal ambiguity mapping requires independent validation before promotion.

4. **Handle direction/volume**
   - Source repeatedly describes a gentle downward drift and quiet/subsiding volume.
   - Current handle state machine does not encode these as primary handle-quality evidence.
   - Finding: this is a representation omission, but Golden 10 must not be used to invent numerical slope/volume cutoffs.

### R1-B frozen conclusions

- Keep >=5-session minimum unchanged.
- Do **not** relax 12% numerically from Golden failures.
- Test a representation change for upper-half placement: distinguish **handle placement/midpoint** from **absolute handle-low excursion**.
- Treat >12% initially as quality/context evidence rather than assuming a universal categorical veto; this remains a hypothesis until independent controls.
- Do not add slope/volume thresholds without separately preregistered source-backed definitions.

R1-C must now inspect whether existing landmarks contain enough information to calculate a causal handle-level placement statistic without oracle inputs, and whether assembly selection itself creates the apparent deep/midpoint faults.


## R1-C — assembly and representation audit

Status: **COMPLETE / REPRESENTATION GAP LOCALIZED / NO ENGINE CHANGE**

Current engine code was inspected against the frozen Golden diagnosis.

### Confirmed-handle representation

`build_handle_geometry()` persists only:
- right-rim as `handle_high`;
- one `handle_low`;
- one later `handle_recovery`;
- duration, peak-to-low depth, cup midpoint, boolean `low_in_upper_half`, and recovery/right-rim ratio.

The upper-half verdict is therefore derived from one extreme:
`handle_low.price >= cup_midpoint`.

The representation does **not** persist the handle price path, handle midpoint/central tendency, fraction of handle sessions in the upper half, slope of lows, or handle-volume contraction. Consequently the current state machine cannot distinguish:
- a handle predominantly formed in the upper half with a brief shakeout below midpoint; from
- a handle structurally residing in the lower half.

That is a representation limitation, not evidence for a new numeric cutoff.

### Open-right-edge representation

`observe_open_right_edge_handle()` has the same limitation. It measures the right-rim to selected low and evaluates the same absolute-low midpoint boolean. Thus confirmed and open-right-edge paths share the same semantics mismatch; fixing only one path would create contract divergence.

### Assembly selection

The Golden cases also show that source-target misses cannot all be repaired by changing the final handle gate:
- EW has source-like cup depth/landmarks but no source-target CWH assembly.
- RBLX recognizes another CWH on the same security while the source-near structure remains ambiguous.
- DUOL reconstructs the source pivot essentially exactly but has alternate handle lineages with different terminal faults.

Therefore CWH vNext requires two separable hypotheses:
- **H-placement:** represent where the handle as a region forms, rather than equating placement with its single lowest price.
- **H-assembly:** independently test candidate/lineage selection around the source-near right rim and post-rim pullback. Do not let a relaxed final gate conceal boundary-selection errors.

### Existing cup-body interaction

The Cup body has separate research proxies (`SHARP_V`, `FRAGMENTED_BOTTOM`, weak recovery). Those must remain separately observable. CWH vNext must not silently erase Cup-body ambiguity merely to recover source CWH labels.

### R1-C conclusion

The engine has enough OHLCV in the input frame to calculate causal handle-region descriptors, but the current `HandleGeometry` discards that path information. A vNext representation can add evidence fields without oracle inputs and without changing landmark generation. The first development change should therefore be **additive measurement**, not immediate state remapping.

R1-D preregistration should freeze the descriptors and validation questions before any Golden replay is used to judge them.


## R1-D — preregistered CWH vNext development hypotheses

Status: **PREREGISTERED / GOLDEN LOCKED / READY FOR INDEPENDENT DEVELOPMENT COHORT**

No numeric recognition threshold is selected in this phase.

### H1 — additive handle-region evidence

For every causally observable handle interval from right rim through as-of/recovery, persist path-level descriptors before changing states:
- handle session count;
- peak-to-low depth (existing);
- median close position within the cup range;
- fraction of handle closes at/above cup midpoint;
- minimum close position within the cup range;
- linear slope of handle closes normalized by right-rim price and session count;
- median handle volume / preceding-20-session median volume when sufficient history exists.

These are evidence fields, not recognition cutoffs.

### H2 — upper-half semantics

Test whether authoritative positive CWH examples are better represented by **handle-region placement** than by the current single absolute-low boolean. Development may compare descriptors, but Golden 10 may not select a cutoff.

A state change is permitted only after a source-backed operational definition is frozen using non-Golden development/control evidence.

### H3 — depth semantics

Retain 12% as a normal-handle quality reference. Test >12% as context/quality evidence rather than assuming it is a universal categorical ambiguity rule. Do not select a replacement maximum from Golden positives.

### H4 — assembly is independent

For each development case, report whether source-near cup/right-rim geometry exists before scoring handle morphology. A source-target assembly miss remains an assembly/boundary failure and cannot be converted into a morphology pass by a downstream rule.

### H5 — cup-body faults remain visible

`SHARP_V`, `FRAGMENTED_BOTTOM`, `WEAK_RIGHT_RIM_RECOVERY`, duration, and depth remain independently reported. No CWH candidate may suppress Cup-body evidence.

### Development/validation protocol

1. Freeze a new source-backed DEVELOPMENT positive cohort not present in Golden CWH 10.
2. Freeze negative/control cases, including malformed or lower-half/deep handles where authoritative evidence is available.
3. Add measurement-only instrumentation first.
4. Replay development/control cohort.
5. Freeze candidate state semantics before untouched holdout.
6. Select untouched positive/negative CWH cases not used in Golden or development.
7. Promote only if source-target fidelity improves without collapsing negative controls and all four-core regressions remain green.

Golden CWH 10 remains diagnosis-only throughout.


## R2-A — independent DEVELOPMENT/control cohort registry

Status: **COHORT FROZEN BEFORE ENGINE REPLAY**

Golden CWH 10 are excluded: LRCX, EW, NVO, OLED, TSLA, TOL, URBN, SHOP, RBLX, DUOL.

### Positive development cases

1. **NFLX 2023**
   - authoritative IBD retrospective CWH example;
   - cup begins 2023-02-03, base depth 25%;
   - handle depth 10%, duration six weeks, light volume;
   - proper buy point 349.80, breakout 2023-05-18.
   - This is especially useful as a textbook normal-handle positive control.

2. **ELF 2022**
   - MarketSmith/IBD Stock Guide identifies a cup-with-handle breakout on 2022-07-21.
   - Source is sufficient to freeze family/date; exact pivot/handle numeric dimensions must remain NOT_SCORED unless independently sourced before replay.
   - Useful as a positive assembly case, not a numeric-threshold calibration case.

### Semantics/control anchors (not detector positives)

3. **IBD CWH checklist/infographic**
   - base minimum seven weeks; typical base depth 15–30%; ideal buy point above the peak in the handle.
   - methodology control only.

4. **LRCX source semantics**
   - retained only as a methodology anchor for the documented normal 8–12% handle guideline and >=5 trading-session minimum.
   - LRCX itself remains Golden and is forbidden from development scoring.

### Negative-control policy

No negative stock case is admitted merely because the frozen engine labels it malformed. A negative/control security must have independent source evidence that the candidate was not a proper CWH or that a specific structural defect was documented. Until such a source is frozen, synthetic malformed handles may be used only for unit invariants, not source-fidelity scoring.

### Leakage guardrail

R2-A registry is frozen before any vNext measurement replay on NFLX/ELF. No threshold may be selected from Golden 10 or from later holdout cases.


## R2-B — corrected independent DEVELOPMENT synthesis

Status: **5/5 DEVELOPMENT AUDITED / CANDIDATE SEMANTICS FROZEN / VALIDATION STILL LOCKED**

The earlier R2-A registry is superseded for split assignment. The authoritative P8 label registry already classifies NFLX 2023 as VALIDATION, so NFLX MUST remain untouched until after candidate semantics are frozen. ELF is not used for threshold selection here.

Actual DEVELOPMENT cohort:
- CTSH 2004 (`p8-label-0003`)
- FOUR 2024 (`p8-label-0004`)
- APH 2026 (`p8-label-0013`)
- NVDA 2026 (`p8-label-0014`)
- BAC 2025 (`p8-label-0015`)

NFLX 2023 (`p8-label-0002`) remains locked VALIDATION.

### Development synthesis

- **CTSH:** source-near pivot geometry exists. Absolute handle low falls below cup midpoint, while 11/12 handle closes (91.67%) are at/above the midpoint. This supports the preregistered H-placement representation concern, but cup-body/assembly disagreement remains independently visible.
- **FOUR:** source pivot is practically exact and cup/placement geometry is otherwise clean. The source-positive handle is about 12.33% deep, just above the frozen 12% normal-quality reference, so the universal >12% ambiguity mapping is not source-faithful as a categorical veto.
- **APH:** source CWH is present but source-target pivot/assembly is not reconstructed faithfully. The selected lineage also carries cup-body and deep-handle evidence. This case therefore cannot be repaired or scored as a pure handle-gate problem.
- **NVDA:** source pivot is practically exact and handle morphology is clean (duration and depth within current normal bands, upper-half placement clear). Remaining disagreement is cup-body/lineage morphology, not handle semantics.
- **BAC:** unique source-equivalent CWH candidate with pivot within 1%; handle is within current normal depth band and entirely upper-half by close-region evidence. Remaining ambiguity is cup-body `SHARP_V`, not handle morphology.

### Frozen candidate semantics for validation

The DEVELOPMENT evidence supports a deliberately narrow handle-layer change:

1. Keep minimum handle duration at **>=5 sessions**.
2. Keep **12%** as a normal-handle quality reference and continue reporting `DEEP_HANDLE_EXCEPTIONAL`, but **do not use >12% alone as a categorical CWH ambiguity veto**.
3. Keep the absolute-low `BELOW_CUP_MIDPOINT` observation as explicit evidence, but **do not let one sub-midpoint excursion alone hard-reject an otherwise upper-half handle region**.
4. Handle-region placement must remain causally measured and reported. No new numeric region-placement cutoff is selected from these five positives.
5. Cup-body faults (`SHARP_V`, `FRAGMENTED_BOTTOM`, etc.) remain independently state-bearing; the handle-layer revision MUST NOT erase them.
6. Assembly/boundary/pivot disagreement remains independent and cannot be converted to a morphology pass by relaxed handle semantics.
7. Slope and volume descriptors remain **diagnostic only**; no recognition cutoff is introduced.
8. Confirmed and open-right-edge handles must use parity semantics.

This freeze is intentionally conservative: it removes unsupported universal handle veto behavior without inventing a replacement threshold from positive examples.

### Validation gate

NFLX 2023 is now eligible for the first untouched positive validation replay because the candidate semantics above are frozen before inspecting its vNext result. Validation must report source dimensions, handle evidence, cup-body faults, assembly/pivot agreement, and final state. A validation failure must be diagnosed by layer; it must not trigger post-hoc threshold tuning.

Promotion remains blocked until:
- measurement implementation is corrected to the preregistered OLS slope definition;
- preceding-volume evidence requires a full 20-session denominator;
- invalid/non-positive cup range fails closed for measurements;
- confirmed/open-right parity and causality/state-invariance tests pass;
- untouched validation is complete;
- four-core regression is green.
