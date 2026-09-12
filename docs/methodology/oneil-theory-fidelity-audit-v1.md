# O'Neil Theory Fidelity Audit v1

Date: 2026-09-12
Status: ACTIVE

## Purpose
Audit frozen CAN SLIM quantitative v1 against William J. O'Neil / IBD methodology. Theory first: `Theory -> specification -> implementation -> validation -> performance`. The 10,731 v1 candidates remain evidence for the old proxy, not CAN SLIM ground truth.

## Workstream status
| # | Workstream | Status |
|---|---|---|
| 25 | Theory Fidelity Audit | ACTIVE |
| 26 | Proper-base definitions | COMPLETE — theory audit |
| 27 | Pivot / buy-point definition | COMPLETE — theory audit |
| 28 | Breakout + volume confirmation | COMPLETE — theory audit |
| 29 | RS / leadership fidelity | COMPLETE — theory audit |
| 30 | C/A/S/I/M role fidelity | NEXT |
| 31 | Sell / risk-management fidelity | NOT STARTED |
| 32 | Theory-faithful candidate specification | NOT STARTED |
| 33 | O'Neil Pattern Recognition Engine | NOT STARTED |
| 34 | Theory-faithful candidate generator | NOT STARTED |
| 35 | New-candidate validation | NOT STARTED |
| 36 | Execution / entry research | PARKED |

## #26 Proper Base — conclusion
Overall v1 proper-base fidelity: **WEAK_PROXY**. The generic prior-35-session/depth<=40% rule captures consolidation broadly but not O'Neil-specific morphology. Future specification must distinguish cup with handle, cup without handle/cup base, double bottom, flat base, and preserve base-on-base, ascending base and IPO-base special structures. No detector thresholds are authorized by #26.

## #27 Pivot / Buy Point — conclusion
Overall v1 pivot fidelity: **WEAK-to-REASONABLE_PROXY**.

```text
pivot_level = pattern-specific structural resistance
```

| Pattern | Structural pivot |
|---|---|
| Cup with handle | highest price in valid handle |
| Cup without handle / cup base | prior / left-side high |
| Double bottom | middle peak of W |
| Flat base | base / left-side high |
| Ascending base | final / pattern structural resistance |
| Base-on-base | pivot from second-base morphology |

Legacy fixed-price buffers above resistance must remain documented as legacy. The 5% buy zone is execution/anti-chasing, not pivot definition. Early/aggressive entries remain separate and X1-X4 remain parked.

## #28 Breakout + Volume Confirmation — conclusion
Overall v1 breakout/volume fidelity: **REASONABLE_PROXY**. Its volume rule is highly faithful; its daily-close condition is stricter than the theory trigger and it conflates the 5% execution zone with candidate-day screening.

### Breakout event vs breakout quality
A conventional breakout begins when price **passes/clears the proper pattern-specific buy point**. A close above resistance and a close high in the day's range are desirable strength evidence, but daily close above pivot is not the universal definition of whether a pivot crossing occurred.

Carry separately into #32:

```text
pivot_crossed_intraday
close_above_pivot
close_position_quality
```

### Volume confirmation
Canonical daily-EOD strong-volume confirmation:

```text
volume_ratio = Volume(T0) / mean(Volume of prior 50 completed sessions)
strong_volume_confirmed = volume_ratio >= 1.40
```

Initial-breakout-day volume confirmation is preferred. If later volume confirms an initially light pivot cross, chronology must be preserved rather than backdating confirmation.

### Gap breakouts and extension
A gap through a proper pivot can be a legitimate breakout. Daily OHLCV R2 can identify `Open > pivot`, gap magnitude, daily price action and daily volume. Intraday breakaway-gap protocols using 5/15-minute bars belong to #36. The normal 5% buy zone is execution/extension state, not breakout identity.

### Audit of frozen v1
| v1 component | Verdict |
|---|---|
| `Close > pivot` | **OVER-STRICT PROXY** |
| `Close <= pivot*1.05` | **SEMANTIC MISMATCH / REASONABLE EXECUTION PROXY** |
| `Volume >=1.40x prior 50d avg` | **HIGH FIDELITY** |
| confirmation only on T0 | **TOO STRICT FOR FULL THEORY** |
| gap handling | **PARTIAL** |

## #29 RS / Leadership Fidelity — conclusion
Overall v1 L/leadership fidelity: **REASONABLE_PROXY, INCOMPLETE**.

The frozen v1 correctly captures one important O'Neil/IBD idea: leaders should rank near the top of the market by relative price performance. But **L is not exhausted by a single cross-sectional percentile threshold**. Authoritative IBD material distinguishes at least three related but non-identical objects:

1. **RS Rating** — cross-sectional price-performance rank versus other stocks;
2. **RS line** — stock price performance versus a benchmark, conventionally the S&P 500;
3. **industry-group leadership** — whether the stock is a leader within a strong/leading group rather than a sympathy laggard.

### RS Rating
IBD's traditional RS Rating is a 1–99 percentile-style rank of price performance over roughly the prior 12 months, with greater emphasis on recent performance. IBD guidance commonly treats **80 or higher** as desirable for emerging leaders; some historical educational material uses 85 or 90 as a stronger screening preference rather than a universal identity rule.

Frozen v1 uses:

```text
RS_proxy_raw =
    0.40 * return_63d
  + 0.20 * return_126d
  + 0.20 * return_189d
  + 0.20 * return_252d

RS_proxy_percentile >= 80
```

This is a transparent approximation and not the proprietary IBD formula. It is conceptually aligned with the historical idea of a recency-weighted 12-month rank and the >=80 leadership threshold.

