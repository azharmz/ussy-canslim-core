# Decision Log

## 2026-09-10 — Independent CAN SLIM project
`ussy-canslim-research` is an independent strategy research program. `ussy-trendfoll` remains a separate strategy and is used only as a comparator/reference source.

## 2026-09-10 — Freeze `ussy-fundamentals`
SEC/PIT extraction, production readiness, R2 publication, immutable snapshots, and incremental updates are complete/frozen. Re-open only for regression, factual extraction error, PIT violation, defensible unsupported SEC pattern, or approved contract change.

## 2026-09-10 — PIT boundary
Historical fundamental state may only use SEC information available by the decision-time cutoff. Availability is governed by `accepted_at`, not fiscal-period end.

## 2026-09-10 — R2 production consumer contract
Consumers resolve `fundamentals/current.json` to the latest successfully audited immutable snapshot. Completed research must pin the resolved manifest/checksum, not merely the word `current`.

## 2026-09-10 — Missing/readiness semantics
`UNSUPPORTED_FPI`, `UNRESOLVED_CIK`, `INSUFFICIENT_HISTORY`, and structurally unavailable states are data/readiness states, not automatic CAN SLIM economic verdicts. Missing is not zero; unsupported is not failed.

## 2026-09-10 — Legacy universe is not a CAN SLIM rule
The approximately 199-stock legacy TrendFoll universe came from XTB availability intersected with Musaffa compliance. This external constraint must not be treated as strategy logic.

## 2026-09-10 — Filled/Open H+1 remains an open research issue
TrendFoll's realistic Open H+1 fill is operationally implemented but remains a research issue because large signal-day moves and execution gaps can create chased entries/retracement risk.

## 2026-09-10 — Entry Quality workstream
Entry Quality and fundamental selection are separate causal questions. Research must distinguish improvements from entry discipline versus C/A selection.

## 2026-09-10 — Pre-specified pivot-extension variants
Signal pivot-extension variants are 3%, 5%, and 8%. Do not select a new threshold merely because it maximizes CAGR/PF on observed data.

## 2026-09-10 — Freeze C-v1
C-v1: latest usable quarter EPS YoY >=25% AND revenue YoY >=25%. Undefined/missing growth remains NOT_EVALUABLE, not zero.

## 2026-09-10 — Freeze A-v1
A-v1: latest three consecutive annual EPS YoY observations all evaluable and each >=25%. `PASS_3Y_FALLBACK` remains a separate provenance tier.

## 2026-09-10 — First C/A distribution study
Workflow run `34431101727` completed successfully using pinned fundamentals snapshot:

`fundamentals/snapshots/2026-09-09/run-34417104650/manifest.json`

Among 901 production-ready securities:
- C-v1: 69 PASS, 520 FAIL, 312 NOT_EVALUABLE
- A-v1: 11 PASS, 483 FAIL, 407 NOT_EVALUABLE
- C+A: 3 PASS, 437 FAIL, 461 NOT_EVALUABLE
- C+A PASS symbols: FIX, NBIX, NVDA

Trading-performance metrics were not consulted. **Decision:** keep C-v1/A-v1 frozen; the distribution is evidence about strictness/evaluability, not a reason to tune thresholds.

## 2026-09-10 — Freeze independent technical baseline v1
CAN SLIM must not inherit TrendFoll technical rules by default. A separate, versioned technical baseline is frozen before performance testing.

Primary v1 rules:
- historical Musaffa eligibility, using PIT membership;
- separate $15 price guardrail;
- N-price proxy: generic prior-35-session consolidation, max depth 40%, T0 close above pivot and within 5% of pivot;
- S: T0 volume >=1.40x prior 50-session average volume;
- L: transparent recency-weighted 3/6/9/12-month RS proxy, percentile >=80 within historical eligible universe;
- M: SPY/QQQ follow-through/distribution proxy; Day 4+ FTD >=1.00% on higher volume, distribution day <=-0.20% on higher volume, block at >=6 active distribution days in 25 sessions;
- I remains `NOT_IMPLEMENTED`, never implicit PASS.

IBD/O'Neil concepts and our quantitative proxies are explicitly distinguished. Proprietary IBD RS ratings, pattern recognition and market exposure models are not claimed to be replicated.

Implementation: `src/canslim_research/technical.py`.
CI run `34431906311`: **SUCCESS** after fixing exact 5% boundary floating-point handling. The fix preserved the frozen rule; it did not change the threshold.

## 2026-09-10 — E0 rolling smoke is not historical strategy evidence
Workflow run `34432960298` successfully executed technical baseline v1 against `production/ready/current.json` and pinned SPY data. It produced 14 candidate rows across 13 symbols and 7 dates after the 252-day RS warm-up.

**Decision:** classify this as `ROLLING_CURRENT_MEMBERSHIP_SMOKE_NOT_FULL_PIT_BACKTEST`.

## 2026-09-10 — Full-history OHLCV exists, but PIT membership history does not
Audit run `34433104954` found 1,300 full histories under `backtest/ohlcv/{security_id}.parquet`, but only one historical membership snapshot: `universe/membership/2026-08-28.json`. No QQQ benchmark contract exists.

**Decision:**
- a true expanded-universe PIT track begins only on 2026-08-28 and grows forward as membership snapshots accumulate;
- historical studies that freeze 2026-08-28 membership backward are exploratory/static-universe evidence only;
- current membership must never be backfilled historically and described as PIT;
- exploratory M may be SPY-only only when explicitly labeled; full M-v1 remains SPY-or-QQQ.

