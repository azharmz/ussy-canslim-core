# Decision Record — FWD1 Enters Genuine Forward Accumulation

Date: 2026-09-11

Status: LIVE / ACCUMULATING

## Decision

FWD1 has passed its frozen post-boundary source-freshness gate and is now accumulating genuine forward evidence under the unchanged frozen baseline.

The strategy definition is unchanged:

```text
Primary: Technical Baseline v1 + X3 pivot-hold execution + Portfolio Construction v1
Control: Technical Baseline v1 + X1 immediate T+1 execution + Portfolio Construction v1
```

C/A remain descriptors, not hard filters. EXH2 remains separate. No TrendFoll rule is inherited.

## Canonical evidence

Recovery/validation workflow:

```text
run_id = 34568992370
code_sha = c1241537fd79d8f5fa549ee722afe16289c1fbb1
status = SUCCESS
```

The workflow passed the frozen execution tests, complete forward-window collection, source-freshness gate, conflict-safe evidence persistence, and immutable Actions artifact upload.

Canonical gate state:

```text
forward_boundary_exclusive = 2026-09-09
forward_start = 2026-09-10
market_data_asof = 2026-09-10
data_gate_pass = true
status = ACCUMULATING
candidate_zero_interpretable = true
completed_calendar_months = 0
closed_x3_portfolio_trades = 0
calendar_gate_pass = false
trade_gate_pass = false
review_eligible = false
production_ready = false
```

## First interpretable forward observation

The first post-boundary observation contains no qualifying frozen-baseline signals/trades:

```text
forward_candidate_count = 0
forward_candidate_symbols = 0
X1 candidate trades = 0
X1 portfolio entries = 0
X1 closed portfolio trades = 0
X3 candidate trades = 0
X3 portfolio entries = 0
X3 closed portfolio trades = 0
```

Unlike the earlier stale-SPY observations, this zero is now interpretable because the market-regime source reaches the first forward session. It is only one forward-session observation and is not evidence for strategy quality, failure, or success.

## Upstream data resolution

The separate `ussy-data` SPY benchmark recovery run `34566034032` completed successfully and advanced the SPY benchmark through `2026-09-10` with QC passing and no incomplete rows in that refetch. The prior incomplete 2026-09-10 Yahoo placeholder condition is therefore resolved without manufacturing a bar or bypassing revision/adjustment safeguards.

The production OHLCV recovery run `34563561158` also completed successfully before FWD1 was collected.

## Frozen review gate

Formal evidence review remains blocked until both conditions are satisfied:

```text
>= 12 completed calendar months
AND
>= 50 closed X3 portfolio trades
```

Passing these gates makes FWD1 `REVIEW_ELIGIBLE` only. It does not auto-promote the strategy to production.

## Anti-data-mining guardrail

No FWD1 rule may be changed in response to interim forward outcomes. Any change to technical rules, X3 execution, PORT1 construction, thresholds, hard filters, M semantics, or forward boundary requires a new versioned hypothesis and a new independent forward clock.
