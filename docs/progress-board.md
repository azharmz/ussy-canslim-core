# CAN SLIM Progress Board

Last updated: 2026-09-10

Estimated overall research-program progress: **~80%**.

This percentage describes research-program completion, not literal CAN SLIM fidelity and not production readiness.

| Area | Status | Evidence / note |
|---|---|---|
| Independent project boundary | COMPLETE | CAN SLIM independent from TrendFoll |
| Research-universe definition | COMPLETE / FROZEN | frozen contemporary/current Musaffa-compliant universe; historical Musaffa status is not a strategy input |
| Expanded canonical universe | COMPLETE | 1,327 current Musaffa-compliant securities |
| SEC/PIT fundamental engineering | COMPLETE / FREEZE | `ussy-fundamentals` |
| R2 production contract + incremental updater | LIVE | `fundamentals/current.json` |
| C-v1 methodology | COMPLETE / FROZEN | EPS YoY >=25% AND revenue YoY >=25% |
| A-v1 methodology | COMPLETE / FROZEN | latest 3 annual EPS YoY each >=25% |
| C/A label implementation | COMPLETE | deterministic labels + tests |
| C/A distribution study | COMPLETE / VALIDATED | 901 production-ready symbols |
| C/A period-semantics audit | COMPLETE / PASS | run `34434268817` |
| Historical C/A as-of methodology | COMPLETE / FROZEN | `accepted_at <= T0 16:00 ET`; stable identity bridge |
| Historical C/A label attachment | **COMPLETE / VALIDATED** | run `34479060107`; explicit SEC FY identity + anti-look-ahead audit |
| Independent technical baseline v1 | COMPLETE / FROZEN | N-price/S/L/M proxies; I deferred |
| Technical/execution unit tests | COMPLETE / CI PASS | technical `34431906311`; execution `34433458116` |
| E0 historical technical candidates | COMPLETE | 10,731 candidates / 860 securities |
| E1-E4 entry diagnostics | COMPLETE | run `34433673545` |
| Entry Timing X1-X4 basis test | COMPLETE / VALIDATED | run `34464861119`; X3 currently preferred, X1 retained control |
| Post-breakout exhaustion diagnostic | COMPLETE / EXPLORATORY | run `34466747136`; high shock × T+1 rejection is the important mechanism |
| Exhaustion validation protocol | PRE-REGISTRATION REQUIRED | separate workstream; do not tune cutoff on discovery sample |
| C / C+A ablation | **NEXT / UNBLOCKED** | X3 baseline vs X3+C vs X3+C+A; X1 equivalents mandatory control |
| Portfolio construction | NOT FROZEN | required before portfolio return/max-DD claims |
| Robustness / holdout | PARTIAL | entry timing PF ex-top10/subperiod done; exhaustion needs independent/forward validation |
| Institutional sponsorship (I) | DEFERRED | never implicit PASS |
| QQQ benchmark for full M-v1 | MISSING INPUT | current exploratory engine uses SPY-only proxy |
| Production integration | BLOCKED | research evidence + forward validation first |

## Research universe

Primary historical experiments use the selected current/contemporary Musaffa-compliant universe frozen at the research snapshot. Historical Musaffa eligibility is not required and is not a blocker. PIT discipline remains mandatory for actual decision inputs: historical OHLCV/market state and SEC fundamental evidence after `accepted_at` only.

## C/A foundation

Pinned production snapshot for first current-state distribution:

`fundamentals/snapshots/2026-09-09/run-34417104650/manifest.json`

| Label | PASS | FAIL | NOT_EVALUABLE |
|---|---:|---:|---:|
| C-v1 | 69 | 520 | 312 |
| A-v1 | 11 | 483 | 407 |
| C+A | 3 | 437 | 461 |

C/A thresholds remain frozen. Period-semantics audit run `34434268817` = **SUCCESS**.

## Historical C/A attachment v1

Validated workflow run `34479060107` on the 10,731 historical technical candidates. Pinned fundamentals snapshot:

`fundamentals/snapshots/2026-09-10/run-34470910341/manifest.json`

