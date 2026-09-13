# #38 Technical Deterioration Evidence v1 — Freeze Decision

Date: 2026-09-14
Status: **EVIDENCE LAYER COMPLETE / FROZEN v1**

## Decision

Freeze contract:

`38-technical-deterioration-evidence-v1`

#38 implements reproducible daily technical-deterioration evidence downstream of frozen #37 without promoting a new mandatory sell action.

## Frozen evidence semantics

- MA10 = current completed close + prior 9 completed closes.
- MA21 = current completed close + prior 20 completed closes.
- MA50 = current completed close + prior 49 completed closes.
- break requires `close < MA`; equality is not a break.
- missing required history remains `NOT_EVALUABLE`.
- `volume_ratio_50` uses current volume divided by the mean of the **prior 50 completed sessions**, excluding current volume from the denominator.
- heavy-volume break evidence requires the corresponding break plus `volume_ratio_50 >= 1.40`.
- the 1.40 boundary is classified as a project-consistent quantitative evidence proxy inherited from the frozen volume convention, not a newly asserted universal O'Neil sell threshold.
- largest down-volume evidence is preserved descriptively since breakout.
- below-pivot evidence references pivot; loss evidence references actual fill.
- 10-week break remains explicitly `NOT_IMPLEMENTED_REQUIRES_WEEKLY_AGGREGATION_SPEC`; 50 daily sessions are not silently declared identical to 10 calendar weeks.
- all close/volume/MA evidence is known only after the daily session closes.
- action promotion remains `EVIDENCE_ONLY_NO_CANONICAL_SELL_ACTION`.

## Canonical semantic validation

Workflow:

`.github/workflows/38-technical-deterioration-v1.yml`

Canonical run:

- run `34788119495`
- job `103807226405`
- commit `3b7a25ead2590cf62b330420553df29cfc9d2dcf`
- result: **SUCCESS**
- tests: **12 passed in 0.04s**

No semantic/causal finding was observed.

## Governance consequence

#38 is frozen as an evidence layer only. It does not alter #37's practical ~7% capital-protection action, and it does not authorize historical-return tuning or a mandatory MA-based exit.

Any promotion of a 50d/10w deterioration state into a canonical sell action requires a separate explicit action specification and validation. A faithful 10-week implementation first requires a completed-week aggregation specification.

Frozen upstream #33/#34/#35/#36/#37, FWD1, EXH2 and P6 boundaries remain unchanged.
