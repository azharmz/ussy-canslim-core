# Decision — #48 Major Index Source Audit

Date: 2026-09-14
Status: `SOURCE AUDIT COMPLETE / YAHOO-YFINANCE APPROVED FOR INITIAL PRODUCTION INPUT v1`
Upstream contract: `47-market-input-data-contract-v1`
Consumer classifier: `46-market-state-classification-v1`

## Scope

Independent audit executed in `azharmz/ussy-data` against the three frozen #47 canonical major-index identities:

| Canonical index | Yahoo symbol | Verdict |
|---|---|---|
| `NASDAQ_COMPOSITE` | `^IXIC` | PASS |
| `SP500` | `^GSPC` | PASS |
| `DJIA` | `^DJI` | PASS |

Run: `34807791390`
Job: `103862942417`
Head commit: `cfb5970c0f515fd08350592596f1cbd0bcef3c22`
Artifact: `major-index-source-audit-34807791390`
Artifact id: `10333836848`
Artifact digest: `sha256:c4943ec895549b1ddd192f7a4c7d37704555fd6616db5cec6d436c19acfd5dab`

Audit source versions:
- yfinance `0.2.66`
- pandas `2.3.3`
- pyarrow `23.0.1`

## Audit result

Each source returned 548 daily rows from 2024-07-08 through 2026-09-11 under the preregistered fetch window. The latest 60 returned sessions were audited.

### Nasdaq Composite / `^IXIC`

PASS on all preregistered checks:
- non-empty;
- required OHLCV columns present;
- dates parseable, unique, monotonic;
- recent OHLC complete and envelope-valid;
- recent volume complete, non-negative, not all zero, and varying;
- recent volume range: 6,529,110,000 to 18,286,150,000;
- 59 distinct recent volume values across 60 rows.

### S&P 500 / `^GSPC`

PASS on all preregistered checks.
Recent volume range: 4,006,370,000 to 9,105,600,000; 60 distinct recent values.

### Dow Jones Industrial Average / `^DJI`

PASS on all preregistered checks.
Recent volume range: 319,610,000 to 1,297,680,000; 60 distinct recent values.

## Decision

Yahoo/yfinance is approved as the **initial production input source v1** for these exact canonical mappings:

```text
NASDAQ_COMPOSITE -> ^IXIC
SP500            -> ^GSPC
DJIA             -> ^DJI
```

This approval is limited to the tested retrieval semantics and provenance contract. It does not claim Yahoo is exchange-authoritative, nor does it authorize silent provider substitution.

SPY, QQQ and DIA remain non-canonical for #46 and must not substitute for the three index series.

## Production requirements

The future production publisher must:
1. preserve raw Yahoo index OHLCV with `auto_adjust=False`;
2. retain source symbol/provider, fetch timestamp and contract version;
3. publish immutable run objects plus an official pointer per canonical index;
4. perform the same OHLC/date/volume validation before pointer advancement;
5. never impute missing volume from ETFs or other indexes;
6. stop pointer advancement if source identity, volume semantics or historical overlap materially changes;
7. expose only completed sessions to #46.

## Governance consequence

#48 resolves the provider-selection blocker for major-index OHLCV. The next clean workstream is production publication/wiring of these three audited series from `ussy-data` into #47/#46.

No #33-#47 semantics are changed. FWD1, X3 and EXH2 remain unchanged.
