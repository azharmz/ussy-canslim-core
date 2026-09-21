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


## R1-C — representation measurement preregistration

Status: **IMPLEMENTED ADDITIVELY / REGRESSION PASS / NO STATE CHANGE**

Measurement implementation lives on `ussy-oneil-patterns:research/cwoh-vnext-measurement`.

Commits:
- `3cf19ca754483fedef806d7db83cfd76d9802921` — additive cup-shape diagnostics;
- `8d10648cc310010cbd5e510f3d89f75df142294f` — schema/range/state-invariance tests.

Draft PR: `ussy-oneil-patterns#18`.
CI run: `35584090735` — pytest SUCCESS. P8/P6 compute jobs were correctly skipped; this change requires only unit/regression coverage.

Frozen additive measurements:
- decline sessions and recovery sessions;
- left/right time ratio;
- 5%-of-trough dwell fraction;
- 10%-of-trough dwell fraction;
- lower-third occupancy fraction;
- maximum contiguous run within 10% of trough;
- 10%-bottom continuity ratio;
- right-rim / left-rim recovery ratio (pre-existing, retained).

These measurements are observational. They do not alter `CupBodyState`, `CupBodyFault`, thresholds, candidate ranking, or source matching. The diagnostic schema advances from `p8-cup-body-diagnostic-v0.1` to `v0.2`.

### Preregistered interpretation

No single measurement is a replacement rule for `FRAGMENTED_BOTTOM`. Independent DEVELOPMENT must first determine whether source-labelled rounded cups systematically disagree with the current 0.75 continuity state gate while remaining acceptable on duration/depth and non-V evidence.

The development analysis must report the measurements continuously; it must not search cutoffs that maximize agreement.

### R1-D entry gate

Select independent authoritative source-labelled Cup/CWOH DEVELOPMENT cases that are not in the Golden 10. Freeze identities/source facts before detector replay. Include:
- clean positive controls;
- at least one rounded source-positive case capable of discriminating fragmentation semantics;
- representation/candidate-multiplicity controls where available.

Only after DEVELOPMENT may a candidate state semantic be frozen. Validation remains locked until then.


## R1-D — independent DEVELOPMENT corpus freeze

Status: **SOURCE FACTS FROZEN BEFORE DETECTOR REPLAY**

Four independent authoritative IBD/MarketSurge Cup-family positives are frozen for bottom-shape DEVELOPMENT. None is in the CWOH Golden 10.

1. **TSLA 2017** — IBD explicitly identifies a cup-without-handle base, buy point 287.30, breakout 2017-04-03.
2. **ARWR 2019** — IBD identifies a cup base, buy point 36.90; first breakout 2019-10-17 and definitive recross 2019-10-22.
3. **BNTX 2020** — IBD identifies a cup base, buy point 48.95; breakout on 2020-03-17.
4. **AVGO 2025** — IBD/MarketSurge identifies a weekly cup base with buy point 376.23; article dated 2025-10-31 reports shares trading inside the resulting buy zone.

Guardrail: ARWR/BNTX/AVGO are Cup-family body positives, not asserted as handle-identity labels beyond what the source states. They are used to test shared Cup-body roundedness/fragmentation measurements. TSLA is the direct CWOH positive control.

Source facts are frozen before any replay against the v0.2 measurements. No Golden case is included. No threshold will be fitted to these four cases.

The discriminating question is preregistered: among source-positive Cup bodies that pass source-supported duration/depth semantics, does the current `FRAGMENTED_BOTTOM` proxy create source disagreement independently of sharp-V evidence? Measurements will be reported continuously, not optimized into a cutoff.


## R2 — independent DEVELOPMENT adjudication

Status: **DEVELOPMENT COMPLETE / CANDIDATE SEMANTICS FROZEN**

Engine replay run: `35584701478`
Artifact: `10631549153`
Digest: `sha256:b0b686a64f73a84a25d1e9a2afec33726355f22f610ff049e698db9a12bcecbf`
Replay SHA: `c338260b63acc3043ad7df3d5d21d236c722348c`

