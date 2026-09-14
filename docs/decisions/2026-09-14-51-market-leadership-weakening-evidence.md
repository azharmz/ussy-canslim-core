# Decision — #51 Market Leadership / Weakening Evidence

Date: 2026-09-14

## Verdict

**EVIDENCE CONTRACT COMPLETE / PRODUCTION BOOLEAN SOURCE DEFERRED**

Frozen contract: `51-market-leadership-weakening-evidence-v1`.

## Decision

Authoritative O'Neil/IBD evidence is sufficient to establish that general-market interpretation should use the behavior of market-leading stocks alongside major-index price/volume action. Constructive evidence includes new leaders moving to new highs with institutional demand; deterioration evidence includes a majority of leaders ceasing to make new highs/breaking down together with institutional selling.

The public authoritative evidence reviewed does not justify inventing a universal quantitative algorithm for selecting a broad-market leader cohort or thresholds for breakout counts, RS, breadth, moving averages, or lookbacks.

Therefore:

1. #51 freezes a tri-state evidence aggregation boundary (`True` / `False` / `NOT_EVALUABLE`).
2. A broad-market cohort and PIT provenance are mandatory.
3. The current restricted USSY/Musaffa universe may not be silently used as broad-market leadership evidence.
4. Future winners/returns may not define leaders retrospectively.
5. Missing required evidence remains `NOT_EVALUABLE`.
6. Frozen #46 and #45 semantics remain unchanged.
7. Production #50 must continue supplying `None` for `leadership_confirming` and `weakening_confirmed` until a separately versioned broad-market PIT producer satisfies #51.

## Implementation

- `docs/methodology/51-market-leadership-weakening-evidence-v1.md`
- `src/canslim_research/market_leadership_evidence_v1.py`
- `tests/test_market_leadership_evidence_v1.py`

## Preserved debt / next work

The remaining gap is **data-source/producer validation**, not semantic threshold tuning. A future workstream must establish a reproducible PIT broad-market leadership cohort and evidence producer before #50 may populate the frozen #46 auxiliary booleans.