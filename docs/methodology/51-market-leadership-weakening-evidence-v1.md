# 51 — Market Leadership / Weakening Evidence v1

Status: **EVIDENCE CONTRACT COMPLETE / PRODUCTION BOOLEAN SOURCE DEFERRED**

Contract: `51-market-leadership-weakening-evidence-v1`

## Purpose

Provide a theory-faithful, point-in-time evidence contract for the two auxiliary inputs already accepted by frozen `46-market-state-classification-v1`:

- `leadership_confirming`
- `weakening_confirmed`

This workstream does **not** change #46 thresholds or transitions, #45 exposure semantics, #29 stock-level RS semantics, or any frozen stock lifecycle contract.

## Authoritative basis

William J. O'Neil's market-direction framework treats market-leading stocks as a second evidence family alongside major-index price/volume action. In an up-trending market, new market leaders are among the first stocks to move to new highs while the market rises on strong volume, with institutional money moving into those leaders. In a down-trending market, the majority of new leaders stop making new highs and institutional selling appears in the leaders. O'Neil also describes major-average heavy-volume selling and breakdowns in leading stocks as joint evidence of market deterioration.

Supporting sources reviewed for this contract:

1. William J. O'Neil, AAII Journal, *The Big Picture: How to Decipher What the Market Is Saying* (2004).
2. William J. O'Neil, AAII Journal, *The Big Picture: How to Determine the Stock Market's Direction* (2003).
3. AAII summary of O'Neil's revised CAN SLIM approach, which explicitly says to follow market leaders for clues on market strength and notes faltering original quality leaders as a topping clue.
4. IBD/MarketSmith educational material describing new potential leaders around follow-through periods as stocks with strong relative strength and emphasizing confirmation from successful leading-stock action.

The sources support the **direction and character** of leadership evidence. They do not provide a sufficiently stable, universal, public quantitative rule for converting an arbitrary stock universe into the two production booleans required by #46.

## Frozen boundary

### Leadership confirmation

A production observation may support `leadership_confirming=True` only when all of the following are explicitly evidenced as of the decision date:

- the observed cohort is a valid **broad-market leadership cohort**, not merely the project's restricted Sharia-compliant universe;
- new/current market leaders are making or moving into new highs / constructive breakout leadership;
- institutional accumulation/demand in those leaders is explicitly evidenced;
- the evidence is point-in-time and has source/provenance metadata.

If those required channels are available and any is explicitly false, the evidence result may be `False`. If a required channel is unavailable, the result is `NOT_EVALUABLE` (`None` in the Python adapter).

### Weakening confirmation

A production observation may support `weakening_confirmed=True` only when all of the following are explicitly evidenced as of the decision date:

- the observed cohort is a valid broad-market leadership cohort;
- a majority of the observed leaders are explicitly evidenced as no longer making new highs / breaking down;
- institutional selling/distribution in leaders is explicitly evidenced;
- the evidence is point-in-time and has source/provenance metadata.

`majority` retains the ordinary meaning **more than half of the valid observed leadership cohort**. This is not a fitted threshold. No additional count, RS cutoff, moving-average threshold, return threshold, or lookback is invented here.

If required channels are available and any is explicitly false, the evidence result may be `False`. If a required channel is unavailable, the result is `NOT_EVALUABLE`.

## Restricted-universe prohibition

The current/frozen USSY Sharia-compliant universe must **not** be silently treated as a representative broad-US-market leadership or breadth universe. It can remain the tradable stock universe for the strategy, but a leadership signal derived only from that restricted membership cannot be promoted to #46's general-market `leadership_confirming` or `weakening_confirmed` without a separately validated representativeness contract.

This prevents selection bias from becoming a market-state input.

## PIT contract

Every production evidence packet must preserve at least:

- `asof_date`
- evidence-source identity
- source observation timestamp / availability timestamp where applicable
- cohort definition/version
- cohort membership provenance
- number of valid observed leaders
- leadership-new-high evidence state
- institutional accumulation evidence state
- leader-breakdown/no-new-high evidence state
- institutional selling evidence state
- producer version
- source run/object identifiers or digests when available

No observation after `asof_date` may influence the packet. Future returns may never be used to decide retrospectively which stocks were leaders.

## Explicitly unauthorized in v1

This contract does **not** authorize:

- deriving broad-market leadership solely from the frozen 1,300-security RS universe or current Musaffa universe;
- using future winners to define the leader cohort;
- inventing a universal number of leaders, breakout-success rate, RS threshold, breadth threshold, moving-average threshold, or distribution-day count;
- converting #29 stock-level leadership qualification directly into general-market leadership confirmation;
- using SPY/QQQ/DIA as substitutes for a stock-leadership cohort;
- changing #46's frozen FTD/distribution semantics;
- changing #45's exposure bands.

## Machine adapter

`src/canslim_research/market_leadership_evidence_v1.py` freezes the tri-state aggregation boundary. It intentionally consumes already-observed evidence channels rather than fabricating a production leader cohort.

The adapter returns:

- `True` — all required evidence channels are evaluable and jointly confirm the condition;
- `False` — all required evidence channels are evaluable but do not jointly confirm it;
- `None` — required evidence/provenance is incomplete or the cohort is not valid for broad-market inference.

## Terminal decision

**EVIDENCE CONTRACT COMPLETE / PRODUCTION BOOLEAN SOURCE DEFERRED**

The authoritative record is strong enough to freeze what counts as acceptable leadership/weakening evidence and to prohibit biased substitutes. It is not strong enough to invent a universal quantitative broad-market stock-cohort algorithm from the data currently available in the project.

Therefore #50 must continue passing `None` for these two inputs until a separately versioned PIT broad-market leadership data source/producer satisfies this contract. This is preserved evidence debt, not permission to tune a threshold from returns.