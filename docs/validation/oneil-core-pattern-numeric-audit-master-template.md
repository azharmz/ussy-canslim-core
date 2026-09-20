# Master Template — One-by-One Numeric Audit for O'Neil Core Patterns

Status: **VALIDATION TEMPLATE / NEVER PRODUCTION**

Purpose: provide one canonical audit format for every historical/source-backed case across the four frozen core families:

- `CUP_WITH_HANDLE`
- `CUP_WITHOUT_HANDLE`
- `DOUBLE_BOTTOM`
- `FLAT_BASE`

This template is for source-fidelity diagnosis. A mismatch is evidence, not permission to tune the frozen detector. Source oracle fields must never become detector inputs. Dimensions not stated by the authoritative source are `NOT SCORED`.

Frozen reference engine for the historical reconstruction workstream:
`azharmz/ussy-oneil-patterns@c433cc1e35a5aa32a46f732cd8c5545935e36e40`
(schema `oneil-pattern-output-v2`, engine `33-core-p8-frozen-v1`).

---

# Audit numerik [FAMILY] #[N] — [SYMBOL] [YEAR]

**Status:** [IN PROGRESS / COMPLETE]  
**Source/oracle:** [source title + URL]  
**As-of / breakout date:** [YYYY-MM-DD / NOT STATED]  
**Price basis:** [raw / split-normalized / other + lineage]  
**Frozen engine SHA:** `c433cc1e35a5aa32a46f732cd8c5545935e36e40`

## A. Ringkasan source vs engine

| Komponen | Oracle / source | Frozen engine | Hasil |
| --- | --- | --- | --- |
| Pattern family | [ ] | [ ] | [EXACT / FAMILY MATCH / MISMATCH] |
| Pivot / buy point | [ ] | [ ] | [delta absolute / %] |
| Structural start | [ / NOT STATED] | [ ] | [EXACT / NEAR / NOT SCORED] |
| Structural end / right edge | [ / NOT STATED] | [ ] | [ ] |
| Duration | [weeks / NOT STATED] | [sessions + distinct trading weeks] | [ ] |
| Depth / correction | [% / NOT STATED] | [%] | [delta / NOT SCORED] |
| Final state | n/a unless source states one | [RECOGNIZED / AMBIGUOUS / REJECTED] | diagnostic only |
| Candidate semantics | n/a | [confirmed/open-right-edge/etc.] | diagnostic only |
| Detector faults | n/a | [ ] | diagnostic only |

**Headline finding:**  
[One concise sentence locating the agreement/disagreement.]

## B. Source oracle freeze

Record only facts explicitly supported by the source.

| Oracle field | Frozen value | Evidence status |
| --- | --- | --- |
| Family | [ ] | SOURCE-BACKED |
| Pivot | [ ] | SOURCE-BACKED |
| Breakout/as-of date | [ ] | [SOURCE-BACKED / NOT STATED] |
| Duration | [ ] | [SOURCE-BACKED / NOT STATED] |
| Depth | [ ] | [SOURCE-BACKED / NOT STATED] |
| Named landmarks / structure | [ ] | [SOURCE-BACKED / NOT STATED] |
| Other family-specific fact | [ ] | [SOURCE-BACKED / NOT STATED] |

Anything absent from source: **NOT SCORED**. Do not infer an oracle from engine output.

## C. Candidate lineage

| Layer | Engine observation | Audit result |
| --- | --- | --- |
| Landmark generation | [ ] | [MATCH / NEAR / MISS / NOT SCORED] |
| Boundary construction | [ ] | [MATCH / NEAR / MISS / NOT SCORED] |
| Family assembly | [ ] | [ ] |
| Pivot reconstruction | [ ] | [exact delta] |
| Morphology gates | [ ] | [ ] |
| Final recognition | [ ] | [ ] |

Preserve the diagnostic order:

`landmark/boundary/pivot → family assembly/morphology → final gates → breakout execution → price-basis/corporate-action diagnostics`.

Do not rewrite a later-layer failure as an earlier-layer failure.

## D. Core numeric measurements

| Metric | Oracle | Engine | Delta / interpretation |
| --- | ---: | ---: | --- |
| Pivot | [ ] | [ ] | [ ] |
| Duration sessions | NOT SCORED unless source supports sessions | [ ] | [ ] |
| Distinct trading weeks | [ ] | [ ] | [ ] |
| Depth % | [ ] | [ ] | [ ] |
| Structural high | [ ] | [ ] | [ ] |
| Structural low | [ ] | [ ] | [ ] |

Add family-specific rows from Section E. Do not force metrics from another family into this case.

## E. Family-specific module

### If CUP_WITH_HANDLE

| Metric / landmark | Oracle | Engine | Result |
| --- | --- | --- | --- |
| Left rim | [ ] | [ ] | [ ] |
| Cup low | [ ] | [ ] | [ ] |
| Right rim | [ ] | [ ] | [ ] |
| Cup duration | [ ] | [ ] | [ ] |
| Cup depth | [ ] | [ ] | [ ] |
| Right-rim / left-rim ratio | [ ] | [ ] | [ ] |
| Handle start | [ ] | [ ] | [ ] |
| Handle low | [ ] | [ ] | [ ] |
| Handle duration | [ ] | [ ] | [ ] |
| Handle depth | [ ] | [ ] | [ ] |
| Handle midpoint relation | [ ] | [ ] | [ ] |
| Handle state/fault | n/a | [ ] | diagnostic |

