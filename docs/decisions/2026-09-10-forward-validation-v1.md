# Decision Record — Forward Validation v1

Date: 2026-09-10

Status: FROZEN / WAITING FOR POST-BOUNDARY DATA

## Decision

The historical strategy-development phase is closed for the current baseline. Genuine forward validation begins strictly after `2026-09-09`.

Primary forward track:

```text
Technical Baseline v1
+ X3 pivot-hold execution
+ Portfolio Construction v1
```

Mandatory control:

```text
Technical Baseline v1
+ X1 immediate T+1 execution
+ Portfolio Construction v1
```

No TrendFoll rule is inherited. C/A are not hard filters and EXH2 remains a separate hypothesis.

## Frozen gates

Before any forward candidate/trade count is interpreted, the market-regime source must reach the forward period:

```text
SPY market_data_asof >= 2026-09-10
```

If this data gate fails, status is `WAITING_FOR_POST_BOUNDARY_DATA`; zero candidates are not evidence of zero signals.

After the data gate passes, a formal evidence review is allowed only after both conditions are also true:

```text
>= 12 completed calendar months since 2026-09-10
AND
>= 50 closed X3 portfolio trades
```

Passing all gates means `REVIEW_ELIGIBLE`, not `PRODUCTION_READY`.

## Collector

Workflow: `.github/workflows/forward-validation-v1.yml`

Scheduled collection: `04:30 UTC Tuesday-Saturday`, plus manual dispatch. The timing is deliberately after the upstream daily OHLCV refresh and SPY benchmark job for the prior US session.

The collector recomputes the complete forward window on every run from the fixed boundary. This makes each observation reproducible from the frozen logic while allowing source data to advance naturally.

The first successful collector smoke, run `34493433671`, found the SPY market-regime source only through `2026-09-04`, before the forward start. Its `forward_candidate_count = 0` is therefore an infrastructure/data-readiness observation only and must not be treated as trading evidence.

The upstream `ussy-data` production updater does incrementally maintain `backtest/ohlcv/{security_id}.parquet`, so the security-history path used by the frozen historical engine is also advanced by production. The identified blocker is the separate SPY benchmark pointer required by M.

## Upstream SPY repair status — 2026-09-11

The `ussy-data` SPY updater failure was diagnosed from workflow `34425500954`: the actual failure was `Normalization dropped rows; source requires review`, not an adjustment-basis or historical-close revision.

The upstream repair preserves all existing safeguards. Yahoo rows with incomplete required OHLC are now explicitly audited to `discarded-incomplete-source-rows.csv`; only valid source rows may be normalized/published, while duplicate valid dates, adjustment-ratio changes, historical-close revisions, hash failures, or unexplained valid-row loss still stop publication.

Upstream workflow `34545442393` = SUCCESS. It advanced the immutable SPY pointer from `last_date=2026-09-04` to `last_date=2026-09-09`, with QC PASS. The run received 12 Yahoo source rows: 11 valid and one incomplete. The incomplete row was `2026-09-10`, where Open/High/Low/Volume were present but Close/Adj Close were absent, so it was correctly not manufactured into a market bar.

Confirmation run `34545529977` = SUCCESS / unchanged and observed the same incomplete 2026-09-10 row. The upstream SPY schedule was therefore moved to `03:45 UTC Tuesday-Saturday`, after the production OHLCV refresh and with a larger Yahoo EOD-settlement buffer. FWD1 remains `WAITING_FOR_POST_BOUNDARY_DATA` until a valid SPY bar dated at least 2026-09-10 is published. This is a source-freshness state only and does not change any FWD1/CAN SLIM rule or forward boundary.

## Persistent evidence

Canonical long-horizon evidence is committed under:

```text
evidence/fwd1/
```

`latest/` stores the newest complete forward snapshot and `observations.csv` is append-only by workflow run ID. Git history preserves the sequence of observed states. GitHub Actions artifacts provide a detailed run mirror.

An initial infrastructure attempt to write immutable FWD1 evidence into R2 failed with `PutObject: AccessDenied`. Existing consumer credentials are therefore treated as read-only. This is an infrastructure limitation only; no strategy rule, boundary, threshold, or validation gate was changed because of it.

## Anti-data-mining rule

Interim forward results may be recorded mechanically but cannot be used to alter FWD1. Any rule change after the boundary is a new versioned hypothesis with a new independent forward clock.
