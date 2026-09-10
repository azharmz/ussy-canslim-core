# Decision Log

## 2026-09-10 — Establish `ussy-canslim-research` as research HQ

**Decision:** This repository is the source of truth for CAN SLIM methodology, experiment specifications, evidence, progress, and research decisions.

**Not owned here:** production trading logic, canonical universe data, SEC extraction, or large data artifacts.

---

## 2026-09-10 — Freeze `ussy-fundamentals`

**Decision:** SEC/PIT extraction and operational engineering are considered complete and frozen.

Re-open only for regression, factual extraction error, PIT violation, defensible material unsupported SEC pattern, or an approved data-contract change.

**Rationale:** The extraction layer must not be optimized to improve CAN SLIM pass-rate or trading performance.

---

## 2026-09-10 — PIT availability boundary is `accepted_at`

**Decision:** Historical strategy state may only use SEC information that was available by the decision time. Fiscal-period end is not an availability timestamp.

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

## 2026-09-10 — Legacy technical strategy remains the baseline, not literal O'Neil

**Decision:** `ussy-trendfoll` is treated as a quantitative breakout/trend-following baseline with partial CAN SLIM-like N/S/L/M characteristics. It is not described as a literal O'Neil implementation.

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

Expanded-universe results must therefore establish a new canonical baseline before attributing changes to C/A or entry rules.

---

## 2026-09-10 — Filled/Open H+1 remains an open research issue

**Decision:** Operational implementation of Filled/Open H+1 is complete, but entry quality is not considered research-closed.

Walk-forward observations include large T0 moves and severe H+1 gaps followed by retracement. This creates a dedicated Entry Quality & Execution workstream.

Do not solve the issue by post-hoc threshold fitting on the small walk-forward sample.

---

## 2026-09-10 — Pre-specify Pivot Extension variants

**Decision:** Research variants for signal pivot extension are 3%, 5%, and 8% above pivot.

These values are pre-specified hypotheses. Do not change them after seeing which threshold produces the best CAGR/PF without a separately justified protocol.

---

## 2026-09-10 — Separate entry-quality effects from fundamental-selection effects

**Decision:** Entry Quality (E) and C/A fundamental selection are separate causal questions.

Research must be able to distinguish:

- better results because poor/chased entries were avoided;
- better results because growth fundamentals selected better companies;
- interaction between both.

Ablation design must preserve this distinction.

---

## 2026-09-10 — Freeze C and A methodology before performance optimization

**Decision:** Define C and A ex ante, with clear treatment of missing, negative-base, zero-base, turnaround, fallback and PIT states, before selecting thresholds based on trading performance.

Pass/fail distributions may be inspected before backtesting to detect pathological specifications, but CAGR/PF must not drive initial rule selection.
