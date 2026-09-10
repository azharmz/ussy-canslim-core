# Forward Validation v1 (FWD1)

Date frozen: 2026-09-10

Status: FROZEN / COLLECTION PROTOCOL

## Purpose

FWD1 is the genuine forward-validation track for the already-selected CAN SLIM research baseline. It begins strictly after the historical research boundary and must not be used to retune historical rules while evidence is accumulating.

## Forward boundary

Historical research ends at:

```text
2026-09-09
```

Eligible FWD1 signal dates are therefore:

```text
signal_date > 2026-09-09
```

The first possible forward signal date is 2026-09-10.

## Frozen strategy inputs

Primary:

```text
X3 pivot-hold execution
+ Technical Baseline v1
+ Portfolio Construction v1
```

Mandatory control:

```text
X1 immediate T+1 execution
+ same Technical Baseline v1
+ same Portfolio Construction v1
```

FWD1 must reuse the existing frozen implementations rather than re-expressing the rules in a new tuned implementation.

## Portfolio rules

Unchanged from `docs/methodology/portfolio-construction-v1.md`:

- initial equity = 100,000 arbitrary units;
- long-only, no leverage;
- maximum 7 concurrent positions;
- target notional per new position = 1/7 prior-session closing equity;
- no partial fills when cash is insufficient;
- no pyramiding / one live position per security;
- same-session priority = `rs_percentile DESC`, then `volume_ratio DESC`, then ticker ASC;
- entries occur before same-day exits, so same-day exit proceeds cannot fund morning entries;
- stop = 7% below actual fill;
- target = 20% above pivot;
- same-bar stop/target ambiguity = stop-first;
- boundary `CENSORED_OPEN` positions remain mark-to-market and are not forced exits;
- report gross and 10 bps entry + 10 bps exit cost sensitivity.

## Explicit exclusions

FWD1 does **not** add or tune:

- C-v1 or A-v1 as hard filters;
- EXH2 / exhaustion filters;
- new RS thresholds;
- new base definitions;
- new market-regime thresholds;
- max-position/sizing/ranking changes;
- stop/target/time-stop changes;
- TrendFoll rules.

C/A may be attached later as non-causal descriptors for analysis only, but they cannot alter FWD1 entry eligibility or portfolio allocation.

## Data and causality

The research universe remains the frozen current/contemporary Musaffa-compliant universe used by the historical program. Historical Musaffa status is not reconstructed.

Daily OHLCV and market-state calculations may use information only through each signal day T0. Because T0 close and volume are EOD facts, execution remains no earlier than allowed by the frozen X1/X3 definitions.

Each collector run recomputes the entire forward window from the frozen boundary using the then-current source data, but preserves an immutable run snapshot so later source corrections cannot silently overwrite what was observed previously.

## Evidence persistence

Each run must produce a local GitHub Actions artifact and attempt immutable publication to R2 under a run-specific key. A mutable `latest.json` pointer may identify the newest immutable FWD1 run, but the pointer is never itself sufficient research evidence.

Minimum evidence per run:

- run metadata / code SHA;
- forward candidate rows;
- X1/X3 executable trade candidates;
- capital-constrained portfolio entries/skips/equity curves where applicable;
- censored-position audit;
- gate status;
- frozen membership snapshot and SPY pointer evidence.

## Production review gate

FWD1 does not automatically promote anything to production.

The earliest evidence-review gate requires **both**:

```text
>= 12 completed calendar months of forward observation
AND
>= 50 closed X3 portfolio trades
```

Before both conditions are satisfied, the status remains `ACCUMULATING` regardless of apparent performance.

When both are satisfied, status becomes `REVIEW_ELIGIBLE`, not `PRODUCTION_READY`.

## Metrics allowed during accumulation

Operational counts and data-quality audits may be monitored continuously. Performance metrics may be recorded mechanically by the pipeline, but no rule may be changed because of interim performance.

At the review gate, evaluate at minimum:

- X3 vs X1 total return / CAGR / max drawdown;
- cost sensitivity;
- realized trade PF and PF ex-largest winners where sample supports it;
- annual/subperiod stability;
- concentration;
- benchmark-relative context;
- divergence from historical expectations.

## Anti-data-mining rule

Any strategy-rule change proposed after 2026-09-09 is a new versioned hypothesis. It cannot replace FWD1 retroactively and must receive its own independent forward-validation clock.
