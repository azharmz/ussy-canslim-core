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
