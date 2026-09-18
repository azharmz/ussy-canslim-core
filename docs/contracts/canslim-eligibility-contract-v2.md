# CAN SLIM Eligibility Contract v2

Date: 2026-09-18  
Status: **FROZEN FOR SHADOW IMPLEMENTATION DESIGN — NO v1 MUTATION**

Authority:
- `docs/decisions/2026-09-18-original-canslim-production-v2-contract.md`
- `docs/decisions/2026-09-18-canslim-v2-ca-source-lock.md`
- `docs/contracts/canslim-watchlist-contract-v2.md`
- `docs/methodology/oneil-theory-fidelity-audit-v1.md`
- `docs/methodology/theory-faithful-candidate-spec-v1.md`

## Purpose

Replace v1's semantically uniform seven-letter Boolean gate with a role-aware v2 eligibility boundary while preserving O'Neil/IBD concepts, explicit proxies, PIT causality, and the frozen #33 morphology contract.

This is not a performance-driven relaxation. No return/candidate-count result authorizes a gate.

## Preconditions

A stock reaches this contract only if:

1. it belongs to the canonical READY decision-date universe;
2. its v2 watchlist state is `QUALIFIED`;
3. C and A therefore passed the frozen v2 fundamental core;
4. frozen #33 has produced a valid recognized core pattern and structural pivot for the evaluated setup.

## Role matrix

| Component | v2 role | Hard eligibility effect |
|---|---|---|
| C | fundamental screen | already required upstream |
| A | fundamental screen | already required upstream |
| N | “new” evidence; price and non-price dimensions separated | price/setup evidence preserved; unavailable catalyst is not fabricated into FAIL |
| S | supply/demand evidence | strong breakout demand is required through breakout-volume confirmation; broader supply descriptors are evidence |
| L | individual leadership screen plus broader leadership evidence | individual L PASS/STRONG required; RS-line/industry evidence attached separately unless later source-locked |
| I | sponsorship evidence/quality/trend | attached PIT-safe evidence; not a universal hard veto in v2 |
| M | global market context and new-buy gate | must permit new buys at candidate/entry boundary |

## Hard eligibility path

For the first v2 shadow implementation:

```text
watchlist_state == QUALIFIED
AND pattern_state == RECOGNIZED
AND pivot_state == DEFINED
AND pivot_crossed == TRUE
AND breakout_volume_state == CONFIRMED_ON_BREAKOUT
AND L_individual_state in {PASS, STRONG}
AND M_entry_state == ALLOW_NEW_BUYS
```

Because watchlist `QUALIFIED` already means C PASS and A PASS, C/A are not recomputed here. Their evidence identity must still be carried into the candidate lineage.

## N semantics

N is not represented by one universal Boolean.

Persist separately:

```text
N_price_state
N_catalyst_state
N_evidence_reason
```

The recognized setup / price movement may provide price-based N evidence. A non-price catalyst that is unavailable remains `NOT_IMPLEMENTED` or `NOT_EVALUABLE`.

Do not claim `N_FULL_PASS` merely because price crossed a pivot.

For v2 shadow eligibility, unavailable non-price catalyst evidence does not automatically veto an otherwise valid price-pattern candidate.

## S semantics

Breakout demand is a timing requirement:

```text
volume_ratio = breakout_day_volume / mean(prior 50 completed-session volume)
CONFIRMED_ON_BREAKOUT when volume_ratio >= 1.40
```

This is the hard S-related demand confirmation in the initial v2 candidate path.

Broader supply descriptors remain evidence:

```text
shares_outstanding
float
buyback_state
accumulation_distribution_evidence
broader_supply_state
```

Do not invent a second universal S Boolean that duplicates the breakout-volume gate.

## L semantics

Individual leadership remains a hard screen using the already-authorized transparent RS proxy:

```text
L_individual_state in {PASS, STRONG}
```

with the current theory-faithful minimum corresponding to RS proxy percentile >=80.

Preserve separately:

```text
rs_line_state
rs_line_new_high_before_price
rs_line_bearish_divergence
industry_evidence_state
industry_group_strength
stock_rank_within_group
```

Do not fabricate proprietary IBD RS Rating or industry ranking. Any later hard gate based on RS-line/industry evidence requires a separately source-locked version before performance inspection.

