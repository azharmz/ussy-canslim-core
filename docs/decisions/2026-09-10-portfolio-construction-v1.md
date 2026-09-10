# Decision Record — Portfolio Construction v1

Date: 2026-09-10

Status: COMPLETE / VALIDATED DESCRIPTIVE

## Scope

Apply the pre-registered capital-constrained portfolio model to the frozen X3 BASE strategy track and mandatory X1 BASE control. No C/A hard filter and no EXH2 exhaustion filter are applied.

The methodology was frozen before portfolio outcome review in `docs/methodology/portfolio-construction-v1.md`.

## Frozen portfolio specification

- initial equity: 100,000 arbitrary units;
- long-only, no leverage, no shorting;
- max 7 concurrent positions;
- new-position target notional = 1/7 of prior-session closing equity;
- no partial fills when cash is insufficient;
- one position per security, no pyramiding;
- same-session allocation priority: `rs_percentile DESC`, then `volume_ratio DESC`, then ticker ASC;
- entries occur before same-day exits;
- 7% stop from actual fill and 20% target from pivot remain unchanged;
- same-bar ambiguity is stop-first;
- censored positions at the sample boundary remain mark-to-market and are not forced liquidations;
- gross curve plus 10 bps entry + 10 bps exit cost sensitivity.

## Workflow and evidence

Canonical successful workflow run: `34488197400`

Code head: `35e62cdc53894381c5528560036a1201ba406699`

Artifact: `portfolio-construction-v1-34488197400`

Artifact SHA-256: `687c9557b975802ae388861228c3c3fc0ffed191c4730affb38bccd470080636`

This supersedes PORT1 run `34485765478` only for metric/accounting finalization. Portfolio allocations and frozen strategy rules were unchanged. The finalizer makes two accounting invariants explicit: boundary `CENSORED_OPEN` positions remain mark-to-market with no phantom exit cost, and CAGR is calculated consistently from the declared 100,000 initial capital rather than the first post-entry EOD equity.

Censored audit: X1 has 4 and X3 has 2 final censored positions, all at the 2026-09-09 sample boundary; mid-sample censored positions = 0.

## Portfolio results

| Metric | X1 BASE | X3 BASE |
|---|---:|---:|
| Candidate trades | 5,777 | 3,604 |
| Portfolio entries | 1,424 | 1,129 |
| Capacity skips | 1,010 | 564 |
| Cash skips | 3,343 | 1,911 |
| Gross total return | +30.70% | **+172.90%** |
| Gross CAGR | +0.80% | **+3.04%** |
| Gross max drawdown | -66.89% | **-43.36%** |
| Cost20bp total return | -20.86% | **+121.37%** |
| Cost20bp CAGR | -0.70% | **+2.40%** |
| Cost20bp max drawdown | -85.78% | **-50.94%** |
| Median positions | 5 | 4 |
| Median gross exposure | 70.5% | 59.1% |
| Top-1 abs PnL contribution share | 1.04% | 1.46% |
| Top-5 abs PnL contribution share | 4.56% | 5.21% |

Research span is roughly March 1993 through 2026-09-09.

## Interpretation

X3 remains clearly superior to X1 after capital constraints: it produces higher total return/CAGR and materially lower drawdown under both gross and cost-sensitive curves.

However, the absolute portfolio profile is weak for a production claim. Even X3 produces only about 3.0% gross CAGR over the long sample with roughly 43% gross maximum drawdown; with 20 bps round-trip cost sensitivity, CAGR is about 2.4% and maximum drawdown about 51%. X1 is economically unattractive after costs.

Therefore PORT1 does **not** justify production deployment. It validates that the X3 entry-selection advantage survives portfolio construction, while also showing that the current overall strategy edge is not strong enough on an absolute risk-adjusted basis.

The high cash/capacity skip counts are a real portfolio effect, not missing trades: accepted + capacity skips + cash skips exactly reconcile to the frozen candidate-trade counts for both X1 and X3.

## Decision

1. Mark PORT1 COMPLETE / VALIDATED DESCRIPTIVE.
2. Retain X3 BASE as the primary research track and X1 BASE as mandatory control.
3. Do not tune max positions, sizing, ranking, cost assumptions or event ordering from these outcomes.
4. Do not promote the strategy to production from PORT1.
5. Proceed to ROB1 robustness and genuine forward validation, with EXH2 still separate.
6. Treat C/A as descriptors only; do not reintroduce them as hard filters based on PORT1.
