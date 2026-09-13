# #37 Sell / Risk v1 — Freeze Decision

Date: 2026-09-14
Status: **IMPLEMENTATION COMPLETE / FROZEN v1**

## Scope

Freeze the initial theory-faithful sell/risk state machine downstream of frozen #36 entry execution.

This decision does not reopen or modify #33, #34, #35, #36, the frozen 60-case corpus, FWD1, EXH2, or P6 governance.

## Canonical contract

Specification:

`docs/methodology/37-theory-faithful-sell-risk-spec-v1.md`

Version:

`37-sell-risk-v1`

Implementation:

- `src/canslim_research/sell_risk_v1.py`
- `tests/test_sell_risk_v1.py`
- `.github/workflows/37-sell-risk-v1.yml`

## Frozen semantic boundaries

1. Practical ~7% capital-protection trigger references **actual fill price**.
2. Historical/legacy 8% level is preserved as ceiling/severity evidence, not a planned first trigger.
3. Gap-through the defensive trigger executes at the observed open rather than fabricating a stop-price fill.
4. A non-gap daily low crossing the practical trigger uses an explicit daily-OHLC mechanical stop convention.
5. Normal +20%-25% profit zone references the proper buy point/pivot.
6. Entering +20%-25% is profit-management evidence, not an automatic full liquidation rule.
7. Fast +20% within the first three weeks activates exceptional-winner/eight-week context; daily-data 15/40-session counts are implementation calendar conventions, not O'Neil terminology.
8. Round-trip remains evidence-only because no new unsupported numeric precondition was invented.
9. Climax/exhaustion remains not implemented canonically; EXH2 is not relabelled as #37.
10. Market-level exposure remains separate from stock-level sell action.

## Validation history

Initial run `34787869372` failed one boundary assertion because floating-point arithmetic represented exactly -7% slightly above `-0.07`.

Classification:

`IMPLEMENTATION NUMERIC-BOUNDARY BUG / NO SPEC CHANGE`

The classifier was corrected to compare observed price directly with the frozen 93%/92% price thresholds. No sell threshold, theory semantic, execution convention, or upstream contract changed.

Canonical semantic-validation run:

- run `34787905360`
- commit `ff052942f2ba7bafe6fa616b3883a6ad188ff8c1`
- result: **SUCCESS**
- tests: **10 passed**

## Governance verdict

`IMPLEMENTATION COMPLETE / FROZEN v1`

No trading-performance claim is made. This freeze validates semantics and causal execution boundaries only.

## Performance boundary

Performance research remains closed until separately preregistered. Any later study must not tune 7%, 8%, 20%-25%, 15-session, or 40-session conventions from realized returns.

Legacy `execution-exit-v1.md`, X1-X4/X3 and PORT1 remain frozen historical research. EXH2 remains separate prospective research.