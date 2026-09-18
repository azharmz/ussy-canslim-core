# Historical CAN SLIM backtest — readiness audit

Date: 2026-09-18
Status: **BLOCKED BEFORE FIRST TRADE / DATA-CONTRACT GAPS IDENTIFIED**

This note records the evidence audit performed after freezing the FA-first runner boundary. It is not a performance result and does not authorize tuning.

## Frozen fundamental artifact recovered

Authoritative successful workflow:

- run: `35175083156`
- artifact: `historical-fundamental-screener-v1-35175083156`
- artifact digest: `sha256:15f126b7f7adb1be233ef3e9353b9b761bdb7bf5c198e6f465dacf506024293b`
- state transitions: 47,817
- C+A PASS transition rows: 8
- PASS intervals: 5
- PASS decision-date rows: 515
- PASS decision dates: 392
- securities ever PASS: 3
- future accepted-at violations: 0
- duplicate transition rows: 0

Exact PASS intervals:

| security_id | symbol | pass_from_accepted_at | pass_until_accepted_at_exclusive |
|---|---|---|---|
| US58506Q1094 | MEDP | 2021-07-27T20:40:08Z | 2021-10-26T20:06:41Z |
| US09739D1000 | BCC | 2022-05-05T20:49:08Z | 2022-08-01T20:21:17Z |
| US1727551004 | CRUS | 2022-08-02T20:03:00Z | 2022-11-01T20:03:53Z |
| US58506Q1094 | MEDP | 2022-04-26T20:06:11Z | 2023-02-14T21:07:36Z |
| US58506Q1094 | MEDP | 2023-04-25T20:03:36Z | 2023-10-24T20:02:38Z |

The artifact also materializes NYSE decision dates, so interval timestamp boundaries must not be naively converted to calendar dates. The runner should consume `ca_pass_by_decision_date.csv` (or derive an equivalent session list under the same cutoff contract).

## Frozen #33 adapter feasibility

Pinned #33 SHA `c433cc1e35a5aa32a46f732cd8c5545935e36e40` exposes:

`oneil_patterns.production.engine.analyze_security(security_id, ticker, frame, asof_date)`

It rejects future bars and delegates directly to the canonical P8 prediction adapter. Therefore the historical runner can call the exact frozen engine on a per-security OHLCV prefix; no second detector is needed.

Input columns are raw `open/high/low/close` plus volume and chronology. Morphology uses raw OHLC. Current READY rolling depth (250–300 bars) is an upstream live-consumption constraint, not authorization to reconstruct 2021–2023 history from today's READY object.

## Blocking gaps

### H1 — historical stock OHLCV source not yet bound

The five PASS intervals are 2021–2023. Current production READY is rolling and cannot itself supply those historical prefixes. Existing BT5 infrastructure/history may be reusable, but this backtest must bind a canonical historical stock OHLCV source with identity, raw-price semantics, checksum/provenance, and no future-bar leakage before invoking #33.

**Disposition:** FAIL CLOSED. Do not fetch ad-hoc Yahoo inside the backtest runner.

### H2 — historical M is explicitly not authorized by current long-history artifact

The existing long-history canonical-index publisher writes:

`historical_replay_authorized: false`

Therefore its index history cannot be silently treated as governed historical M evidence for this backtest. Production #50 exact-date market-state consumption is frozen, but historical replay needs an explicit data/governance authorization or a separately frozen historical-M artifact.

**Disposition:** M = NOT_EVALUABLE until authorized historical exact-date state exists.

### H3 — historical I must use historical 13F semantics, not current live state retroactively

Full eligibility makes I mandatory and accepts only `POSITIVE`. The repository has a historical 13F methodology with conservative availability `filing_date + 1 calendar day`, while the live resolver uses exact accepted-at for current/live evidence.

The backtest therefore needs the canonical historical 13F event-state artifact and must not attach the current live sponsorship table retroactively.

**Disposition:** I = NOT_EVALUABLE until the historical event artifact is bound and validated for each decision date.

### H4 — L historical attachment remains to be bound

Full eligibility also makes L mandatory. RS-line evidence code exists, but the historical runner still needs the exact frozen production leadership classification/evidence adapter and canonical S&P 500 historical provenance for the same decision date.

**Disposition:** no full `CANSLIM_ELIGIBLE` signal may be emitted until L is causally wired.

## Consequence

The next implementation target is not trade simulation. It is a **one-interval evidence bundle**:

```text
fundamental decision dates
+ canonical historical stock OHLCV prefix
+ pinned #33 assessments
+ historical L
+ historical I
+ historical exact-date M
=> frozen #34 candidate
```

Only when all mandatory letters are evaluable may #36 T+1 Open be invoked.

No heavy compute was started by this audit.
