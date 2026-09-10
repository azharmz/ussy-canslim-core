# Entry Timing Basis Test v1 — Evidence Record

Workflow run: `34464861119` — **SUCCESS**

Research universe: `CURRENT_COMPLIANT_UNIVERSE_FROZEN_AT_2026_08_28`

Candidate events: **10,731** across **860 securities**.

This study asks how historical CAN SLIM technical candidates behave within the frozen current-compliant research universe. Historical Musaffa membership is not a strategy input to this research question.

All variants use identical exit/risk logic: 7% stop from actual fill, 20% target from pivot, gap-through at open, same-bar ambiguity stop-first, no time stop. Portfolio metrics are not computed.

## Main comparison

| Variant | Entry rule | Entries | Fill rate | Median delay | PF | PF ex-top10 | Target rate | Stop rate | Median MFE | Median MAE |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| X1 | valid T+1 Open | 5,777 | 53.83% | 1 | 1.093 | 1.082 | 30.95% | 68.98% | 6.71% | -5.10% |
| X2 | first valid Open T+1..T+3 | 6,158 | 57.39% | 1 | 1.096 | 1.086 | 31.02% | 68.89% | 6.77% | -5.09% |
| X3 | pivot-hold close confirmation, then next Open | 3,604 | 33.58% | 2 | **1.163** | **1.146** | **32.77%** | **67.18%** | **7.29%** | -5.12% |
| X4 | near-pivot retest-and-hold, then next Open | 4,216 | 39.29% | 2 | 1.109 | 1.093 | 30.95% | 69.00% | 6.92% | -5.13% |

Median realized return is -7% for all variants because more than half of realized trades end at the common hard stop. Therefore PF, hit rates, MFE/MAE, and trade count are more informative than the median alone.

## Subperiod PF

| Variant | <=2004 | 2005-09 | 2010-14 | 2015-19 | 2020-26 |
|---|---:|---:|---:|---:|---:|
| X1 | 1.129 | 0.914 | 1.198 | 1.038 | 1.134 |
| X2 | 1.101 | 0.927 | 1.195 | 1.044 | 1.147 |
| X3 | **1.134** | **1.071** | 1.184 | **1.131** | **1.234** |
| X4 | 1.043 | 1.019 | **1.263** | 1.086 | 1.110 |

X3 exceeds X1 in 4 of 5 coarse subperiods. On annual PF, X3 exceeds X1 in 22 of 34 years where both variants have realized observations; the median annual PF difference is approximately +0.061.

## Concentration robustness

Removing the ten largest positive-return trades leaves:

```text
X1 PF ex-top10 = 1.082
X2 PF ex-top10 = 1.086
X3 PF ex-top10 = 1.146
X4 PF ex-top10 = 1.093
```

Top-10 symbols account for only about 3.7-4.0% of trades in each variant. The top five positive-contributing symbols account for about 5.2-5.4% of positive symbol-level contribution. The X3 result is therefore not visibly driven by a tiny set of symbols.

## Mechanism diagnostic: X1 vs X3

There are **2,775** signal/security events traded by both X1 and X3.

On those common trades:

```text
X1 PF = 1.224
X3 PF = 1.172
mean X3 minus X1 realized return ≈ -0.25 percentage points
```

By contrast, the **3,002 X1 trades not shared with X3** have PF approximately **0.982**. The 829 X3-only trades created by different position timing/availability have PF approximately 1.135.

Interpretation: X3's overall improvement does **not** appear to come from delayed entry producing better fills on the same trades. Its main value is the **pivot-hold confirmation gate**, which avoids a large subset of weaker breakout attempts. The delayed next-open fill slightly hurts the common-trade subset but the selection benefit more than offsets it overall.

## Decision

- X2 adds trades but provides essentially no quality improvement versus X1.
- X4 provides only a modest aggregate improvement and is less stable than X3.
- X3 has the strongest aggregate PF, PF ex-top10, target/stop profile, MFE, and broad subperiod stability, while retaining 3,604 entries.

**Research decision:** promote **X3 pivot-hold confirmation** to the preferred execution baseline for subsequent C/A ablation, while retaining X1 as the control comparator. This is a research-baseline freeze, not a production deployment decision.

Do not tune the X3 hold definition or X4 +2% retest band using this same evidence set. Any altered rule must be versioned as a new hypothesis and independently tested.
