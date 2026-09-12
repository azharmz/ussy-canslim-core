# Decision — Theory Fidelity Audit and dedicated O'Neil Pattern Recognition Engine

Date: 2026-09-12
Status: ACCEPTED

## Decision

The post-v1 CAN SLIM research path is theory-first. Quantitative v1 remains frozen as the completed legacy research stack; its 10,731 historical candidates are not assumed to be faithful O'Neil/CAN SLIM candidates.

Theory Fidelity Audit (#25) is the parent workstream. Current child status:

- #26 Proper Base — COMPLETE (theory audit)
- #27 Pivot / Buy Point — COMPLETE (theory audit)
- #28 Breakout + Volume — NEXT
- #29 RS / Leadership — pending
- #30 C/A/S/I/M role fidelity — pending
- #31 Sell / Risk Management — pending

After #25 is complete, freeze #32 Theory-Faithful Candidate Specification before any implementation.

## Dedicated implementation workstream

Create a distinct workstream:

**#33 — O'Neil Pattern Recognition Engine**

It owns reproducible quantification of O'Neil base morphology from the existing daily OHLCV R2 data, including base segmentation, landmarks, CWH, cup-without-handle, double bottom, flat base, ascending base, base-on-base relationships, faulty-base flags, ambiguity/confidence, and morphology validation.

This separates two questions:

1. `ussy-canslim-research`: What does O'Neil/IBD theory require?
2. Pattern engine: Can the frozen specification be recognized reproducibly from OHLCV?

The engine must not be trained/tuned against CAGR, PF, FWD1 outcomes, or other trading-performance outcomes to decide what constitutes a pattern. Initial validation is pattern/landmark fidelity against preregistered definitions and labelled fixtures.

## Renumbering

The implementation tail is now:

- #32 Theory-Faithful Candidate Specification
- #33 O'Neil Pattern Recognition Engine
- #34 Theory-Faithful Candidate Generator
- #35 New-Candidate Validation
- #36 Execution / Entry Research (parked until candidate validity is established)

## Frozen theory findings so far

### #26 Proper Base

v1 `generic prior-35-session base proxy` is classified overall as **WEAK_PROXY** for O'Neil proper-base identification. Pattern morphology, prior uptrend, pattern-specific duration/depth, handles, W landmarks, tightness, base history, and faulty-base semantics are materially missing.

### #27 Pivot / Buy Point

The structural pivot is pattern-specific. CWH uses the handle high; cup-without-handle uses prior/left-side high; double bottom uses the middle W peak; flat base uses base/left-side high; ascending base uses final/pattern structural resistance; base-on-base inherits the pivot of its second-base morphology.

The historical fixed-price buffer above resistance is legacy methodology. The 5% buy zone is an execution/anti-chasing concept and is not the pivot itself. Whether v1 `T0 close > pivot` is faithful breakout confirmation is deferred to #28.

## Non-effects

This decision does not alter:

- FWD1 frozen v1 semantics;
- EXH2;
- historical v1 results;
- X1-X4/X3 results;
- PORT1;
- C/A/I/M historical ablation verdicts.

No coding or pattern-engine implementation is authorized by this decision. The next research action is #28.
