# #40 Technical Deterioration Action v1 — Freeze Decision

Date: 2026-09-14
Status: **IMPLEMENTATION COMPLETE / FROZEN v1**

## Decision

Freeze canonical action contract:

`40-technical-deterioration-action-v1`

#40 promotes one narrowly defined weekly deterioration condition into a canonical stock-level exit without modifying #37's universal capital-protection rule.

## Frozen trigger

A completed week is actionable only when:

```text
weekly close < frozen 10-week moving average
AND
weekly volume > mean(volume of prior 10 completed weeks)
```

Equivalent frozen quantitative condition:

```text
break_10w_state == TRUE
AND weekly_volume_ratio_prior10 > 1.00
```

Equality to the moving average is not a break. Equality to average weekly volume is not above-average volume.

A low-volume close below the 10-week line remains deterioration evidence but does not force the #40 action.

## Chronology and execution

- the first completed week satisfying the full trigger is the signal week;
- earlier non-actionable low-volume breaks do not consume the later action opportunity;
- the weekly signal becomes known only after that week completes;
- no fill is backdated into the signal week;
- canonical execution is the first observed trading session after the completed signal week;
- fill price is that session's observed open;
- if no later trading-session bar exists, state remains `NO_NEXT_SESSION_BAR`;
- no synthetic MA-level, Friday-close, weekend, or intraday fill is created.

Execution source:

`DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_WEEK`

## Relationship to #37

The frozen #37 practical ~7% capital-protection rule remains independent and may produce an earlier causal exit. #40 does not delay, override, retune, or rewrite #37 thresholds or prior fill history.

For a complete position lifecycle, the earliest causal exit among frozen action contracts governs; that lifecycle arbitration is downstream from this isolated #40 action module.

## Canonical semantic validation

Workflow:

`.github/workflows/40-technical-deterioration-action-v1.yml`

Canonical run:

- run `34789559782`
- job `103811139345`
- commit `b5d8dd488ea8eb5df5d00fff039a6ddc146f6c7b`
- result: **SUCCESS**

The A40 semantic boundary suite passed, covering price/volume boundaries, missing evidence, low-volume non-actionability, later actionable-break chronology, next-session causality, observed-open execution, lineage, and no backdating.

## Governance consequence

#40 is frozen before any performance comparison. Historical returns may not be used to retune the `close < ma10w` or `volume_ratio_prior10 > 1.00` conditions.

#38's daily `>=1.40x` heavy-volume evidence proxy remains separate and is not substituted for the weekly above-average-volume action rule.

Frozen #33/#34/#35/#36/#37/#38/#39, FWD1, EXH2, and P6 boundaries remain unchanged.
