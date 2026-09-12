# O'Neil Theory Fidelity Audit v1

Date: 2026-09-12
Status: COMPLETE — #25 theory audit closed; #32 specification is next

## Purpose
Audit frozen CAN SLIM quantitative v1 against William J. O'Neil / IBD methodology. Theory first: `Theory -> specification -> implementation -> validation -> performance`. The 10,731 v1 candidates remain evidence for the old proxy, not CAN SLIM ground truth.

## Workstream status
| # | Workstream | Status |
|---|---|---|
| 25 | Theory Fidelity Audit | COMPLETE |
| 26 | Proper-base definitions | COMPLETE — theory audit |
| 27 | Pivot / buy-point definition | COMPLETE — theory audit |
| 28 | Breakout + volume confirmation | COMPLETE — theory audit |
| 29 | RS / leadership fidelity | COMPLETE — theory audit |
| 30 | C/A/S/I/M role fidelity | COMPLETE — theory audit |
| 31 | Sell / risk-management fidelity | COMPLETE — theory audit |
| 32 | Theory-faithful candidate specification | NEXT |
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

Legacy fixed-price buffers above resistance remain documented as legacy. The 5% buy zone is execution/anti-chasing, not pivot definition. Early/aggressive entries remain separate and X1-X4 remain parked.

## #28 Breakout + Volume Confirmation — conclusion
Overall v1 breakout/volume fidelity: **REASONABLE_PROXY**. Its volume rule is highly faithful; its daily-close condition is stricter than the theory trigger and it conflates the 5% execution zone with candidate-day screening.

Carry separately into #32:

```text
pivot_crossed_intraday
close_above_pivot
close_position_quality
volume_ratio
strong_volume_confirmed
later_volume_confirmation_date
gap_through_pivot
extension_from_pivot
```

Canonical daily-EOD strong-volume confirmation:

```text
volume_ratio = Volume(T0) / mean(Volume of prior 50 completed sessions)
strong_volume_confirmed = volume_ratio >= 1.40
```

Initial-breakout-day volume confirmation is preferred. A later confirmation must preserve chronology rather than backdate T0. Gap-through-pivot can be valid; special intraday breakaway-gap protocols belong to #36. The 5% buy zone is execution/extension state, not breakout identity.

## #29 RS / Leadership Fidelity — conclusion
Overall v1 L/leadership fidelity: **REASONABLE_PROXY, INCOMPLETE**.

The frozen v1 correctly captures one important O'Neil/IBD idea: leaders should rank near the top of the market by relative price performance. But `L` is not exhausted by a single cross-sectional percentile threshold. Authoritative IBD material distinguishes RS Rating, RS line, and industry-group leadership.

Frozen principles for #32:

```text
rs_rating_proxy_percentile
rs_line_value
rs_line_slope
rs_line_base_period_high
rs_line_at_base_period_high
rs_line_new_high_before_price
rs_line_bearish_divergence
industry_group_strength
stock_rank_within_group
```

The v1 `RS_proxy_percentile >= 80` is a faithful general leader screen, but the 40/20/20/20 formula remains a transparent legacy-aligned proxy rather than an exact current-IBD replication. RS-line and industry leadership are not implemented in v1.

## #30 C/A/S/I/M Role Fidelity — conclusion
The central finding is that CAN SLIM letters are **not all the same kind of Boolean gate**. O'Neil/IBD combines screening criteria, confirmation/evidence, market context and timing/disqualification. A theory-faithful engine should preserve those roles instead of forcing every letter into identical `PASS/FAIL` semantics.

| Component | Primary theoretical role | Secondary role | v1 role fidelity |
|---|---|---|---|
| C | **fundamental screening criterion** | growth quality / acceleration | **REASONABLE but over-Boolean** |
| A | **fundamental screening criterion** | consistency / quality | **REASONABLE but over-Boolean** |
| S | **supply-demand confirmation/evidence** | float/shares/buyback descriptor | **PARTIAL** |
| I | **institutional sponsorship confirmation/evidence** | sponsorship trend / sponsor quality | **PARTIAL** |
| M | **market context + entry timing gate** | exposure/risk throttle; disqualifier for new buys in correction | **CONCEPTUALLY HIGH, implementation proxy** |

This distinction is frozen:

```text
THEORY_ROLE != HISTORICAL_ABLATION_RESULT
```

Hard C/I or stricter M not improving historical v1 CAGR/PF does not redefine the theoretical role of C/I/M.

