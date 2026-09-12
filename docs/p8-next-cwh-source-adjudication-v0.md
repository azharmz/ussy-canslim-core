# P8 next CUP_WITH_HANDLE source adjudication v0

Date: 2026-09-13
Scope: DEVELOPMENT corpus expansion only. No return/CAGR/PF evidence is used.

## Purpose

After the TW withdrawal, new authoritative examples must be source-first: a detector-comparable field is populated only when the inspected source actually supports it. Missing exact boundaries or landmarks are not reconstructed from the chart merely to make an example evaluable.

## Candidate: TSM, late 2024 CUP_WITH_HANDLE

Authoritative IBD evidence inspected:

- IBD Stock Of The Day, 2024-12-13: TSM is explicitly described as being in a `cup-with-handle base` with a `205.63` buy point.
- IBD technology coverage, 2024-10-28: TSM had reached a record high of `212.60` on 2024-10-17 after earnings.
- IBD earnings coverage later records the eventual 2024-12-23 breakout from the cup-with-handle at `205.63`.

Adjudication: **DO NOT PROMOTE TO DEVELOPMENT YET.**

Reason: the inspected authoritative text supports the named pattern and buy point, but it does not explicitly publish the exact cup/base start boundary. Treating the 2024-10-17 record high as the exact base start would be analyst inference, not a source-provided morphology anchor. The current v0.6 labelled evaluator intentionally requires at least a source-anchored `window_start`; therefore TSM remains a source candidate rather than a frozen label.

References:

- https://www.investors.com/research/ibd-stock-of-the-day/tsm-stock-taiwan-semiconductor-basks-in-ai-glow/ (prior September base context)
- https://www.investors.com/news/technology/tsm-stock-taiwan-semiconductor-falls-china-trade-breach/ (2024-10-17 record-high context)
- https://www.investors.com/research/ibd-stock-of-the-day/tsm-stock-actionable-after-broadcom-boost/ (explicit late-2024 CWH / 205.63)
- https://www.investors.com/news/technology/tsm-stock-taiwan-semiconductor-q4-2024-earnings/ (Dec. 23 breakout / 205.63)

## Candidate: OLED, 2019 CUP_WITH_HANDLE

Authoritative IBD Top Stocks 2019 evidence explicitly states that Universal Display broke out on 2019-06-18 from a second-stage `cup-with-handle base` at a `177.05` buy point.

Adjudication: **DO NOT PROMOTE TO DEVELOPMENT YET.**

Reason: the inspected source supports pattern type, stage, breakout date and buy point, but does not publish an exact base-start boundary in the available text. Under the same source-first rule, an inferred start is not written into `labels_v0.csv`.

Reference:

- https://shop.investors.com/images/promotional/shop/assets/pdf/TopStocks-2019.pdf

## Evaluator v0.6 CI status

The branch workflow run triggered by commit `ce7b68378b7bf2e3147a176843ac307497fd726c` (`P8: test partial source boundary semantics`) completed successfully as run `34705192430`.

This verifies the v0.6 partial-end semantics in CI while leaving the untouched NFLX VALIDATION example locked.

## Decision

1. Keep SNPS as the sole frozen DEVELOPMENT match for now.
2. Keep NFLX (`p8-label-0002`) VALIDATION locked and untouched.
3. Keep TSM and OLED in adjudication/source-candidate state; do not manufacture exact start boundaries.
4. Continue searching for a non-FLAT authoritative example that explicitly supplies a detector-comparable start anchor. If none can be sourced, change the evaluator schema only through a separately documented semantic decision that supports independent optional dimensions; do not weaken it ad hoc for a desired example.
