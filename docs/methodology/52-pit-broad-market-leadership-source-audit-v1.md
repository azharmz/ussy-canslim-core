# 52 — PIT Broad-Market Leadership Data Source Audit v1

Status: **SOURCE AUDIT COMPLETE / NO PRODUCTION BOOLEAN SOURCE APPROVED**

Contract: `52-pit-broad-market-leadership-source-audit-v1`

## Purpose

Select or reject candidate source stacks capable of supplying the frozen #51 evidence contract without changing #46/#45 semantics and without using the restricted USSY/Musaffa universe as a proxy for the broad U.S. market.

A candidate source stack must be able to support, point-in-time:

1. a valid broad-market stock cohort;
2. identification of market-leading stocks without future returns;
3. evidence that leaders are making/approaching new highs or constructive breakouts;
4. explicit institutional accumulation/demand evidence;
5. the corresponding weakening channels: leaders ceasing to make new highs/breaking down plus institutional selling;
6. reproducible membership and observation provenance.

This workstream audits sources. It does not invent a leader threshold or mutate `51-market-leadership-weakening-evidence-v1`.

## Authoritative theory boundary

William J. O'Neil's market-direction framework uses leading-stock action alongside major-index price/volume. For uptrends, new leaders moving to new highs with institutional money moving into them are confirming evidence. For downtrends/weakening, the majority of leaders stopping new highs plus institutional selling are deterioration evidence.

The theory does not provide a universal public algorithm for converting an arbitrary all-stock universe into a leader cohort. Therefore #52 may approve a source only if the leader designation and institutional-flow channels are themselves defensible and point-in-time, rather than tuned from later returns.

## Candidate A — Nasdaq Trader Symbol Directory

Current files:

- `nasdaqlisted.txt`
- `otherlisted.txt`

Nasdaq Trader documents these as current symbol-directory files, updated during the day. They expose exchange/listing identity, ETF flag for other-listed securities, test-issue status, and file creation timestamps. Together they can form a broad current U.S. exchange-listed membership source with immutable daily snapshots.

### Verdict

**APPROVED AS A BROAD-MARKET MEMBERSHIP INPUT CANDIDATE; NOT APPROVED AS A #51 BOOLEAN SOURCE.**

Why:

- suitable for broad membership discovery/current snapshot provenance;
- can be archived prospectively to create PIT membership history from go-live;
- does not itself designate O'Neil-style market leaders;
- does not provide the required institutional accumulation/selling evidence.

Historical backtests must never apply a current directory snapshot retroactively. Before archived snapshots exist, historical membership remains NOT_EVALUABLE unless another separately validated historical membership source is adopted.

## Candidate B — Broad-universe daily OHLCV (for example Yahoo/yfinance)

Price/volume data can measure new highs, breakouts, and selling pressure once a valid membership/leader cohort exists.

### Verdict

**NOT APPROVED AS A STANDALONE #51 BOOLEAN SOURCE.**

OHLCV is an observation layer, not an authoritative leader selector. A numeric RS cutoff, lookback, breakout-count rule, or breadth threshold would need a separately frozen theory/evidence contract; #52 may not infer one from future market returns.

This does not revoke the #48 approval of Yahoo/yfinance for the three canonical major indexes. That approval is a different contract and purpose.

## Candidate C — IBD / MarketSurge leadership lists and ratings

IBD materials explicitly use curated/computer-generated leadership lists such as IBD 50 and ratings such as Relative Strength and Accumulation/Distribution to identify leading growth stocks and institutional buying/selling characteristics. This is the candidate family closest to the #51 theory boundary.

### Verdict

**THEORY-ALIGNED / PRODUCTION ACCESS CONTRACT NOT ESTABLISHED — DEFERRED.**

Before production approval, the project needs evidence of:

- stable machine-readable access permitted for the intended internal automation;
- exact snapshot availability time;
- immutable membership/rating provenance or an archive we create prospectively;
- unambiguous symbol identity;
- sufficient coverage to observe leader membership changes and institutional-flow evidence without scraping future-revised pages;
- explicit handling of missing days/source outages.

Until those operational/PIT properties are established, #50 must not consume IBD-derived booleans automatically.

## Candidate D — USSY/Musaffa restricted universe

### Verdict

**REJECTED for broad-market inference.**

It remains the strategy's tradable universe but is not a representative all-market leadership cohort. Using it as #51's market-wide source would violate the frozen restricted-universe prohibition.

## Source-stack acceptance gate

A production #51 source stack is approved only if all of the following are true:

- `broad_market_membership_valid = true`
- `membership_pit_provenance = true`
- `leader_selection_authoritative_or_separately_frozen = true`
- `institutional_flow_explicit = true`
- `machine_reproducible = true`
- `availability_timestamped = true`
- `future_returns_not_used = true`
- `restricted_universe_not_used_as_proxy = true`

If any required item is unknown, the stack is not approved and #51 remains `NOT_EVALUABLE` for production booleans.

## Recommended production path

1. Start prospectively archiving immutable Nasdaq Trader membership snapshots in the data layer.
2. Keep price/volume observation sourcing separate from membership.
3. Audit whether an IBD/MarketSurge account/source can provide a stable permitted machine-accessible leadership/rating snapshot contract.
4. If not, conduct a separately preregistered theory study for an open-data leader selector. Do not derive thresholds from future returns.
5. Only after an approved source stack exists may a producer generate #51 evidence packets and wire them into #50.

## Terminal decision

**SOURCE AUDIT COMPLETE / NO PRODUCTION BOOLEAN SOURCE APPROVED.**

Nasdaq Trader is accepted only as an upstream broad-market membership candidate. No currently audited source stack satisfies every frozen #51 requirement for both leader identity and institutional-flow evidence. Production `leadership_confirming` and `weakening_confirmed` therefore remain `None`.