## #31 Sell / Risk-Management Fidelity — conclusion
O'Neil/IBD sell discipline is not a single exit rule. It is a layered state machine combining **capital protection, failed-breakout defense, profit-taking, exceptional-winner hold logic, technical deterioration, climax behavior and market-level exposure reduction**. Frozen v1's X1-X4/X3 work was an execution experiment and must not be treated as a faithful implementation of the original sell discipline.

### 1. Initial loss cutting — hard defensive ceiling
The clearest defensive rule is to cut a losing position at roughly **7%-8% below the actual purchase price**, not 7%-8% below the chart pivot. Current IBD practical guidance increasingly describes 7% as the actionable trigger while historical O'Neil/IBD materials commonly state 7%-8% as the absolute maximum. The average realized loss should ideally be smaller, and weak/bear markets can justify earlier exits around 3%-5%.

Canonical semantics for #32/#36:

```text
initial_stop_reference = actual_fill_price
hard_loss_limit_legacy = 7_to_8_percent
current_practical_trigger ≈ 7_percent
```

This is a **capital-protection rule**, not a pattern-quality rule. A stock can remain fundamentally attractive after the position is sold; re-entry on a later valid setup is allowed.

### 2. Failed breakout / early deterioration
A breakout that quickly fails is important evidence. The system should preserve separately:

```text
fell_back_below_pivot
loss_from_fill
break_10d_or_21d
break_50d_or_10w
heavy_volume_break
largest_down_volume_since_breakout
```

The hard loss ceiling remains independent of these technical warnings. A sharp break of the 50-day/10-week line in heavy volume is a major sell signal because it indicates institutional distribution. A first decisive break of the 10-week line after a sustained advance is especially important. Shorter moving averages such as the 10-day/21-day can provide earlier, more tactical warnings but are not substitutes for the universal maximum-loss discipline.

### 3. Default profit-taking zone
The standard O'Neil/IBD offensive rule is to take at least some profits after a normal winner rises about **20%-25% from the proper buy point**. The rationale is that many leaders pause or correct after an initial run of that magnitude.

Canonical state:

```text
profit_from_buy_point
normal_profit_zone = 20_to_25_percent
```

This is a default profit-management rule, not a claim that every position must be fully liquidated at +20% or +25%.

### 4. Eight-week hold exception for exceptional strength
A major exception applies when a stock rises **20% or more within roughly the first 1-3 weeks after breakout**. O'Neil/IBD treats that unusually fast advance as evidence of a potential exceptional leader and recommends trying to hold it for **at least eight weeks from the breakout** before reassessing.

Preserve chronology:

```text
reached_20pct_within_first_3_weeks
exceptional_winner_hold_rule_active
eight_week_assessment_date
```

This exception must not be confused with blindly ignoring hard loss or severe technical sell signals.

### 5. Round-trip sell behavior
If a stock earns a meaningful/double-digit gain and then gives back the entire advance to the buy point, O'Neil/IBD treats that round trip as a sell warning/rule. A former winner should not automatically be allowed to turn into a loser merely because it once showed strength.

Preserve:

```text
max_gain_from_entry
round_trip_to_buy_point
```

This is distinct from the initial 7%-8% stop: the position first created a profit cushion and then lost it.

### 6. Climax-top / exhaustion behavior
For mature winners after a substantial run, O'Neil/IBD recognizes **climax tops**: the advance becomes abnormally fast and extended, often accompanied by exhaustion gaps, unusually large daily point gains, wide price swings, sharp reversals and extreme distance above long moving averages. Historical IBD guidance describes a hallmark as roughly **25%-50% gain in three weeks or less**, often after the stock has already been advancing for many weeks; extreme extension above the 200-day line is additional evidence.

This is not an ordinary fixed take-profit threshold. It is a **late-stage exhaustion state** requiring multiple contextual features. #32 should preserve the concept and evidence fields; exact detector design belongs to later specification/implementation and must not be tuned from returns.

### 7. Market-level defense
Sell/risk management also interacts with M. O'Neil/IBD explicitly identifies reducing exposure because of market distribution as one of the main reasons to sell. Therefore stock-level exits and portfolio-level exposure are separate layers:

```text
stock_sell_state
market_exposure_state
```

A weakening market can justify raising cash, taking profits, avoiding new buys and tightening risk even before every individual stock hits a hard sell threshold.

### 8. Position sizing is part of risk management, but not the same as the sell signal
IBD risk-management education commonly illustrates sizing positions so that a predefined stop corresponds to a controlled portfolio loss (for example, a 1% portfolio-risk budget). This is useful portfolio construction, but the exact risk-budget percentage is not frozen here as a universal O'Neil CAN SLIM identity rule.

Carry the separation:

```text
position_size_policy
initial_stop_policy
sell_signal_state
```

Do not optimize one by silently changing another.

