# Decision Log

## 2026-09-10 — Independent CAN SLIM project
`ussy-canslim-research` is an independent strategy research program. `ussy-trendfoll` remains separate and is only a comparator/reference source.

## 2026-09-10 — Freeze `ussy-fundamentals`
SEC/PIT extraction, readiness, R2 publication, immutable snapshots, and incremental updates are COMPLETE/FROZEN. Re-open only for regression, factual extraction error, PIT violation, defensible unsupported SEC pattern, or approved contract change.

## 2026-09-10 — Fundamental PIT boundary
Historical fundamental state may only use SEC information known by the decision-time cutoff. Availability is governed by `accepted_at`, never fiscal-period end.

## 2026-09-10 — R2 consumer contract
Consumers resolve `fundamentals/current.json` to an immutable snapshot. Research evidence must pin the resolved manifest/checksum, not merely the word `current`.

## 2026-09-10 — Missing/readiness semantics
Missing is not zero. Unsupported is not failed. `UNSUPPORTED_FPI`, `UNRESOLVED_CIK`, `INSUFFICIENT_HISTORY`, and structural-unavailability states are data/readiness states, not automatic CAN SLIM economic verdicts.

## 2026-09-10 — Legacy TrendFoll universe is not CAN SLIM logic
The approximately 199-stock TrendFoll universe came from XTB availability intersected with Musaffa compliance. This external constraint is not inherited as CAN SLIM strategy logic.

## 2026-09-10 — Research universe = frozen current-compliant universe
**This supersedes the earlier assumption that historical Musaffa membership is required for the primary historical research track.**

The primary CAN SLIM research question is:

> How would the strategy rules have behaved historically on the securities that belong to the selected contemporary/current Musaffa-compliant research universe?

Therefore:

- freeze the selected current Musaffa-compliant universe for reproducibility;
- historical Musaffa compliance is **not** a strategy input and is **not a blocker**;
- do not claim this reconstructs which stocks were compliant at every historical date;
- PIT rules still apply to information actually used to make the historical decision: OHLCV/market state through T0 and SEC facts only after `accepted_at`.

Historical membership snapshots may still be useful for a separate historical-eligibility research question, but they are not required for this project's primary backtest.

## 2026-09-10 — C-v1 frozen
Latest usable quarterly state known at decision time:

```text
EPS YoY >= 25%
AND
Revenue YoY >= 25%
```

Undefined/missing growth remains NOT_EVALUABLE.

## 2026-09-10 — C-v1 revenue evaluability guardrail
Revenue growth is a required C-v1 input, not an optional enhancement or fallback field. The consumer must not issue an EPS-only C verdict when revenue YoY is missing or undefined.

Frozen semantics:

```text
EPS evaluable + Revenue missing      -> NOT_EVALUABLE
EPS missing    + Revenue evaluable    -> NOT_EVALUABLE
EPS missing    + Revenue missing      -> NOT_EVALUABLE
Both evaluable; either < 25%          -> FAIL
Both evaluable; both >= 25%           -> PASS
```

Missing revenue is therefore a coverage/evaluability condition. It must not be coerced to 0%, treated as FAIL merely because it is missing, or silently ignored to manufacture PASS. This guardrail applies to current and historical C attachment and must be enforced before any C/C+A performance ablation is considered valid.

## 2026-09-10 — A-v1 frozen
Latest three consecutive annual EPS YoY states must all be evaluable and each >=25%. `PASS_3Y_FALLBACK` remains a separate provenance tier.

## 2026-09-10 — First C/A distribution
Run `34431101727`, pinned manifest `fundamentals/snapshots/2026-09-09/run-34417104650/manifest.json`:

```text
C-v1   PASS 69 | FAIL 520 | NOT_EVALUABLE 312
A-v1   PASS 11 | FAIL 483 | NOT_EVALUABLE 407
C+A    PASS  3 | FAIL 437 | NOT_EVALUABLE 461
```

No trading metrics were used. Thresholds remain frozen.

## 2026-09-10 — Independent technical baseline v1 frozen
CAN SLIM does not inherit TrendFoll technical rules by default.

Primary technical v1:

- price floor $15;
- generic prior-35-session base proxy, max depth 40%;
- T0 close above pivot and <=5% above pivot;
- breakout volume >=1.40x prior 50-session average;
- transparent recency-weighted RS proxy, percentile >=80;
- M follow-through/distribution proxy; current historical exploratory work is SPY-only because QQQ contract is absent;
- I remains NOT_IMPLEMENTED, never implicit PASS.

Technical CI run `34431906311` = SUCCESS.

## 2026-09-10 — Historical technical candidate set
Using the frozen current-compliant universe and long OHLCV, the historical engine generated **10,731 technical candidates across 860 securities**.

These candidates are valid for the stated research-universe question. They should not be described as a historical Musaffa-eligibility reconstruction.

## 2026-09-10 — Daily-EOD information timing
The T0 breakout and complete T0 volume are only known after T0 close. Therefore an assumed fill at the same T0 close is not executable in the daily-EOD pipeline.

