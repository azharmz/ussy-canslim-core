# Decision — I1 ownership and current blocker

Date: 2026-09-11

## Decision

Institutional Sponsorship (`I`) data acquisition belongs upstream in `azharmz/ussy-fundamentals`, not in the CAN SLIM research repository.

`ussy-canslim-research` remains the consumer of point-in-time sponsorship states and must not own a second independent SEC client when `ussy-fundamentals` already provides the production SEC/PIT foundation used by C/A.

## Evidence

`ussy-fundamentals` already has:

- identified `SEC_USER_AGENT` handling;
- throttled SEC access;
- immutable SEC cache semantics;
- submissions ingestion;
- explicit `filed_at` and `accepted_at` semantics;
- amendment-aware fundamental processing;
- scheduled GitHub Actions production workflows.

The existing `SecClient` was extended without changing its JSON behavior to support text/binary SEC sources needed by EDGAR filing indexes and submission documents.

New upstream components:

```text
azharmz/ussy-fundamentals
  src/ussy_fundamentals/sec_13f_index.py
  tests/test_sec_13f_index.py
  .github/workflows/sec-13f-index-probe.yml
```

The 13F index collector is intentionally pre-strategy. It discovers `13F-HR` / `13F-HR/A` accessions from the official quarterly EDGAR master index and hydrates a small sample of exact `<ACCEPTANCE-DATETIME>` values from SEC submission text. No strategy returns are inspected.

A staged bulk normalizer also exists in `ussy-canslim-research` as a fallback boundary, but it cannot make records PIT-ready by itself because the official bulk 13F files do not provide the exact acceptance timestamp needed for decision-time joins.

## Current infrastructure blocker

The first `ussy-canslim-research` SEC endpoint probe and the new I1 staged normalizer both failed before GitHub allocated a hosted runner:

```text
runner_id = 0
steps = empty
```

The new upstream `ussy-fundamentals` 13F index probe (`34598181594`) failed the same way before any workflow step executed. Therefore this failure is not evidence that SEC `data.sec.gov` or EDGAR Archives are inaccessible.

Separately, an earlier I0 run that did receive a runner established that the official bulk 13F ZIP endpoint returned HTTP 403 from that GitHub-hosted runner. That specific bulk-path result remains valid.

## Guardrails

1. `I_state` remains `NOT_IMPLEMENTED` in frozen FWD1.
2. `period_of_report` and `filed_date` must never substitute for `accepted_at`.
3. `13F-HR/A` amendments remain unresolved until accession lineage semantics are audited.
4. Non-US-ISIN securities remain `NOT_EVALUABLE` unless a deterministic audited identifier crosswalk is available.
5. No I threshold or performance ablation may be run until the upstream PIT dataset passes data-quality gates.
6. No current runner/platform failure may be bypassed with an unverified third-party mirror.

## Next valid step

When GitHub-hosted runners are available again, re-run `SEC 13F index probe` in `ussy-fundamentals`. If quarterly index discovery and acceptance hydration succeed, extend the upstream collector from sample hydration to complete relevant accessions, then audit amendment lineage and publish a versioned PIT sponsorship dataset for downstream I1 research.