Important methodology evolution: in 2026 IBD publicly revised the Relative Strength Rating methodology. The 12-month, 6-month and 3-month ratings now use **more data points, multiple comparison periods and adjusted weightings** to respond faster and reduce drop-off effects. Therefore the simple 40/20/20/20 formula must remain labelled a **legacy-aligned proxy**, not an exact current-IBD replication.

### RS line
The RS line is separate from the RS Rating. Conceptually:

```text
RS_line_t ∝ StockPrice_t / Benchmark_t
```

IBD conventionally compares with the S&P 500. A rising line means the stock is outperforming the benchmark; a falling line means underperformance.

For a proper breakout, IBD prefers the RS line to be at or near a new high. A particularly bullish condition is the RS line reaching new high ground **before** the stock's own price breakout. Current IBD guidance also clarifies that the line need not be at an all-time high: being at the highest level of the base-forming period is acceptable, and if short of that level it should at least be trending upward. A falling RS line as price approaches highs is a bearish divergence.

Carry separately into #32 rather than collapsing into `RS_percentile`:

```text
rs_rating_proxy_percentile
rs_line_value
rs_line_slope
rs_line_base_period_high
rs_line_at_base_period_high
rs_line_new_high_before_price
rs_line_bearish_divergence
```

A stock can have a high trailing RS Rating while its current RS line is deteriorating. Therefore `RS percentile >=80` alone can retain former leaders that are weakening now.

### Industry leadership
O'Neil/IBD methodology prefers **leading stocks in leading industry groups**, not weaker sympathy plays. This is distinct from individual-stock RS Rating.

IBD's industry taxonomy/ranking is itself an evolving proprietary data product. In April 2026 IBD consolidated its long-standing 197 industry groups to **145 groups**; 142 groups currently participate in performance ranking. The refreshed ranking uses market-cap weighting and a six-month performance horizon with more data points for responsiveness. This means a faithful research specification must distinguish the enduring theory concept (strong group / strong stock within group) from any specific historical IBD taxonomy or proprietary current ranking.

The current project does not have a PIT-compatible replica of IBD's proprietary industry-group history. Therefore #29 does **not** authorize inventing a hard industry-group threshold from incompatible classifications. Industry leadership should remain an explicit evidence state until a defensible PIT group/ranking contract exists.

### Leader vs laggard semantics
`L` should be interpreted as **leadership evidence**, not merely "RS >= 80 = PASS, otherwise FAIL." A theory-faithful representation should preserve at least:

```text
individual_RS_rating_strength
RS_line_confirmation_or_divergence
industry_group_strength
stock_rank_within_group
```

These may ultimately have different roles (screening criterion, confirmation, descriptor or disqualifier); #30 will audit that role taxonomy across CAN SLIM components before #32 freezes Boolean semantics.

### Audit of frozen v1 L
| v1 component | Verdict | Reason |
|---|---|---|
| recency-weighted ~12-month price-strength score | **REASONABLE_PROXY** | captures historical RS Rating concept, but not proprietary/current 2026 formula |
| cross-sectional percentile rank | **HIGH CONCEPTUAL FIDELITY** | RS Rating is fundamentally a relative rank vs other stocks |
| threshold `>=80` | **HIGH FIDELITY AS GENERAL LEADER SCREEN** | current/historical IBD commonly uses 80+ as desirable, not a universal standalone buy rule |
| RS line vs S&P 500 | **NOT_IMPLEMENTED** | distinct leadership evidence missing |
| RS line new high / base-period high | **NOT_IMPLEMENTED** | important breakout confirmation / early leadership evidence missing |
| RS line bearish divergence | **NOT_IMPLEMENTED** | weakening leader state not represented |
| industry-group strength | **NOT_IMPLEMENTED as strategy input** | v1 diagnostic-only; proprietary/PIT taxonomy not replicated |
| stock leadership within group | **NOT_IMPLEMENTED** | leader-vs-laggard group context missing |

### Frozen #29 principles for #32
1. Preserve **RS Rating** and **RS line** as separate concepts.
2. `RS >=80` is a faithful general leadership screen, not sufficient proof of complete `L` fidelity.
3. Do not claim the v1 40/20/20/20 formula exactly reproduces IBD; current IBD changed its RS calculations in 2026.
4. Add RS-line state relative to the S&P 500 using PIT daily prices available at T0.
5. Prefer RS-line strength at/near the base-period high; preserve "new high before price" as especially bullish evidence.
6. Preserve falling RS line near a price high as bearish-divergence evidence.
7. Keep industry-group leadership conceptually separate from individual RS Rating.
8. Do not fabricate a proprietary IBD industry ranking from incompatible sector classifications; require a defensible PIT classification/ranking contract or preserve `NOT_EVALUABLE/NOT_IMPLEMENTED`.
9. Do not tune RS thresholds or industry cutoffs from CAGR/PF before #32 is frozen.

## #33 — O'Neil Pattern Recognition Engine
After #32 is frozen, #33 will translate the theory specification into reproducible pattern/landmark recognition using existing daily OHLCV R2. Scope includes base segmentation, swing/landmark extraction, named-pattern detectors, base relationships, quality/fault flags, ambiguity handling and morphology validation. It must not optimize definitions against trading performance.

## Guardrails
- Do not retrofit theory-fidelity changes into FWD1.
- Do not mix EXH2 with this audit.
- Do not optimize X3 or other entry rules now.
- Do not tune pattern/breakout/RS thresholds from historical returns.
- Do not treat v1 candidates as O'Neil ground truth.
- Do not start #33 before #32 is frozen.
- Preserve explicit uncertainty/evidence states rather than forcing full confirmation.

## Next action
Proceed with **#30 — C/A/S/I/M Role Fidelity**. Audit whether each CAN SLIM letter functions in O'Neil methodology as a hard Boolean filter, screening criterion, confirmation, descriptor, context, or disqualifier. Then complete #31 before freezing #32.