The consumer resolves annual source accession to explicit SEC fiscal year from the immutable long PIT artifact, chooses latest accepted state per FY, and requires the latest three resolved FY to be consecutive before A can PASS. Unresolved FY identity remains `NOT_EVALUABLE`; calendar-year guessing is prohibited.

Structural audit:

```text
candidate rows                         10,731
candidate securities                      860
duplicate attachment rows                   0
future accepted_at violations               0
identity-missing-CIK rows                   56
annual states                           11,703
annual FY resolved                     10,307
annual FY unresolved                    1,396
```

Historical distribution:

| Label | PASS | FAIL | NOT_EVALUABLE |
|---|---:|---:|---:|
| C-v1 | 703 | 3,475 | 6,553 |
| A-v1 | 34 | 768 | 9,929 |
| C+A | 2 | 650 | 10,079 |

All A-PASS rows contain exactly three resolved consecutive FY and zero unresolved FY states. The two C+A PASS candidate events are CRUS on 2022-08-03 and MEDP on 2023-07-25. No performance metric was used in this validation.

Decision record: `docs/decisions/2026-09-10-historical-ca-attachment-v1.md`.

## Technical candidate baseline

Historical candidate engine on the frozen current-compliant universe produced **10,731 candidates across 860 securities**.

## Entry Timing Basis Test v1

Workflow run `34464861119` = **SUCCESS**. All timing variants use the same 7% stop from actual fill and 20% target from pivot.

| Variant | Entries | Fill rate | Median delay | PF | PF ex-top10 | Target | Stop |
|---|---:|---:|---:|---:|---:|---:|---:|
| X1 T+1 immediate | 5,777 | 53.83% | 1 | 1.093 | 1.082 | 30.95% | 68.98% |
| X2 first valid T+1..T+3 | 6,158 | 57.39% | 1 | 1.096 | 1.086 | 31.02% | 68.89% |
| **X3 pivot-hold** | **3,604** | **33.58%** | **2** | **1.163** | **1.146** | **32.77%** | **67.18%** |
| X4 retest-hold | 4,216 | 39.29% | 2 | 1.109 | 1.093 | 30.95% | 69.00% |

X3 remains the current preferred research execution baseline, not a final production rule.

## Post-breakout exhaustion diagnostic

Workflow run `34466747136` = **SUCCESS**.

The raw shock relationship is not sufficient by itself. The strongest result is the interaction between a large T-1->T0 expansion and rejection on T+1.

Within the highest shock quintile:

| T+1 state | Candidates | X1 PF | Stop rate | Retest pivot by T+3 | Breakdown below pivot by T+3 |
|---|---:|---:|---:|---:|---:|
| Bearish and Close < T0 Close | 962 | **0.560** | **80.84%** | 74.32% | 60.60% |
| Bearish only | 171 | 0.675 | 76.40% | 34.50% | 25.15% |
| Close < T0 only | 120 | 1.601 | 61.25% | 61.67% | 43.33% |
| No rejection | 893 | **1.573** | **59.63%** | 21.61% | 14.22% |

Top shock decile median move was about **+8.70%**, with X1 PF ~**1.05**, versus bottom shock decile median ~**+0.78%**, PF ~**1.36**. But shock alone is not a sufficient rule because the T+1 state separates weak and strong high-momentum breakouts much more clearly.

**Current interpretation:** the legacy problem is best framed as **post-breakout exhaustion confirmation**, not simply “momentum T-1->T0 too high.” No hard momentum threshold has been adopted. EXH2 remains separate from the fundamental ablation and cannot be silently added to X3/X1.

## Next sequence

1. Run the pre-specified fundamental ablation: X3 baseline vs X3+C vs X3+C+A, with X1 equivalents as mandatory control.
2. Report trade count, PF, PF ex-top10, fill/opportunity effects, subperiod stability, and symbol/sector concentration; do not tune C/A thresholds from the result.
3. Keep EXH2 as a separately pre-registered independent/forward validation workstream.
4. Freeze portfolio construction and position sizing before portfolio-return/max-drawdown claims.
5. Compute portfolio return/max drawdown and remaining robustness diagnostics.
6. Holdout/forward validation before any production proposal.
