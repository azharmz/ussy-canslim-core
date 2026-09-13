# #36 Execution / Entry v1 — Start and Implementation Record

Date: 2026-09-14
Status: IMPLEMENTED / SEMANTIC VALIDATION PENDING

## Governance boundary

#36 opened only after #35 terminal freeze. #33, #34, #35, the frozen 60-case corpus, and P6 production exclusion remain unchanged.

Canonical upstream contract remains:

```text
#33 pattern/pivot -> #34 candidate/qualification -> #35 validation -> #36 execution
```

## Frozen #36 v1 baseline

Specification: `docs/methodology/36-execution-entry-spec-v1.md`

Version: `36-execution-entry-v1`

The canonical baseline is intentionally narrow:

```text
CANSLIM_ELIGIBLE at T
-> information available after T close
-> first causal executable session = T+1
-> execute at observed T+1 open iff pivot <= open <= pivot * 1.05
```

States outside that range are preserved without fabricated fills:

- above +5%: `MISSED_EXTENDED_AT_OPEN`;
- below pivot: `BELOW_PIVOT_AT_OPEN`;
- no next bar: `NO_NEXT_SESSION_BAR`;
- upstream stage below CANSLIM_ELIGIBLE: `NOT_ENTRY_ELIGIBLE`.

No same-day hindsight fill, arbitrary T+2/T+3 waiting window, retest band, or performance-selected rule is included.

## Risk-reference semantics carried from #31

For an executed position:

- stop reference = actual fill price;
- practical defensive trigger = ~7% below actual fill;
- legacy hard-loss ceiling = 8% below actual fill;
- normal +20%-25% profit zone remains referenced to the proper buy point/pivot, not silently to fill.

These fields are recorded as execution/risk references; this is not yet the full sell engine.

## Implementation

Added:

- `src/canslim_research/execution_entry_v1.py`
- `tests/test_execution_entry_v1.py`
- `.github/workflows/36-execution-entry-v1.yml`

Boundary tests cover:

- open exactly at pivot;
- open just above pivot;
- open exactly +5%;
- open above +5%;
- gap within buy zone;
- open below pivot;
- missing T+1 bar;
- non-eligible upstream candidate;
- actual-fill stop reference;
- pivot-referenced profit zone;
- rejection of noncausal fill dates.

A direct semantic logic check was also performed after implementation and passed the frozen boundary cases. GitHub Actions has not yet produced a terminal run for the newly added workflow, so this record does **not** classify #36 as validation-complete or frozen implementation.

## Next gate

Before performance research:

1. obtain terminal semantic-validation run;
2. require zero E36-A..F semantic findings;
3. record implementation freeze only after validation is green;
4. only then consider preregistered delayed/retest execution variants or performance comparison.

Trading returns, CAGR, PF, and win rate are not implementation acceptance criteria.
