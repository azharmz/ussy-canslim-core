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

The legacy concern was tested explicitly: a large T-1->T0 expansion may be followed by T+1 rejection/profit-taking and subsequent weakness.

Key descriptive findings:

- bottom shock decile median T-1->T0 move ~0.78%, X1 PF ~1.36;
- top shock decile median move ~8.70%, X1 PF ~1.05;
- however extreme shock alone did **not** produce a higher raw T+1..T+3 pivot-retest rate; low-shock candidates were actually closer to the pivot and retested it more often mechanically;
- the important interaction appears when a high-shock breakout is followed by T+1 rejection.

Within the **highest shock quintile**:

| T+1 state | Candidates | X1 PF | Stop rate | Retest pivot by T+3 | Breakdown below pivot by T+3 |
|---|---:|---:|---:|---:|---:|
| Bearish **and** Close < T0 Close | 962 | **0.560** | **80.84%** | 74.32% | 60.60% |
| Bearish only | 171 | 0.675 | 76.40% | 34.50% | 25.15% |
| Close < T0 only | 120 | 1.601 | 61.25% | 61.67% | 43.33% |
| No rejection | 893 | **1.573** | **59.63%** | 21.61% | 14.22% |

This strongly supports the *mechanism hypothesis* that **large T0 expansion becomes dangerous when the following session confirms rejection**, rather than a simplistic rule that all large T0 momentum is bad.

**Decision:**

- do **not** add a hard T-1->T0 momentum cutoff from this same sample;
- do **not** treat raw return-to-pivot frequency as the sole exhaustion definition, because distance from pivot mechanically differs by shock size;
- register `high shock × T+1 rejection` as an exploratory exhaustion hypothesis for independent/forward validation;
- X3 remains preferred for current research, but is not declared the final execution model solely from ET1; its pivot-hold behavior is directionally consistent with avoiding the identified T+1 rejection mechanism;
- C/A ablation should wait until this entry-quality hypothesis is clearly versioned so fundamental effects are not confused with a newly discovered execution filter.

Artifacts: `candidate_exhaustion_features.csv`, `shock_deciles.csv`, `shock_x_t1_rejection.csv` from workflow artifact `post-breakout-exhaustion-v1-34466747136`.

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

## Next decision gate

Version the post-breakout exhaustion hypothesis without tuning a cutoff on the discovery sample, define its independent/forward validation protocol, then implement historical C/A attachment. After that compare X3 baseline vs X3+C vs X3+C+A with X1 retained as control. Portfolio construction must be frozen before portfolio-return/max-drawdown claims.
