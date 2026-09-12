# O'Neil Theory Fidelity Audit v1

Date: 2026-09-12
Status: ACTIVE

## Purpose

Audit whether the frozen CAN SLIM quantitative v1 candidate generator faithfully represents William J. O'Neil / IBD methodology. This is a theory-first workstream. It must not be shaped by historical CAGR, PF, FWD1 outcomes, EXH2 outcomes, or convenience of implementation.

Required order:

```text
Theory -> specification -> implementation -> validation -> performance
```

The frozen v1 and its 10,731 historical candidates remain valid evidence for the old quantitative proxy, but they are not CAN SLIM ground truth.

## Workstream status

| # | Workstream | Status |
|---|---|---|
| 25 | Theory Fidelity Audit | ACTIVE |
| 26 | Proper-base definitions | COMPLETE — theory audit |
| 27 | Pivot / buy-point definition | COMPLETE — theory audit |
| 28 | Breakout + volume confirmation | NEXT |
| 29 | RS / leadership fidelity | NOT STARTED |
| 30 | C/A/S/I/M role fidelity | NOT STARTED |
| 31 | Sell / risk-management fidelity | NOT STARTED |
| 32 | Theory-faithful candidate specification | NOT STARTED |
| 33 | O'Neil Pattern Recognition Engine | NOT STARTED |
| 34 | Theory-faithful candidate generator | NOT STARTED |
| 35 | New-candidate validation | NOT STARTED |
| 36 | Execution / entry research | PARKED |

## #26 Proper Base — conclusion

Overall v1 proper-base fidelity: **WEAK_PROXY**.

The v1 `generic prior-35-session base proxy` captures the broad idea of consolidation before breakout, but it does not identify O'Neil-specific morphology. A theory-faithful system must distinguish at least the core base families and their structural landmarks rather than treating every acceptable rolling range as the same base.

Core morphology for the future specification:

- cup with handle;
- cup without handle / cup base;
- double bottom;
- flat base.

Additional legitimate structures to preserve for later implementation:

- base-on-base (a relationship between bases, not a single independent morphology);
- ascending base;
- IPO base as a special-case pattern for newly public stocks.

Key fidelity gaps in v1 include missing prior-uptrend semantics, pattern classification, cup shape / V-shape distinction, handle semantics, double-bottom W landmarks, flat-base tightness, base-on-base history, and faulty/wide-and-loose structure checks.

The fixed 35-session duration is only a reasonable duration proxy for some patterns (notably the approximately seven-week minimum associated with cup-with-handle and double bottom). It is not a faithful base-identification rule. Likewise, `depth <= 40%` is not a universal O'Neil base-depth rule; acceptable/normal depth is pattern-specific and context-sensitive.

No quantitative detector thresholds are frozen by #26. Pattern quantification belongs after the theory-faithful specification is complete.

## #27 Pivot / Buy Point — conclusion

Overall v1 pivot fidelity: **WEAK-to-REASONABLE_PROXY**.

Canonical structural principle:

```text
pivot_level = pattern-specific structural resistance
```

It must not be defined as the highest price in an arbitrary N-session window.

Theory mapping to carry into the future specification:

| Pattern | Structural pivot / conventional buy-point landmark |
|---|---|
| Cup with handle | highest price in the valid handle |
| Cup without handle / cup base | prior / left-side high |
| Double bottom | middle peak of the W |
| Flat base | base / left-side high |
| Ascending base | final / pattern structural resistance high |
| Base-on-base | pivot derived from the morphology of the second base |

The historical O'Neil/IBD convention of adding a small fixed amount above resistance (later commonly `$0.10`) must be documented as legacy methodology, not silently restored as a current rule. Current IBD convention uses the structural resistance itself as the conventional buy point.

The 5% buy zone is conceptually separate from the pivot. It is an execution / anti-chasing range above the proper buy point, not a definition of the pivot itself. Therefore v1 `T0 close <= pivot * 1.05` is a reasonable proxy for the concept but places an execution-range idea inside candidate-day screening semantics.

The v1 requirement `T0 close > pivot` is a stricter breakout/hold proxy, not established here as the universal definition of crossing the buy point. Its exact fidelity belongs to #28 breakout + volume confirmation.

Early/aggressive entries must remain separate from the canonical structural pivot. X1-X4, including X3, remain parked while theory fidelity is being established.

## Dedicated pattern-recognition workstream

Pattern recognition is now explicitly separated from the generic candidate-generator implementation.

### #33 — O'Neil Pattern Recognition Engine

Purpose: translate the frozen theory-faithful pattern specification into reproducible pattern and landmark recognition from the existing daily OHLCV data infrastructure (R2).

Expected scope after #32 is frozen:

- candidate-base segmentation;
- swing / landmark extraction;
- cup-with-handle detector;
- cup-without-handle detector;
- double-bottom detector;
- flat-base detector;
- ascending-base detector;
- base-on-base relationship/state tracking;
- faulty-base / quality flags;
- pattern confidence / ambiguity handling;
- morphology validation fixtures and human-labelled validation set.

This workstream must not begin by optimizing trading performance. First validation is morphology/landmark agreement and reproducibility. Performance research occurs only after candidate validity is established.

Primary data basis: existing daily OHLCV in R2. No new market-data source is implied by this decision.

## Guardrails

- Do not retrofit theory-fidelity changes into FWD1; FWD1 remains evidence for frozen v1.
- Do not mix EXH2 with the theory-fidelity audit.
- Do not optimize X3 or other entry rules now.
- Do not tune pattern thresholds from historical returns.
- Do not treat the 10,731 v1 candidates as O'Neil ground truth.
- Do not start #33 implementation before #32 theory-faithful candidate specification is frozen.
- Preserve uncertainty: a future detector may emit `UNCLASSIFIED_BASE` / ambiguous evidence rather than forcing every consolidation into a named pattern.

## Next action

Proceed with **#28 — Breakout + Volume Confirmation**. Audit price-crossing semantics, close-versus-intraday requirements, breakout-day volume expectations/requirements, comparison window, breakout quality, gaps, and extension/chasing guidance. Only after #28 continue to #29–31 and then freeze #32.
