# CAN SLIM Watchlist Contract v2

Date: 2026-09-18  
Status: **FROZEN FOR SHADOW IMPLEMENTATION DESIGN**

Authority:
- `docs/decisions/2026-09-18-original-canslim-production-v2-contract.md`
- `docs/decisions/2026-09-18-canslim-v2-ca-source-lock.md`

## Purpose

Define the first per-stock production selection boundary before expensive #33 morphology work.

This contract does not alter frozen v1.

## Identity

Each watchlist assessment is identified by:

```text
security_id
decision_date
ready_key
ready_sha256
fundamental_snapshot_identity
contract_version = canslim-watchlist-contract-v2
```

Symbol is descriptive/as-of metadata, not canonical identity.

## Required inputs

For each security:

- canonical READY membership for the decision date;
- PIT-safe C evidence;
- PIT-safe A evidence;
- available leadership/evidence inputs where attached;
- explicit source lineage.

No future filing or later amendment may be visible before its allowed information-availability timestamp.

## Stage 1 — fundamental core

```text
C_state == PASS
AND
A_state == PASS
```

is required to enter the v2 CAN SLIM stock watchlist.

C v2:

```text
latest quarterly EPS YoY >= 25%
AND latest quarterly revenue/sales YoY >= 25%
```

A v2:

```text
latest three required annual EPS YoY observations
are evaluable
AND each >= 25%
```

Missing/undefined required evidence yields `NOT_EVALUABLE`, never implicit zero.

## Stage 2 — watchlist evidence

The watchlist record may attach:

- L individual RS proxy / RS-line evidence;
- N price/catalyst evidence;
- broader S supply/demand evidence;
- I institutional sponsorship evidence;
- industry evidence;
- M reference identity.

These fields do not alter the Stage-1 fundamental identity unless a separately versioned role-aware contract explicitly authorizes a gate.

For the first shadow implementation, L should be calculated/attached before #33 so the next eligibility layer can apply the already-authorized individual leadership screen without rerunning upstream data work.

## States

```text
QUALIFIED
C_FAIL
A_FAIL
C_NOT_EVALUABLE
A_NOT_EVALUABLE
INPUT_NOT_EVALUABLE
```

Reason codes must preserve all applicable causes rather than only the first failure.

## Output minimum schema

```text
security_id
symbol_asof
decision_date
watchlist_state
reason_codes

C_state
C_quarter
C_eps_yoy
C_revenue_yoy
C_available_at

A_state
A_periods
A_growth_values
A_available_at

L_state
rs_proxy_percentile
N_price_state
N_catalyst_state
S_evidence_state
I_evidence_state
M_state_reference

ready_key
ready_sha256
fundamental_source_identity
institutional_source_identity
market_state_identity
contract_version
producer_commit
producer_run
created_at
```

Fields unavailable from current upstream contracts remain explicit null + state/reason; they must not be fabricated.

## Publication/checkpoint

The qualified watchlist is a durable recovery boundary before #33.

A reusable checkpoint must pin:

- READY key + SHA;
- fundamental source identity;
- decision date;
- contract version;
- producer commit/run;
- row count;
- qualified count;
- content checksum.

Resume fails closed if any pinned identity is incompatible.

## Idempotency

Same input lineage + same contract version + same decision date must produce the same logical watchlist.

A second run must reuse/no-op or verify identical content rather than create competing canonical watchlists.

## Downstream boundary

Only `QUALIFIED` securities enter the CAN SLIM v2 critical-path #33 morphology evaluation.

This does not prevent the separate Pattern Intelligence service from scanning the full universe periodically.

## Market M

M is global context and may be computed before this stock-level screen. A stock can be placed on the watchlist while M blocks new buys; final Candidate/Entry remains blocked until the role-aware eligibility/entry contract permits it.

## Non-goals

This contract does not:

- define a trade;
- define a pattern;
- define a pivot;
- authorize an entry;
- change #33;
- make I a universal veto;
- claim N catalyst implementation;
- change v1 production;
- use returns to tune the watchlist.

## Acceptance before shadow compute

Implementation must have tests for:

1. C PASS + A PASS -> QUALIFIED.
2. C FAIL -> not qualified.
3. A FAIL -> not qualified.
4. missing C/A -> NOT_EVALUABLE path.
5. PIT cutoff prevents future filings.
6. same lineage is deterministic/idempotent.
7. lineage mismatch fails closed on resume.
8. only QUALIFIED identities are handed to #33.
