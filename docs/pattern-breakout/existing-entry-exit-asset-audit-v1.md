# Pattern Breakout Core v1 — Existing Asset Audit

Audit target: existing O'Neil/CAN SLIM technical entry and exit machinery on `main`.

## Executive result

Reuse infrastructure and already-frozen technical semantics selectively. Do not inherit CAN SLIM eligibility or TrendFoll decision logic.

| Existing asset | Decision | Pattern Breakout treatment |
|---|---|---|
| `ussy-oneil-patterns` frozen engine | REUSE | Canonical morphology/landmarks/pivot dependency unchanged |
| `execution_entry_v1.py` | EXTRACT/ADAPT | Reuse causal T+1 and buy-zone mechanics only after removing CANSLIM stage coupling |
| `execution_entry_v2.py` | DO NOT REUSE DIRECTLY | CAN SLIM v2 stage adapter only |
| `sell_risk_v1.py` | PARTIAL REUSE AFTER SOURCE LOCK | Capital-protection/profit-zone/eight-week evidence is useful; incomplete technical/climax fields must remain explicit |
| `technical_deterioration_v1.py` | EVIDENCE REUSE CANDIDATE | Daily MA/volume deterioration evidence; not itself a sell action |
| `technical_deterioration_action_v1.py` | PARTIAL REUSE AFTER SOURCE LOCK | 10-week break + volume action is causal but needs Pattern Breakout-specific provenance acceptance |
| `round_trip_action_v1.py` | PARTIAL REUSE AFTER SOURCE LOCK | Technical round-trip rule and causal next-open action are separable from fundamentals |
| `position_lifecycle_v2.py` | REUSE ARBITRATION PATTERN, NOT NAME/CONTRACT | Earliest executable exit and same-session ambiguity handling are valuable engineering semantics |
| `publish_production_entries.py` | INFRASTRUCTURE REFERENCE ONLY | R2 lineage, timeliness and no-retroactive-fill patterns useful; CAN SLIM namespace/schema not reusable |
| `publish_production_lifecycle.py` | DO NOT REUSE AS PRODUCT PUBLISHER | CAN SLIM production guard/namespace; Pattern Breakout needs independent namespace |
| TrendFoll strategy rules | REJECT AS METHODOLOGY SOURCE | No methodological dependency |

## Entry audit

### Reusable

`execution_entry_v1.py` already provides:

- causal next-session open;
- structural pivot as buy-zone floor;
- +5% buy-zone ceiling;
- `MISSED_EXTENDED_AT_OPEN`;
- `BELOW_PIVOT_AT_OPEN`;
- no inferred later/retest fill;
- actual observed T+1 Open as fill;
- validator for causal date, observed fill and buy-zone boundary.

### Must be decoupled

The current function only executes when `candidate_stage == CANSLIM_ELIGIBLE`.

Pattern Breakout must never translate a technical candidate into a fake CAN SLIM stage merely to reuse this function.

Required implementation: a Pattern Breakout-specific adapter/contract whose accepted upstream stage is `TECHNICAL_BREAKOUT_CANDIDATE`, while preserving frozen T+1 mechanics only where source-locked.

### Publisher lessons to reuse

`publish_production_entries.py` has valuable engineering behavior:

- immutable candidate/source lineage;
- exact READY hash validation;
- candidate publication timeliness check before T+1 open;
- no retroactive fill for late recovery;
- current READY used to observe a later T+1 bar.

These are ENGINEERING semantics, not O'Neil rules.

## Exit audit

### sell_risk_v1

Useful implemented evidence includes:

- 7% practical loss trigger from actual fill;
- 8% legacy hard-loss ceiling from actual fill;
- 20–25% normal profit zone referenced to pivot/buy point;
- fast +20% / eight-week-hold evidence;
- below-pivot state.

Important boundaries already present:

- technical deterioration was explicitly not fully implemented in this module;
- climax remains explicitly not implemented;
- unsupported round-trip numeric trigger is rejected.

Therefore do not treat `sell_risk_v1` as a complete Pattern Breakout exit engine.

### technical_deterioration_v1

Evidence-only layer calculates:

- 10D/21D/50D MA breaks;
- volume ratio against prior 50 sessions;
- heavy-volume MA breaks;
- largest down-volume observation since breakout;
- return below pivot.

It explicitly refuses to promote those observations to a canonical sell action. Preserve that separation.

### technical_deterioration_action_v1

Promotes one weekly condition:

`weekly close < 10-week MA AND weekly volume > prior-10-week average`

to a causal next-session-open exit.

This is potentially reusable, subject to source-lock verification.

### round_trip_action_v1

Implements:

- prior double-digit gain from buy point;
- later close back at/below pivot;
- causal next-session-open exit;
- same-session ambiguity if first +10% gain and return to pivot occur in the same daily bar.

Potentially reusable, subject to source-lock verification.

### position_lifecycle_v2

The arbiter is useful as an engineering pattern:

- no entry -> NOT_OPENED;
- no executable exit -> OPEN;
- earliest executable exit wins;
- same observed-open convergence is recognized;
- source conflicts fail closed;
- unknown same-session ordering remains ambiguous.

Pattern Breakout should create its own lifecycle contract/version rather than silently adopting CAN SLIM lifecycle identity.

## Gaps before coding

1. Freeze authoritative source for breakout-volume threshold and denominator.
2. Freeze authoritative source for 5% buy zone.
3. Freeze authoritative source for 7–8% defensive loss rule.
4. Freeze authoritative source for 20–25% profit zone and eight-week exception.
5. Verify the 10-week technical-deterioration action against authoritative IBD/O'Neil material.
6. Verify round-trip-to-buy-point action against authoritative material.
7. Decide whether climax/abnormal action is sufficiently specifiable for Core v1; otherwise leave UNAVAILABLE/DEFERRED.
8. Define Pattern Breakout namespace/schema/stages independent of CAN SLIM.

## Coding recommendation after source lock

Minimal new code:

- `pattern_breakout_entry_v1.py`: technical-candidate T+1 adapter/contract;
- `pattern_breakout_exit_v1.py`: compose only source-locked technical exit channels;
- `pattern_breakout_lifecycle_v1.py`: independent lifecycle identity using fail-closed arbitration;
- tests proving no CAN SLIM/fundamental dependency and no max-hold/time exit.

Do not build Weinstein/VCP in this branch.