### 9. Earnings/event risk
Earnings announcements can gap through ordinary stops. IBD discusses managing earnings risk separately, including reducing exposure or using specific options strategies. The daily-OHLCV CAN SLIM candidate specification should record event-risk state where available, but #31 does not authorize fabricating intraday fills or option mechanics. Those belong to execution/risk research (#36) if pursued.

### Audit of frozen v1 execution/sell work
| Area | v1 state | Fidelity verdict |
|---|---|---|
| 7%-8% max loss from actual fill | not the governing canonical X3 rule | **NOT FAITHFULLY IMPLEMENTED as core sell discipline** |
| early failed-breakout state | partially observable in OHLCV, not canonical exit framework | **PARTIAL** |
| 50d/10w heavy-volume break | not canonical sell engine | **NOT IMPLEMENTED as theory-faithful rule** |
| normal +20%-25% profit zone | not canonical sell engine | **NOT IMPLEMENTED** |
| 8-week hold exception | not canonical sell engine | **NOT IMPLEMENTED** |
| round-trip rule | not canonical sell engine | **NOT IMPLEMENTED** |
| climax/exhaustion sell state | EXH2 is separate prospective research and must not be relabeled as canonical O'Neil implementation | **SEPARATE / NOT IMPLEMENTED in CAN SLIM v1** |
| market-driven exposure reduction | v1 M studied mainly as candidate gate/ablation | **PARTIAL** |
| position sizing/risk budget | PORT1 exists, but not derived as O'Neil-faithful risk contract | **SEPARATE PROXY** |

### Frozen #31 principles for #32/#36
1. Treat **capital protection** as first priority; preserve a hard maximum-loss discipline referenced to **actual purchase/fill price**.
2. Preserve historical 7%-8% language and current practical ~7% trigger without pretending the evolution never occurred.
3. Failed breakout and technical deterioration are additional sell evidence, not replacements for the maximum-loss rule.
4. Preserve 50-day/10-week heavy-volume breaks as major institutional-selling evidence.
5. Preserve the normal **20%-25% profit zone** as default profit-management guidance.
6. Preserve the **8-week hold exception** when +20% is reached within the first 1-3 weeks after breakout.
7. Preserve **round-trip** behavior separately from ordinary stop loss.
8. Treat climax tops as contextual late-stage exhaustion, not a single arbitrary percentage threshold.
9. Keep stock-level sell signals separate from market-level exposure/risk throttling.
10. Keep position sizing, stop placement, event risk and execution mechanics as distinct contracts.
11. Do not retrofit #31 into frozen FWD1/X3 or EXH2.
12. Do not tune sell thresholds from historical CAGR/PF before the theory-faithful specification is frozen.

## #25 Theory Fidelity Audit — consolidated close
Workstreams #26-#31 are now complete. The main conclusion is that frozen CAN SLIM quantitative v1 is a **transparent proxy research system**, not a faithful reconstruction of O'Neil/IBD methodology. Its strongest fidelity areas are breakout-volume confirmation and general RS percentile leadership screening; its largest gaps are proper-base morphology, pattern-specific landmarks/pivots, full RS-line/group leadership context, nuanced component roles, and canonical O'Neil sell/risk discipline.

This closes the **theory audit**, not the implementation project. The next required step is #32: translate the frozen theory findings into an explicit, versioned, testable **Theory-Faithful Candidate Specification** without selecting rules based on historical performance.

## #33 — O'Neil Pattern Recognition Engine
After #32 is frozen, #33 will translate the theory specification into reproducible pattern/landmark recognition using existing daily OHLCV R2. Scope includes base segmentation, swing/landmark extraction, named-pattern detectors, base relationships, quality/fault flags, ambiguity handling and morphology validation. It must not optimize definitions against trading performance.

## Guardrails
- Do not retrofit theory-fidelity changes into FWD1.
- Do not mix EXH2 with this audit or relabel EXH2 as the O'Neil sell engine.
- Do not optimize X3 or other entry rules now.
- Do not tune pattern/breakout/RS/C/A/S/I/M/sell thresholds from historical returns.
- Do not treat v1 candidates as O'Neil ground truth.
- Do not start #33 before #32 is frozen.
- Preserve explicit uncertainty/evidence states rather than forcing full confirmation.

## Next action
Proceed with **#32 — Theory-Faithful Candidate Specification**. Convert #26-#31 into a versioned contract covering required data, evidence states, pattern/base semantics, pivot, breakout/volume, leadership, component-role semantics and candidate eligibility. Keep execution/entry mechanics and the detailed sell engine outside the candidate-generation contract where appropriate; those remain downstream concerns.