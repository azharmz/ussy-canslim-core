# CUP_WITHOUT_HANDLE vNext — R1 source-semantics diagnosis

Status: **R1-A/R1-B COMPLETE / RESIDUAL GAP ISOLATED / NO ENGINE CHANGE**

Date: 2026-09-21

Golden evidence baseline: `acd326676dd001316aecdc23669f77eabc2ac326`
Current production engine: `10668bbe9e27780d0dfe2464b9370e25e996fda5`
AX current-production replay: run `35582876895`, artifact `10631525330`, digest `sha256:8e6ceca3c7a51303cdb0db1bcbfbac051a61192ed1ce6905d9cd0d09cc0c646a`

## Scope and guardrail

CWOH Golden cases are diagnosis evidence only. They are not a threshold-tuning set. No return/performance evidence is used. No production state mapping is changed in R1.

## R1-A — residual diagnosis

The closed Golden tranche contains ten CWOH cases: AMD 2019, AVTR 2021, SE 2019, AMZN 2023, JPM 2023, COST 2024, AX 2024, NFLX 2024, ALL 2024, NVDA 2023.

Most source-target structures are reconstructable; the residual disagreements are not a general CWOH failure. The current-production AX replay isolates the remaining bottom-shape issue cleanly:

- source family: CUP_WITHOUT_HANDLE;
- source pivot: 60.00;
- current engine pivot: 60.00 exactly;
- source agreement: MATCH;
- candidate resolution: UNIQUE;
- current state: CUP_WITHOUT_HANDLE_AMBIGUOUS;
- sole matched fault: FRAGMENTED_BOTTOM;
- source-target structure: left rim 2024-01-31, open-right trough 2024-04-16, depth 19.20%.

The engine also emits a RECOGNIZED 54.64-pivot CWOH, but it is not source-equivalent and must not substitute for the 60.00 source structure.

Therefore AX is a state-semantics/representation disagreement after source-target reconstruction, not a pivot-generation or candidate-identity miss.

## Current implementation contract

`FRAGMENTED_BOTTOM` is not an O'Neil/IBD term. It is an internal research proxy.

Current code computes:

`continuity = max_bottom_run_10pct / sessions_within_10pct_of_trough`

and emits `FRAGMENTED_BOTTOM` when continuity < 0.75. Any SHARP_V, FRAGMENTED_BOTTOM, or WEAK_RIGHT_RIM_RECOVERY fault maps an otherwise theory-valid Cup body to AMBIGUOUS.

The 0.75 continuity cutoff is explicitly described in production code as a **research-only morphology band**, separate from source-supported duration/depth gates.

AX diagnostic evidence also shows that alternative confirmed sub-bodies can produce different bottom interpretations; therefore the proxy is sensitive to landmark/segment representation even when the source pivot is exact.

## R1-B — source-semantics audit

Authoritative IBD educational material located for Cup morphology supports qualitative shape semantics:

1. a well-formed Cup is U-shaped / rounded;
2. a sharp V-shaped recovery is undesirable because it does not provide the same time for weak holders to exit;
3. standard Cup depth/duration guidance is described separately.

What the located source material does **not** establish:

- no 75% bottom-contiguity rule;
- no 10%-of-trough occupancy definition;
- no source rule named FRAGMENTED_BOTTOM;
- no source statement that a discontinuous run under this numerical proxy is categorically non-recognizable.

Thus the qualitative O'Neil/IBD concept (rounded U rather than sharp V) and the engine's numerical continuity proxy must not be treated as equivalent without independent evidence.

## Frozen R1 conclusion

- Preserve duration/depth theory gates.
- Preserve SHARP_V as a separate hypothesis; do not merge it with fragmentation.
- Preserve FRAGMENTED_BOTTOM measurement as diagnostic evidence for now.
- Do **not** promote AX from AMBIGUOUS by fiat.
- Do **not** tune the 0.75 cutoff from Golden cases.
- The next research question is whether FRAGMENTED_BOTTOM should remain state-bearing or become diagnostic/quality evidence when duration/depth and non-V roundedness evidence otherwise pass.
- This question must be answered on independent DEVELOPMENT examples selected from authoritative source-labelled Cup/CWOH cases, followed by a frozen candidate semantic and locked VALIDATION.

## Next gate

R1-C: preregister representation measurements that distinguish:
- roundedness / sharp-V behavior;
- bottom dwell time;
- continuity/fragmentation;
- left/right recovery symmetry;
- candidate/landmark sensitivity.

Measurements are additive only. No state remapping is allowed before independent DEVELOPMENT evidence.
