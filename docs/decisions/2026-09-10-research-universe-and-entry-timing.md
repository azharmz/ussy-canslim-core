# Decision — Research Universe and Entry Timing

Date: 2026-09-10

## Research universe

The primary historical research universe is the set of securities in the selected **current/contemporary Musaffa-compliant snapshot**, frozen for reproducibility.

Historical Musaffa compliance is not a strategy input for this research question. Therefore the absence of historical membership snapshots is **not a blocker** to studying historical CAN SLIM behavior on today's frozen compliant universe.

The resulting evidence must be described precisely as historical behavior of the frozen current-compliant research universe. It must not be described as a reconstruction of the universe that would have been known compliant at each historical date.

Point-in-time discipline remains mandatory for information that actually drives the historical decision: OHLCV/market state through T0 and SEC facts only after `accepted_at`.

## Daily-EOD execution

The breakout and complete T0 volume are only known after T0 close. Therefore T0-close entry is not an executable assumption for the daily-EOD pipeline. T+1 Open is the earliest clean executable control, but it is not assumed to be the optimal entry rule.

## Basis test

Pre-specified variants:

- X1: valid T+1 Open only;
- X2: first valid Open during T+1..T+3;
- X3: full-bar pivot-hold confirmation on T+1/T+2, then next valid Open by T+3;
- X4: near-pivot retest-and-hold confirmation on T+1/T+2, then next valid Open by T+3.

All variants retain identical exit/risk rules so the comparison isolates entry timing. Close-based confirmation can only be executed at the following Open.

X3/X4 parameters are pre-specified before comparative review and must not be tuned from the same basis-test result.
