# CAN SLIM Progress Board

Last updated: 2026-09-12

Estimated infrastructure/methodology progress: **~100% for the currently defined v1 research stack**.

This is **not production readiness**. Genuine forward evidence (FWD1) is still at the beginning of its observation clock.

| Area | Status | Canonical evidence / note |
|---|---|---|
| Independent project boundary | COMPLETE | CAN SLIM independent from TrendFoll |
| Research universe | COMPLETE / FROZEN | 1,327 current Musaffa-compliant securities |
| SEC/PIT fundamental engine | COMPLETE / FROZEN | upstream `ussy-fundamentals` |
| C-v1 / A-v1 | COMPLETE / FROZEN | PIT-safe; historical attachment validated |
| Technical baseline | COMPLETE / FROZEN | N/S/L/M proxy baseline |
| Historical candidates | COMPLETE | 10,731 candidates / 860 securities |
| Entry timing X1-X4 | COMPLETE / VALIDATED | X3 preferred; X1 mandatory control |
| Portfolio construction PORT1 | COMPLETE / VALIDATED | frozen 100k / max 7 / 1/7 sizing / RS+volume priority |
| Historical robustness ROB1 | COMPLETE | retrospective, not OOS |
| QQQ/full-M | COMPLETE / NOT PROMOTED | run `34576910915`; risk throttle, lower CAGR |
| EXH2 | PRE-REGISTERED / LIVE | prospective exhaustion sidecar; cannot alter FWD1 |
| FWD1 | LIVE / ACCUMULATING | frozen post-2026-09-09 forward validation |
| I0 identifier feasibility | COMPLETE | 1,010/1,327 deterministic US-ISIN→CUSIP9 |
| I1 current/live 13F PIT | COMPLETE / DATA GATE PASS | run `34603142916` |
| I1 historical 13F state | COMPLETE / VALIDATED | run `34654725293`; all 53 official SEC datasets |
| I1 uncertainty mask | COMPLETE / VALIDATED | run `34656995462` |
| I1 canonical R2 snapshot | COMPLETE / READY | publish run `34663714292` |
| Historical I-v1 attachment | COMPLETE / VALIDATED | run `34663929577`; 0 future-availability violations |
| I-v1 historical ablation | **COMPLETE / NOT PROMOTED** | canonical run `34664388792`; hard I filter not additive for preferred X3 |
| Production integration | BLOCKED | FWD1 review gate not met; historical economics remain weak vs passive SPY |

## Frozen historical baseline

Preferred execution remains X3; X1 remains mandatory control.

```text
X3 trade-level PF            ≈ 1.163
X3 PF ex-top10               ≈ 1.145
PORT1 X3 gross CAGR          ≈ 3.02–3.04%
PORT1 X3 gross max DD        ≈ -43.36%
PORT1 X3 CAGR @20bp RT       ≈ 2.38–2.40%
PORT1 X3 max DD @20bp RT     ≈ -50.94%
SPY price-only CAGR context  ≈ 8.80%
```

C-v1 and A-v1 remain descriptors rather than hard performance filters. Full-M SPY+QQQ was also not promoted.

## Institutional Sponsorship — I-v1

### Data layer

Current/live filing-level validation `34603142916` = SUCCESS:

```text
filings = 9,731
fetch success = 100%
accepted_at complete = 100%
period_of_report complete = 100%
amendments = 383 / 383 classified
ambiguous lineage = 0
latest period = 2026-06-30
latest-period mapped securities = 996
```

Historical state canonical run `34654725293` = SUCCESS:

```text
official SEC datasets = 53 / 53
13F filings = 313,055
state-change events = 14,529,166
unclassified amendment filings = 53
new-holdings without valid base = 0
```

Historical uncertainty run `34656995462` = SUCCESS. Ambiguous lineages are quarantined rather than interpreted as zero sponsorship.

Canonical immutable snapshot was published by run `34663714292`:

```text
pointer = institutional_sponsorship/current.json
manifest = institutional_sponsorship/snapshots/2026-09-12/run-34663714292/manifest.json
history source run = 34654725293
uncertainty source run = 34656995462
```

Historical availability is conservatively frozen as:

