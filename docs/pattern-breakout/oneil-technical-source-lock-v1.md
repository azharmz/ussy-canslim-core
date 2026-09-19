# Pattern Breakout Core v1 — O'Neil/IBD Source Lock

Purpose: freeze only rules supported strongly enough for Core v1 implementation. No performance result was consulted.

## Classification

ORIGINAL = documented O'Neil/IBD methodology concept.
OPERATIONALIZATION = deterministic machine translation for daily-EOD implementation.
ENGINEERING = causal/data/lineage behavior, not methodology.
DEFERRED = insufficient source lock for Core v1.

## Entry / breakout

### Proper pivot / buy point

Authority: existing frozen O'Neil Pattern Engine and its independent morphology governance. Core v1 does not recompute or redefine pivot.

### Breakout volume

Official IBD source:
https://www.investors.com/how-to-invest/investors-corner/chart-reading-basics-how-a-buy-point-marks-a-time-of-opportunity/

Source states breakout trading should swell at least 40% above the stock's 50-day average volume.

Core machine rule: breakout_day_volume divided by mean(prior 50 completed-session volumes), confirmed when ratio >= 1.40. Excluding the breakout day from its own denominator is a causal daily OPERATIONALIZATION.

### Buy zone

Official IBD source:
https://www.investors.com/how-to-invest/investors-corner/buy-zone-nvidia-stock/

IBD defines the buy zone as up to 5% above a proper buy point.

Core T+1 adaptation:
- T breakout is established from completed daily data.
- earliest USSY fill is observed T+1 Open.
- pivot <= T+1 Open <= pivot * 1.05 -> executable.
- T+1 Open > pivot * 1.05 -> MISSED_EXTENDED_AT_OPEN.
- T+1 Open < pivot -> BELOW_PIVOT_AT_OPEN / no fill.

The 5% zone is ORIGINAL IBD methodology. Waiting until T+1 Open is USSY OPERATIONALIZATION, not original O'Neil timing.

## Defensive exit

### 7–8% loss rule

Official IBD overview:
https://www.investors.com/how-to-invest/when-to-sell-stocks/

IBD documents cutting losses around 7%–8% below purchase price.

Existing sell_risk_v1.py uses actual fill as the loss reference, with 7% practical trigger and 8% hard ceiling. Eligible for extraction only with explicit Pattern Breakout identity.

## Offensive exit / profit protection

### 20–25% profit zone

Official IBD source:
https://www.investors.com/how-to-invest/investors-corner/when-to-sell-stocks-best-sell-rule-for-growth-stocks/

Official overview:
https://www.investors.com/how-to-invest/when-to-sell-stocks/

IBD documents taking gains around 20%–25% from the proper buy point as a standard offensive sell rule. Core v1 must not convert this into an arbitrary fixed-R target.

### Eight-week hold exception

Official IBD overview:
https://www.investors.com/how-to-invest/when-to-sell-stocks/

IBD documents an exception for unusually strong stocks that gain more than 20% within roughly three weeks, where an eight-week hold rule may apply. Existing machine semantics require dedicated acceptance tests before extraction.

## Technical deterioration

### 10-week moving-average violation in heavy/above-average volume

Official IBD source:
https://www.investors.com/how-to-invest/pulte-phm-stock-americas-greatest-opportunities/

The O'Neil-authored historical lesson states that after buying correctly and being ahead, a winner closing for a week clearly below its 10-week moving average on larger-than-normal volume is a sell rule.

Supporting IBD source:
https://www.investors.com/how-to-invest/investors-corner/when-to-sell-stocks-best-sell-rule-for-growth-stocks/

Existing technical_deterioration_action_v1.py uses weekly close < 10-week MA AND weekly volume > prior-10-week average, then executes at next daily session open. The evidence condition is source-aligned; exact deterministic boundary and next-session-open execution are OPERATIONALIZATION.

## Other technical sell evidence

Official IBD source:
https://www.investors.com/how-to-invest/investors-corner/selling-stocks-netflix-super-micro-tesla-stock/

IBD/O'Neil describes a largest one-day decline after an extended advance as a possible sell signal when confirmed by other evidence; examples include 10-day MA break, long trend-line break, or new highs in declining volume.

Official IBD volume source:
https://www.investors.com/how-to-invest/investors-corner/how-to-sell-stocks-new-highs-in-declining-volume-signal-weakness/

These are ORIGINAL evidence concepts but not yet a single deterministic Core v1 action. Keep EVIDENCE/DEFERRED; do not invent a composite sell score.

## Round-trip rule

Existing round_trip_action_v1.py encodes a prior >=10% gain from buy point followed by a close back at/below pivot.

Current source-lock review did not establish sufficiently direct authoritative support for that exact deterministic threshold/action combination.

Status: DEFERRED FOR PATTERN BREAKOUT CORE V1. Do not copy it merely because it exists.

## Climax top / upper-channel rules

Official IBD educational material documents these concepts, but Core v1 does not yet have a sufficiently complete deterministic source specification for faithful automation.

Status: DEFERRED.

## Core v1 source-locked action set

Entry:
1. frozen proper pattern + pivot;
2. pivot crossing;
3. breakout volume >= 1.40 x prior-50-session mean;
4. causal T+1 Open;
5. 5% buy-zone executability.

Exit:
1. defensive 7–8% loss discipline from actual fill, with causal gap handling;
2. 20–25% offensive profit-zone rule from proper buy point;
3. eight-week exception only after acceptance tests freeze exact machine semantics;
4. weekly 10-week-MA violation on above-normal volume, with causal next-session execution.

Evidence-only / deferred:
- largest one-day decline;
- 10D/21D/50D deterioration observations;
- new highs in declining volume;
- round-trip >=10% then back to pivot;
- climax top;
- upper-channel-line rule.

## No time exit

There is no max-hold rule in Pattern Breakout Core v1. The eight-week rule is a methodology-specific hold exception/profit-management rule, not a generic maximum holding period.

## Implementation gate

Coding may proceed for the source-locked subset only. Anything DEFERRED must remain absent or explicitly evidence-only; it may not silently become an exit action.
