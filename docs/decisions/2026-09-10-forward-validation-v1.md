# Decision Record — Forward Validation v1

Date: 2026-09-10

Status: FROZEN / ACCUMULATION GATE

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

## Frozen gate

A formal evidence review is allowed only after both conditions are true:

```text
>= 12 completed calendar months since 2026-09-10
AND
>= 50 closed X3 portfolio trades
```

Passing the gate means `REVIEW_ELIGIBLE`, not `PRODUCTION_READY`.

## Collector

Workflow: `.github/workflows/forward-validation-v1.yml`

Schedule: weekdays at 23:30 UTC, after the US regular-session close, plus manual dispatch.

The collector recomputes the complete forward window on every run from the fixed boundary. This makes each observation reproducible from the frozen logic while allowing source data to advance naturally.

## Persistent evidence

Canonical long-horizon evidence is committed under:

```text
evidence/fwd1/
```

`latest/` stores the newest complete forward snapshot and `observations.csv` is append-only by workflow run ID. Git history preserves the sequence of observed states. GitHub Actions artifacts provide a detailed run mirror.

An initial infrastructure attempt to write immutable FWD1 evidence into R2 failed with `PutObject: AccessDenied`. Existing consumer credentials are therefore treated as read-only. This is an infrastructure limitation only; no strategy rule, boundary, threshold, or validation gate was changed because of it.

## Anti-data-mining rule

Interim forward results may be recorded mechanically but cannot be used to alter FWD1. Any rule change after the boundary is a new versioned hypothesis with a new independent forward clock.