## 2026-09-10 — E0 static-history candidate evidence is exploratory only
Workflow run `34433339770` produced 10,731 technical candidate rows across 860 symbols using a static 2026-08-28 compliant universe and long OHLCV history.

Evidence class: `STATIC_2026_08_28_UNIVERSE_EXPLORATORY_NOT_PIT_UNIVERSE`.

**Decision:** use this event set for mechanism diagnostics and implementation development, not for unbiased historical performance inference.

## 2026-09-10 — Freeze independent execution/exit baseline X1
Primary execution baseline `X1_7PCT_STOP_20PCT_PIVOT_TARGET` is frozen as the **control variant**, not as the final CAN SLIM execution model:

- T0 signal after close;
- H+1 open is executable only when `pivot < Open_H+1 <= 1.05 * pivot`;
- one active position per security; later candidate while open = `SKIP_ALREADY_OPEN`;
- hard stop = 7% below actual H+1 fill;
- primary target = 20% above pivot;
- gap-through exits use the session open;
- same-bar stop/target ambiguity is resolved stop-first;
- no arbitrary time stop; sample-end open positions are censored.

This does not inherit TrendFoll ATR stop, EMA20 exit, or 45-session time stop. Eight-week hold is registered as a separate future variant, not silently approximated.

CI run `34433458116`: **SUCCESS**.

## 2026-09-10 — EOD data makes T+1 the first executable control, not a CAN SLIM law
The research pipeline uses completed daily OHLCV. Breakout and full-day volume confirmation for T0 are only known after the T0 close. Therefore an entry at the same T0 close would use information that was not fully available before that fill. The first clean executable opportunity for an EOD-generated signal is the next session, T+1.

This is an **information-availability/execution constraint of the quantitative implementation**, not a claim that original discretionary O'Neil CAN SLIM requires waiting until T+1. Original CAN SLIM is price/setup-driven and may act during the breakout while it is occurring; our daily-EOD implementation cannot claim that intraday fill without intraday data.

**Decision:**
- keep X1 = immediate valid T+1 Open as the executable control;
- do **not** declare T+1 the final/best entry timing rule;
- test alternative causal entry models using only information available before each fill, including a first-valid-entry window through approximately T+3 and pivot-hold/retest confirmation variants;
- any condition evaluated using a day's close can only be filled at the following session's Open;
- hold exit/risk rules constant when comparing entry-timing variants so the experiment isolates timing/execution rather than changing multiple mechanisms at once;
- treat the entry-timing comparison as a basis test before C/C+A strategy ablation.

The purpose is to test whether immediate next-open execution or a short confirmation/retest window better translates CAN SLIM breakout behavior to daily EOD data without look-ahead.

## 2026-09-10 — E1-E4 supports fill-aware anti-chasing, not a new momentum cutoff
Workflow run `34433673545` evaluated 10,731 static-universe candidates under the frozen X1 execution logic.

Entry funnel:
- 5,777 accepted trades;
- 501 `ABOVE_BUY_ZONE_AT_FILL`;
- 726 `BELOW_PIVOT_AT_FILL`;
- 3,727 `SKIP_ALREADY_OPEN`.

The highest T-1->T0 shock quartile was weaker than the lowest, and high shock/gap materially increased the chance that H+1 was already outside the 5% buy zone. Among accepted fills, larger H+1 gaps mainly reduced payoff-to-target rather than changing target-hit rate.

**Decision:**
- the legacy H+1 chasing concern is real as an execution mechanism;
- the frozen 5% actual-fill buy-zone rule is the primary anti-chasing control;
- do not create a new post-hoc momentum or gap threshold from this biased static study;
- keep 3%/5%/8% extension variants pre-specified for later controlled comparison.

The descriptive trade-level PF 1.093 from this run is not a strategy verdict because historical membership is not PIT and portfolio construction is absent.

## 2026-09-10 — Freeze historical C/A identity and as-of contract v1
Audit runs `34433970918` and `34434046658` confirmed:

- fundamental PIT rows are keyed by `symbol + CIK`, not `security_id`;
- the pinned fundamentals snapshot contains `current_universe.csv` with 1,327 unique `security_id` values and one-to-one current symbol/ticker bridge;
- the final readiness report maps symbol to CIK.

Historical research therefore uses the pinned identity chain:

```text
security_id
-> pinned current_universe.csv symbol
-> pinned final readiness report CIK
-> SEC PIT rows
```

Signal cutoff is **16:00 America/New_York on T0**, converted DST-aware to UTC. Only SEC evidence with `accepted_at <= cutoff` may be used.

For C, select the latest fiscal quarter known at cutoff; a later amendment to an older period must not displace a newer fiscal quarter merely because its `accepted_at` is later. Within the chosen fiscal period, use the latest accepted state known by cutoff. If the latest quarter's growth is undefined/missing, C is NOT_EVALUABLE; do not skip backward to manufacture an evaluable value.

For A, within each FY use the latest annual evidence known by cutoff, then evaluate the latest three consecutive FY growth states. Amendments affect only cutoffs after their own acceptance.

Hard invariant: `max(source accepted_at used) <= signal_cutoff_utc`.

Methodology: `docs/methodology/historical-ca-asof-v1.md`.
