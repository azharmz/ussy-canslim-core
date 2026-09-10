# USSY CAN SLIM Research HQ

Independent CAN SLIM research program for USSY.

This repository is **not** an upgrade branch of `ussy-trendfoll` and is not a production trading application. It owns CAN SLIM methodology, experiment specifications, evidence, progress, and research decisions.

## Project boundaries

| Repository | Ownership |
|---|---|
| `ussy-data` | Canonical universe and historical membership |
| `ussy-fundamentals` | SEC facts, PIT normalization, readiness, immutable R2 production snapshots |
| `ussy-trendfoll` | Independent legacy TrendFoll strategy and paper-trading implementation |
| `ussy-canslim-research` | Independent CAN SLIM methodology, labels, experiments, evidence, decisions |

TrendFoll is a comparator/reference source only. CAN SLIM may adopt, modify, or reject any TrendFoll rule without changing TrendFoll production.

## Current state — 10 Sep 2026

- Canonical Musaffa universe: **1,327 securities**
- Fundamental production-ready: **901** (`857 PASS_FULL` + `44 PASS_3Y_FALLBACK`)
- Domestic SEC-supported readiness: **87.05%**
- `ussy-fundamentals`: **PRODUCTION-OPERATIONAL / FREEZE**
- R2 consumer entry point: `fundamentals/current.json`
- C-v1 methodology: **FROZEN**
- A-v1 methodology: **FROZEN**
- C/A label implementation: **COMPLETE**
- C/A distribution study: **COMPLETE / VALIDATED**
- Trading-performance metrics were **not** used in the distribution study.

## Frozen C-v1

Latest usable quarterly observation known at decision time:

```text
EPS YoY >= +25%
AND
Revenue YoY >= +25%
```

Undefined/missing growth is not coerced to zero.

## Frozen A-v1

```text
Latest 3 consecutive annual EPS YoY observations
all evaluable
AND each >= +25%
```

`PASS_3Y_FALLBACK` remains a separate provenance tier.

## First C/A distribution result

Pinned fundamentals snapshot:

```text
fundamentals/snapshots/2026-09-09/run-34417104650/manifest.json
```

Among **901 production-ready securities**:

| Label | PASS | FAIL | NOT_EVALUABLE |
|---|---:|---:|---:|
| C-v1 | 69 | 520 | 312 |
| A-v1 | 11 | 483 | 407 |
| C+A | 3 | 437 | 461 |

C+A PASS symbols in this snapshot: **FIX, NBIX, NVDA**.

These results are a methodology/distribution sanity check, **not a trading verdict** and not a reason to change thresholds.

## Research principles

- Preserve facts; version interpretations.
- Freeze methodology before performance testing.
- Never optimize the SEC extraction layer for CAN SLIM pass-rate or CAGR/PF.
- `accepted_at` is the fundamental information-availability boundary.
- Historical universe eligibility must use PIT membership, never current membership backfilled into history.
- Completed experiments must pin immutable universe/fundamental inputs and checksums.
- Missing is not zero. Unsupported is not failed. Insufficient history is not a bad-company verdict.

## Next research blocks

1. Establish an independent CAN SLIM technical baseline on the expanded universe.
2. Run Entry Quality & Execution diagnostics (E0-E6).
3. Integrate frozen PIT C/A labels into historical candidate states.
4. Run ablations and robustness only after the technical baseline is specified.
5. Extend N/S/L/I/M as independent CAN SLIM components, not by silently inheriting TrendFoll production rules.
