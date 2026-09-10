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
