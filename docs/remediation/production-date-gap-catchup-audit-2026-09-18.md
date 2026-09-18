# CAN SLIM Production Date-Gap / Catch-Up Audit — 2026-09-18

Status: **CLOSED / VERIFIED**

## Incident and root cause

Canonical `ussy-data` READY 2026-09-17 existed while downstream Candidate history visibly stopped at 2026-09-16. The cadence gate compared only `production/ready/current.json` with `canslim/candidates/current.json`, while the Candidate publisher always consumed READY current. There was no durable concept of the earliest unresolved immutable READY date. With multiple READY sessions accumulated after a production failure, an intermediate required date could therefore be silently skipped.

Classification: **MISSING CATCH-UP + POINTER SEMANTICS**. Frozen trading semantics are unchanged.

## Candidate contract and recovery

`canslim/candidates/snapshots/YYYY-MM-DD/run-*` is a Candidate decision/as-of session date. One canonical Candidate snapshot per required finalized READY trading date is the invariant; zero eligible candidates still produces a canonical assessment.

The orchestrator now enumerates immutable `production/ready/runs/YYYY-MM-DD.parquet` objects up to authoritative READY current and selects the earliest unresolved date greater than Candidate current. That immutable key and expected date are passed explicitly to the Candidate publisher. The publisher validates the actual terminal date against the expected date and records the selected immutable key in READY lineage. Upstream READY immutability is untouched.

## No retroactive Entry

Historical completeness and live execution eligibility are separate. Intermediate catch-up does not run Entry/Lifecycle. In addition, Entry now requires Candidate `updated_at` to precede the first available T+1 09:30 America/New_York open. A Candidate reconstructed after that open returns `LATE_RECOVERY_NO_RETROACTIVE_ENTRY` and cannot authorize a hindsight order.

## Institutional Sponsorship contract

The `ussy-fundamentals` publisher names institutional snapshots from `datetime.now(timezone.utc)` and records source history/uncertainty/live run identities plus exact EDGAR `accepted_at` semantics. Thus `institutional_sponsorship/snapshots/YYYY-MM-DD/` is an **evidence publication/version date**, not a required CAN SLIM decision-date materialization.

A missing physical institutional 2026-09-17 directory is therefore not, by itself, a production hole. Candidate decisions reuse the applicable PIT evidence through the decision cutoff. No synthetic institutional 2026-09-17 snapshot is authorized.

## Changed surfaces

- `.github/workflows/remediation-phase9-e2e-orchestrator.yml`: earliest unresolved READY reconciliation; explicit immutable target; catch-up/live-execution separation.
- `scripts/publish_production_candidates.py`: immutable READY recovery target + expected-date fail-closed validation.
- `scripts/publish_production_entries.py`: publication-timeliness guard preventing retroactive T+1 execution.
- `tests/test_phase9_cross_session_handoff.py`: timely, late-recovery, and missing-timestamp cases.

## Validation / closure

A narrow temporary push-path workflow `recovery-gap-lightweight-validation.yml` was added and triggered for compile + Entry/Phase7/Phase8/Phase9 regressions. The available GitHub connector cannot enumerate push-triggered workflow runs, so terminal evidence is still required before closure. No heavy #33 R2-backed rerun has been started by this remediation.

Do not mark CLOSED until lightweight validation is PASS, storage preflight is safe, one controlled reconciliation restores Candidate 2026-09-17, actual R2 object/manifest/pointer state is verified, no retroactive Entry/Lifecycle mutation occurred, retention/storage post-state is verified, and the temporary validation trigger/workflow is removed.


## Closure evidence — 2026-09-18

- Controlled production recovery run `35334136085`: **SUCCESS**.
- Cadence resolved `candidate_current=2026-09-16` -> immutable READY target `2026-09-17`; `proceed=true`.
- Prior Candidate was late for the 2026-09-17 T+1 open and Entry correctly returned `LATE_RECOVERY_NO_RETROACTIVE_ENTRY`; no retroactive Entry was published.
- Candidate publication completed with 933,098 records: NOT_ELIGIBLE 845,763; PIVOT_DEFINED 85,729; PIVOT_CROSSED 1,123; BREAKOUT_CONFIRMED 483.
- Candidate current pointer is `2026-09-17`; retained canonical snapshot is exactly one run: `run-35334136085`.
- Compaction and retention succeeded; post-run R2 audit reported 1.82 GiB.
- Read-only post-verification run `35335975701`: **SUCCESS**.
- Read-only lineage verification run `35336201587`: **SUCCESS**. Manifest `ready_pointer.parquet_key` is `production/ready/runs/2026-09-17.parquet` and SHA-256 is `0c008dcff3a4383073b1353a046ebce2766a2e477cab3275b1db4ac89146df16`, matching the canonical immutable READY object.
- Compaction preserves `first_published_at=2026-09-18T10:34:06.894460Z`; later pointer maintenance updates `updated_at` independently.
- Institutional sponsorship snapshot date remains publication/version semantics, not a required per-decision-date snapshot. No synthetic 2026-09-17 institutional snapshot was created.

The production date-gap incident is therefore **CLOSED / VERIFIED**. Reopen only on contradictory evidence or a new unresolved canonical READY date.