## I semantics

Institutional sponsorship remains important CAN SLIM evidence, but the current PIT 13F representation is a narrow proxy for the full concept.

Persist:

```text
I_evidence_state
I_manager_count
I_manager_count_delta
I_period_of_report
I_available_at
I_source_identity
```

States may include:

```text
POSITIVE
NEUTRAL
NEGATIVE
NOT_EVALUABLE
NOT_IMPLEMENTED
```

Initial v2 does not require `I == POSITIVE` as a universal veto.

PIT causality remains mandatory. Missing/unmapped sponsorship must never become implicit positive evidence.

## M semantics

M is not a stock-level quality score.

Required final new-buy state:

```text
M_entry_state == ALLOW_NEW_BUYS
```

Market state is computed independently and referenced by immutable identity. A stock may remain on the watchlist or retain a valid setup while M blocks a new purchase.

If M is stale, missing, incompatible, or `NOT_EVALUABLE`, final eligibility fails closed.

## Candidate stages

```text
WATCHLIST_QUALIFIED
BASE_RECOGNIZED
PIVOT_DEFINED
PIVOT_CROSSED
BREAKOUT_CONFIRMED
CANSLIM_V2_ELIGIBLE
NOT_ELIGIBLE
NOT_EVALUABLE
```

Stages preserve chronology. A later stage never backdates an earlier event.

## Eligibility reason codes

At minimum:

```text
WATCHLIST_NOT_QUALIFIED
PATTERN_NOT_RECOGNIZED
PATTERN_AMBIGUOUS
PIVOT_UNDEFINED
PIVOT_NOT_CROSSED
BREAKOUT_VOLUME_UNCONFIRMED
L_SCREEN_FAIL
L_NOT_EVALUABLE
M_BLOCK_NEW_BUYS
M_NOT_EVALUABLE
M_STALE
INPUT_LINEAGE_MISMATCH
```

N catalyst, broader S and I evidence states are persisted as evidence/reasons but are not converted into artificial hard-failure codes for the initial v2 contract.

## Minimum lineage

Every v2 candidate must pin:

```text
security_id
decision_date
watchlist_identity/checksum
ready_key
ready_sha256
fundamental_source_identity
pattern_engine_version
pattern/base_id
leadership_source_identity
institutional_source_identity
market_state_identity
eligibility_contract_version = canslim-eligibility-contract-v2
producer_commit
producer_run
created_at
```

Resume/reuse fails closed if required identities are incompatible.

## Execution boundary

`CANSLIM_V2_ELIGIBLE` is a candidate state, not a historical fill.

Daily-EOD causality remains:

```text
decision information through T close
-> earliest executable production fill T+1 Open
```

The existing execution layer must separately verify temporal eligibility and extension/buy-zone constraints. A recovered historical candidate must never create a retroactive live entry.

## v1 comparison boundary

v1 remains frozen and continues to mean its existing deterministic seven-letter contract.

Never rewrite old `CANSLIM_ELIGIBLE` artifacts as if they were v2.

Shadow outputs must use explicit v2 versioning so both systems can be compared without semantic collision.

## Required tests before shadow publication

1. qualified watchlist + valid pattern + confirmed breakout + L pass + M allow -> eligible;
2. C/A cannot be bypassed because non-qualified watchlist cannot enter;
3. I negative/not-evaluable remains visible but does not silently veto initial v2;
4. N catalyst unavailable remains visible and is not mislabeled PASS;
5. breakout volume below threshold blocks;
6. L fail/not-evaluable blocks;
7. M correction/block/stale/not-evaluable blocks;
8. ambiguous/rejected pattern blocks;
9. lineage mismatch blocks resume/reuse;
10. repeated identical inputs produce deterministic logical output;
11. historical recovery cannot authorize a retroactive T+1 entry.

## Next implementation boundary

Implement v2 as a **shadow path beside v1**:

```text
freeze inputs
-> build/watchlist checkpoint
-> run frozen #33 only for qualified identities
-> evaluate role-aware v2 eligibility
-> validate
-> publish shadow artifacts
```

Do not cut over live Entry/Lifecycle until shadow semantic validation is complete and an explicit cutover decision exists.
