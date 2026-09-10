# Independent CAN SLIM Technical Baseline v1

Status: **FROZEN FOR INITIAL RESEARCH**

Date: 2026-09-10

## Purpose

Define a reproducible N/S/L/M-side technical baseline for the independent `ussy-canslim-research` strategy. This is not inherited from `ussy-trendfoll`; TrendFoll remains a comparator only.

The baseline deliberately distinguishes:

1. O'Neil/IBD-derived concepts;
2. transparent quantitative proxies needed because proprietary IBD ratings/pattern engines are unavailable;
3. deferred CAN SLIM components that must not be silently treated as PASS.

## Universe and non-CAN-SLIM guardrail

Eligibility is based on historical Musaffa membership from `ussy-data`, using `security_id` as identity. Current membership must never be backfilled into historical dates.

For v1, exclude securities below **$15 at signal time** as an investability/quality guardrail. This is not one of the seven CAN SLIM letters; it is recorded separately as `price_guardrail_pass`.

Reference rationale: IBD's educational material advises avoiding cheap stocks and generally focusing on stocks priced $15 or higher.

## Frozen technical signal

A v1 technical candidate requires all of the following at end of signal day T0:

```text
historically eligible Musaffa security
AND price_guardrail_pass
AND N_price_pass
AND S_pass
AND L_pass
AND M_pass
```

C-v1 and A-v1 remain separate frozen fundamental labels. They are not silently folded into this technical baseline.

## N — New / price breakout proxy

`N` in literal CAN SLIM includes new products/services, new management, new conditions and/or new price highs. In v1 we only implement the **price/new-high side** because a defensible PIT catalyst dataset does not yet exist.

Frozen `N_price_v1`:

- a base/pivot must be identified using only data available through T0;
- T0 closes above the pivot/buy point;
- T0 close must be no more than **5% above the pivot**;
- the signal records proximity to the 52-week high;
- catalyst state is stored as `N_catalyst_state = NOT_IMPLEMENTED`, never auto-PASS.

The initial base detector may be a transparent quantitative approximation, but its exact implementation must be versioned before backtest. Pattern names such as cup-with-handle must not be claimed unless the algorithm actually identifies those structures.

## S — Supply and demand

Frozen `S_v1` uses observable demand at breakout:

```text
T0 volume >= 1.40 * average daily volume over prior 50 sessions
```

This corresponds to the IBD/O'Neil guidance that a breakout should show a minimum roughly 40-50% increase above average daily volume.

Shares outstanding/float are not hard gates in S-v1 because a fully audited PIT supply dataset is not yet part of this research contract. If available, they may be logged as observations only.

## L — Leader or laggard

IBD's proprietary RS Rating cannot be reproduced exactly. L-v1 therefore uses a transparent proxy while preserving the O'Neil idea that leaders should rank near the top of the market.

`L_v1`:

1. compute a recency-weighted price-strength score from total returns:

```text
RS_proxy_raw =
    0.40 * return_63d
  + 0.20 * return_126d
  + 0.20 * return_189d
  + 0.20 * return_252d
```

2. rank `RS_proxy_raw` cross-sectionally within the historically eligible universe on T0;
3. require `RS_proxy_percentile >= 80`.

This formula is **our quantitative proxy**, not IBD's proprietary RS formula. The threshold of 80 is O'Neil/IBD-aligned.

Sector/industry leadership is recorded for diagnostics where a PIT classification exists, but is not a v1 hard gate so that we do not invent an IBD industry-group ranking from incompatible sector taxonomies.

## M — Market direction

IBD's current market exposure model is proprietary and cannot be reconstructed exactly from public daily data. M-v1 uses a transparent follow-through/distribution proxy on SPY and QQQ.

### Distribution day

For each index ETF, a distribution day is:

```text
daily return <= -0.20%
AND volume > previous session volume
```

Distribution days expire after 25 trading sessions.

### Rally attempt and follow-through proxy

A rally attempt starts after a correction when an index makes a 10-session closing low and subsequently posts its first positive close; that positive session is Day 1.

A valid follow-through proxy occurs on Day 4 or later of that rally attempt when:

```text
daily return >= +1.00%
AND volume > previous session volume
```

A follow-through proxy is invalidated if the index later closes below the rally-attempt low.

### M gate

`M_pass = TRUE` when:

- at least one of SPY or QQQ has a currently valid follow-through proxy; and
- neither index has 6 or more active distribution days in the last 25 sessions.

The 1.00% FTD threshold reflects modern IBD educational descriptions; the 6-in-25 distribution block is a conservative quantitative adaptation of IBD's warning around clustered distribution. Both are versioned and must not be retuned after seeing strategy CAGR/PF.

## I — Institutional sponsorship

`I` is **not implemented in technical baseline v1**.

```text
I_state = NOT_IMPLEMENTED
```

This means the resulting strategy is still an incomplete CAN SLIM implementation. Price/volume accumulation is useful evidence but must not be mislabeled as a complete institutional-ownership implementation.

## Signal and execution separation

Technical signal validity is evaluated at T0 close. Execution is a separate research layer.

Initial historical execution model may use Open H+1 for realism, but H+1 entry quality is explicitly investigated through E1-E6. A technical signal passing N/S/L/M does not imply any H+1 fill is acceptable.

## No post-hoc tuning

The following are frozen before performance testing:

- price guardrail: $15;
- N buy-zone cap: 5% above pivot;
- S breakout volume ratio: 1.40x 50-day average;
- L RS proxy threshold: 80th percentile;
- M FTD proxy: Day 4+, >=1.00% gain, higher volume;
- M distribution definition: <=-0.20% with higher volume;
- M distribution block: >=6 active days within 25 sessions.

Any alternative must receive a new version and untouched validation evidence.

## Primary references

- IBD How To Buy Stocks infographic: breakout from a chart pattern on high volume; buy within 5% of the buy point.
- IBD educational material on breakout volume: minimum roughly +40-50% above average daily volume.
- IBD Relative Strength guidance: RS Rating 80 or higher is generally desirable for leaders.
- IBD market-trend guidance: follow-through day on Day 4 or later with a significant gain on higher volume; distribution days track institutional selling.
