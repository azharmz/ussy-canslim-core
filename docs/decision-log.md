# Decision Log

## 2026-09-10 — Establish `ussy-canslim-research` as research HQ

**Decision:** This repository is the source of truth for CAN SLIM methodology, experiment specifications, evidence, progress, and research decisions.

**Not owned here:** canonical universe data, SEC extraction, large data artifacts, or TrendFoll production logic.

---

## 2026-09-10 — CAN SLIM is an independent strategy project

**Decision:** `ussy-canslim-research` is not an upgrade path whose destination is `ussy-trendfoll`.

`ussy-trendfoll` remains an independent strategy and production paper-trading project. CAN SLIM may reuse its evidence, features, execution assumptions or experiment ideas as references, but may adopt, modify or reject them.

No CAN SLIM result automatically changes TrendFoll. Any future CAN SLIM production implementation is governed separately.

---

## 2026-09-10 — Freeze `ussy-fundamentals`

**Decision:** SEC/PIT extraction and operational engineering are complete and frozen.

Re-open only for regression, factual extraction error, PIT violation, defensible material unsupported SEC pattern, or an approved data-contract change.

**Rationale:** The extraction layer must not be optimized to improve CAN SLIM pass-rate or trading performance.

---

## 2026-09-10 — PIT availability boundary is `accepted_at`

**Decision:** Historical strategy state may only use SEC information available by the decision time. Fiscal-period end is not an availability timestamp.

For daily research, any after-cutoff filing handling must be explicit and reproducible.

---

## 2026-09-10 — Fundamental production consumer contract

**Decision:** Consumers resolve `fundamentals/current.json` in Cloudflare R2 to the latest successfully audited immutable production snapshot.

For reproducible research, record the resolved immutable snapshot, manifest and checksum. Never rely on an unpinned `current` reference in a completed experiment.

---

## 2026-09-10 — Missing/readiness semantics are not CAN SLIM verdicts

**Decision:** `UNSUPPORTED_FPI`, `UNRESOLVED_CIK`, `INSUFFICIENT_HISTORY`, and structurally unavailable states remain data/readiness states. They must not be silently converted into economic FAIL labels.

Missing is not zero. Unsupported is not failed. Intentionally undefined growth is not 0%.

---

## 2026-09-10 — Legacy technical strategy is reference evidence, not literal O'Neil

**Decision:** `ussy-trendfoll` is treated as an independent quantitative breakout/trend-following strategy with partial CAN SLIM-like N/S/L/M characteristics. It is not a literal O'Neil implementation and is not inherited automatically by CAN SLIM.

Legacy production entry is:

```text
hard_filter PASS
+ breakout above prior pivot
+ breakout volume percentile >= 80
-> signal T0 close
-> Open H+1 realistic fill
```

Legacy stop/exit:

```text
stop = Open H+1 - 2 x ATR14(T0)
exit = intraday stop OR close < EMA20 OR 45 trading days
```

---

## 2026-09-10 — Legacy universe is an external constraint, not a CAN SLIM rule

**Decision:** The approximately 199-stock legacy universe originated from XTB availability intersected with Musaffa compliance. Research must not confuse this broker/universe constraint with strategy logic.

CAN SLIM will use its own independently specified universe/eligibility contract built on `ussy-data`.

---

## 2026-09-10 — Filled/Open H+1 remains an open research issue

**Decision:** Operational implementation of Filled/Open H+1 is complete in TrendFoll, but entry quality is not research-closed for CAN SLIM.

Walk-forward observations include large T0 moves and severe H+1 gaps followed by retracement. This creates a dedicated Entry Quality & Execution workstream.

Do not solve the issue by post-hoc threshold fitting on the small walk-forward sample.

---

## 2026-09-10 — Pre-specify Pivot Extension variants

**Decision:** Research variants for signal pivot extension are 3%, 5%, and 8% above pivot.

These values are pre-specified hypotheses. Do not change them after seeing which threshold produces the best CAGR/PF without a separately justified protocol.

---

## 2026-09-10 — Separate entry-quality effects from fundamental-selection effects

**Decision:** Entry Quality (E) and C/A fundamental selection are separate causal questions.

Research must distinguish:

- better results because poor/chased entries were avoided;
- better results because growth fundamentals selected better companies;
- interaction between both.

Ablation design must preserve this distinction.

---

## 2026-09-10 — Freeze methodology before performance optimization

**Decision:** Define C and A ex ante, with clear treatment of missing, negative-base, zero-base, turnaround, fallback and PIT states, before selecting thresholds based on trading performance.

Pass/fail distributions may be inspected before backtesting to detect pathological specifications, but CAGR/PF must not drive initial rule selection.

---

## 2026-09-10 — Freeze C-v1

**Decision:** CAN SLIM C-v1 is frozen before trading-performance testing.

At each decision point, use the latest usable fiscal quarter whose SEC information is available by the configured decision cutoff.

Frozen C-v1 rule:

```text
latest quarterly EPS YoY >= +25%
AND
latest quarterly revenue YoY >= +25%
```

Both numeric comparisons are required for `C_pass = TRUE`.

`C_pass` uses nullable semantics:

- `TRUE`: both comparisons are defined and pass;
- `FALSE`: required comparisons are defined but at least one is below threshold;
- `NULL`: required comparison is not defensibly evaluable because of missing/readiness/undefined-base state.

Acceleration is recorded as a diagnostic, not a C-v1 hard gate.

Turnaround from a nonpositive prior EPS base remains an explicit turnaround state with undefined EPS YoY; C-v1 does not invent a percentage or silently pass it.

**Rationale:** IBD/O'Neil guidance calls for recent quarterly earnings and sales to rise about 25% or more and prefers acceleration. Keeping acceleration diagnostic in v1 isolates the primary current-growth hypothesis and avoids combining too many gates before the first ablation.

Any methodology change after performance review requires a new version such as `C-v2`; C-v1 history must remain reproducible.
