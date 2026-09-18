# CAN SLIM v2 — C/A authoritative source lock

Date: 2026-09-18  
Status: **SOURCE-LOCKED FOR CONTRACT DESIGN — NO v1 MUTATION**

## Purpose

Resolve the first blocker in the v2 architecture decision: exact machine-facing interpretation of C and A must be grounded in O'Neil/IBD material before a v2 watchlist or eligibility adapter is coded.

This is methodology work, not performance tuning.

## Authoritative evidence used

Primary IBD educational source: *20 Rules for Your Investment Success*.

The source states, in substance:

- recent quarterly earnings **and sales** should be up **25% or more**;
- investors should compare the latest quarter with the same quarter a year earlier and look for accelerating growth;
- for annual quality, consider companies with **each of the last three years' earnings up 25% or more**, while also looking for ROE around 17%+ and accelerating recent earnings/sales;
- elsewhere in the same rule it describes screening for firms averaging at least 25% profit growth over the past three years.

A current IBD Investors Corner article (2025) likewise describes the CAN SLIM rule of thumb as seeking **25%+ increases in earnings and sales in the most recent quarter**, with acceleration as an important quality signal.

These sources are sufficient to correct the ambiguity recorded in the older #32 candidate spec. They support the existing production C-v1 conjunction more strongly than #32's softer wording implied.

## C — v2 source lock

### Original concept

Current quarterly growth is a primary stock-selection screen.

### Machine contract

For ordinary evaluable companies:

```text
C_v2_PASS =
    latest PIT-available quarterly EPS YoY >= 25%
    AND
    latest PIT-available quarterly sales/revenue YoY >= 25%
```

Availability remains governed by SEC information availability, not fiscal period end.

If either required comparison is not defensibly evaluable:

```text
C_v2_state = NOT_EVALUABLE
```

Do not coerce missing/undefined comparisons to zero.

### Evidence, not additional hard gate

Persist separately:

```text
EPS acceleration
sales acceleration
prior-quarter growth sequence
margin/quality evidence where available
```

Acceleration is methodologically important, but this source lock does not invent a new numerical acceleration gate.

### Classification

- quarterly EPS growth criterion: **ORIGINAL**
- quarterly sales growth criterion: **ORIGINAL**
- 25% machine threshold: **OPERATIONALIZATION strongly anchored to IBD guidance**
- SEC accepted-time mapping: **DATA_ADAPTATION / PIT operationalization**

## A — v2 source lock

### Original concept

Strong multi-year annual earnings growth is a primary stock-selection screen.

### Machine contract

The strongest explicit IBD wording available in the audited educational material is:

```text
each of the last three years' earnings up 25% or more
```

Therefore initial v2 deterministic contract is:

```text
A_v2_PASS =
    latest 3 required annual EPS growth observations are PIT-evaluable
    AND
    each >= 25%
```

If fewer than the required observations are defensibly available or a required comparison is structurally undefined:

```text
A_v2_state = NOT_EVALUABLE
```

This preserves the existing production A-v1 hard growth shape rather than replacing it with a post-hoc CAGR formula.

### Additional quality evidence

Persist separately:

```text
three-year EPS growth rate / average growth descriptor
ROE
recent EPS/sales acceleration
annual consistency / stability
```

IBD's educational material explicitly discusses ROE around 17%+ and accelerating recent growth as desirable quality evidence. This decision does **not** add ROE as a universal v2 hard gate because the current upstream C/A production contract does not yet provide a frozen PIT ROE input and the source language is framed as a screening/quality consideration rather than enough evidence here to justify silently changing the existing C/A data contract.

### Classification

- sustained annual earnings growth: **ORIGINAL**
- three annual growth observations >=25%: **OPERATIONALIZATION strongly anchored to explicit IBD wording**
- ROE/acceleration: **ORIGINAL quality evidence; currently not a new hard v2 gate**
- SEC accepted-time mapping: **DATA_ADAPTATION / PIT operationalization**

## Resolution of #32 ambiguity

The older theory-faithful #32 spec said:

- sales growth was required evidence but did not freeze revenue >=25% as a universal C conjunction;
- A was sustained multi-year growth around 25% but did not freeze the old each-year rule as canonical identity.

That caution was appropriate when evidence had not yet been source-locked.

This decision supersedes only that ambiguity **for v2 contract design** because explicit IBD educational wording now supports:

```text
C: quarterly EPS >=25% AND quarterly sales >=25%
A: each of last three annual earnings growth observations >=25%
```

It does not rewrite historical #32 or frozen v1 documents.

## What does NOT change

- v1 remains frozen.
- Missing remains NOT_EVALUABLE, not FAIL/zero.
- PIT availability remains mandatory.
- Negative/zero-base accounting semantics remain explicit.
- No performance result was consulted to choose these rules.
- No new ROE hard gate is authorized.
- No acceleration threshold is invented.
- This does not decide N/S/L/I/M roles; those remain governed by the v2 architecture decision.

## Implementation consequence

C/A no longer block design of the v2 watchlist contract.

The next contract may safely use:

```text
fundamental_core_pass = C_v2_PASS AND A_v2_PASS
```

as the first per-stock production selection gate, with full reason codes and PIT lineage.

## Source references

- Investor's Business Daily, *20 Rules for Your Investment Success*.
- Investor's Business Daily, Investors Corner, *How To Pick Great Stocks: Do You Look For This Factor In Earnings?*, 2025-03-20.

Repository documentation should retain source titles and retrieval context; do not copy long copyrighted passages.
