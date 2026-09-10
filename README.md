# USSY CAN SLIM Research HQ

Independent CAN SLIM research program for USSY.

This repository is **not** an upgrade branch of `ussy-trendfoll` and is not a production trading application. It owns CAN SLIM methodology, experiment specifications, evidence, progress, and research decisions.

## Project boundaries

| Repository | Ownership |
|---|---|
| `ussy-data` | Canonical universe and OHLCV data contracts |
| `ussy-fundamentals` | SEC facts, PIT normalization, readiness, immutable R2 production snapshots |
| `ussy-trendfoll` | Independent legacy TrendFoll strategy and paper-trading implementation |
| `ussy-canslim-research` | Independent CAN SLIM methodology, labels, experiments, evidence, decisions |

TrendFoll is a comparator/reference source only. CAN SLIM may adopt, modify, or reject any TrendFoll rule without changing TrendFoll production.

## Research-universe definition

The primary historical research question uses a **frozen contemporary/current Musaffa-compliant universe**. We ask how CAN SLIM rules behave historically on the securities that are in the selected compliant research universe now.

Historical Musaffa compliance is therefore **not** a strategy input and is not required for this research design. We do not claim that the resulting historical sample reconstructs which securities were known compliant in each historical year.

Point-in-time discipline remains mandatory for information actually used to make historical strategy decisions, especially:

- OHLCV and market-state data through the decision date only;
- SEC fundamental evidence only after `accepted_at`;
- no future filings, future prices, or later amendments before their acceptance time.

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
- Independent technical baseline: **FROZEN / IMPLEMENTED**
- Entry-timing basis test X1-X4: **IN PROGRESS**

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
- Define the research universe explicitly and do not confuse current-universe historical research with historical-eligibility reconstruction.
- Completed experiments must pin immutable universe/fundamental inputs and checksums.
- Missing is not zero. Unsupported is not failed. Insufficient history is not a bad-company verdict.
- Daily-EOD signals may only use completed daily information; close-based conditions are filled no earlier than the next session Open.

## Next research blocks

1. Complete the X1-X4 entry-timing basis test.
2. Freeze the preferred executable entry model only after comparative evidence review.
3. Integrate frozen PIT C/A labels into historical candidate states.
4. Run C and C+A ablations after entry timing is frozen.
5. Freeze portfolio construction before portfolio return/max-drawdown claims.