All four source cases resolve to source-dimension MATCH after applying the frozen TSLA 15x corporate-action comparison factor.

| Case | Pivot agreement | Matched production state | Matched fault | Adjudication |
|---|---:|---|---|---|
| TSLA 2017 | 0.000313% error | RECOGNIZED | none | clean direct-CWOH control |
| ARWR 2019 | 0.002710% | AMBIGUOUS | SHARP_V | supports keeping sharp-V hypothesis separate |
| BNTX 2020 | 0.002043% | REJECTED | TOO_DEEP | source-positive exceptional-depth disagreement; out of current fragmentation scope |
| AVGO 2025 | 0.005316% | AMBIGUOUS | FRAGMENTED_BOTTOM | independent discriminating source-positive fragmentation disagreement |

AVGO is the key independent discriminator: source pivot reconstruction is effectively exact and the matched source structure is held at AMBIGUOUS solely by the internal `FRAGMENTED_BOTTOM` research band. This reproduces the residual AX phenomenon without using AX/Golden for tuning.

### Frozen candidate semantics

For the next validation gate only:

1. retain `FRAGMENTED_BOTTOM` as explicit measured evidence;
2. test removal of `FRAGMENTED_BOTTOM` from state-bearing ambiguity faults when it is the only Cup-body research-band fault;
3. retain `SHARP_V` as state-bearing AMBIGUOUS;
4. retain `WEAK_RIGHT_RIM_RECOVERY` as state-bearing AMBIGUOUS;
5. retain source-supported duration/depth hard gates unchanged;
6. make no numerical cutoff change, including no tuning of the existing 0.75 continuity measurement;
7. candidate construction, pivot ranking, source matching, and pattern-family routing remain unchanged.

This is a semantic remap candidate, not a threshold fit.

No production promotion is authorized by DEVELOPMENT. The candidate must now face locked independent VALIDATION selected and frozen before detector replay.


## R2-A — DEVELOPMENT numeric audit 1/4: TSLA 2017

| Component | Source oracle | Engine source-equivalent candidate | Result |
|---|---|---|---|
| Pattern | CUP_WITHOUT_HANDLE | CUP_WITHOUT_HANDLE | family match |
| Pivot | 287.30 pre-split | 19.1593323 post-split; 287.389984 after 15x normalization | practical exact, 0.00031321% evaluator error |
| Left boundary | not source-scored | 2017-02-14 | NOT SCORED |
| Cup low | not source-scored | 2017-02-27 | NOT SCORED |
| Structural end | breakout/as-of 2017-04-03 | 2017-04-03 open-right candidate | compatible; end semantic not scored |
| Depth | not source-provided | 15.7904% | NOT SCORED |
| Resolution | — | UNIQUE source-equivalent candidate | clean |
| State/faults | source positive | RECOGNIZED / none | clean positive control |

Audit conclusion: TSLA is a clean direct-CWOH control. The 15x price-basis normalization is required and is now explicit; no morphology disagreement is present.

## R2-B — DEVELOPMENT numeric audit 2/4: ARWR 2019

| Component | Source oracle | Engine source-equivalent candidate | Result |
|---|---|---|---|
| Pattern | source identifies a cup base | CWOH body candidate | Cup-body comparable; handle identity not inferred |
| Pivot | 36.90 | 36.7999992 | practical near-exact, 0.00271005% evaluator error |
| Left boundary | not source-scored | 2019-08-30 | NOT SCORED |
| Cup low | not source-scored | 2019-09-30 | NOT SCORED |
| Structural end | source recross 2019-10-22 | 2019-10-22 open-right candidate | compatible; end semantic not scored |
| Depth | not source-provided | 29.4293% | NOT SCORED |
| Resolution | — | UNIQUE source-equivalent candidate | clean |
| State/faults | source positive Cup body | AMBIGUOUS / SHARP_V | morphology disagreement |

