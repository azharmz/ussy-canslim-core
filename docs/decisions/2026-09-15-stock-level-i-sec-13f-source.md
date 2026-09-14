# Decision — Stock-Level CAN SLIM I via SEC 13F

Date: 2026-09-15

Status: **STOCK-LEVEL I SOURCE AVAILABLE / #54 MARKET-DEMAND CHANNEL STILL SEPARATE**

## Purpose

Record the boundary between two concepts that must not be conflated:

1. stock-level CAN SLIM `I — Institutional Sponsorship`; and
2. #51/#54 market-level institutional accumulation/selling evidence used to confirm or weaken general-market leadership.

## Canonical stock-level I source

`azharmz/ussy-fundamentals` already has a PIT Form 13F pipeline and canonical R2 publication.

Current-state evidence:

- run `34603142916` / job `103275091513` — SUCCESS;
- universe 1,327 securities;
- 1,010 deterministic U.S.-ISIN identities;
- 996 mapped securities in latest report period 2026-06-30;
- 9,731 current filing-calendar 13F filings processed;
- 100% filing fetch success and accepted-at completeness;
- 383/383 amendments classified;
- data-quality gate PASS.

Canonical sponsorship publication:

- run `34663714292` / job `103471275697` — SUCCESS;
- R2 snapshot prefix `institutional_sponsorship/snapshots/2026-09-12/run-34663714292`;
- pointer status READY.

The production identity mapping for U.S. securities is deterministic from the project U.S. ISIN: the 9-character CUSIP is the ISIN body after the `US` prefix and before the final ISIN check digit. OpenFIGI is therefore not a production prerequisite for these securities.

## What this source can support

The 13F state may support stock-level institutional-sponsorship evidence such as:

- number of reporting institutional managers;
- reported aggregate shares/value;
- changes across available filing states;
- PIT availability/provenance and amendment uncertainty.

This is suitable evidence for CAN SLIM `I` subject to the frozen stock-level classification contract.

## What it cannot support

13F is quarterly and delayed. It must not be represented as:

- real-time institutional buying/selling;
- IBD Accumulation/Distribution Rating;
- a daily market-leader accumulation signal;
- `leadership_confirming=True` or `weakening_confirmed=True` for frozen #46.

Therefore this finding does **not** close #51/#54's market-level institutional-demand/selling evidence debt.

## #54 implication

#54 no longer needs to investigate SEC 13F as if it were an unavailable stock-level `I` source. That source already exists and is live in the fundamentals repository.

#54 should remain focused on the unresolved market-level question: whether a defensible PIT source/calculation can evidence institutional accumulation/selling in leaders without fabricating a proprietary IBD A/D measure or rebuilding unnecessary broad-market infrastructure.

## Terminal boundary

**STOCK-LEVEL `I`: AVAILABLE THROUGH CANONICAL SEC 13F DATA**

**MARKET-LEVEL INSTITUTIONAL DEMAND/SELLING FOR #51/#54: UNRESOLVED / SEPARATE**
