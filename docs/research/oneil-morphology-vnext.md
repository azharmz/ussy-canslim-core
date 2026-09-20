# O'Neil Morphology vNext Research

Status: **OPEN — research only**

## Purpose

Use the closed 40-case historical golden reconstruction as **diagnostic evidence** to formulate testable hypotheses about morphology fidelity. This track must not modify or tune the frozen production engine directly.

Frozen baseline:

- engine repo: `azharmz/ussy-oneil-patterns`
- engine SHA: `c433cc1e35a5aa32a46f732cd8c5545935e36e40`
- schema: `oneil-pattern-output-v2`
- golden deep audit: **40/40 complete**
- evidence source: `docs/validation/historical-reconstruction-golden-cases-v1.md`

## Research boundary

The 40 golden cases are a **development/diagnostic set from this point forward**. They may identify failure modes and motivate candidate definitions, but they may not serve as the independent validation set for vNext.

No threshold or morphology change may be promoted because it improves these same 40 examples. Any candidate vNext detector must be frozen first, then evaluated on a separate, source-backed holdout set not used to design it.

Production remains unchanged.

## Evidence-driven priority

### R1 — FLAT_BASE recognition semantics

Highest-priority investigation.

Closed audit evidence:

- 10/10 source cases audited.
- 8/10 reconstruct the source pivot practical-exact/near-exact.
- 0/10 source-target cases reach clean `RECOGNIZED`.
- `WIDE_LOOSE` is the recurring final recognition gate.
- `TOO_SHORT` is a demonstrated source-duration semantics discrepancy only where the source explicitly supplies duration (for example SNPS, TW, AMZN).
- NOW and CPRT are a different failure class: source pivot is not reconstructed, so their primary issue is upstream boundary/landmark/pivot generation.

Research question: **what exactly does the frozen `WIDE_LOOSE` rule measure, and does that measurement correspond to O'Neil/IBD flat-base morphology?**

Do not begin by loosening its threshold. First decompose the rule into its inputs, window, normalization, and boundary dependence, then replay the 10 golden cases to determine why each is classified as wide/loose.

### R2 — CWH handle/bottom/boundary semantics

The source-near cup/pivot geometry is often present. Investigate handle depth, handle midpoint, bottom-shape, and boundary-selection semantics independently rather than treating CWH as a single detector failure.

### R3 — DOUBLE_BOTTOM trough/rebound semantics

Separate `NO_SECOND_TROUGH_UNDERCUT` and middle-rebound semantics from WMT's upstream landmark-generation miss.

### R4 — CWOH regression anchor

CWOH is the strongest fidelity family in the closed set. Preserve it as a regression anchor while changing shared morphology infrastructure. Split-normalized replay diagnostic defects are tracked separately from morphology.

## Phase plan

1. **R1-A: frozen-code anatomy** — trace FLAT_BASE candidate generation and `WIDE_LOOSE` / `TOO_SHORT` gates to exact code and formulas.
2. **R1-B: diagnostic replay** — produce per-case gate inputs for all 10 FLAT_BASE golden cases without changing decisions.
3. **R1-C: source semantics research** — establish what source-backed O'Neil/IBD definitions actually constrain (duration, depth, tightness, weekly-vs-daily interpretation).
4. **R1-D: hypothesis specification** — write candidate morphology definitions before coding; no parameter search over the golden set.
5. **R1-E: independent validation set** — collect new source-backed FLAT_BASE cases not present in the 40-case development set.
6. Only then implement and freeze a vNext candidate for holdout evaluation.

## First deliverable

The next executable task is **R1-A only**: inspect the frozen `ussy-oneil-patterns` SHA and document the exact FLAT_BASE pipeline and the formulas/thresholds that produce `WIDE_LOOSE` and `TOO_SHORT`. No production modification and no threshold change.
