# E1-E4 Static Trade Diagnostics v1

Workflow run: `34433673545` — **SUCCESS**

Evidence class: `STATIC_2026_08_28_UNIVERSE_EXPLORATORY_NOT_PIT_UNIVERSE`

This study uses the frozen independent technical baseline and frozen execution baseline `X1_7PCT_STOP_20PCT_PIVOT_TARGET`. It is exploratory mechanism evidence only. The 2026-08-28 Musaffa membership is held fixed backward through history, M is SPY-only, and no portfolio construction is modeled.

## Event funnel

From **10,731** technical candidate events across **860** symbols:

| Entry event | Count |
|---|---:|
| `ENTRY_ACCEPTED_V1` | **5,777** |
| `ABOVE_BUY_ZONE_AT_FILL` | **501** |
| `BELOW_PIVOT_AT_FILL` | **726** |
| `SKIP_ALREADY_OPEN` | **3,727** |

Thus H+1 execution is materially different from automatic H+1 filling: 1,227 non-overlap candidate events were rejected because the next open was outside the executable pivot buy zone.

## Accepted-trade outcomes

Accepted trades: **5,777**  
Realized: **5,773**  
Censored open at sample boundary: **4**

| Exit | Count |
|---|---:|
| hard stop 7% | 3,472 |
| stop gap-through | 513 |
| +20% pivot target | 1,528 |
| target gap-through | 260 |
| censored open | 4 |

Descriptive trade-level PF: **1.093**. This is not a production/backtest verdict because the historical universe is not PIT.

Median realized return is **-7.0%** because more than half of realized trades hit the loss side; the positive expectancy/PF comes from the asymmetric target payoff. Median pre-exit MFE is **+6.71%**, median pre-exit MAE **-5.10%**.

## E1 — T-1 -> T0 signal-day shock

Candidate-event distribution:
- p25: +1.99%
- p50: +3.26%
- p75: +4.89%
- p90: +6.91%

Among accepted trades, descriptive quartiles show:

| T-1 -> T0 quartile | PF | Target rate | Stop rate |
|---|---:|---:|---:|
| <= ~2.27% | **1.34** | 34.3% | 65.6% |
| ~2.27-3.59% | 1.00 | 29.1% | 70.9% |
| ~3.59-5.14% | 1.07 | 31.1% | 68.9% |
| > ~5.14% | **0.98** | 29.3% | 70.5% |

Interpretation: the highest-shock quartile is weaker than the lowest-shock quartile, consistent with the legacy retracement concern, but the middle quartiles are not monotonic. This is hypothesis-supporting exploratory evidence, **not** justification to create a new momentum threshold.

High T0 shock also materially increases the chance that H+1 is already above the 5% buy zone: roughly **12.9%** of candidate events in the highest shock quartile versus **0.6%** in the lowest quartile.

## E2 — H+1 execution gap

Candidate-event gap distribution:
- p25: -0.39%
- p50: +0.03%
- p75: +0.60%
- p90: +1.34%

Accepted-trade descriptive quartiles:

| H+1 gap quartile | PF | Target rate | Stop rate |
|---|---:|---:|---:|
| lowest | **1.13** | 31.0% | 68.9% |
| Q2 | 1.12 | 31.0% | 69.0% |
| Q3 | 1.09 | 30.9% | 69.0% |
| highest | **1.04** | 31.0% | 69.0% |

Target/stop rates are almost unchanged, while PF declines with a higher gap. A key mechanism is mechanical: the target is anchored at `pivot * 1.20`, so a higher H+1 purchase price reduces reward-to-target while the hard stop remains 7% below actual fill.

Across all candidate events, **17.0%** of the highest H+1-gap quartile were above the executable 5% buy zone; the lower half had essentially none. Thus the fill-aware buy-zone rule directly prevents a meaningful amount of chasing.

## E3/E4 — Pivot extension

All candidate events, actual H+1 fill extension from pivot:

| Pre-specified threshold | Within | Above |
|---|---:|---:|
| 3% | 7,898 | 2,833 |
| 5% | 10,071 | 660 |
| 8% | 10,622 | 109 |

The primary execution baseline remains **5%** because that was frozen from CAN SLIM methodology before performance testing. The 3% and 8% variants remain pre-specified research comparisons; these counts alone do not select among them.

For accepted trades, the lowest H+1-fill-extension quartile has descriptive PF **1.21**, while the other quartiles are around **1.04-1.07**. The relationship is not cleanly monotonic, so no tighter extension threshold is inferred from this static study.

## Verdict

1. **The legacy H+1 concern is real as an execution mechanism**, especially because large T0 shocks and positive H+1 gaps increase the probability of an overextended H+1 fill.
2. The frozen CAN SLIM 5% fill-zone rule prevents those fills rather than chasing them.
3. Among fills that remain inside the 5% zone, H+1 gap has little relationship with target-hit probability, although larger gaps reduce payoff-to-target.
4. Large T0 shock shows some adverse association, but not enough monotonic evidence to justify a post-hoc momentum cutoff.
5. **Do not tune shock/gap thresholds from this dataset.** Historical membership is not PIT, QQQ is absent, and these are independent trade diagnostics rather than portfolio results.
