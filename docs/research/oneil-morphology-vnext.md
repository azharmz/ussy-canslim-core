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


## R1-B — 10-case diagnostic replay (complete)

Authoritative diagnostic run: `35504278574`, job `106061322494`, artifact `flat-base-r1b-diagnostic` (artifact id `10603332294`).

The replay recomputed the frozen Flat Base gate inputs on the oracle-nearest pivot lineage without changing detector behavior.

| Case | Nearest pivot vs oracle | Confirmed sessions | Confirmed range | Confirmed close dispersion | Confirmed state | Open-edge sessions | Open-edge range | Open-edge close dispersion | Open-edge state |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- |
| AAPL 2019 | practical exact | 4 | 13.01% | 3.56% | REJECTED: TOO_SHORT + WIDE_LOOSE | 30 | 13.92% | 3.00% | AMBIGUOUS: WIDE_LOOSE |
| SNPS 2023 | practical exact | 15 | 8.25% | 1.15% | REJECTED: TOO_SHORT + WIDE_LOOSE | 32 | 12.30% | 2.20% | AMBIGUOUS: WIDE_LOOSE |
| META 2024 | practical exact | 34 | 8.94% | 1.96% | AMBIGUOUS: WIDE_LOOSE | 41 | 10.61% | 2.18% | AMBIGUOUS: WIDE_LOOSE |
| TW 2024 | +0.0037% | 17 | 8.06% | 2.00% | REJECTED: TOO_SHORT + WIDE_LOOSE | 31 | 9.47% | 2.18% | AMBIGUOUS: WIDE_LOOSE |
| NOW 2024 | -4.12% | 101* | 21.75%* | 4.37%* | REJECTED: TOO_DEEP + WIDE_LOOSE | 141* | 25.58%* | 5.21%* | REJECTED: TOO_DEEP + WIDE_LOOSE |
| DECK 2023 | practical exact | — | — | — | — | 58 | 17.26% | 4.27% | AMBIGUOUS: WIDE_LOOSE |
| CROX 2021 | practical exact | 13 | 13.64% | 2.72% | REJECTED: TOO_SHORT + WIDE_LOOSE | 25 | 17.73% | 3.21% | AMBIGUOUS: WIDE_LOOSE |
| CPRT 2020 | -9.52% | 13* | 8.78%* | 1.99%* | REJECTED: TOO_SHORT + WIDE_LOOSE | 75* | 18.40%* | 4.60%* | AMBIGUOUS: WIDE_LOOSE |
| AMZN 2020 | -0.0030% | 7 | 12.74% | 2.54% | REJECTED: TOO_SHORT + WIDE_LOOSE | 32 | 14.56% | 3.31% | AMBIGUOUS: WIDE_LOOSE |
| KKR 2024 | practical exact | 21 | 11.17% | 2.71% | REJECTED: TOO_SHORT + WIDE_LOOSE | 39 | 14.84% | 3.25% | AMBIGUOUS: WIDE_LOOSE |

`*` NOW and CPRT are nearest-engine lineages, not oracle-pivot reconstructions, so their morphology metrics must not be interpreted as measurements of the source Flat Base.

### R1-B findings

1. **No oracle-nearest lineage is TIGHT under the frozen research band.** Every measured lineage has normalized range above the 3% TIGHT ceiling; therefore none can become clean `RECOGNIZED` under the current state machine even if WIDE_LOOSE were merely removed as a fault.
2. For the eight cases whose pivot is practical-exact/near-exact, **all eight source-nearest lineages are classified WIDE_LOOSE**. This is primarily driven by normalized high-low range >=7%; close dispersion is not required to trigger the fault.
3. The positive TIGHT gate and negative WIDE_LOOSE band leave a large semantics gap relative to the source-backed examples. Several source examples have engine-measured ranges around 8–15% while still being identified by the source as Flat Bases.
4. Confirmed-structure `TOO_SHORT` and open-right-edge behavior are materially different. AAPL, SNPS, TW, CROX, AMZN, and KKR lose TOO_SHORT once the observation extends to the as-of date, yet remain AMBIGUOUS because of WIDE_LOOSE/non-TIGHT morphology.
5. META is especially diagnostic: its confirmed structure already passes the 25-session duration gate (34 sessions) and <=15% depth, but remains AMBIGUOUS solely because the research tightness semantics classify its 8.94% range as WIDE_LOOSE.
6. NOW and CPRT remain upstream reconstruction problems and must not be used to infer a replacement tightness threshold.

