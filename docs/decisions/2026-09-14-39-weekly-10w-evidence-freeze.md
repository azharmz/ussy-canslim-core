# #39 Weekly Aggregation / 10-Week Evidence v1 — Freeze Decision

Date: 2026-09-14
Status: **WEEKLY AGGREGATION + 10W EVIDENCE COMPLETE / FROZEN v1**

## Decision

Freeze contract:

`39-weekly-10w-evidence-v1`

#39 implements completed-week aggregation and a true weekly 10-week evidence line without equating it to 50 daily sessions.

## Frozen weekly semantics

- weeks are partitioned by ISO `(year, week)`;
- the current ISO week is excluded until the data stream advances into a later ISO week;
- holiday-shortened weeks remain valid completed weeks;
- weekly OHLC uses first open, max high, min low, last close;
- weekly volume is the sum of component daily volumes only when all are available;
- `ma10w` is the mean of the latest 10 completed weekly closes;
- fewer than 10 completed weeks yields `NOT_EVALUABLE`;
- a break requires completed weekly close strictly below `ma10w`; equality is not a break;
- weekly volume ratio uses the latest completed week divided by the mean of the prior 10 completed-week volumes, excluding the latest week from the denominator;
- `>=1.40x` heavy-volume evidence remains an inherited project-consistent quantitative proxy, not a newly asserted universal O'Neil sell threshold;
- first-break chronology is preserved only when the prior completed week's 10-week state is evaluable;
- weekly evidence becomes available only after the completed week is known complete;
- no Friday-close hindsight execution is fabricated;
- MA50 daily is not treated as identical to the 10-week line;
- #39 does not promote a new canonical sell action.

## Canonical semantic validation

Workflow:

`.github/workflows/39-weekly-10w-v1.yml`

Canonical run:

- run `34788414986`
- job `103808042129`
- commit `2fa62e52c022e54bb2a85895cddb859eb0dd9ac6`
- result: **SUCCESS**
- tests: **10 passed in 0.04s**

No semantic/causal finding was observed.

## Governance consequence

#39 closes the weekly-data semantic gap left deliberately open by #38. It remains evidence-only.

Any promotion of a first decisive 10-week break, heavy-volume 10-week break, or other weekly deterioration state into a mandatory sell action requires a separate explicit action specification and validation. It must not be chosen from favorable historical performance.

Frozen upstream #33/#34/#35/#36/#37/#38, FWD1, EXH2 and P6 boundaries remain unchanged.
