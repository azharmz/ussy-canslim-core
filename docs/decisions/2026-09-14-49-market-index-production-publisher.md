# #49 Production Market Index Publisher

Date: 2026-09-14
Status: `PRODUCTION WIRING COMPLETE / LIVE v1`
Publisher: `49-market-index-publisher-v1`

## Boundary

`ussy-data` now publishes the three #47 canonical index identities using the #48-approved Yahoo/yfinance source:

- `NASDAQ_COMPOSITE` <- `^IXIC`
- `SP500` <- `^GSPC`
- `DJIA` <- `^DJI`

No SPY/QQQ substitution is permitted.

## R2 layout

Each publisher run writes immutable objects:

```text
market/indexes/runs/{run_id}/NASDAQ_COMPOSITE.parquet
market/indexes/runs/{run_id}/SP500.parquet
market/indexes/runs/{run_id}/DJIA.parquet
market/indexes/runs/{run_id}/manifest.json
```

Only after all three data objects and the manifest are written does the publisher replace:

```text
market/indexes/official.json
```

The official pointer records publisher version, run id, manifest key, manifest SHA-256, and publication timestamp. Each parquet object also records SHA-256 metadata. This preserves immutable run lineage while allowing a stable consumer pointer.

## Validation and first live publication

Workflow: `ussy-data/.github/workflows/publish-market-indexes.yml`

First live production publication:
- run `34808006835`
- job `103863577188`
- result: `SUCCESS`
- publisher version: `49-market-index-publisher-v1`
- manifest: `market/indexes/runs/34808006835/manifest.json`
- manifest SHA-256: `53b58e146815be9f2a552195fb9e969e4e0a3ead85d9a5576e8921a309fc57e5`
- official pointer: `market/indexes/official.json`
- published at: `2026-09-14T05:00:08.893605+00:00`

## Governance consequence

The #47 -> #46 major-index data boundary is no longer only a specification: a production R2 publication now exists. #46 itself remains frozen and unchanged.

The next integration boundary is a consumer that resolves `market/indexes/official.json`, verifies manifest/object lineage, adapts the selected canonical index series into frozen #46, and persists market-state output with PIT provenance. Leadership/weakening evidence remains a separate unresolved input contract and must not be fabricated by that consumer.
