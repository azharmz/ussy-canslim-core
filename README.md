# USSY CAN SLIM Research HQ

Research coordination repository for extending `ussy-trendfoll` toward a defensible, point-in-time CAN SLIM research framework.

This repository is **not** a production trading application. It stores methodology, experiment specifications, decision history, progress, and reproducibility metadata.

## Current status — 10 Sep 2026

- Legacy technical baseline: `azharmz/ussy-trendfoll`
- Canonical universe / historical membership: `azharmz/ussy-data`
- Fundamental SEC/PIT engine: `azharmz/ussy-fundamentals` — **PRODUCTION-OPERATIONAL / FREEZE**
- Fundamental production entry point: `fundamentals/current.json` in Cloudflare R2
- Current canonical Musaffa universe: **1,327 securities**
- Fundamental production-ready: **901** (`857 PASS_FULL` + `44 PASS_3Y_FALLBACK`)
- Domestic SEC-supported readiness: **87.05%**
- CAN SLIM C/A methodology: **NEXT**
- Expanded-universe legacy baseline: **PENDING**
- Entry Quality & Execution research: **PENDING**

## Core research principle

Preserve facts, freeze methodology before performance testing, and never optimize the SEC extraction layer to improve CAN SLIM pass-rates or trading results.

```text
SEC facts
  -> PIT normalization
  -> production readiness
  -> CAN SLIM interpretation
  -> experiment labels
  -> backtest / robustness
  -> forward validation
```

## Source-of-truth boundaries

| Repository | Ownership |
|---|---|
| `ussy-data` | Canonical universe and historical membership |
| `ussy-fundamentals` | SEC facts, PIT normalization, readiness, R2 production snapshots |
| `ussy-trendfoll` | Legacy strategy and production paper-trading implementation |
| `ussy-canslim-research` | CAN SLIM methodology, experiments, evidence, decision log |

## Legacy technical baseline

Production entry in `ussy-trendfoll`:

```text
hard_filter_status == PASS
+ breakout above previous pivot
+ breakout volume percentile >= 80
-> signal at T0 close
-> realistic entry = Open H+1
-> stop = Open H+1 - 2 x ATR14(T0)
-> exit = intraday stop OR close < EMA20 OR 45 trading days
```

Legacy universe was approximately **199 securities**, originating from the intersection of XTB availability and Musaffa-compliant securities. That universe constraint is not a CAN SLIM rule.

## Open research issue: entry quality

Filled/Open H+1 is operationally realistic but remains a research issue. Walk-forward observations include cases where T0 had a very large move or H+1 opened far above the signal price and subsequently retraced.

The dedicated Entry Quality workstream studies:

- T-1 -> T0 signal-day shock
- T0 close -> H+1 open execution gap
- T0 extension above pivot
- actual H+1 fill extension above pivot
- interactions with MAE, MFE, realized return, PF and drawdown

Pivot extension thresholds **3% / 5% / 8%** are pre-specified research variants. Do not infer new thresholds from a small set of losing walk-forward trades.

## Fundamental PIT contract

For backtests, information is visible only when available at the decision time. SEC filing availability is governed by `accepted_at`, not fiscal period end.

For production consumers, resolve:

```text
fundamentals/current.json
```

For reproducible research, pin the immutable snapshot/manifest/checksum actually used. Never store only the word `current` in an experiment record.

## Roadmap

```text
Expanded-universe exact legacy baseline
        -> Entry Quality diagnostics
        -> Freeze C specification
        -> Freeze A specification
        -> Compute PIT labels / distribution
        -> C ablation
        -> C+A ablation
        -> robustness / holdout
        -> forward validation
        -> production review only if evidence supports it
```

See `docs/progress-board.md`, `docs/decision-log.md`, and `experiments/registry.md` for the working state.
