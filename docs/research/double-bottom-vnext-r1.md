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


## R2 — independent DEVELOPMENT replay

Status: **5/5 AUDITED / SEMANTIC QUESTION NARROWED / NO ENGINE CHANGE**

Production engine SHA: `10668bbe9e27780d0dfe2464b9370e25e996fda5`.
Replay run: `35576443466`.
Artifact digest: `sha256:128055219bc2e32267b59f301a598278c34e61c6026276bd2b197bf3c3797351`.

All five authoritative DOUBLE_BOTTOM DEVELOPMENT labels remain source-dimension MATCH. Candidate multiplicity is retained rather than resolved from detector state.

### SEI 2024

- source pivot 12.74; matched engine pivot 12.73999977, practical exact;
- matched confirmed core-W candidate is `DOUBLE_BOTTOM_REJECTED` only on `TOO_SHORT`;
- source-equivalent set contains both REJECTED confirmed structure and RECOGNIZED completion semantics;
- this supports the existing v3 duration-representation solution rather than a lower duration threshold.

### NVDA 2023

- source pivot 47.61; engine 47.60900116, practical exact;
- source-equivalent candidates are consistently `DOUBLE_BOTTOM_RECOGNIZED`;
- matched candidate has no faults;
- this remains the clean positive morphology control.

### SPOT 2025

- source pivot 621.20; engine 621.20001221, practical exact;
- matched candidate is `DOUBLE_BOTTOM_AMBIGUOUS` only on `NO_SECOND_TROUGH_UNDERCUT`;
- source-equivalent set contains AMBIGUOUS and REJECTED candidates, but no RECOGNIZED source-equivalent candidate;
- this is the strongest independent DEVELOPMENT evidence that no-undercut should be examined as quality evidence rather than an identity veto.

### WMT 2024

- current production stack now source-matches pivot 60.89 at 60.88999939 through `LOCAL_TURN_AUX:p8-db-local-turn-v0.1`;
- matched candidate is `DOUBLE_BOTTOM_RECOGNIZED` with no faults;
- this differs from the older Golden frozen-engine result where the April-May structure was absent upstream. The difference is attributable to later landmark/local-turn engineering, not a morphology relaxation;
- WMT therefore no longer supports changing the undercut rule in the current production stack.

### EMBJ 2026

- source pivot 71.68; engine 71.68000031, practical exact;
- deterministic matched candidate is AMBIGUOUS on `NO_SECOND_TROUGH_UNDERCUT`;
- however the source-equivalent candidate set contains AMBIGUOUS, RECOGNIZED and REJECTED states;
- because source-equivalent lineages disagree, EMBJ is evidence for candidate/lineage multiplicity and cannot independently authorize undercut state remapping.

## R2 synthesis

The independent cohort does **not** support a broad Double Bottom rewrite.

- Duration: existing open-right completion semantics already solve the SEI representation issue without changing the 35-session hard threshold.
- Upstream landmarks: WMT is repaired in the current stack by local-turn auxiliary generation; keep that separate from morphology.
- Undercut: NVDA is a clean recognized control; SPOT is a clean source-positive no-undercut disagreement; EMBJ is mixed because source-equivalent lineages disagree.
- Research-only `SHALLOW_UNDERCUT` and `WEAK_MIDDLE_REBOUND` remain insufficiently isolated by this cohort to justify numerical changes.

### Candidate semantic proposal

The only morphology change with enough evidence to advance to a future validation gate is narrow:

> retain `NO_SECOND_TROUGH_UNDERCUT` as explicit morphology/quality evidence, but test whether it should cease to be state-bearing when duration/depth and the remaining W structure pass.

This proposal is **not implemented** here. A fresh DOUBLE_BOTTOM holdout, not used in Golden diagnosis or P8 DEVELOPMENT, is required before production remapping. No cutoff may be selected from SPOT, EMBJ, IPHI or other positive examples.

Until such a holdout is frozen, production remains unchanged.


## R3 — frozen VALIDATION gate

Status: **SOURCE-FIDELITY PASS / DISCRIMINATING GATE NOT SATISFIED / NO PROMOTION**

After the R2 candidate semantics were frozen, three new authoritative IBD Double Bottom cases were frozen as VALIDATION before detector comparison:

1. MELI 2025 — source pivot 2146.82.
2. TJX 2024 — source pivot 102.04.
3. LII 2024 — source pivot 499.27.

The candidate implementation changed only one semantic: `NO_SECOND_TROUGH_UNDERCUT` remains explicit evidence but is no longer by itself state-bearing. Duration/depth hard gates and the research-only `SHALLOW_UNDERCUT` / `WEAK_MIDDLE_REBOUND` ambiguity bands were preserved.

### MELI

Run `35578291570`, artifact digest `sha256:d7a0729c9ebfeb19c7db5cb455a34edf62c9aef10de0b20a25a25ceddcc50295`.

- source pivot 2146.82; engine source-equivalent pivot 2146.820068, practical exact;
- source-dimension agreement MATCH;
- deterministic matched state RECOGNIZED;
- however the matched source-pivot candidate is fault-free and does not exercise `NO_SECOND_TROUGH_UNDERCUT`;
- source-equivalent multiplicity remains explicit.

MELI is a source-fidelity positive control but is non-discriminating for the proposed semantic change.

### TJX

Run `35578446972`, artifact digest `sha256:ea910547db5014db427fc654b0459c0c396cafde537258d8d1f3e51d5338f474`.

- source pivot 102.04; engine source-equivalent pivot 102.0400009, practical exact;
- source-dimension agreement MATCH;
- deterministic matched candidate remains AMBIGUOUS on `WEAK_MIDDLE_REBOUND`, not on no-undercut;
- another source-equivalent exact-pivot lineage is RECOGNIZED with no faults;
- 23 source-equivalent candidates span RECOGNIZED / AMBIGUOUS / REJECTED and multiple semantics.

TJX is not a clean discriminator of the undercut proposal; it instead exposes lineage/candidate multiplicity and the separate research-only rebound band.

### LII

Run `35578568506`, artifact digest `sha256:53928a36e5fd969c9c1fe00a96fa30be03943a6cea8511e6179f606f28e55e66`.

- source pivot 499.27; engine 499.269989, practical exact;
- source-dimension agreement MATCH;
- deterministic matched candidate RECOGNIZED with no faults;
- source-equivalent multiplicity remains, including rejected alternatives.

LII is another positive source-fidelity control but does not exercise the proposed no-undercut remapping.

## R3 adjudication

All three untouched authoritative holdouts confirm that the current engine can reconstruct the published Double Bottom pivots without breaking source fidelity. Full regression under the candidate implementation is green.

However, **none of the three holdouts cleanly tests the semantic delta itself**. MELI and LII match through fault-free source-pivot candidates; TJX's deterministic disagreement is `WEAK_MIDDLE_REBOUND` plus heavy candidate multiplicity. Therefore the validation set cannot establish that removing the state-bearing effect of `NO_SECOND_TROUGH_UNDERCUT` improves source fidelity rather than merely broadening recognition.

Promotion gate: **BLOCKED**.

The candidate implementation must remain research-only and must not be merged to production. Production SHA `10668bbe9e27780d0dfe2464b9370e25e996fda5` remains authoritative for DOUBLE_BOTTOM.

A future promotion attempt requires an authoritative holdout whose published/source-grounded geometry actually discriminates the trough relationship, ideally with both troughs documented or otherwise uniquely reconstructable. Do not keep sampling ordinary positive Double Bottom articles until one happens to fit; that would turn holdout selection into post-hoc search.

This is a methodological stop, not an engineering failure.
