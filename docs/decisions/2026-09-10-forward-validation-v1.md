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

The upstream `ussy-data` production updater does incrementally maintain `backtest/ohlcv/{security_id}.parquet`, so the security-history path used by the frozen historical engine is also advanced by production. The identified blocker is the separate SPY benchmark pointer required by M, whose scheduled updater failed conservatively rather than overwrite a potentially revised series.

## Persistent evidence

Canonical long-horizon evidence is committed under:

```text
evidence/fwd1/
```

`latest/` stores the newest complete forward snapshot and `observations.csv` is append-only by workflow run ID. Git history preserves the sequence of observed states. GitHub Actions artifacts provide a detailed run mirror.

An initial infrastructure attempt to write immutable FWD1 evidence into R2 failed with `PutObject: AccessDenied`. Existing consumer credentials are therefore treated as read-only. This is an infrastructure limitation only; no strategy rule, boundary, threshold, or validation gate was changed because of it.

## Anti-data-mining rule

Interim forward results may be recorded mechanically but cannot be used to alter FWD1. Any rule change after the boundary is a new versioned hypothesis with a new independent forward clock.
