# #42 Round-Trip Sell Action v1 — Freeze Decision

Date: 2026-09-14
Status: **IMPLEMENTATION COMPLETE / FROZEN v1**

Contract: `42-round-trip-sell-action-v1`

## Authoritative resolution

The previously unresolved #37 numeric precondition is now supported by authoritative IBD evidence: the round-trip rule applies after a stock has produced a double-digit gain from the ideal/proper buy point and then gives that gain back toward/below the buy point.

#42 operationalizes the lower bound of double-digit gain as +10% from the pivot. This threshold is theory-derived, not performance-selected.

## Frozen semantics

- reference is the proper buy point / pivot, not actual fill;
- qualifying prior gain requires `prior_max_high >= pivot * 1.10`;
- the gain must occur on a completed session strictly before the trigger session;
- canonical reproducible trigger is later completed daily close `<= pivot`;
- no numeric near-pivot band is invented;
- if the first +10% high and return-to/below-pivot close occur on the same daily bar, state is `AMBIGUOUS_SAME_SESSION` because OHLCV does not establish intraday ordering;
- actionable completed-close trigger executes at the first later observed session open;
- missing next bar remains `NO_NEXT_SESSION_BAR`;
- #37 practical ~7% capital protection is unchanged;
- frozen #41 v1 is not mutated; integration of #42 requires a later lifecycle version.

## Validation history

Initial run `34793309984` failed one exact-boundary test because binary floating-point represented +10% slightly below the literal threshold. This was classified as an implementation numeric-boundary defect only; no theory or specification change was made.

Fix commit `8685869e0030abd55b9082c9c8c922f0d747b835` introduced only a tiny numeric comparison tolerance at the already frozen +10% boundary.

Canonical run:
- run `34793348883`
- job `103821631323`
- commit `8685869e0030abd55b9082c9c8c922f0d747b835`
- result: **SUCCESS**
- tests: **10 passed in 0.03s**

## Governance consequence

Round-trip is no longer merely `EVIDENCE_ONLY / NOT_FULLY_IMPLEMENTED`; #42 provides a separately frozen executable action contract. No performance claim is made and no historical-return tuning is authorized.
