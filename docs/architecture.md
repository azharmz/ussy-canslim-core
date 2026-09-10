# Research Architecture

## Independence boundary

`ussy-canslim-research` is an **independent strategy research program**. It does not evolve into `ussy-trendfoll`, and `ussy-trendfoll` does not become CAN SLIM by default.

```text
ussy-data
  canonical universe + historical membership
        |
        +--------------------+
        |                    |
        v                    v
ussy-trendfoll        ussy-fundamentals
 independent              SEC/PIT facts
 strategy                    |
                              v
                     ussy-canslim-research
                     independent CAN SLIM
```

TrendFoll is a comparator/reference source for technical ideas and execution lessons only.

## Data / interpretation flow

```text
SEC facts
  -> PIT normalization
  -> readiness
  -> immutable R2 snapshot
  ============================ freeze boundary
  -> CAN SLIM interpretation
  -> PIT labels
  -> experiment configs
  -> backtests
  -> robustness
  -> forward validation
```

## Reproducibility contract

Every completed experiment should record:

- experiment ID and hypothesis;
- code commit SHA;
- historical universe snapshot/version;
- resolved fundamentals immutable snapshot;
- manifest/checksum;
- methodology/config version;
- date range and holdout protocol;
- trade-log location;
- result artifact location;
- verdict.

Do not store large production raw/processed datasets in this repository unless necessary. Prefer immutable object-storage references plus checksums.

## PIT boundaries

### Fundamentals
Only information available by the explicit decision-time cutoff may be used. SEC availability is governed by `accepted_at`, not fiscal-period end.

### Universe
Current Musaffa membership must never be backfilled into historical dates. Use the historical membership snapshot actually available on or before each historical as-of date.

## Research layers

1. **Facts** — owned upstream; no economic interpretation.
2. **CAN SLIM interpretation** — versioned C/A/N/S/L/I/M labels and reason codes.
3. **Strategy experiment** — technical baseline, entry-quality variants, fundamental ablations.
4. **Robustness** — trade count, PF, PF ex-top10, return, max DD, subperiod, sector/symbol concentration, MAE/MFE where relevant.

## Production boundary

No research result automatically changes `ussy-trendfoll` or any other production strategy. A future CAN SLIM production implementation, if created, is a separate project and requires its own evidence/review path.
