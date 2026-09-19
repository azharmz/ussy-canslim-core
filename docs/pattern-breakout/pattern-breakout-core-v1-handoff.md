# HANDOFF — USSY Pattern Breakout Core v1

Status: DESIGN FROZEN FOR CORE IMPLEMENTATION  
Branch: `feat/pattern-breakout-core-v1`

## Mission

Build an independent technical-only swing system from the already-frozen O'Neil Pattern Engine.

Core path:

```
canonical OHLCV
  -> frozen O'Neil Pattern Engine
  -> recognized proper base + pivot
  -> near trigger
  -> pivot crossing + breakout-volume confirmation
  -> TECHNICAL_BREAKOUT_CANDIDATE
  -> causal T+1 Open execution
  -> OPEN position
  -> O'Neil-derived technical sell evidence
  -> HOLD / TECHNICAL EXIT
```

## Frozen design decisions

1. No C/A/N/I or other fundamental eligibility.
2. Fundamental failure never removes a technical candidate.
3. O'Neil Pattern Engine is the morphology authority; do not create a second detector.
4. Supported frozen patterns remain CUP_WITH_HANDLE, CUP_WITHOUT_HANDLE, DOUBLE_BOTTOM, FLAT_BASE.
5. No max-hold and no forced time exit.
6. No fixed 2R target or ATR exit inherited from older USSY research.
7. Exit is driven by technical/risk evidence only.
8. Signal uses completed daily bar T; earliest USSY execution is T+1 Open.
9. Preserve valid breakout separately from T+1 executability. A valid breakout can become MISSED_EXTENDED without becoming a bad pattern.
10. TrendFoll is not a methodology dependency. Reuse infrastructure/generic utilities only after semantic verification.
11. Weinstein and Minervini/VCP are outside Core v1. Future modules begin as independently versioned evidence-only extensions.
12. No composite score in Core v1.
13. No Wyckoff, Darvas, MACD, RSI, stochastic, Bollinger or other unrelated indicators in Core v1.
14. Methodology provenance must distinguish ORIGINAL, OPERATIONALIZATION, DATA_ADAPTATION, PROXY, ENGINEERING, UNAVAILABLE.

## Canonical morphology dependency

Repository: `azharmz/ussy-oneil-patterns`  
Frozen SHA: `c433cc1e35a5aa32a46f732cd8c5545935e36e40`  
Schema: `oneil-pattern-output-v2`  
Engine: `33-core-p8-frozen-v1`

Do not tune frozen morphology based on returns.

## Lifecycle principle

Holding period is an outcome, not an exit rule.

A position may close quickly if technical sell evidence fires, or remain open beyond an arbitrary swing-day count while the technical structure remains healthy.

## Separation from CAN SLIM

`CANSLIM_ELIGIBLE` and `CANSLIM_V2_ELIGIBLE` are not Pattern Breakout states.

Use Pattern Breakout-specific states such as:

- PATTERN_RECOGNIZED
- PIVOT_DEFINED
- NEAR_TRIGGER
- BREAKOUT_CONFIRMED
- TECHNICAL_BREAKOUT_CANDIDATE
- EXECUTED_T1_OPEN
- OPEN
- TECHNICAL_EXIT
- CLOSED

CAN SLIM v1 remains a frozen historical baseline. CAN SLIM v2 remains the fundamental-first CAN SLIM successor. Pattern Breakout is an independent technical product.

## Compute / recovery governance

Before heavy full-universe compute, preserve recovery boundaries:

```
prepare
 -> frozen READY identity
 -> raw O'Neil morphology checkpoint
 -> breakout candidate checkpoint
 -> T+1 execution checkpoint
 -> lifecycle checkpoint
 -> validate/report
```

Durable checkpoints must carry source identity/hash, schema/version, config/contract identity, producer commit/run and created_at. Resume fails closed on lineage mismatch.

## Immediate implementation gate

Do not code new entry/exit semantics until:

1. existing O'Neil entry/exit assets are audited for reuse;
2. unresolved breakout/entry/sell rules have authoritative source-locks;
3. every reused rule is classified by methodology provenance.

Then implement the smallest independent Pattern Breakout adapter/contracts without modifying the frozen O'Neil Pattern Engine or CAN SLIM production contracts.
