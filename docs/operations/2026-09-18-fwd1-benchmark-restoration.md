# FWD1 legacy benchmark publication restoration — 2026-09-18

Status: **RESTORED / VALIDATED**

Scope: infrastructure/data freshness only. Frozen X3/PORT1/FWD1 semantics are unchanged.

## Incident

The 2026-09-17 audit established that the legacy FWD1 SPY/QQQ benchmark publication path had become stale after the standalone scheduled publishers were removed from `azharmz/ussy-data`. The latest persisted FWD1 observation therefore remained interpretable only through its available benchmark coverage and could not be treated as fresh zero-signal evidence for later sessions.

## Repair

The original isolated benchmark updater implementations and fail-closed QC semantics were preserved. Only their scheduled workflow wrappers were restored in `azharmz/ussy-data`:

- SPY workflow restoration commit: `3d4030bef9c6b13f9be515205f0e703bd614fb42`
- SPY validation/publication run: `35325197489` — **SUCCESS**
- SPY canonical benchmark advanced to `last_date=2026-09-17`, `rows=8466`, `qc=passed`, with `discarded_incomplete_source_rows=0`.
- QQQ workflow restoration commit: `8cc51a3f1c8d6495e1c97473e92c11b2e887b637`
- QQQ validation/publication run: `35325207953` — **SUCCESS**

The restored cadence remains upstream of the frozen FWD1 scheduled observation window. Existing updater safeguards remain in force, including schema/identity validation, explicit incomplete-row accounting, overlap verification, adjustment-basis continuity checks, historical-close revision checks, immutable run publication and pointer-last promotion.

## Other audited state

- `ussy-data` Production daily OHLCV run `35300480223` — **SUCCESS**. Canonical READY is finalized through `2026-09-17`; 1,224 securities terminate on that date, while residual older terminal dates remain explicit rather than being fabricated forward.
- Latest persisted FWD1 canonical evidence before this restoration remains run `35205748408` / observation commit `21b136b45039d23b79900d306fbdfa75e5fad800`: `ACCUMULATING`; the previously recorded counts remain 0 forward candidates, 0 X3 candidate trades, 0 X3 portfolio entries, 0 closed X3 portfolio trades, and 0 completed calendar months. Those counts must not be reinterpreted as newly refreshed evidence until the next FWD1 observation consumes the restored benchmark pointer.
- EXH2 latest scheduled run `35207920329` — **SUCCESS / ACCUMULATING**. It remains separate and prospective.
- `ussy-fundamentals` latest incremental fundamentals run `35217282641` — **SUCCESS**. No new 13F/I promotion evidence was observed; the last canonical 13F publication/retention validation remains green and I remains descriptor/evidence only under the frozen contract.
- Production Entry→Lifecycle observation remains `BLOCKED_ON_PRODUCTION_ENTRY_POPULATION`; no synthetic population was introduced.

## Governance disposition

The benchmark publication blocker is closed at the infrastructure layer. FWD1 itself remains `LIVE / ACCUMULATING`; freshness beyond the old `2026-09-11` benchmark boundary becomes canonical only when a subsequent FWD1 run consumes the restored pointer and persists its own evidence. No forward outcome was used to tune historical rules, and no frozen production or FWD1 trading semantics were changed.
