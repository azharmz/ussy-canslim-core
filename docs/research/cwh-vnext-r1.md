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