T+1 Open is the earliest clean executable opportunity, but **T+1 is not assumed to be the best entry rule or a literal O'Neil requirement**.

Any rule that requires a day's Close may only enter at the following session Open.

## 2026-09-10 — X1 control execution
X1 is retained as the immediate executable control:

```text
T0 signal after close
-> T+1 Open if pivot < Open <= 1.05*pivot
-> stop = actual fill * 0.93
-> target = pivot * 1.20
-> gap-through uses Open
-> same-bar stop/target ambiguity = stop first
-> no arbitrary time stop
```

Execution CI run `34433458116` = SUCCESS.

## 2026-09-10 — Entry-quality mechanism evidence
Run `34433673545` on 10,731 candidates under X1:

```text
5,777 entries
501 T+1 above 5% buy zone
726 T+1 at/below pivot
3,727 skipped because same security already open
```

Large T0 shocks/gaps increase chasing risk, but no post-hoc momentum/gap threshold is adopted. The 5% actual-fill buy-zone rule remains the anti-chasing control.

## 2026-09-10 — X1-X4 entry timing basis test pre-specified
To isolate entry timing, all variants use identical stop/target rules.

- X1: valid T+1 Open;
- X2: first valid Open T+1..T+3;
- X3: full-bar pivot-hold confirmation on T+1/T+2, then next valid Open by T+3;
- X4: near-pivot retest-and-hold proxy on T+1/T+2, then next valid Open by T+3.

X3/X4 definitions were frozen before comparative performance review. See `docs/methodology/entry-timing-basis-test-v1.md`.

## 2026-09-10 — Entry Timing Basis Test result: X3 preferred
Run `34464861119` = SUCCESS; 13 timing/execution tests passed.

| Variant | Entries | PF | PF ex-top10 | Target rate | Stop rate |
|---|---:|---:|---:|---:|---:|
| X1 | 5,777 | 1.093 | 1.082 | 30.95% | 68.98% |
| X2 | 6,158 | 1.096 | 1.086 | 31.02% | 68.89% |
| **X3** | **3,604** | **1.163** | **1.146** | **32.77%** | **67.18%** |
| X4 | 4,216 | 1.109 | 1.093 | 30.95% | 69.00% |

X3 exceeds X1 in 4/5 coarse subperiods and in 22/34 individual years with observations for both. PF ex-top10 remains stronger and the result is not visibly concentrated in a few symbols.

Mechanism check:

- 2,775 events traded by both X1 and X3: X1 PF ~1.224 vs X3 PF ~1.172;
- 3,002 X1 trades not shared with X3: PF ~0.982.

Interpretation: X3's improvement primarily comes from **filtering breakout attempts that fail to demonstrate pivot hold**, not from delayed entry improving the same trades.

**Decision:** X3 is the current preferred research execution baseline and X1 remains mandatory control. This preference is not a production decision and does not close additional entry-quality research.

Detailed record: `results/entry-timing-basis-test-v1/README.md`.

## 2026-09-10 — Post-breakout exhaustion diagnostic: interaction matters more than shock alone
Run `34466747136` = SUCCESS on the same 10,731 technical candidates.

Within the highest shock quintile, T+1 bearish rejection plus Close < T0 Close is strongly associated with poor outcomes, while high shock without rejection is not. This supports the *mechanism hypothesis* that large T0 expansion becomes dangerous when the following session confirms rejection, rather than a simplistic rule that all large T0 momentum is bad.

**Decision:** no hard T-1->T0 momentum cutoff is adopted from this discovery sample; register `high shock × T+1 rejection` as EXH2 for independent validation.

## 2026-09-10 — Historical C/A identity and as-of contract
Fundamental PIT rows are keyed by symbol+CIK, while the pinned universe bridge exposes security_id. Historical research uses:

```text
security_id
-> pinned universe symbol
-> CIK
-> SEC PIT rows
```

Decision cutoff: 16:00 America/New_York on T0, converted DST-aware to UTC. Only `accepted_at <= cutoff` is eligible.

For C, choose latest fiscal period known at cutoff, then latest accepted state within that period. Older-period amendments cannot displace a newer fiscal period merely because they are accepted later. If the latest quarter is undefined, do not skip backward to manufacture an evaluable C state.

For A, retain latest accepted annual state within each FY, then evaluate the latest three consecutive FY growth states.

Hard invariant: `max(source accepted_at used) <= signal_cutoff_utc`.

## 2026-09-10 — C/A period-semantics audit passed
Run `34434268817` = SUCCESS. The dataset supports the frozen latest-period/latest-accepted-within-period selector. Q4 and amendments remain governed by upstream semantics; downstream must not reinterpret missing Q4 EPS as zero.

## 2026-09-10 — Historical C/A attachment validated
Run `34479060107` = SUCCESS. All 10,731 technical candidates receive exactly one C/A attachment; future accepted-at violations = 0. A-PASS requires three resolved consecutive SEC fiscal years. Historical distribution:

