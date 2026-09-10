# C/A Label Distribution v1 — Result

Status: **COMPLETE / VALIDATED**

GitHub Actions workflow run: `34431101727`

Pinned fundamentals snapshot:

`fundamentals/snapshots/2026-09-09/run-34417104650/manifest.json`

Fundamentals source commit: `ad5084193840c77cf401c0ed7e9ab6c38513a509`

Denominator: **901 production-ready securities** (`857 PASS_FULL`, `44 PASS_3Y_FALLBACK`).

No trading-performance metrics were used.

## Distribution

| Label | PASS | FAIL | NOT_EVALUABLE | PASS rate |
|---|---:|---:|---:|---:|
| C-v1 | 69 | 520 | 312 | 7.66% |
| A-v1 | 11 | 483 | 407 | 1.22% |
| C+A | 3 | 437 | 461 | 0.33% |

C+A PASS symbols: **FIX, NBIX, NVDA**.

## Primary NOT_EVALUABLE reasons

- C-v1: `EPS_YOY_UNDEFINED_OR_MISSING` — 312
- A-v1: `ANNUAL_GROWTH_UNDEFINED_OR_MISSING` — 381
- A-v1: `INSUFFICIENT_ANNUAL_HISTORY` — 26

This does not mean the upstream parser failed. Production readiness and downstream economic evaluability are separate concepts.

## Interpretation boundary

These counts show that C-v1/A-v1 are strict and that many ready issuers do not have numerically meaningful growth comparisons under the frozen semantics. This result must **not** be used to tune thresholds before trading evidence. The next work should establish the independent CAN SLIM technical baseline and historical PIT label integration.
