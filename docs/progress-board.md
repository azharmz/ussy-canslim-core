# CAN SLIM Progress Board

Last updated: 2026-09-10

Estimated overall research-program progress: **~70%**.

This is project progress (data, methodology, implementation, experiments, robustness, validation), not a claim that the strategy is 70% literal CAN SLIM.

| Area | Status | Notes |
|---|---|---|
| Independent project boundary | COMPLETE | CAN SLIM separated from TrendFoll |
| Expanded canonical universe | COMPLETE | 1,327 current Musaffa-compliant securities |
| SEC/PIT fundamental engineering | COMPLETE / FREEZE | `ussy-fundamentals` |
| R2 production contract + incremental updater | LIVE | `fundamentals/current.json` |
| C-v1 methodology | COMPLETE / FROZEN | EPS YoY >=25% AND revenue YoY >=25% |
| A-v1 methodology | COMPLETE / FROZEN | latest 3 annual EPS YoY each >=25% |
| C/A label implementation | COMPLETE | deterministic labels + tests |
| C/A distribution study | COMPLETE / VALIDATED | 901 production-ready symbols, no trading metrics |
| Independent technical baseline v1 | COMPLETE / FROZEN | N-price/S/L/M proxies versioned; I deferred |
| Execution & exit baseline X1 | COMPLETE / FROZEN / CI PASS | H+1 fill inside 5% zone, 7% stop, 20% pivot target; run `34433458116` |
| E0 rolling implementation smoke | COMPLETE / VALIDATED | run `34432960298`; 14 candidate rows / 13 symbols; not PIT historical evidence |
| E0 historical-input audit | COMPLETE | 1,300 full OHLCV histories, but only one membership snapshot: 2026-08-28; QQQ absent |
| E0 static-history candidate study | COMPLETE / EXPLORATORY | 10,731 candidates / 860 symbols; static 2026-08-28 universe, survivorship/eligibility biased |
| E0 true PIT historical baseline | NOT AVAILABLE PRE-2026-08-28 | PIT membership history did not exist before first snapshot |
| E0 PIT-forward track | OPEN | valid from 2026-08-28 onward as membership snapshots accumulate |
| Entry Quality E1-E4 | COMPLETE / EXPLORATORY | run `34433673545`; fill-aware 5% mitigates chasing; no post-hoc momentum/gap threshold |
| Entry Quality E5-E6 | PENDING | interactions + robustness / portfolio-aware diagnostics |
| Historical C/A identity audit | COMPLETE | `security_id -> pinned universe symbol -> CIK -> SEC PIT` bridge confirmed |
| Historical C/A as-of methodology v1 | COMPLETE / FROZEN | signal cutoff 16:00 America/New_York; `accepted_at <= cutoff` |
| Historical C/A label attachment | IN PROGRESS | next implementation step |
| C / C+A ablation | BLOCKED | after historical label attachment; static study can only be exploratory |
| Portfolio construction / DD methodology | NOT FROZEN | required before portfolio return/drawdown claims |
| Robustness / holdout | BLOCKED | final historical membership limitation must be respected |
| Institutional sponsorship (I) | DEFERRED | 13F/ownership not started; never auto-PASS |
| QQQ benchmark for M-v1 | MISSING INPUT | exploratory work is explicitly SPY-only until contract exists |
| Forward validation | OPENING SOON | PIT universe valid from 2026-08-28 onward |

## Key evidence so far

### C/A distribution

Pinned snapshot: `fundamentals/snapshots/2026-09-09/run-34417104650/manifest.json`

| Label | PASS | FAIL | NOT_EVALUABLE | PASS rate of 901 |
|---|---:|---:|---:|---:|
| C-v1 | 69 | 520 | 312 | 7.66% |
| A-v1 | 11 | 483 | 407 | 1.22% |
| C+A | 3 | 437 | 461 | 0.33% |

Thresholds remain frozen despite low pass rates.

### Technical baseline v1

- price guardrail: $15;
- generic prior-35-session base, maximum depth 40%;
- N-price breakout above pivot and <=5% above pivot;
- S volume >=1.40x prior 50-session average;
- L recency-weighted RS proxy percentile >=80;
- M concept: SPY OR QQQ follow-through/distribution proxy;
- I: `NOT_IMPLEMENTED`, never implicit PASS.

Rule-engine CI run `34431906311` = **SUCCESS**.

### Execution baseline X1

Frozen before performance inspection:

```text
T0 candidate after close
-> H+1 open only if pivot < Open_H+1 <= 1.05*pivot
-> one active position/security
-> stop = entry * 0.93
-> target = pivot * 1.20
-> gap-through exits use open
-> same-bar stop/target = stop-first
-> no arbitrary time stop
```

CI run `34433458116` = **SUCCESS**.

### Historical data boundary

Audit run `34433104954` found:

- 1,300 `backtest/ohlcv/{security_id}.parquet` full histories;
- only one PIT membership snapshot: `universe/membership/2026-08-28.json`;
- no QQQ benchmark contract.

Therefore a multi-year expanded-universe study using the 2026-08-28 membership is exploratory/static-universe evidence, **not** PIT-universe evidence.

### E0 static candidate study

Run `34433339770`:

- 6,095,031 feature-evaluable rows;
- 10,731 technical candidate rows;
- 860 candidate symbols;
- 3,266 candidate dates.

Evidence class: `STATIC_2026_08_28_UNIVERSE_EXPLORATORY_NOT_PIT_UNIVERSE`.

### E1-E4 entry diagnostics

Run `34433673545`:

- candidates: 10,731;
- accepted H+1 trades: 5,777;
- skipped above H+1 5% buy zone: 501;
- skipped at/below pivot: 726;
- skipped because same security already open: 3,727;
- descriptive trade-level PF on biased static evidence: 1.093 (not a strategy verdict).

Large T0 shock increases probability that H+1 is already outside the 5% buy zone, and larger H+1 gaps reduce reward-to-target. However, accepted-trade results do not support a clean post-hoc momentum/gap cutoff. The frozen 5% fill-aware rule remains the primary anti-chasing mechanism.

### Historical C/A join

Fundamental PIT does not expose `security_id`, but the pinned fundamentals snapshot contains a one-to-one `current_universe.csv` bridge with 1,327 unique security IDs. Historical C/A v1 therefore uses:

```text
security_id
-> pinned current_universe symbol
-> pinned final readiness report CIK
-> SEC PIT rows
```

Decision-time cutoff is 16:00 America/New_York on T0, converted DST-aware to UTC. Only `accepted_at <= cutoff` may be used.

## Next sequence

1. Audit quarterly/annual row-selection semantics in the PIT dataset, especially Q4 and latest-quarter identification.
2. Implement historical C/A as-of labels for technical candidate events with hard anti-look-ahead assertions.
3. Validate label coverage/distribution on the static candidate set without tuning thresholds.
4. Run exploratory C and C+A trade ablation on the static universe, clearly labeled biased.
5. Freeze portfolio construction before making portfolio-return or max-drawdown claims.
6. Continue E0 PIT-forward / forward validation from 2026-08-28 as real membership history accumulates.
7. Add QQQ benchmark contract before claiming full M-v1 implementation.
