# Research Architecture

## Purpose

`ussy-canslim-research` coordinates methodology and evidence for an **independent CAN SLIM strategy track**. It must not become a production data repo, and it must not be treated as an upgrade layer whose destination is `ussy-trendfoll`.

## Project topology

```text
                     ussy-data
          canonical + historical universe
                        |
          +-------------+-------------+
          |                           |
          v                           v
  ussy-trendfoll              ussy-fundamentals
 independent strategy          SEC/PIT data engine
          |                           |
          |                           v
          |                 immutable R2 snapshots
          |                           |
          |                           v
          |                 ussy-canslim-research
          |                 independent CAN SLIM
          |                           |
          v                           v
 TrendFoll evidence          CAN SLIM evidence
 / paper trading              / forward validation
```

TrendFoll may serve as a reference baseline or source of reusable research ideas. CAN SLIM may adopt, modify, or reject any TrendFoll rule. No CAN SLIM experiment automatically changes TrendFoll production.

## Data / decision flow for CAN SLIM

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
  C/A/N/S/L/I/M methodology
  -> PIT labels
  -> independent strategy specifications
  -> experiment configs
  -> backtests
  -> evidence
        |
        v
independent CAN SLIM forward validation / production proposal
```

## Reproducibility contract

Every completed experiment should record at minimum:

- experiment ID and hypothesis;
- code commit SHA;
- canonical universe snapshot / historical-membership version;
- resolved fundamentals immutable snapshot and manifest/checksum;
- CAN SLIM strategy/config version;
- any TrendFoll reference version if used as comparator;
- date range and holdout protocol;
- trade log location;
- result artifact location;
- decision/verdict.

Do not store large raw/processed datasets here unless specifically justified. Prefer immutable object-storage references plus checksums.

## PIT rules

### Fundamentals

SEC facts become available according to `accepted_at` and the explicit decision-time cutoff.

### Universe

Current Musaffa membership must never be backfilled into historical periods. Historical eligibility must use the membership snapshot actually available on or before the historical as-of date.

## Research layers

### Layer 1 — Facts

No economic interpretation. Owned by upstream data repositories.

### Layer 2 — CAN SLIM interpretation

Examples: `C_pass`, `A_pass`, component labels and reason codes. Methodology belongs here and must be versioned.

### Layer 3 — Independent CAN SLIM strategy

Defines technical entry, portfolio, risk and exit rules for CAN SLIM itself. TrendFoll rules may be used as comparator/reference but are not inherited automatically.

### Layer 4 — Experiments and ablations

Examples:

- independent CAN SLIM technical baseline;
- entry-quality variants;
- baseline + C;
- baseline + C + A;
- interactions among technical and fundamental components.

### Layer 5 — Robustness

Required metrics include trade count, PF, PF ex-top10, return, max drawdown, subperiod stability, sector/symbol concentration, and MAE/MFE/exit diagnostics where relevant.

## Production boundary

No experiment automatically changes either production strategy. CAN SLIM may receive its own production implementation only after methodology freeze, documented backtests, robustness review and forward validation. `ussy-trendfoll` remains independent unless explicitly changed through its own governance.
