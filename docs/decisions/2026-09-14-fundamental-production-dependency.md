# Decision — CAN SLIM C/A Production Dependency on PIT Fundamental Feed

Date: 2026-09-14
Status: **DEPENDENCY RECORDED**
Upstream owner: `azharmz/ussy-fundamentals`

## Dependency

The CAN SLIM C/A production path depends on a point-in-time-safe fundamental feed produced by `azharmz/ussy-fundamentals`.

The CAN SLIM research repository does **not** own SEC discovery, filing ingestion, amendment handling, incremental recomputation, or fundamental snapshot publication. Those responsibilities remain in `ussy-fundamentals`.

## Required upstream properties

Before CAN SLIM v1 is called fully production-ready, the upstream fundamental feed must preserve at least:

- SEC filing identity/provenance;
- `filing_date` and `accepted_at`;
- form type (`10-Q`, `10-Q/A`, `10-K`, `10-K/A` where supported);
- fiscal period/year identity;
- PIT visibility (`accepted_at <= decision time`);
- immutable publication/run lineage;
- explicit missing/unsupported/failure states rather than silent coercion.

The production updater should operate incrementally: discover new SEC filings, recompute only affected securities, merge into the current baseline, and publish a new immutable snapshot only after validation succeeds.

## Governance boundary

This dependency must not change frozen CAN SLIM C/A theory semantics. Fundamental infrastructure supplies PIT-safe facts; CAN SLIM classification remains downstream and separately governed.

No historical backtest may use a filing before its SEC acceptance time. No future amendment may be backfilled into an earlier decision state.

## Upstream decision

The detailed updater architecture and hardening roadmap are canonical in:

`azharmz/ussy-fundamentals/docs/decisions/2026-09-14-automated-incremental-sec-update.md`

Current upstream status:

`AUTOMATED INCREMENTAL SEC UPDATER / IMPLEMENTED — HARDENING & OPERATIONAL AUDIT REMAIN`
