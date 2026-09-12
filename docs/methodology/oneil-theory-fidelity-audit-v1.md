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
| 30 | C/A/S/I/M role fidelity | COMPLETE — theory audit |
| 31 | Sell / risk-management fidelity | NEXT |
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

### C — Current quarterly earnings
Authoritative IBD guidance treats strong recent quarterly earnings and sales growth as a **primary fundamental screening criterion**. A common rule of thumb is roughly `>=25%` year-over-year EPS growth, preferably accompanied by strong sales growth and acceleration. Current-quarter strength is evidence that the business is already producing the growth institutions seek.

Role classification:

```text
PRIMARY_SCREENING_CRITERION
+ quality/context evidence (sales growth, acceleration, margins)
```

The v1 rule `EPS YoY >=25% AND Revenue YoY >=25%` is a deliberately strict quantitative approximation. It is faithful to the broad growth-screen concept but should not be described as the only literal O'Neil definition of C. O'Neil/IBD also looks at acceleration, quality and context; exceptional IPO/recovery situations can be discussed separately rather than silently forced into the normal screen.

### A — Annual earnings
Strong annual earnings growth over multiple years is likewise a **primary fundamental screening criterion**, intended to distinguish sustained business quality from a one-quarter spike. Historical O'Neil/IBD material commonly emphasizes about `25%+` growth and strong ROE/consistency.

Role classification:

```text
PRIMARY_SCREENING_CRITERION
+ quality/consistency evidence
```

The v1 requirement that each of the latest three consecutive annual EPS YoY observations be >=25% is a transparent strict proxy. It captures sustained growth but is stronger/more Boolean than the broader theory, which also considers multi-year growth rate, stability, ROE and business context.

### S — Supply and demand
S is fundamentally the **market mechanism** behind price movement, not merely one numeric breakout-volume rule. O'Neil emphasizes supply of shares/float, demand from institutions, volume behavior, buybacks and accumulation. Breakout volume is one important observable manifestation of demand.

Role classification:

```text
CONFIRMATION / DEMAND EVIDENCE
+ structural descriptor (share supply / float / buybacks)
```

Therefore v1 `Volume >=1.40x prior-50d average` is highly faithful as a **breakout-demand confirmation**, but it is not a complete representation of S. Shares outstanding/float/buybacks and broader accumulation remain separate evidence rather than mandatory invented gates.

### I — Institutional sponsorship
I asks whether capable institutional investors are sponsoring the stock and whether sponsorship is improving. Authoritative IBD material favors **increasing institutional ownership**, quality of owning funds and price/volume accumulation; institutions are also the dominant source of demand in leading growth stocks.

Role classification:

```text
CONFIRMATION / QUALITY EVIDENCE
+ trend descriptor
```

The theory does **not** support treating one arbitrary manager-count-delta threshold as the whole meaning of I. The v1 13F rule `manager_count_latest - manager_count_prior > 0` is a transparent narrow proxy for increasing sponsorship. Its historical non-promotion as a hard filter is therefore not a contradiction of CAN SLIM: I can remain important evidence without functioning as a universal binary gate.

For #32 preserve distinct evidence such as:

```text
fund_count_trend
quality_of_sponsors          # if defensibly measurable
ownership_concentration
price_volume_accumulation
institutional_state_evaluable
```

Do not invent unavailable proprietary Sponsorship/Accumulation ratings.

### M — Market direction
M has the clearest **timing-gate/context** role. IBD states that most stocks move with the general market; a follow-through day gives a green light to begin buying leading stocks, while a `market in correction` means **new buys are off the table**. Distribution days and exposure guidance modulate risk as an uptrend weakens.

Role classification:

```text
MARKET_CONTEXT
+ ENTRY_TIMING_GATE
+ RISK_THROTTLE / DISQUALIFIER for new buys in correction
```

This is categorically different from C/A. M is not a company-quality attribute; it controls whether otherwise attractive setups should be acted upon and at what exposure.

The frozen v1 SPY-only/full-M proxies are acknowledged approximations of proprietary IBD market-state interpretation. The prior full-M SPY+QQQ ablation result must not be used to redefine theory: lower historical CAGR does not negate M's theoretical timing/risk role.

### Role matrix
| Component | Primary theoretical role | Secondary role | v1 role fidelity |
|---|---|---|---|
| C | **Screening criterion** | growth quality/acceleration | **REASONABLE but over-Boolean** |
| A | **Screening criterion** | consistency/quality | **REASONABLE but over-Boolean** |
| S | **Demand confirmation/evidence** | supply/float descriptor | **PARTIAL** — breakout volume strong, full S incomplete |
| I | **Institutional confirmation/evidence** | sponsorship trend/quality descriptor | **PARTIAL** — manager-count delta narrow proxy |
| M | **Market timing/context gate** | exposure/risk throttle, disqualifier for new buys in correction | **CONCEPTUALLY HIGH, implementation proxy** |

### Implication for prior ablations
The historical findings that hard C, hard I and stricter full-M did not improve v1 economics must **not** be reinterpreted as evidence that C/I/M are theoretically irrelevant. Those ablations answered whether specific quantitative Boolean proxies added historical performance to v1; #30 answers a different question: what role the original methodology assigns to each component.

This distinction is now frozen:

```text
THEORY_ROLE != HISTORICAL_ABLATION_RESULT
```

A component can remain theoretically important while a particular proxy is not promoted as a hard performance filter.

### Frozen #30 principles for #32
1. Do not force all CAN SLIM letters into identical Boolean semantics.
2. Treat C and A primarily as **fundamental screening criteria**, while preserving growth quality/acceleration context.
3. Treat S primarily as **supply/demand evidence and breakout confirmation**; breakout volume is not the entirety of S.
4. Treat I as **institutional sponsorship confirmation/evidence**, not automatically a single hard manager-count gate.
5. Treat M as **market context + timing gate + risk throttle**; correction state can disqualify new buys even when company/setup evidence is strong.
6. Preserve `NOT_EVALUABLE/NOT_IMPLEMENTED` rather than coercing missing evidence to FAIL or PASS.
7. Keep theory roles separate from v1 performance-ablation outcomes.
8. No threshold changes may be selected from historical CAGR/PF before #32 is frozen.

## #33 — O'Neil Pattern Recognition Engine
After #32 is frozen, #33 will translate the theory specification into reproducible pattern/landmark recognition using existing daily OHLCV R2. Scope includes base segmentation, swing/landmark extraction, named-pattern detectors, base relationships, quality/fault flags, ambiguity handling and morphology validation. It must not optimize definitions against trading performance.

## Guardrails
- Do not retrofit theory-fidelity changes into FWD1.
- Do not mix EXH2 with this audit.
- Do not optimize X3 or other entry rules now.
- Do not tune pattern/breakout/RS/C/A/S/I/M thresholds from historical returns.
- Do not treat v1 candidates as O'Neil ground truth.
- Do not start #33 before #32 is frozen.
- Preserve explicit uncertainty/evidence states rather than forcing full confirmation.

## Next action
Proceed with **#31 — Sell / Risk-Management Fidelity**. Audit initial loss cutting, failed breakouts, profit-taking, holding exceptional winners, round-trip behavior and major sell signals. After #31, freeze #32 before any #33 implementation.