# Decision — P8 prior-uptrend operational correction v0.2

Date: 2026-09-12
Status: ACCEPTED FOR DEVELOPMENT
Scope: #33 / P8 morphology only

## Trigger

The first reference-first authoritative DEVELOPMENT example, SNPS 2023 Flat Base, exposed a detector-definition mismatch before any return/CAGR/PF evidence was inspected.

The frozen source label identifies:

- pattern: `FLAT_BASE`
- left/source anchor: 2023-04-04, high 392.79
- breakout/source end: 2023-05-18
- provenance: Investor's Business Daily

With R2 truncated at the source as-of date, the base body through 2023-05-17 satisfies the existing Flat Base duration, depth and left-high containment gates. The only remaining rejection is the v0.1 prior-uptrend proxy: exactly 40 completed sessions, close-to-close gain >=20%.

Observed DEVELOPMENT diagnostic, using only information available by 2023-04-04:

- 40-session first-close -> pre-base close: +8.05%
- 60-session first-close -> pre-base close: +21.34%
- 80-session first-close -> pre-base close: +20.12%
- lowest low in prior 120 completed sessions -> base-start high: +47.11%

Thus the security clearly had a substantial prior price advance, but the arbitrary exact-40-session sampling point failed to represent it.

## Source/theory check

IBD educational material describes the relevant requirement as a prior price advance rather than an exact 40-session close-to-close change. An IBD Top Stocks educational example states that investors should first seek evidence a stock can move and "demand that they gain 30% or more from any price point" before looking for a flat base. Separate IBD material on base staging says a stock advances through base stages after rising at least 20% from a prior correct buy point to the start of the next base.

Source references:

- https://shop.investors.com/images/promotional/shop/assets/pdf/TopStocks-2020.pdf
- https://shop.investors.com/images/promotional/shop/assets/pdf/TopStocks-2019.pdf

Neither source specifies `40 sessions close-to-close >=20%` as the canonical definition.

## Decision

Replace the v0.1 prior-uptrend proxy with the following v0.2 operational rule:

```text
lookback = prior 120 completed sessions
origin = lowest daily low within that trailing window
endpoint = high of the first session of the proposed base
prior advance = endpoint / origin - 1
PASS if prior advance >= 30%
```

Semantics:

- 30% is source-grounded by the IBD educational guidance above.
- 120 completed sessions (~6 trading months) is a **research-only reproducibility parameter**, not claimed as a uniquely canonical O'Neil horizon.
- Only bars strictly before the base start are searched for the origin; the endpoint is the base-start high. There is no future leakage.
- If 120 completed prior sessions are not supplied, state remains `NOT_EVALUABLE`; the detector must not silently shorten the horizon.
- The production/data runner must therefore provide warm-up context before the requested evaluation interval.

## Flat Base source-window clarification

The authoritative source window may use the breakout day as its end date. The Flat Base body itself is evaluated through the preceding completed session when that session already supplies the valid 5+ week base body. The breakout day is not allowed to inflate body depth or invalidate left-high containment merely because price crossed the pivot.

No new breakout-confirmation rule is introduced here; #28/#32 breakout semantics remain separate. For labelled morphology comparison, a detector body ending immediately before the source breakout date is an acceptable boundary match under the preregistered evaluator tolerance.

## Guardrails

This correction is permitted because it is driven by authoritative morphology disagreement, not trading performance. No post-breakout return, CAGR, PF, win rate, or FWD1 outcome was inspected to choose the rule.

The `VALIDATION` example remains untouched. This decision applies only to DEVELOPMENT until the corrected detector is rerun against a broader reference-first DEVELOPMENT corpus.
