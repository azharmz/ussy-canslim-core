# Research Architecture

## Purpose

`ussy-canslim-research` coordinates interpretation and evidence. It should not become another production data/application repo.

## Data / decision flow

```text
ussy-data
  canonical universe + historical membership
        |
        v
ussy-fundamentals
  SEC facts -> PIT normalization -> readiness -> immutable R2 snapshots
        |
        v
ussy-canslim-research
  C/A methodology -> PIT labels -> experiment configs -> backtests -> evidence
        |
        v
production review
        |
        v
ussy-trendfoll (only if a change is explicitly approved)
```

## Reproducibility contract

Every completed experiment should record at minimum:

- experiment ID and hypothesis;
- code commit SHA;
- canonical universe snapshot / historical-membership version;
- resolved fundamentals immutable snapshot and manifest/checksum;
- strategy/config version;
- date range and holdout protocol;
- trade log location;
- result artifact location;
- decision/verdict.

Do not store large raw/processed datasets in this repository unless there is a specific reason. Prefer immutable object-storage references plus checksums.

## PIT rules

### Fundamentals

SEC facts become available according to `accepted_at` and the explicit decision-time cutoff.

### Universe

Current Musaffa membership must never be backfilled into historical periods. Historical eligibility must use the membership snapshot that was actually available on or before the historical as-of date.

## Research layers

### Layer 1 — Facts

No economic interpretation. Owned by upstream data repositories.

### Layer 2 — CAN SLIM interpretation

Examples:

- `C_pass`
- `A_pass`
- component labels / reason codes

Methodology belongs here and must be versioned.

### Layer 3 — Strategy experiment

Examples:

- exact legacy baseline
- pivot-extension variant
- baseline + C
- baseline + C + A

### Layer 4 — Robustness

Required metrics include:

- trade count;
- profit factor;
- PF excluding top 10 trades;
- return;
- max drawdown;
- performance by subperiod;
- sector concentration;
- symbol concentration;
- MAE/MFE and exit-reason diagnostics when relevant.

## Production boundary

No experiment automatically changes production. A research variant can only become a production proposal after methodology freeze, documented backtest, robustness review, and forward-validation plan.
