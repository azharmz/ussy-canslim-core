# USSY CAN SLIM Research HQ

Independent research repository for building a defensible, point-in-time CAN SLIM strategy.

`ussy-canslim-research` is **not an extension or replacement of `ussy-trendfoll`**. TrendFoll remains an independent strategy/project. This repository may reuse lessons, features, execution assumptions, and baseline evidence from TrendFoll, but CAN SLIM is free to adopt, modify, or reject them.

This repository is **not** a production trading application. It stores methodology, experiment specifications, decision history, progress, evidence, and reproducibility metadata.

## Current status — 10 Sep 2026

- Independent CAN SLIM strategy track: **ACTIVE**
- Legacy reference/baseline: `azharmz/ussy-trendfoll`
- Canonical universe / historical membership: `azharmz/ussy-data`
- Fundamental SEC/PIT engine: `azharmz/ussy-fundamentals` — **PRODUCTION-OPERATIONAL / FREEZE**
- Fundamental production entry point: `fundamentals/current.json` in Cloudflare R2
- Current canonical Musaffa universe: **1,327 securities**
- Fundamental production-ready: **901** (`857 PASS_FULL` + `44 PASS_3Y_FALLBACK`)
- Domestic SEC-supported readiness: **87.05%**
- C methodology: **C-v1 FROZEN**
- A methodology: **NEXT**
- Independent expanded-universe CAN SLIM baseline: **PENDING**
- Entry Quality & Execution research: **PENDING**

## Core research principle

Preserve facts, freeze methodology before performance testing, and never optimize the SEC extraction layer to improve CAN SLIM pass-rates or trading results.

```text
SEC facts
  -> PIT normalization
  -> production readiness
  -> CAN SLIM interpretation
  -> experiment labels
  -> independent CAN SLIM backtest / robustness
  -> forward validation
```

## Source-of-truth boundaries

| Repository | Ownership |
|---|---|
| `ussy-data` | Canonical universe and historical membership |
| `ussy-fundamentals` | SEC facts, PIT normalization, readiness, R2 production snapshots |
| `ussy-trendfoll` | Independent TrendFoll strategy and production paper-trading implementation |
| `ussy-canslim-research` | Independent CAN SLIM methodology, experiments, evidence, decision log |

## Relationship to TrendFoll

TrendFoll is a useful **reference baseline**, not the destination architecture for CAN SLIM.

Its current production entry is:

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

CAN SLIM research can benchmark against those rules, but no result here automatically changes `ussy-trendfoll`.

## Open research issue: entry quality

Filled/Open H+1 is operationally realistic in TrendFoll but remains a research issue for CAN SLIM design. Walk-forward observations include cases where T0 had a very large move or H+1 opened far above the signal price and subsequently retraced.

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
Freeze C specification  ✓
        -> Freeze A specification
        -> Define independent CAN SLIM technical baseline
        -> Entry Quality diagnostics
        -> Produce PIT C/A labels + distribution audit
        -> CAN SLIM ablations
        -> robustness / holdout
        -> independent forward validation
        -> separate production implementation only if evidence supports it
```

See `docs/progress-board.md`, `docs/decision-log.md`, and `experiments/registry.md` for the working state.
