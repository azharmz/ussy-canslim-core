# Decision — #52 PIT Broad-Market Leadership Source Audit

Date: 2026-09-14

Status: **SOURCE AUDIT COMPLETE / NO PRODUCTION BOOLEAN SOURCE APPROVED**

Contract: `52-pit-broad-market-leadership-source-audit-v1`

## Decision

Freeze #52 as a source-audit boundary upstream of #51. No currently audited source stack is approved to emit production `leadership_confirming` or `weakening_confirmed` booleans.

### Accepted upstream component

Nasdaq Trader `nasdaqlisted.txt` + `otherlisted.txt` are accepted as a candidate broad-current-U.S.-exchange membership source for prospective immutable snapshots. This approval is membership-only.

It does not designate O'Neil-style leaders and does not provide the institutional accumulation/selling evidence required by frozen #51.

### Not approved as standalone #51 sources

- broad-universe OHLCV alone;
- current USSY/Musaffa membership;
- any source whose leader cohort is selected using future returns;
- any source stack with unknown PIT membership provenance, observation availability time, institutional-flow evidence, or machine reproducibility.

### Theory-aligned but deferred

IBD/MarketSurge leadership lists and ratings are closest to the authoritative O'Neil evidence family because they explicitly expose market-leading growth-stock lists, relative-strength measures, and institutional accumulation/distribution measures. Production approval is deferred until a stable permitted machine-readable and PIT-auditable access contract is demonstrated.

## Production consequence

Frozen #50 must continue to pass:

- `leadership_confirming=None`
- `weakening_confirmed=None`

until a later source/producer version satisfies all #52 gates.

No change is made to frozen #46 or #45.

## Next clean work

1. Prospectively archive immutable Nasdaq Trader membership snapshots in the data layer.
2. Audit a permitted machine-accessible IBD/MarketSurge source contract if available.
3. If such access is unavailable, preregister a separate open-data leader-selector research workstream before introducing any numeric threshold.

No threshold may be fitted from future market returns.
