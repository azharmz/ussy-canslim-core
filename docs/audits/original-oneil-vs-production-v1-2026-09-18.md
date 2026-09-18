# Original O'Neil / IBD workflow vs CAN SLIM v1 production audit

Date: 2026-09-18  
Status: **HQ AUDIT COMPLETE — NO PRODUCTION SEMANTIC CHANGE AUTHORIZED**

## Question

Does the frozen production pipeline represent the original O'Neil / IBD CAN SLIM workflow faithfully, and could its deterministic eligibility contract be materially stricter than the original methodology?

## Source boundary

This audit compares the repository's frozen theory-fidelity work (#25-#32), frozen production implementation, and current IBD/O'Neil educational material. It does **not** use backtest returns or candidate counts to redefine CAN SLIM.

## Executive finding

The production system is **theory-informed and intentionally deterministic, but it is not a literal reconstruction of discretionary O'Neil/IBD practice**.

The most important distinction is architectural:

```text
O'Neil / IBD conceptual workflow
M / market context
→ identify superior growth leaders (C/A plus N/S/L/I evidence)
→ watchlist
→ proper base / pivot
→ breakout with strong demand
→ buy near the proper buy point
→ manage risk / sell discipline
```

Current production compute order:

```text
READY universe
→ frozen #33 pattern scan across all securities
→ breakout/pivot assessments
→ attach PIT C/A + L/I/M evidence
→ require deterministic C/A/N/S/L/I/M eligibility
→ T+1 Open execution
→ lifecycle
```

The final decision can still be internally coherent even though the compute order differs. The larger fidelity issue is that production converts every C/A/N/S/L/I/M component into a mandatory fail-closed gate for `CANSLIM_ELIGIBLE`, whereas the repository's own #30 theory audit concluded that the letters do **not** all have the same theoretical role.

## Component mapping

| Original concept | Production representation | Fidelity / limitation |
|---|---|---|
| **C — current earnings** | mandatory `PASS`; quarterly EPS YoY **and** revenue YoY both evaluable and >=25% | **Stricter deterministic interpretation.** C is a genuine fundamental screen, but production freezes a precise dual threshold. |
| **A — annual earnings** | mandatory `PASS`; latest three consecutive annual EPS YoY states each evaluable and >=25% | **Stricter deterministic interpretation.** Useful reproducible screen, not proof that original discretionary practice was a universal identical Boolean. |
| **N — new** | mandatory `PASS`, currently derived from first pivot crossing / new-price evidence; catalyst remains `NOT_IMPLEMENTED` | **Partial.** Original N includes “new” dimensions beyond price; production deliberately does not fabricate catalyst evidence. |
| **S — supply/demand** | mandatory `POSITIVE`; breakout volume >=1.40 × prior-50-session average | **Reasonable but narrowed proxy.** Strong demand is represented; shares/float/buyback dimensions are not the production gate. |
| **L — leader** | mandatory `PASS/STRONG`; transparent RS percentile proxy | **Reasonable proxy, incomplete.** RS line and industry/group leadership are not fully reproduced. |
| **I — institutional sponsorship** | mandatory `POSITIVE` from canonical PIT 13F evidence | **Potentially restrictive.** #30 classifies I primarily as confirmation/evidence, while production requires it for full eligibility. |
| **M — market direction** | mandatory `ALLOW_NEW_BUYS`; frozen major-index market-state path | **Role-faithful in architecture.** Exact classifier is our deterministic implementation, not proprietary IBD market data. |
| Proper base | frozen #33 four-core morphology | **Strong governed approximation**, but conditional morphology validation debt remains disclosed. |
| Pivot / buy point | pattern-specific structural pivot from #33 | **Theory-faithful design.** 5% zone is kept separate from pivot identity. |
| Breakout | first tradeable daily bar crossing pivot | **Causal daily-data representation.** |
| Volume confirmation | >=40% above prior 50-session average | **High fidelity to the frozen theory audit**, while still a precise implementation choice. |
| Buy timing | only after completed T signal; T+1 Open must be pivot..+5% | **Not literal discretionary O'Neil timing.** This is a deliberate daily-EOD causality contract preventing hindsight; an O'Neil trader may buy during the breakout session. |
| Initial loss control | ~7% practical trigger / 8% legacy ceiling from actual fill | **High conceptual fidelity.** |
| Profit / sell discipline | downstream lifecycle contracts; broader theory audit preserves +20–25%, 8-week exception, deterioration, round-trip, climax concepts | **Not all original sell nuance is represented as a single production rule.** |

## The key mismatch: identical hard-gate treatment

Repository #30 already froze this conclusion:

- C/A are primarily **fundamental screening criteria**;
- S/I are primarily **confirmation/evidence**;
- M is **market context + entry timing / exposure gate**;
- L includes multiple leadership dimensions;
- N is broader than price breakout alone.

Production `canslim-eligibility-contract-v1` nevertheless requires:

```text
C = PASS
A = PASS
N = PASS
S = POSITIVE
L = PASS or STRONG
I = POSITIVE
M = ALLOW_NEW_BUYS
```

Every item is mandatory and every missing / NOT_EVALUABLE / NOT_IMPLEMENTED state fails closed.

This is an engineering-safe production contract, but it should be described as **our frozen deterministic CAN SLIM v1 eligibility contract**, not as proof that William O'Neil required seven identical Boolean gates before every purchase.

## Why zero eligible candidates cannot by itself justify relaxing the contract

The latest production observation with zero eligible entries is evidence about the current frozen implementation and current population. It does **not** establish that a particular letter is “too strict.”

Changing C/A/I/S/L/M because candidate count is low would violate the existing governance order:

```text
Theory → specification → implementation → validation → performance
```

Any proposed v2 must therefore start from authoritative methodology evidence and a preregistered specification, not from a desire to manufacture more trades.

## Production disposition

1. **Keep CAN SLIM v1 frozen.**
2. Do not change #33 morphology, C/A thresholds, I gate, M gate, volume rule, or T+1 execution from this audit.
3. Label `CANSLIM_ELIGIBLE` precisely as a **deterministic production contract**, not a literal O'Neil term.
4. Keep the existing production-ordering observation on HOLD; watchlist-first is conceptually closer to O'Neil but requires semantic-equivalence validation before any production refactor.
5. If a more literal “Original CAN SLIM” implementation is desired, create a **separate v2 theory-fidelity workstream**. The first question should be component-role semantics—especially whether S and I are hard disqualifiers or evidence states—not performance.
6. Backtest work remains separate and must not be used to tune this production baseline.

## HQ conclusion

**CAN SLIM v1 production is operationally coherent and governed, but “theory-faithful” must not be read as “identical to discretionary original CAN SLIM.”**

The largest known conceptual compression is not the pattern engine. It is the conversion of heterogeneous CAN SLIM roles into one all-mandatory eligibility gate, followed by the deliberately causal T+1 Open execution model.

No production change is authorized by this audit.