```text
C-v1   PASS 703 | FAIL 3,475 | NOT_EVALUABLE 6,553
A-v1   PASS  34 | FAIL   768 | NOT_EVALUABLE 9,929
C+A    PASS   2 | FAIL   650 | NOT_EVALUABLE 10,079
```

## 2026-09-10 — Fundamental ablation result
Run `34481587218` = SUCCESS.

Hard C filtering does not improve X3 or X1. For X3, PF falls from ~1.163 to ~1.020 and PF ex-top10 from ~1.146 to ~0.861. C+A is too sparse for strategy inference with only two historical events.

**Decision:** C and A remain frozen CAN SLIM descriptors; do not promote hard C/C+A filters as additive edge and do not tune the 25% thresholds post hoc.

## 2026-09-10 — Portfolio construction validated
Canonical run `34488197400` = SUCCESS. Frozen PORT1 specification: 100,000 initial equity, long-only/no leverage, max 7 positions, 1/7 prior-close-equity sizing, deterministic RS/volume priority, entries before same-day exits, X3 BASE primary, X1 BASE mandatory control.

Canonical X3 results:

```text
gross total return  +172.90%
gross CAGR           +3.04%
gross max DD        -43.36%
20bp RT CAGR          +2.40%
20bp RT max DD       -50.94%
```

X3 retains a clear relative advantage over X1 under capital constraints, but the absolute profile is not production-ready. Censored positions at the sample boundary remain mark-to-market, not forced exits.

## 2026-09-10 — ROB1 historical robustness validated
Run `34488295631` = SUCCESS. Artifact SHA-256 `5e1ff152b9e0cb75ebb517e716dede8624dfac01885d6d898efd1274d02977eb`.

ROB1 is retrospective historical robustness evidence only and must **not** be described as true OOS because X3 was selected using historical evidence before ROB1.

Key findings:

```text
accepted portfolio PF:
X1 ~1.060
X3 ~1.162

capital-constrained not-accepted PF:
X1 ~1.104
X3 ~1.164
```

The frozen RS/volume priority therefore shows essentially no incremental selection edge for X3.

X3 gross five coarse calendar-block returns:

```text
+63.45%
 -8.30%
 -9.09%
+33.74%
+49.89%
```

Two of five blocks lose money. Across 34 calendar years, X3 gross has 21 positive and 13 negative years, with median annual return ~+2.38%.

Comparable SPY price-only context is ~8.80% CAGR with ~-56.47% max DD, versus X3 gross ~3.04% CAGR with ~-43.36% max DD. SPY dividends are excluded, so a total-return benchmark would widen the return gap.

**Decision:** retain X3 as research baseline versus X1 control, but do not tune X3/PORT1 from ROB1, do not promote to production, and do not relabel any retrospective split as OOS.

Detailed record: `docs/decisions/2026-09-10-robustness-v1.md`.

## 2026-09-10 — Genuine forward-validation gate frozen
The next evidentiary stage is FWD1. Forward observations begin strictly after 2026-09-09 using unchanged X3/PORT1 rules.

Production inference is blocked until both are satisfied:

```text
>= 12 calendar months
>= 50 closed X3 portfolio trades
```

EXH2 remains a separate independently versioned hypothesis. C/A remain descriptors. QQQ/full-M and I remain separate methodology gaps, never implicit PASS.

## 2026-09-10 — FWD1 collector is live; source freshness is a hard gate
Canonical infrastructure run `34495098994` = SUCCESS. The collector now passes frozen execution tests, recomputes the post-boundary window, applies a source-freshness gate, persists evidence conflict-safely under `evidence/fwd1/`, and uploads a detailed Actions artifact.

The market-regime SPY source is currently only through `2026-09-04`, before the first forward date `2026-09-10`. Frozen interpretation:

```text
market_data_asof < 2026-09-10
-> data_gate_pass = false
-> status = WAITING_FOR_POST_BOUNDARY_DATA
-> zero candidates/trades are NOT interpretable as zero signals
```

No fallback M rule is introduced. The blocker must be resolved by advancing/repairing the separate SPY benchmark source while preserving its data-quality contract.

Collector schedule is `04:30 UTC Tuesday-Saturday`, intentionally after upstream daily OHLCV and SPY jobs. Consumer R2 credentials are read-only for `PutObject`, so canonical long-horizon FWD1 evidence uses Git repository history plus Actions artifacts; this persistence change does not alter strategy semantics.

Once the source-freshness gate passes, FWD1 status may become `ACCUMULATING`; formal review still requires both >=12 completed calendar months and >=50 closed X3 portfolio trades. Passing all gates is only `REVIEW_ELIGIBLE`.

Detailed record: `docs/decisions/2026-09-10-forward-validation-v1.md`.

## Next decision gate

Advance the SPY benchmark source without changing M semantics. After the FWD1 data gate passes, let the frozen collector accumulate genuine post-boundary evidence. Do not change baseline rules from interim forward observations. EXH2 remains separately versioned.