### R1-B disposition

The evidence narrows the vNext question. A simple threshold tweak is not justified. The current implementation conflates at least two concepts:

- total base depth/range over the structural interval; and
- the notion of price action being “tight” enough for a Flat Base.

Because the frozen `normalized_range = (max(high)-min(low))/max(high)` is structurally close to total base depth, using a 3% positive TIGHT ceiling makes clean recognition incompatible with the audited source examples whose valid base ranges are substantially larger.

No detector change is authorized from R1-B. R1-C must establish source-backed Flat Base semantics before any replacement metric or threshold is proposed.

R1-B status: **COMPLETE — 10/10 diagnostic cases**.


## R1-C — source-backed Flat Base semantics (complete)

Research date: 2026-09-20.

### Primary/source-aligned findings

IBD's own educational material gives the core Flat Base contract as:

- **minimum length: 5 weeks**;
- **base depth: 15% or less**;
- it is a milder correction than cup-with-handle/double-bottom;
- the buy point is above the prior/peak high within the base.

A historical IBD educational booklet adds that the price range will **usually remain fairly tight throughout the pattern**, but it does not define that statement as a universal 3% total high-low range or 1% population standard deviation of closes. It also describes Flat Base as commonly occurring after a prior advance / earlier base.

A later IBD Investors Corner explanation is consistent: Flat Base depth does not exceed 15%, can form in as little as five weeks, should show rangebound action, and tighter trading is preferable to erratic wide-and-loose swings. Again, the source does not supply the frozen engine's 3% total-range + 1% close-dispersion formula as the recognition definition.

### Important semantic distinction: Flat Base vs Three-Weeks-Tight

IBD separately defines a **three-weeks-tight** pattern using weekly closes that remain within roughly 1.5% of one another. That is a different pattern/concept from the five-week-minimum Flat Base.

Therefore a very narrow percentage test on closes must not be imported into Flat Base merely because both are described as “tight.” The source-backed Flat Base constraints available here are primarily duration, maximum correction/depth, sideways/rangebound character, prior advance/context, and pivot geometry; “tighter is better” is qualitative unless a source supplies a specific Flat Base metric.

### Source-backed examples relevant to the golden set

IBD's Apple 2019 retrospective identifies the 221.37 Flat Base buy point and describes the base as the constructive pause after the earlier advance. IBD's Top Stocks 2020 material explicitly identifies AMZN as a **five-week flat base** with a 3,344.39 buy point.

These source examples reinforce the R1-B observation that valid source-labelled Flat Bases need not satisfy the frozen detector's <=3% total high-low range.

### R1-C conclusion

The following can be treated as source-backed Flat Base constraints for vNext research:

1. minimum duration of about **5 weeks**;
2. correction/depth **no more than 15%**;
3. generally sideways/rangebound and comparatively mild/tight price action;
4. pivot/buy point at the prior/peak high of the base (historical source convention may state ten cents above it);
5. context after a prior uptrend / often following an earlier base is relevant.

The following are **NOT established by the reviewed O'Neil/IBD sources as official Flat Base recognition thresholds**:

- total high-low range <=3%;
- population standard deviation of closes <=1%;
- WIDE_LOOSE defined as total high-low range >=7%;
- WIDE_LOOSE defined as close dispersion >=3%.

Those are frozen-engine research operationalizations, not source rules.

### Design implication

R1-C does **not** authorize replacing the research bands with 15%. The 15% source rule is a maximum base correction/depth rule, not automatically a definition of tightness.

vNext must preserve the distinction between:

- **depth/correction**: source-backed <=15%;
- **duration**: source-backed >=5 weeks;
- **tight/sideways quality**: source-backed qualitative morphology that still needs an independently specified operationalization;
- **pivot geometry/context**: separate structural requirements.

Any quantitative tightness metric proposed in R1-D must be justified as an explicit operationalization, must not be presented as an O'Neil threshold, and must be frozen before independent holdout validation.

R1-C status: **COMPLETE**.


## R1-D — vNext hypothesis specification (frozen before holdout)

Status: **FROZEN HYPOTHESIS — not production code**.

This specification is intentionally written before collecting/evaluating the independent holdout. The 40 golden cases motivated the defect class but are not used to select numeric parameters below.

