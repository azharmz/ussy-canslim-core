# CAN SLIM v2 — Production Cutover Gate

Date: 2026-09-21  
Status: **CUTOVER APPROVED IN PRINCIPLE / PUBLISHER NOT YET AUTHORIZED**

## Decision

The v2 methodology and shadow critical path are accepted as the successor architecture to frozen v1. This decision does **not** silently turn the current shadow workflow into a live publisher.

Frozen v1 remains immutable historical/audit baseline. Production replacement requires a separately implemented and regression-tested v2 publisher with atomic pointer semantics and rollback.

## Evidence at the gate

Verified shadow run: `35592806075`. Decision date: `2026-09-18`.

```text
canonical READY
-> PIT C/A watchlist
-> 3 QUALIFIED identities out of 1,225 READY securities
-> promoted #33 production contract (33-core-p8-frozen-v2)
-> role-aware candidate evaluation
-> T+1 execution boundary
-> lifecycle boundary
```

Observed: READY 1,225; C/A qualified 3; #33 input exactly those 3; #33 assessments 1,464; PIVOT_DEFINED 757; BREAKOUT_CONFIRMED 8; CANSLIM_V2_ELIGIBLE 3; T+1 decisions 3; NO_NEXT_SESSION_BAR 3; NOT_OPENED 3; production write false.

Artifact id: `10636010460`. Digest: `sha256:f7d4a76defeab3223543dcebf415b6f9dd4a5c3a7f91aadf4b33677201688935`.

## #33 dependency

v2 consumes canonical #33 production SHA `3d0b35272d89c5a6f1329e8dea865b3cf7a32b0f` with engine `33-core-p8-frozen-v2`. The consumer remains backward-compatible with frozen v1 records for audit/history; this is not permission to mix engine versions inside one canonical production lineage.

## Defects closed by cutover rehearsal

1. v2 candidate consumer rejected the promoted `33-core-p8-frozen-v2` contract.
2. candidate publication used stale lineage key `fundamental_snapshot_identity` instead of canonical `fundamental_source_identity`.
3. T+1 shadow execution referenced the per-security frame before initialization.

The final verified run completed watchlist, #33, candidate, execution, lifecycle, summary, and artifact upload successfully.

## Production publisher requirements

Before live cutover, implement one dedicated v2 publisher. It must consume only a completely successful v2 run; validate READY/fundamental/#33/market/institutional lineage; fail closed on mixed contracts; publish immutable run artifacts before moving any canonical pointer; move the v2 pointer atomically; never synthesize retroactive T+1 fills; preserve the prior pointer as rollback target; be idempotent; expose producer commit/run, decision date and digest; and prove by dry-run/contract test that upstream failure cannot mutate production.

## Explicit non-changes

This gate does not alter C/A thresholds, L threshold, breakout-volume threshold, M semantics, #33 morphology, T+1 Open semantics, lifecycle rules, or frozen v1 artifacts. No rule is changed from shadow results or candidate counts.

## Cutover sequence

```text
shadow-success evidence
-> publisher contract + tests
-> dry-run against frozen shadow artifact
-> atomic v2 publish
-> verify canonical readback + lineage
-> retain v1 as frozen rollback/audit baseline
```

Until that sequence is complete, v2 remains shadow and must not be described as live production.
