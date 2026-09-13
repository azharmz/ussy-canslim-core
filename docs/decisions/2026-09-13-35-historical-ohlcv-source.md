# Decision — #35 Historical OHLCV Research Source

Date: 2026-09-13
Status: **FROZEN FOR #35 VALIDATION**

## Decision

#35 will **not** use `production/ready` as its historical/backtest dataset.

The primary historical OHLCV research source is the existing purpose-built full-history archive owned by `azharmz/ussy-data`:

```text
backtest/ohlcv/{security_id}.parquet
```

This is distinct from the compact production R2 ready snapshot.

## Why this source

`ussy-data/src/bootstrap_ohlcv.py` already bootstraps full daily history from Yahoo Finance using:

```text
yf.download(
    period="max",
    interval="1d",
    auto_adjust=False,
    actions=False,
)
```

and persists:

```text
date
security_id
ticker
open
high
low
close
adj_close
volume
```

The production rolling/ready dataset is then built from these same full-history objects by `ussy-data/src/build_rolling.py`, which tails the archive to the configured production retention (currently 300 bars). Therefore the full-history archive is the cleanest way to obtain longer #35 windows without changing production infrastructure or introducing a new provider semantic.

## Price semantics

For compatibility with current production behavior:

- #33 morphology / pivot / breakout / volume uses raw `open/high/low/close/volume` from the archive, matching the fields passed through the production rolling contract;
- L/RS uses `adj_close`, matching the current #34 RS implementation;
- no silent replacement of raw OHLC with adjusted OHLC is permitted.

This preserves existing production semantics. Corporate-action edge cases, especially split windows, must remain auditable during #35 rather than being silently transformed.

## Provider/version caveat

Yahoo Finance is the acquisition provider for this archive. Historical validation artifacts must record retrieval/object provenance where available. Provider choice is frozen for #35 semantic validation because it matches the existing upstream production lineage; it is not selected from trading performance.

Tiingo/Twelve Data may remain independent data-audit sources but are not introduced as the primary #35 source unless a documented data-semantics defect requires a separate decision.

## Membership caveat

The existence of full price history for a security does not imply historical universe membership. #35 candidate-semantic validation may use selected securities independently of profitability, but any later historical performance study must separately enforce the appropriate PIT universe/membership contract.

## Consequence

300-bar production retention is no longer a #35 blocker. #35 can request as much prehistory as required from `backtest/ohlcv/` while leaving `production/ready` unchanged.