### H1 — remove circular total-range tightness from the positive recognition gate

The frozen detector uses total base high-low range both as a morphology descriptor and, through the TIGHT band, as the decisive positive recognition criterion. R1-B showed this is structurally entangled with base depth.

vNext hypothesis:

> Once a Flat Base satisfies source-backed duration and depth constraints, total base high-low range should not be required to be <=3% for clean recognition.

The source-backed maximum correction remains a separate depth gate.

### H2 — operationalize “tight/sideways” as local weekly behavior, not whole-base depth

Candidate vNext quality representation will be **descriptive first**, with no pass/fail numeric threshold in the first holdout evaluation.

For each candidate, aggregate daily bars into completed trading weeks and emit:

1. `weekly_close_span_pct`: (max weekly close - min weekly close) / max weekly close;
2. `weekly_median_range_pct`: median of weekly (high-low)/high;
3. `weekly_close_change_abs_median`: median absolute week-to-week close return;
4. `weekly_direction_changes`: sign changes in week-to-week close returns;
5. `late_base_contraction_ratio`: median weekly range over the final two completed weeks divided by median weekly range over the preceding completed weeks, when enough weeks exist.

These are research operationalizations, **not O'Neil/IBD thresholds**.

Rationale: they separate sideways/tight trading behavior from the already-measured maximum correction of the entire base and allow the holdout to reveal whether source-labelled Flat Bases exhibit useful local contraction/rangebound structure.

### H3 — provisional recognition state machine for holdout comparison

Two outputs must be evaluated side-by-side:

**A. Source-minimum structural classifier**

```text
duration >= 5 trading weeks
AND depth <= 15%
AND valid Flat Base pivot/boundary construction
-> STRUCTURALLY_ELIGIBLE
```

This is not automatically the final production `RECOGNIZED` definition.

**B. Quality annotation**

Attach the H2 weekly descriptors without allowing them to change A's eligibility during the first holdout pass.

This prevents threshold fitting on the golden set and prevents the independent holdout from being consumed immediately as a parameter-search set.

### H4 — calendar/week semantics must be tested explicitly

The frozen engine approximates five weeks as `duration_sessions >= 25`. Source descriptions are expressed in weeks. vNext holdout must retain both:

- elapsed trading-session count;
- distinct trading-week count / source week span.

No equivalence between “25 sessions” and “5 weeks” is assumed until independently checked. Holiday weeks and boundary placement can otherwise create false TOO_SHORT outcomes.

### H5 — upstream reconstruction remains a separate axis

NOW/CPRT-type failures must not be repaired by Flat Base tightness changes. Holdout reporting must classify failures into:

1. source pivot/boundary not reconstructed;
2. structural duration/depth ineligible;
3. structurally eligible with quality descriptors;
4. downstream breakout/execution observations.

### Pre-registered R1-E acceptance questions

Before viewing the holdout results, the following questions are frozen:

1. What fraction of source-backed holdout Flat Bases have their source pivot reconstructed within the pre-existing practical-near criterion?
2. Among source-pivot-reconstructed cases, what fraction satisfy >=5 trading weeks and <=15% depth?
3. How often does `25 sessions` disagree with explicit week semantics?
4. What are the distributions of the five H2 weekly quality descriptors for source-backed Flat Bases?
5. Does the frozen 3%/1% TIGHT gate reject source-backed holdout cases that otherwise satisfy source duration/depth and pivot geometry?
6. Are any apparent morphology failures actually upstream landmark/boundary failures?

### Anti-tuning rules

- No H2 pass/fail cutoff may be chosen from the original 40 golden cases.
- R1-E source-backed holdout is for evaluating the frozen H1-H5 hypotheses; it must not be repeatedly optimized against.
- If R1-E reveals that a quantitative quality threshold is necessary, threshold development must use a **separate development set**, followed by another untouched validation set.
- No production engine change occurs in R1-D or R1-E.
- Existing CWOH/DB/CWH behavior is outside the scope of this Flat Base hypothesis and must remain regression-protected in any later implementation.

R1-D status: **COMPLETE / HYPOTHESIS FROZEN**.

Next stage: **R1-E independent validation set construction**. Collect new source-backed Flat Base cases absent from the original 40-case golden reconstruction, freeze their source evidence and oracle fields before running the detector, then evaluate H1-H5 exactly as specified above.
