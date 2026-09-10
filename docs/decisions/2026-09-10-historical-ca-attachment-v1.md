# Historical C/A Attachment v1 — Validation Decision

Date: 2026-09-10

Status: **COMPLETE / VALIDATED**

## Purpose

Attach frozen C-v1 and A-v1 labels to every historical technical candidate using only fundamental evidence available by the T0 decision cutoff. This is a consumer-side research step; it does not change `ussy-fundamentals` extraction semantics or CAN SLIM thresholds.

## Validated run

GitHub Actions run: `34479060107`

Code commit: `26892121cb4a650b5fe9e00491a557963b9f49c1`

Pinned fundamentals manifest:

`fundamentals/snapshots/2026-09-10/run-34470910341/manifest.json`

Research universe:

`CURRENT_COMPLIANT_UNIVERSE_FROZEN_AT_2026_08_28`

## C selector

At T0 16:00 America/New_York, DST-aware:

1. keep only PIT rows with `accepted_at <= cutoff`;
2. choose the latest known `fiscal_period_end`;
3. within that quarter choose the latest accepted state;
4. evaluate C-v1 only when both EPS YoY and revenue YoY are numeric;
5. missing/undefined remains `NOT_EVALUABLE`.

Audit confirmed zero future-`accepted_at` uses and zero evaluated C rows with a missing numeric leg.

## A selector and fiscal-year identity

The production wide PIT table carries annual state but does not expose SEC fiscal year. For historical A-v1, the consumer therefore uses the immutable long PIT artifact only as an identity bridge:

`annual_eps_source_accession -> SEC fy`

The long PIT preserves SEC `fy` on filing rows. The selector then:

1. keeps annual states with `annual_eps_accepted_at <= cutoff`;
2. resolves each annual source accession to SEC fiscal year where possible;
3. chooses the latest accepted annual state within each resolved FY;
4. takes the latest three distinct FY;
5. requires those three FY to be consecutive before A can PASS;
6. unresolved FY identity remains `NOT_EVALUABLE` rather than being guessed from calendar dates.

This is intentionally conservative. It prevents amendments or multiple annual source accessions from being mistaken for three separate fiscal years. No A PASS is permitted when FY identity is unresolved or non-consecutive.

## Structural audit

```text
candidate rows                         10,731
candidate securities                      860
duplicate candidate attachment rows         0
future accepted_at violations               0
identity-missing-CIK rows                   56

annual states                           11,703
annual FY resolved                     10,307
annual FY unresolved                    1,396
candidate rows with unresolved FY       4,139
candidate rows with non-consecutive FY     61
```

All 34 A-PASS candidate rows were independently checked to contain exactly three resolved consecutive fiscal years and zero unresolved FY states.

## Historical label distribution

| Label | PASS | FAIL | NOT_EVALUABLE |
|---|---:|---:|---:|
| C-v1 | 703 | 3,475 | 6,553 |
| A-v1 | 34 | 768 | 9,929 |
| C+A | 2 | 650 | 10,079 |

The two C+A PASS candidate events in this run are:

- `CRUS`, signal date `2022-08-03`, annual FY `2020,2021,2022`;
- `MEDP`, signal date `2023-07-25`, annual FY `2020,2021,2022`.

These counts are descriptive attachment results only. No trading performance metric was used to tune or validate the C/A thresholds.

## Evidence contract

Workflow artifact `historical-ca-attachment-v1-34479060107` contains:

- `candidate_ca_labels.csv`
- `summary.json`
- `fundamentals_current_pointer.json`
- `fundamentals_snapshot_manifest.json`
- `membership_snapshot.json`

Artifact SHA-256 reported by GitHub: `be23394a14b3096a491b67fb4836edb2656739e30ad7cefd31c52492e5f9afeb`.

## Decision

CA-HIST is accepted as **COMPLETE / VALIDATED** for the frozen v1 methodology. Unresolved fiscal-year identity is a coverage/evaluability limitation, not a reason to guess or alter upstream data. The next permitted experiment is the pre-specified fundamental ablation:

- X3 baseline vs X3+C vs X3+C+A;
- X1 equivalents retained as mandatory execution control.

The post-breakout exhaustion hypothesis remains a separate exploratory/validation workstream and must not be silently folded into the C/A ablation.
