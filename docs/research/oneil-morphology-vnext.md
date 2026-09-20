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


## R1-A — frozen-code anatomy (complete)

Inspected frozen engine SHA `c433cc1e35a5aa32a46f732cd8c5545935e36e40`.

### Exact Flat Base decision path

The frozen confirmed-structure assessor is `src/oneil_patterns/morphology/flat_base.py::assess_flat_base`.

Hard gates:

```text
MIN_DURATION_SESSIONS = 25
MAX_DEPTH_PCT = 0.15

duration_gate = segment.duration_sessions >= 25
depth_gate    = segment.depth_pct <= 0.15
```

A failure of either hard gate yields `REJECTED`. Therefore `TOO_SHORT` is not a generic “less than five calendar weeks” test; it is specifically **fewer than 25 sessions in the engine segment representation**.

The assessed OHLC region is inclusive from `segment.start_date` through `segment.end_date`. Within that region:

```text
base_high        = max(high)
base_low         = min(low)
mean_close       = mean(close)

normalized_range = (base_high - base_low) / base_high
close_dispersion = population_std(close) / mean_close
upper_band_5pct  = fraction(close >= 0.95 * base_high)
```

`upper_band_5pct` is emitted as evidence but does **not** participate in the frozen state decision.

Research-only bands:

```text
TIGHT:
  normalized_range <= 0.03
  AND close_dispersion <= 0.01

WIDE_LOOSE:
  normalized_range >= 0.07
  OR close_dispersion >= 0.03
```

State mapping:

```text
duration < 25 OR depth > 15%        -> REJECTED
hard gates pass + WIDE_LOOSE        -> AMBIGUOUS
hard gates pass + BOUNDARY_CONTEXT  -> AMBIGUOUS
hard gates pass + TIGHT             -> RECOGNIZED
otherwise                            -> AMBIGUOUS
```

Thus a clean `RECOGNIZED` Flat Base requires not merely passing O'Neil-style duration/depth gates, but also satisfying the **research-only 3% normalized-range AND 1% close-dispersion tight band**. This is the critical anatomy finding behind the 0/10 clean-recognition result.

### Why WIDE_LOOSE is especially important

The frozen code explicitly says the tightness/wide-loose thresholds are **research bands, not claimed official O'Neil/IBD thresholds**. The P8 decision record further documents that source-aligned SNPS 2023 and TW 2024 contradicted the earlier policy that treated WIDE_LOOSE as a hard rejection. v0.2 therefore changed WIDE_LOOSE to `AMBIGUOUS`, but retained the same numeric bands.

However, the state machine still only emits clean `RECOGNIZED` when the candidate passes the separate TIGHT band (<=3% normalized range AND <=1% close dispersion). Therefore removing WIDE_LOOSE as a hard rejection did **not** make source-valid but non-TIGHT bases clean-recognizable; the intermediate region remains `AMBIGUOUS`.

This distinction matters:

- `WIDE_LOOSE` explains a recurring explicit fault;
- the broader **clean-recognition bottleneck is the positive TIGHT requirement itself**;
- those TIGHT thresholds are also research-only.

### Confirmed structure vs open-right-edge

`src/oneil_patterns/validation/open_right_edge_flat.py` reuses the same constants and state bands but changes the observation window. It begins at a confirmed SWING_HIGH and observes through as-of T rather than requiring a fully confirmed high-low-high segment.

For open-right-edge:

```text
duration = number of bars from start.price_date through asof_date
depth    = (start.price - observed_low) / start.price
```

It then applies the same 25-session, 15%-depth, WIDE_LOOSE, and TIGHT thresholds.

This explains why a source-pivot lineage can appear twice with different outcomes: the confirmed structural segment can be `TOO_SHORT`, while its open-right-edge observation has accumulated >=25 sessions and loses `TOO_SHORT`, yet remains `AMBIGUOUS` because of WIDE_LOOSE or because it does not satisfy TIGHT.

### Boundary context

Confirmed-structure assessment adds `BOUNDARY_CONTEXT` when the start, trough, or recovery landmark is marked as a segmentation boundary. Even without WIDE_LOOSE, this forces `AMBIGUOUS`. Open-right-edge validation does not apply this boundary-context check.

### R1-A diagnosis

The frozen FLAT_BASE recognition architecture contains three logically different filters:

1. source/theory-style hard gates: **>=25 sessions and <=15% depth**;
2. research-only negative descriptor: **WIDE_LOOSE** at >=7% normalized range OR >=3% close dispersion;
3. research-only positive recognition requirement: **TIGHT** at <=3% normalized range AND <=1% close dispersion.

The 40-case audit therefore points to a more precise research question than “is WIDE_LOOSE too strict?”:

> **Should clean O'Neil Flat Base recognition require the current research-only TIGHT band at all, and what source-backed morphology should distinguish RECOGNIZED from AMBIGUOUS once duration/depth pass?**

No threshold has been changed. Frozen production behavior remains untouched.

R1-A status: **COMPLETE**.

Next stage: **R1-B diagnostic replay** — capture, for all 10 Flat Base golden cases, the exact duration, depth, normalized range, close dispersion, tight/wide-loose booleans, candidate semantics, and state at the source-target/nearest-source lineage. This is diagnostic extraction only; no detector change.
