# Flat Base vNext R1-E — independent holdout registry

Status: **SOURCE ORACLES FROZEN — detector not yet evaluated**

Freeze date: 2026-09-20

Purpose: construct a source-backed Flat Base holdout absent from the original 40-case golden reconstruction. Source evidence and oracle fields are frozen before detector replay.

## Independence rule

None of the cases below is one of the 10 Flat Base golden cases (AAPL, SNPS, META, TW, NOW, DECK, CROX, CPRT, AMZN, KKR). No frozen-engine output was consulted to select these cases.

The holdout is **not** a threshold-development set. R1-D H1-H5 are evaluated as frozen.

## Frozen holdout

| ID | Symbol | Source as-of | Source-backed Flat Base evidence | Frozen oracle pivot | Oracle duration evidence |
| --- | --- | --- | --- | ---: | --- |
| H01 | TRV | 2024-11-27 | IBD/MarketSurge: six-week Flat Base formed above 50-day line | 269.56 | six weeks |
| H02 | TSM | 2024-11-23 | IBD: five-week Flat Base above prior cup-with-handle | 212.60 | five weeks |
| H03 | KNTK | 2025-01-02 | IBD Stock Of The Day: six-week Flat Base | 62.55 | six weeks |
| H04 | EQT | 2025-01-02 | same IBD article: six-week Flat Base | 48.02 | six weeks |
| H05 | MELI | 2025-06-21 | IBD: five-week Flat Base on top of prior double-bottom consolidation | 2635.88 | five weeks |
| H06 | TOST | 2025-06-21 | IBD: five-week Flat Base atop several months of consolidation | 45.56 | five weeks |
| H07 | ULS | 2025-06-21 | IBD: official five-week Flat Base; source explicitly describes it as 6% deep and very tight | 72.81 | five weeks; 6% depth |
| H08 | BK | 2025-11-10 | IBD Stock Of The Day: Flat Base lasted six weeks | 110.87 | six weeks |

## Source URLs

- TRV: https://www.investors.com/research/ibd-stock-of-the-day/dow-jones-stock-travelers-insurance-breakout-2024-rally/
- TSM: https://www.investors.com/news/nvidia-chipmaker-taiwan-semiconductor-stocks-to-watch/
- KNTK / EQT: https://www.investors.com/research/ibd-stock-of-the-day/kinetik-stock-entry-oil-prices-oxy-stock-eqt-lng/
- MELI / TOST / ULS: https://www.investors.com/news/uber-stock-mercadolibre-meli-five-stocks-near-buy-points/
- BK: https://www.investors.com/research/ibd-stock-of-the-day/bny-mellon-stock-of-the-day-top-u-s-bank-stock-near-buy-point/

## Oracle policy

The source-stated buy point is frozen as the oracle pivot. The source-stated duration/depth is evidence for source semantics, not recomputed ground truth.

Detector replay must:

1. use only OHLC bars available as of the source date;
2. preserve explicit corporate-action price-basis lineage;
3. find the oracle-nearest Flat Base lineage without source labels influencing candidate generation;
4. report pivot delta, candidate semantics, duration sessions, distinct trading-week span, depth, normalized total range, close dispersion, H2 weekly descriptors, frozen TIGHT/WIDE_LOOSE flags and state;
5. classify source-pivot-not-reconstructed separately from morphology-gate disagreement.

No threshold or engine behavior may change during this replay.
