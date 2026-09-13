# Decision — Freeze #34 Theory-Faithful Candidate Generator

Date: 2026-09-13
Status: **COMPLETE / FROZEN v1**
Parent spec: `theory-faithful-candidate-spec-v1`
Pattern input contract: `oneil-pattern-output-v2`
Candidate generator implementation: `34-candidate-generator-v0.2`

## Decision

#34 is frozen as a downstream consumer of the canonical #33 core production contract. It does not own morphology and must not duplicate, extend, or tune the #33 detector.

Accepted core patterns are only:

- `FLAT_BASE`
- `DOUBLE_BOTTOM`
- `CUP_WITHOUT_HANDLE`
- `CUP_WITH_HANDLE`

P6 advanced patterns remain outside production consumption.

## Frozen staged semantics

```text
BASE_RECOGNIZED
→ PIVOT_DEFINED
→ PIVOT_CROSSED
→ BREAKOUT_CONFIRMED
→ CANSLIM_ELIGIBLE
```

`AMBIGUOUS` and `REJECTED` pattern assessments are preserved and cannot be silently promoted.

A T0 pivot crossing is a **first crossing after the #33 structural end**, not merely `High(T0) > pivot`. A prior post-structure crossing prevents the same historical breakout from being recounted at the current as-of date.

Breakout-day strong-volume confirmation is `volume(T0) >= 1.40 × average(volume of prior 50 completed sessions)`.

`CANSLIM_ELIGIBLE` additionally requires frozen core states C PASS, A PASS, individual L PASS, and M `ALLOW_NEW_BUYS`. I, broader S evidence, industry leadership, RS-line evidence, and non-price N catalyst remain evidence/context unless a later frozen specification explicitly promotes them.

## C/A/L/M adapter semantics

- C: PIT-available quarterly EPS YoY, core PASS at `>=25%`.
- A: PIT-available latest three-year-span annual EPS CAGR, core PASS at `>=25%`; nonpositive starting/ending EPS is not coerced into a percentage-growth PASS/FAIL.
- L: transparent cross-sectional RS proxy percentile, PASS at `>=80`.
- M: explicit market state mapping to `ALLOW_NEW_BUYS / CAUTION / BLOCK_NEW_BUYS`; current production smoke uses the documented SPY-only transparent proxy.
- I: manager-count trend remains evidence and is not a hard gate.

## Provenance preservation

Candidate output preserves #33 identity and provenance, including candidate/base/lineage IDs, normalized/native pattern state, candidate semantics, detector faults, structural signature, structural start/end, depth, pivot source, detector contract version, pattern engine version, and labelled-validation status.

## Verification evidence

Final verification used GitHub Actions run `34758050282` on commit `4ad9c303f22b9d05f123f0db1a25f80793b9ea04`.

Result: **SUCCESS**.

- #34 unit contract: `9 passed`.
- canonical `azharmz/ussy-oneil-patterns` dependency checked out and installed.
- bounded live-R2 smoke completed successfully.
- no advanced patterns allowed.
- no trading-performance metrics used.
- smoke as-of: `2026-09-10`.
- pattern/candidate records: `4,056`.
- pattern status: `472 RECOGNIZED`, `2,695 AMBIGUOUS`, `889 REJECTED`.
- candidate stages: `3,584 NOT_ELIGIBLE`, `465 PIVOT_DEFINED`, `7 PIVOT_CROSSED`, `0 BREAKOUT_CONFIRMED`, `0 CANSLIM_ELIGIBLE`.

The zero confirmed/eligible count is **not a strategy verdict**. The bounded smoke is plumbing/semantic verification only and is not authorized for PnL, PF, CAGR, drawdown, or threshold tuning.

The verification artifact is `e0-and-candidate-v2-34758050282` (artifact id `10318315380`, SHA256 `c5111d35fcfff9857192a9e0eb47c7b943247eea648e04edc41bb6441f81ea11`).

The legacy E0 workflow was restored immediately after verification and is not the production #34 contract.

## Production vs historical-validation data boundary

The current R2 ready snapshot is suitable for daily production scanning. Its ~300-bar retention is not adopted as a historical-validation constraint.

#35 historical/new-candidate validation must use purpose-built historical OHLCV of sufficient length when required, rather than treating the production R2 300-bar ready snapshot as the backtest dataset.

## Next boundary

Open #35 **New-Candidate Validation**.

#35 must validate the frozen #33 + #34 chain. It must not retune #33 morphology or #34 thresholds from returns. Any historical OHLCV acquisition required for validation is research infrastructure and does not change the production R2 contract.