### If CUP_WITHOUT_HANDLE

| Metric / landmark | Oracle | Engine | Result |
| --- | --- | --- | --- |
| Left rim | [ ] | [ ] | [ ] |
| Cup low | [ ] | [ ] | [ ] |
| Right rim / pivot | [ ] | [ ] | [ ] |
| Cup duration | [ ] | [ ] | [ ] |
| Cup depth | [ ] | [ ] | [ ] |
| Right-rim / left-rim ratio | [ ] | [ ] | [ ] |
| Bottom morphology | [ ] | [ ] | [ ] |
| Cup state/fault | n/a | [ ] | diagnostic |

### If DOUBLE_BOTTOM

| Metric / landmark | Oracle | Engine | Result |
| --- | --- | --- | --- |
| First trough | [ ] | [ ] | [ ] |
| Middle peak / rebound | [ ] | [ ] | [ ] |
| Second trough | [ ] | [ ] | [ ] |
| Pivot | [ ] | [ ] | [ ] |
| Total duration | [ ] | [ ] | [ ] |
| Overall depth | [ ] | [ ] | [ ] |
| Second-low relation | [ ] | [ ] | [ ] |
| Rebound geometry | [ ] | [ ] | [ ] |
| DB state/fault | n/a | [ ] | diagnostic |

### If FLAT_BASE

| Metric | Oracle | Engine | Result |
| --- | --- | --- | --- |
| Base start | [ ] | [ ] | [ ] |
| Base end/right edge | [ ] | [ ] | [ ] |
| Pivot | [ ] | [ ] | [ ] |
| Duration | [weeks] | [sessions + weeks] | [ ] |
| Depth % | [ ] | [ ] | [ ] |
| Normalized total range | NOT OFFICIAL THRESHOLD | [ ] | diagnostic |
| Close dispersion | NOT OFFICIAL THRESHOLD | [ ] | diagnostic |
| Frozen TIGHT flag | n/a | [ ] | research-only gate |
| Frozen WIDE_LOOSE flag | n/a | [ ] | research-only gate |
| Boundary context | n/a | [ ] | diagnostic |
| State/fault | n/a | [ ] | diagnostic |

For vNext research, when requested, append the preregistered weekly descriptors:
`weekly_close_span_pct`, `weekly_median_range_pct`,
`weekly_close_change_abs_median`, `weekly_direction_changes`,
`late_base_contraction_ratio`.

## F. Breakout-day observation — ORIGINAL/source-faithful layer

Only evaluate if source/as-of data supports it.

| Component | Observation |
| --- | --- |
| Pivot crossed? | [ ] |
| Breakout-day OHLC | [ ] |
| Volume evidence | [ ] |
| Buy-zone relation | [ ] |
| Intraday limitation | [INTRADAY_ENTRY_TIMING_NOT_RECONSTRUCTED when applicable] |

Do not impose USSY T+1 Open on the original O'Neil/source-faithful layer.

## G. USSY execution observation — OPERATIONALIZATION layer

If relevant:

| Component | Observation |
| --- | --- |
| T+1 open | [ ] |
| T+1 vs pivot | [ ] |
| T+1 vs signal close | [ ] |
| Original buy-zone status | [ ] |
| USSY execution classification | [ ] |

Execution adaptation must not overwrite morphology/source-fidelity conclusions.

## H. Failure localization

Select the **earliest genuine disagreement**:

- [ ] PRICE_BASIS / CORPORATE_ACTION
- [ ] LANDMARK_GENERATION
- [ ] BOUNDARY_CONSTRUCTION
- [ ] PIVOT_RECONSTRUCTION
- [ ] FAMILY_ASSEMBLY
- [ ] MORPHOLOGY_SEMANTICS
- [ ] FINAL_RECOGNITION_GATE
- [ ] BREAKOUT_EXECUTION_ADAPTATION
- [ ] NO MATERIAL SOURCE-FIDELITY GAP
- [ ] DATA_UNAVAILABLE

**Primary classification:** `[CLASSIFICATION]`

**Reason:**  
[Explain exactly which source-backed fact and engine observation disagree.]

## I. Audit conclusion

**Source fidelity:** [what matches]  
**Localized gap:** [what differs]  
**Not established by source:** [NOT SCORED dimensions]  
**Production implication:** **NONE from this single audit.**  
**Research implication:** [hypothesis/evidence only; no tuning authorization].

## J. Evidence lineage

- source: [title + URL]
- source accessed: [YYYY-MM-DD]
- reconstruction repo/branch: [ ]
- engine repo/SHA: [ ]
- replay run/job: [ ]
- artifact: [ ]
- price-data source/basis: [ ]
- audit commit: [ ]

---

## Master rules

1. Use the same Sections A–J for all four core families.
2. Only Section E changes by family.
3. Oracle facts are frozen before detector replay.
4. Never use oracle fields as detector inputs.
5. Never score facts the source does not state; use `NOT SCORED`.
6. Separate source fidelity, production adaptation, and data/price-basis diagnostics.
7. Report the earliest genuine disagreement and preserve downstream observations separately.
8. A single case or the golden corpus does not authorize threshold tuning.
9. Golden historical cases are diagnostic/reference evidence, not a parameter-selection dataset.
10. Record exact run/job/artifact/commit lineage so every audit is reproducible.
