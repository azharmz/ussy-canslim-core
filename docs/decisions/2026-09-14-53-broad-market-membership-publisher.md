# 53 — Prospective Broad-Market Membership Publisher

Status: **PRODUCTION MEMBERSHIP ARCHIVE LIVE / LEADERSHIP BOOLEAN STILL DEFERRED**

Contract: `53-broad-market-membership-publisher-v1`

## Purpose

Create a prospective, immutable, point-in-time archive of the broad U.S. exchange-listed symbol directory required by the open-data path left by #52.

This workstream does **not** define O'Neil market leaders and does not emit `leadership_confirming` or `weakening_confirmed`.

## Source

Official Nasdaq Trader Symbol Directory files:

- `nasdaqlisted.txt`
- `otherlisted.txt`

Nasdaq documents these files as the symbol directory for Nasdaq-listed and other-exchange-listed securities, with a `File Creation Time` row that can be used to determine source timeliness. The files are updated periodically during the day.

## Production implementation

Owner: `azharmz/ussy-data`

Publisher:

- `src/publish_broad_market_membership.py`
- version `53-broad-market-membership-publisher-v1`

Workflow:

- `.github/workflows/publish-broad-market-membership.yml`
- scheduled weekdays at 23:30 UTC
- manual dispatch supported
- relevant-path push trigger retained for implementation validation/publication

## R2 contract

Each run writes an immutable prefix:

`market/membership/runs/{run_id}/`

containing:

- `nasdaqlisted.txt` — raw source bytes
- `otherlisted.txt` — raw source bytes
- `membership.parquet` — normalized source records
- `manifest.json` — provenance, counts, source creation times, object SHA-256 digests

Stable pointer:

`market/membership/official.json`

The pointer advances only after raw files, normalized membership and manifest have been written.

## Preservation policy

The publisher preserves source flags such as ETF/test-issue/status fields rather than silently filtering them. A later, separately preregistered leader-cohort study may decide what subset is eligible. #53 must not smuggle a leader-selection rule into the membership layer.

## PIT boundary

#53 is prospective. It archives what Nasdaq Trader exposed when the run fetched the files. It does not backfill historical membership using today's file and does not claim to reconstruct membership before the first successful archive.

The source `File Creation Time`, publisher `fetched_at`, run ID, manifest key and SHA-256 object lineage are preserved.

## First live run

GitHub Actions run `34823149519` / job `103909085792` completed successfully on commit `00d6325668fb0896c379024b131f4d51d47ed703`.

The semantic tests passed and the production publication step succeeded.

## Frozen interpretation boundary

This workstream satisfies only the broad-market **membership history** prerequisite identified by #52.

It does not authorize:

- treating all archived securities as O'Neil leaders;
- deriving leaders from future returns;
- treating ETFs/test issues as leaders by default;
- inventing an RS cutoff, breakout-count threshold, breadth threshold or institutional-flow proxy;
- setting #46 `leadership_confirming` or `weakening_confirmed`.

Therefore #50 continues to pass `None` for both leadership/weakening booleans until a later approved leader-selection/evidence producer satisfies #51 and #52.
