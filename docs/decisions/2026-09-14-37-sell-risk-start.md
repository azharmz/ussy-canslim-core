# #37 Sell / Risk Execution — Start Decision

Date: 2026-09-14
Status: **OPENED / SPEC FROZEN FOR IMPLEMENTATION**

## Scope

Open a new downstream workstream after frozen #36. #37 owns theory-faithful sell/risk execution semantics for already-entered positions.

It does not reopen or modify #33 morphology, #34 candidate staging, #35 validation, #36 entry semantics, the frozen 60-case corpus, FWD1, EXH2, or P6 governance.

## Canonical specification

`docs/methodology/37-theory-faithful-sell-risk-spec-v1.md`

Contract version:

`37-sell-risk-v1`

## Boundary from legacy work

Existing `docs/methodology/execution-exit-v1.md`, X1-X4/X3 and PORT1 remain legacy/frozen research evidence. In particular, the legacy deterministic full target at `pivot * 1.20` must not be relabelled as canonical O'Neil sell semantics.

EXH2 remains a separate prospective exhaustion sidecar and is not the #37 climax engine.

## Initial implementation target

#37 v1 will implement the state machine required by the frozen specification, with one mandatory executable stock-level action:

```text
practical ~7% capital-protection trigger from actual fill
```

Gap-through handling must use the observed market open when price opens through the trigger.

Theory-derived profit-zone, exceptional-winner, technical-deterioration, round-trip, climax and market-risk concepts remain distinct states with implementation status explicit. They are not silently converted into optimized exit rules.

## Validation discipline

```text
specification freeze
-> implementation
-> S37-A..G semantic/causal tests
-> zero findings required
-> implementation freeze
-> only then any performance research
```

No sell threshold may be changed from realized return/CAGR/PF/win-rate evidence during implementation validation.

## Theory vs execution naming

#37 inherits the #36 governance clarification:

- O'Neil/CAN SLIM concepts are labelled theory semantics;
- completed-bar availability is labelled information boundary;
- next-session/same-bar/gap-fill handling is labelled backtest execution convention.

## Next action

Implement `37-sell-risk-v1` and its semantic boundary tests without touching upstream frozen contracts.