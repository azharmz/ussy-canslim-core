# Double Bottom vNext — R1

Status: **R1 DIAGNOSIS FROZEN / NO ENGINE CHANGE**

Golden reconstruction baseline: `acd326676dd001316aecdc23669f77eabc2ac326`.

## Problem decomposition

The Golden reconstruction does not support treating DOUBLE_BOTTOM as one universal detector failure.

- **IPHI 2019** reaches the intended structural neighborhood. Engine pivot 64.75 is near the source 64.85, but the candidate is AMBIGUOUS on `NO_SECOND_TROUGH_UNDERCUT`. This is a morphology-semantics case.
- **TSM 2024** is the positive control. The engine independently recovers the source 148.43 pivot at 148.42999268 and returns `DOUBLE_BOTTOM_RECOGNIZED` with no faults. Therefore the family is operational and the undercut question is not universal.
- **WMT 2024** is not an undercut-gate case. The source-labelled April-May structure is absent from primary, auxiliary and fused landmark vocabularies, leaving downstream segmentation empty. This is an upstream landmark-generation miss and must remain separate from morphology remediation.

## Existing P8 evidence already in the production repository

Before opening new implementation work, the current P8 stack must be treated as evidence rather than rediscovered:

- `double-bottom-v3` already changed `NO_SECOND_TROUGH_UNDERCUT` from hard rejection to explicit AMBIGUOUS evidence because IBD wording describes the second bottom as **usually** lower rather than universally lower.
- The 35-session duration and 40% depth remain hard gates.
- Open-right-edge completion already exists to keep core-W geometry immutable while measuring elapsed duration through causal as-of T.
- Existing authoritative DEVELOPMENT rows include SEI 2024, NVDA 2023, SPOT 2025, WMT 2024 and EMBJ 2026.
- The P8 development freeze recorded five DOUBLE_BOTTOM positives inside a 20-example four-family corpus with source-dimension matches.

Therefore DB vNext must not repeat the CWH workflow mechanically or tune from the Golden cases.

## R1 hypotheses

### H-undercut

Question: should absence of a second-trough undercut remain state-bearing AMBIGUOUS, or should it be retained as quality evidence while other source-faithful W geometry determines recognition?

The existing P8 v0.2 change is only a partial answer: it removed hard rejection but still prevents RECOGNIZED status. Any further change requires independent evidence and controls; IPHI alone cannot authorize it.

### H-research-bands

`SHALLOW_UNDERCUT` (0.5%) and `WEAK_MIDDLE_REBOUND` (50%) are explicitly research-only numerical bands. They must be audited separately from source-backed structural requirements. No replacement cutoff may be selected from Golden positives.

### H-duration

The core-W left-high→trough-2 duration can be shorter than the source-described completed base. Existing open-right-edge semantics address this representational issue without fabricating a recovery landmark. Preserve that separation unless contradictory evidence appears.

### H-upstream

WMT remains a landmark extractor workstream. A morphology rule change is not allowed to rescue a candidate that was never generated.

## Development protocol

1. Reuse the already-frozen independent P8 DOUBLE_BOTTOM DEVELOPMENT cohort before collecting more cases.
2. Audit source-equivalent candidates one by one: SEI → NVDA → SPOT → EMBJ. WMT is tracked separately as upstream evidence.
3. For every case record pivot agreement, candidate class, duration/depth, trough-2 vs trough-1, middle-peak recovery fraction, faults, and final state.
4. Separate source-backed theory gates from research-only bands.
5. Freeze candidate semantics only after the independent cohort synthesis.
6. Preserve malformed-geometry, TOO_SHORT, TOO_DEEP, chronology, PIT and candidate-identity controls.
7. Do not use Golden IPHI/TSM/WMT to select thresholds.
8. Do not change landmark generation inside this morphology workstream.
9. No returns, PF, CAGR or post-breakout outcomes may influence morphology semantics.

## Immediate implementation gate

No engine change is authorized at R1. First execute the independent DEVELOPMENT audit using the current production SHA `10668bbe9e27780d0dfe2464b9370e25e996fda5` and current DB v3 semantics. Only repeated, source-backed disagreement may advance to a state-remapping proposal.
