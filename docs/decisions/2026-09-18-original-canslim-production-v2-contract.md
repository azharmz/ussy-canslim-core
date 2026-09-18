# Original CAN SLIM Production v2 — methodology-first architecture contract

Date: 2026-09-18  
Status: **PROPOSED / THEORY-LOCKED FOR IMPLEMENTATION DESIGN — NO v1 MUTATION**

## Decision

The next production architecture will not inherit the frozen v1 compute order or its all-seven-letters Boolean eligibility contract merely because those contracts already exist.

Methodological authority is O'Neil / IBD. Engineering must preserve the different roles of the CAN SLIM components and make every non-literal implementation explicit. The frozen v1 remains an immutable baseline and audit trail.

## Classification vocabulary

Every production rule must carry one of these labels:

- **ORIGINAL** — directly supported as an O'Neil/IBD methodological concept.
- **OPERATIONALIZATION** — original concept translated into a reproducible machine rule.
- **DATA_ADAPTATION** — changed because our data/execution clock cannot reproduce the original process literally.
- **PROXY** — transparent substitute for unavailable/proprietary evidence.
- **UNAVAILABLE** — original evidence is not defensibly available; do not invent it.

## Component-role contract

| Component | Production role | Classification | v2 treatment |
|---|---|---|---|
| M | market context, new-buy permission and exposure/risk throttle | ORIGINAL concept; OPERATIONALIZATION/PROXY classifier | compute early as global context; final entry still requires market permission |
| C | primary fundamental growth screen | ORIGINAL concept; OPERATIONALIZATION threshold/data mapping | first-stage stock screen |
| A | primary fundamental growth/consistency screen | ORIGINAL concept; OPERATIONALIZATION aggregation | first-stage stock screen |
| N | evidence of something new; price-high/breakout path is only one observable dimension | ORIGINAL concept; price path OPERATIONALIZATION; non-price catalyst may be UNAVAILABLE | preserve price and catalyst states separately; do not claim full N from breakout alone |
| S | supply/demand evidence; strong breakout demand is represented by volume | ORIGINAL concept; volume rule OPERATIONALIZATION | breakout-volume confirmation belongs to timing; broader supply evidence remains attached |
| L | leader screen plus RS/industry evidence | ORIGINAL concept; RS percentile PROXY | leadership screen/watchlist qualification; preserve RS-line/industry evidence separately |
| I | institutional sponsorship evidence/quality/trend | ORIGINAL concept; 13F implementation PROXY/OPERATIONALIZATION | attach PIT-safe evidence; not a universal Boolean veto unless separately authorized |
| proper base/pivot | technical setup and buy-point structure | ORIGINAL concept; frozen #33 is OPERATIONALIZATION | evaluate after stock reaches production watchlist; consume frozen #33 contract |
| breakout + volume | entry timing/confirmation | ORIGINAL concept; daily-EOD detection OPERATIONALIZATION | required technical trigger |
| T+1 Open | executable fill after completed daily signal | DATA_ADAPTATION | preserve explicitly; never describe as original O'Neil timing |

## v2 production decision flow

```text
canonical READY + PIT evidence
        |
        +--> M market context (global, computed independently)
        |
        v
C/A fundamental screen
        |
        v
fundamentally qualified stock population
        |
        v
L / available N / S / I evidence assembly
        |
        v
CAN SLIM watchlist
        |
        v
frozen #33 proper-base / landmark / pivot evaluation
        |
        v
pivot crossing + breakout-volume confirmation
        |
        v
final role-aware eligibility
        |
        +--> M must permit new buys
        |
        v
candidate -> T+1 Open executable check -> lifecycle
```

“Fundamental-first” means the first per-stock expensive selection gate is fundamental. It does not mean global M must be computed after fundamentals. M can already be known and must still authorize the eventual purchase.

## #33 compute architecture

Do not scan the entire READY universe with #33 before fundamental selection on the CAN SLIM critical path.

```text
READY -> PIT fundamental screen -> qualified/watchlist population -> #33 current setup evaluation
```

Full-universe #33 remains useful as a separate Pattern Intelligence product. Initial operational preference: periodic/weekly full-universe scan plus daily watchlist scan. Do not build a complex incremental engine until runtime/storage evidence shows it is needed. Frozen #33 morphology must not change.

## Eligibility correction relative to v1

Frozen v1 currently requires C PASS, A PASS, N PASS, S POSITIVE, L PASS/STRONG, I POSITIVE, and M ALLOW_NEW_BUYS. v2 must not copy this automatically.

The repository's frozen theory audit and candidate specification establish heterogeneous roles. Initial theory-authorized hard path:

```text
C screen PASS
AND A screen PASS
AND L individual leadership PASS
AND valid proper base/pivot
AND breakout demand confirmed
AND M permits new buys
```

Preserve N non-price, broader S, I, RS-line and industry evidence separately according to availability and theory role. This is a methodology correction, not a relaxation made because v1 produced too few candidates.

## C/A threshold warning

Do not blindly copy current production C/A hard formulas into a contract labelled original. Existing repo evidence already distinguishes production C-v1 (EPS YoY >=25% AND revenue YoY >=25%) from theory-faithful #32 (EPS growth core screen; sales growth evidence/confirmation), and production A-v1 (each of three annual YoY observations >=25%) from #32's sustained multi-year annual growth concept. Resolve exact v2 C/A machine formulas from authoritative methodology before coding the new eligibility adapter; never choose formulas from return optimization.

## N / I / M warnings

N must not be equated with breakout alone: persist N_price_state and N_catalyst_state, with unavailable catalyst evidence explicit. Institutional sponsorship is important but the 13F layer is a PIT-safe proxy/evidence representation, not automatically a universal veto. M is global market context and entry/exposure control, not merely another stock-level letter.

## Execution adaptation

Original breakout buying may occur during the breakout session. Our production signal uses completed daily bars, so information through T close implies earliest production fill at T+1 Open. This remains an explicit DATA_ADAPTATION, not original O'Neil timing.

## Migration boundary

v1 stays frozen. Build v2 beside it. Before replacement: freeze v2 component roles and C/A operationalization; implement role-aware watchlist; wire #33 after watchlist selection; prove PIT lineage and candidate chronology; prove T+1 causality; validate unchanged frozen components; run shadow production; compare outputs for explanation, not threshold tuning; explicitly approve cutover.

## Compute/recovery requirement

Before a heavy v2 workflow, identify the durable recovery boundary for a failure near 90%:

```text
prepare -> freeze READY + PIT input identities -> fundamental/watchlist checkpoint -> #33 compute -> raw candidate checkpoint -> validate -> publish -> downstream execution
```

Reusable checkpoints require lineage and fail closed on incompatible input/schema/algorithm identity.

## Explicit non-goals

This decision does not alter frozen #33 morphology or v1 production; authorize retroactive entries; use performance to tune CAN SLIM; merge backtest into production; solve the separate missing-date/institutional snapshot incident; or authorize proprietary IBD data fabrication.

## Next implementation work

1. Source-lock exact v2 C and A machine formulas.
2. Define `canslim-watchlist-contract-v2` with PIT lineage and reason codes.
3. Define role-aware `canslim-eligibility-contract-v2`.
4. Rewire a v2 orchestrator so fundamental/watchlist selection precedes #33 on the critical path.
5. Keep full-universe Pattern Intelligence separate and initially periodic.
6. Validate in shadow mode before cutover.
