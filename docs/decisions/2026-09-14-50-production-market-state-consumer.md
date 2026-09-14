# #50 Production Market-State Consumer

Date: 2026-09-14
Status: `PRODUCTION CONSUMER COMPLETE / LIVE v1`
Consumer: `50-market-state-consumer-v1`
Classifier: frozen `46-market-state-classification-v1`

## Boundary

The production consumer lives in `azharmz/ussy-data` because that repository owns the R2 credentials and market-data publication boundary. It checks out `azharmz/ussy-canslim-research` at runtime and imports the canonical frozen #46 implementation; #46 logic is not copied or reimplemented.

The consumer:
1. resolves `market/indexes/official.json`;
2. fetches the referenced immutable manifest;
3. verifies the manifest SHA-256;
4. fetches all referenced canonical index parquet objects;
5. verifies each object SHA-256 and index identity;
6. replays frozen #46 chronologically using only observations available on or before each as-of date;
7. leaves `leadership_confirming` and `weakening_confirmed` unset (`None`) because no separate PIT evidence contract exists yet;
8. publishes an immutable market-state run plus `market/state/official.json`.

Bootstrap begins from `NOT_EVALUABLE`, not an assumed `CORRECTION`, so the first live state is derived from observed chronology rather than an invented starting regime.

## First live production run

- workflow run: `34809438828`
- job: `103867638277`
- result: `SUCCESS`
- consumer version: `50-market-state-consumer-v1`
- source index run: `34808006835`
- output key: `market/state/runs/34809438828.json`
- output SHA-256: `9fbb2249889e07db858cf98948eb1885c384462f2a20125f06df7bbeaddafe53`
- as-of date: `2026-09-11`
- derived state: `FOLLOW_THROUGH_CONFIRMED`
- official pointer: `market/state/official.json`

## Interpretation boundary

`FOLLOW_THROUGH_CONFIRMED` is the strongest state #50 can derive from index OHLCV alone under current frozen contracts. Because leadership and weakening PIT evidence remain unresolved, #50 must not autonomously promote to `UPTREND_HEALTHY` or `UPTREND_WEAKENING`.

This is not a performance verdict and does not alter #45 or #46 semantics.