```text
available_on = SEC filing_date + 1 calendar day
```

Live/current uses exact EDGAR `accepted_at`. Quarter-end is never treated as availability.

### Frozen I-v1 rule

Preregistered before performance review:

```text
I_delta = manager_count_latest - manager_count_prior
PASS = I_delta > 0
FAIL = I_delta <= 0
NOT_EVALUABLE = missing / non-consecutive / unmapped / uncertain
```

No minimum-manager threshold, percentage-growth threshold, shares threshold, or reported-value threshold was searched.

Historical PIT attachment run `34663929577` = SUCCESS:

```text
candidates       = 10,731
PASS             = 1,902
FAIL             = 2,888
NOT_EVALUABLE    = 5,941
I-evaluable      = 4,790
future violations = 0
```

Main NOT_EVALUABLE reasons were insufficient historical periods (5,778) and unresolved lineage uncertainty (163). Repeated candidate rows from non-US/unmapped securities are also never treated as PASS.

### I-v1 ablation verdict

Canonical run `34664388792` = SUCCESS. Because SEC 13F history begins in 2013, the primary comparison is **I_PASS vs I_EVALUABLE**, not against the 1993–2026 all-history baseline.

Preferred X3:

| Metric | I_EVALUABLE control | I_PASS |
|---|---:|---:|
| Eligible candidates | 4,790 | 1,902 |
| X3 candidate trades | 1,596 | 671 |
| Trade PF | 1.119 | 1.146 |
| PF ex-top10 | **1.086** | **1.071** |
| PORT1 entries | 475 | 331 |
| Gross CAGR | **2.96%** | **2.17%** |
| Gross max DD | **-28.19%** | **-39.02%** |
| CAGR @20bp RT | **2.07%** | **1.57%** |
| Max DD @20bp RT | **-31.97%** | **-43.08%** |

The raw PF increases slightly, but the improvement disappears after removing the ten best trades and portfolio economics deteriorate materially. Therefore **I-v1 is NOT PROMOTED as a hard filter**.

Institutional sponsorship remains a valid CAN SLIM descriptor. No post-hoc search of manager-count thresholds, growth percentages, share growth, or value growth is opened from this result. Any materially different I rule must be a separately preregistered hypothesis with its own validation track.

FWD1 remains unchanged with `I = NOT_IMPLEMENTED` in the frozen strategy semantics.

## FWD1

Forward boundary is exclusive `2026-09-09`; first forward session is `2026-09-10`.

Current canonical state remains:

```text
status = ACCUMULATING
data_gate_pass = true
forward_candidate_count = 0
closed_x3_portfolio_trades = 0
completed_calendar_months = 0
review_eligible = false
```

Formal review requires both:

```text
>= 12 completed calendar months
AND
>= 50 closed X3 portfolio trades
```

Passing the gate means REVIEW_ELIGIBLE, never automatic production promotion.

## EXH2

EXH2 remains prospective and separate from FWD1:

```text
signal_date > 2026-09-11
extreme shock >= +5.3333%
T+1 rejection = Close(T+1) < Open(T+1) AND Close(T+1) < Close(T0)
primary endpoint = breakdown below pivot by T+3
```

Review requires >=50 mature rejected extreme-shock observations and >=50 mature non-rejected extreme-shock controls.

## Periodic control policy

On each control cycle audit `ussy-data`, `ussy-fundamentals`, and `ussy-canslim-research`. Update source-of-truth only for meaningful state transitions, new canonical evidence, resolved blockers, or infrastructure/data-quality failures.

Never modify frozen X3/PORT1/FWD1 semantics from monitoring or interim forward outcomes. Never reinterpret stale/invalid evidence as a zero signal. Do not reopen historical threshold tuning merely to improve outcomes.

## Active work from here

1. Keep FWD1 accumulating unchanged.
2. Keep EXH2 accumulating prospectively.
3. Maintain production OHLCV, SPY/QQQ, fundamentals, and 13F infrastructure/QC.
4. Do not tune C/A, M, I, X3, or PORT1 from retrospective/forward interim outcomes.
5. Revisit production eligibility only when the frozen FWD1 review gate is met.