Audit conclusion: ARWR does **not** provide evidence about FRAGMENTED_BOTTOM. It isolates a different research proxy, SHARP_V. It therefore remains a control demonstrating why sharp-V and fragmentation semantics must not be merged.

## R2-C — DEVELOPMENT numeric audit 3/4: BNTX 2020

| Component | Source oracle | Engine source-equivalent candidate | Result |
|---|---|---|---|
| Pattern | source identifies a cup base | CWOH body candidate | Cup-body comparable; handle identity not inferred |
| Pivot | 48.95 | 48.8499985 | practical near-exact, 0.00204293% evaluator error |
| Left boundary | not source-scored | 2020-01-07 | NOT SCORED |
| Cup low | not source-scored | 2020-03-12 | NOT SCORED |
| Structural end | breakout/as-of 2020-03-17 | 2020-03-17 open-right candidate | compatible; end semantic not scored |
| Depth | not source-provided | 42.6817% | NOT SCORED against source |
| Resolution | — | UNIQUE source-equivalent candidate | clean |
| State/faults | source positive Cup body | REJECTED / TOO_DEEP | separate depth-semantics disagreement |

Audit conclusion: BNTX is outside the fragmentation question. Its source-equivalent candidate is rejected solely by the >33% normal-depth gate. Because the source record used here does not provide detector-comparable depth semantics, this case cannot adjudicate a new depth threshold and must not be used to alter the CWOH fragmentation candidate.

## R2-D — DEVELOPMENT numeric audit 4/4: AVGO 2025

| Component | Source oracle | Engine source-equivalent candidate | Result |
|---|---|---|---|
| Pattern | IBD/MarketSurge weekly cup base | CWOH body candidate | Cup-body comparable; handle identity not inferred |
| Pivot | 376.23 | 374.230011 | practical near match under evaluator tolerance, 0.00531587% evaluator error |
| Left boundary | not source-scored | 2025-09-11 | NOT SCORED |
| Cup low | not source-scored | 2025-10-10 | NOT SCORED |
| Structural end | source article/as-of 2025-10-31 | 2025-10-31 open-right candidate | compatible; end semantic not scored |
| Depth | not source-provided | 13.4089% | NOT SCORED |
| Resolution | — | UNIQUE source-equivalent candidate | clean |
| State/faults | source positive Cup body | AMBIGUOUS / FRAGMENTED_BOTTOM only | independent discriminating disagreement |

Audit conclusion: AVGO is the independent discriminator for the exact CWOH residual under study. Candidate identity is unique; pivot reconstruction is source-near; no competing fault contaminates the matched candidate. The only state-bearing disagreement is FRAGMENTED_BOTTOM.

## R2-E — 4/4 audit synthesis

All four DEVELOPMENT cases have now been audited individually. They must not be treated as four equivalent votes:

- TSLA: clean direct-CWOH positive control.
- ARWR: separate SHARP_V disagreement.
- BNTX: separate TOO_DEEP disagreement.
- AVGO: the sole independent discriminator for FRAGMENTED_BOTTOM.

Therefore the frozen fragmentation candidate is supported by **one clean independent discriminating case (AVGO)** plus the prior Golden diagnostic AX. It is not supported by a 4/4 morphology vote.

The candidate semantic remains narrow: retain FRAGMENTED_BOTTOM evidence but test it as non-state-bearing when it is the sole Cup-body research-band fault. No numeric cutoff changes are authorized. SHARP_V, WEAK_RIGHT_RIM_RECOVERY, duration and depth semantics are explicitly out of scope for this candidate.

The implementation regression at `09183c289b728ecf43cec64244b21244be405bb4` is green: workflow `35584979999` SUCCESS. This proves code/test consistency only; it is not validation evidence.

Next gate: freeze a locked independent VALIDATION cohort before replaying the semantic candidate.
