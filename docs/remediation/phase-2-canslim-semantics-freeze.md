# Phase 2 — CAN SLIM C/A/N/S/L/I/M Semantics Freeze

Status: FROZEN FOR REMEDIATION
Contract: `canslim-eligibility-contract-v1`
Scope: correctness/integration only. No threshold tuning, no new proxy invention, no strategy expansion.

## Canonical letter matrix

| Letter | Production evidence | PASS state for full eligibility | Missing / NOT_EVALUABLE | Mandatory? | Notes |
|---|---|---|---|---|---|
| C | Frozen C-v1 quarterly SEC PIT fundamentals | `PASS` | blocks | YES | EPS YoY **and** revenue YoY must both be evaluable and >=25%. |
| A | Frozen A-v1 annual SEC PIT fundamentals | `PASS` | blocks | YES | Latest three consecutive annual EPS YoY states must each be evaluable and >=25%. `PASS_3Y_FALLBACK` remains separate provenance and is not silently collapsed into canonical PASS. |
| N | Frozen price/new-high breakout evidence already present in candidate path | `PASS` | blocks | YES | `N_price_state` is the canonical v1 production N gate. `N_catalyst_state` remains separate evidence and may remain `NOT_IMPLEMENTED`; no catalyst proxy may be invented during remediation. |
| S | Frozen breakout-volume / supply-demand evidence | `POSITIVE` | blocks | YES | Confirmed breakout-volume evidence is the production v1 S gate. |
| L | Frozen individual leadership state | `PASS` or `STRONG` | blocks | YES | No threshold retuning during remediation. |
| I | Canonical PIT institutional sponsorship | `POSITIVE` | blocks | YES | Must be wired from governed institutional source in Phase 3. `NOT_EVALUABLE` cannot yield full eligibility. |
| M | Canonical governed market-entry state | `ALLOW_NEW_BUYS` | blocks | YES | Phase 4 replaces local proxy/recalculation with the governed M input. |

## N audit conclusion

Existing candidate logic already produces a price/new-high breakout fact: a recognized frozen #33 pattern with a defined pivot must cross the pivot on the first tradeable daily bar after structure. That evidence is already assigned to `N_price_state = PASS` when the first valid pivot cross occurs.

Therefore remediation does **not** create a new N catalyst detector. For v1:

- `N_price_state` = canonical mandatory N gate;
- `N_catalyst_state` = separate evidence channel only;
- `N_catalyst_state = NOT_IMPLEMENTED` must be explicit and must not be converted into PASS;
- future catalyst work requires a separate evidence/governance cycle and is outside this remediation.

This preserves the existing governed breakout semantics while avoiding a new proxy solely to make the acronym complete.

## Current implementation mismatches discovered during Phase 2

The current #34 adapter is not fully aligned with frozen C/A semantics:

1. C adapter currently evaluates quarterly EPS YoY alone. Frozen C-v1 requires both EPS YoY and revenue YoY.
2. A adapter currently computes a four-point / three-year CAGR. Frozen A-v1 requires the latest three consecutive annual EPS YoY states, each >=25%.
3. Candidate eligibility currently hard-gates only C/A/L/M after volume confirmation. It does not yet hard-gate N/S/I according to this contract.
4. I is present as an evidence field but is not yet prospectively wired into the production candidate path.
5. M in the smoke consumer is locally reconstructed; it must later consume the canonical governed M source.

These are correctness/integration mismatches. They are not permission to change thresholds or reinterpret the frozen strategy.

## Freeze rules

- Missing is never zero.
- `NOT_EVALUABLE`, `NOT_IMPLEMENTED`, `UNKNOWN`, or absent mandatory evidence fails closed for full `CANSLIM_ELIGIBLE`.
- No mandatory letter can be inferred from another letter's PASS state.
- `N_catalyst_state` and `industry_evidence_state` are not substitutes for missing canonical mandatory inputs.
- No post-hoc threshold tuning is allowed during remediation.
- The four frozen #33 patterns and their morphology contract remain untouched.

## Phase 2 exit verdict

The semantic contract is frozen. Code integration remains intentionally deferred to the designated remediation phases:

- C/A correctness: remediation correctness work under F03/F05 before final eligibility gate.
- I prospective wiring: Phase 3.
- canonical M and dependency pinning: Phase 4.
- final `CANSLIM_ELIGIBLE` enforcement of all mandatory letters: Phase 5.
