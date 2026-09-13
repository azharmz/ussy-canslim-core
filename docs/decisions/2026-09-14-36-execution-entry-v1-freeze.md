# #36 Execution / Entry v1 — Freeze Decision

Date: 2026-09-14
Status: **IMPLEMENTATION COMPLETE / FROZEN v1**

## Scope

This decision freezes the first theory-faithful downstream execution/entry contract built after frozen #33 Pattern Recognition, #34 Candidate Generator, and #35 Validation.

It does not modify, reopen, or retune #33, #34, #35, the frozen 60-case validation corpus, or P6 advanced-pattern governance.

## Frozen baseline

Version: `36-execution-entry-v1`

Daily-EOD causal boundary:

```text
signal/candidate state known after close T
→ earliest executable fill = observed market open T+1
```

Canonical baseline entry requires the observed T+1 open to remain within the traditional pivot buy zone:

```text
pivot <= T+1 open <= pivot * 1.05
```

Entry outcomes are explicit rather than fabricated:

- executable T+1 open inside the buy zone;
- `MISSED_EXTENDED_AT_OPEN` when T+1 opens >5% above pivot;
- `BELOW_PIVOT_AT_OPEN` when T+1 opens below pivot;
- no fill when no next session exists;
- no same-day hindsight execution;
- no synthetic intraday/retrace fill.

Risk-reference separation is frozen:

```text
initial stop / maximum-loss reference = actual fill price
normal 20%-25% profit-zone reference = proper buy point / pivot
```

This preserves the #31 theory distinction between capital protection from actual purchase price and normal profit management from the proper buy point.

## Semantic validation

Initial CI run `34784341195` failed during test collection before any semantic assertion executed:

```text
ModuleNotFoundError: No module named 'canslim_research'
```

Classification: **VALIDATION TOOLING / IMPORT-PATH ISSUE**.

The workflow was corrected by exposing repository `src/` through `PYTHONPATH`. No specification, entry rule, threshold, implementation semantic, upstream contract, or frozen evidence was changed to obtain a passing result.

Canonical validation run:

- GitHub Actions run: `34785545504`
- commit: `a5785aeb91a154840295b6058862d9d9dbb501dc`
- result: **SUCCESS**
- semantic boundary tests: **11 passed**

## Governance verdict

`IMPLEMENTATION COMPLETE / FROZEN v1`

No performance claim is made by this freeze. It freezes causal execution semantics only.

## Next research boundary

Alternative delayed/confirmation/retest entry rules may be researched only as explicitly preregistered downstream variants. They must:

1. remain separate from the canonical `36-execution-entry-v1` baseline;
2. use only information actually available before each fill;
3. never alter #33/#34/#35 semantics;
4. never retune the frozen 5% traditional buy-zone boundary from realized returns;
5. preserve missed/extended entries rather than invent fills;
6. define selection/acceptance metrics before inspecting performance.

Legacy X1-X4/X3 research is not automatically promoted to the canonical theory-faithful execution contract.