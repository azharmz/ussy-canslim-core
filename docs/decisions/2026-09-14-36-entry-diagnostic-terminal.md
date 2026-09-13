# #36 Entry Diagnostic Terminal Decision

Date: 2026-09-14
Status: **DIAGNOSTIC COMPLETE / NO VARIANT PROMOTION**

## Primary actionable comparison

The preregistered CANSLIM-eligible R0/R1/R2/R3 historical comparison remains:

`BLOCKED_ON_ELIGIBLE_POPULATION`

Canonical #35 historical pool run `34763920536` contains 265,642 observations but zero `CANSLIM_ELIGIBLE` observations. Source-population audit run `34786499862` completed SUCCESS and inspected no performance metrics.

This does not reopen #33/#34/#35 and does not authorize widening the primary actionable population.

## Separate breakout-confirmed execution diagnostic

A separately preregistered diagnostic was run only on frozen `BREAKOUT_CONFIRMED` records.

Run: `34786603831` → **SUCCESS**

- source candidate records: 138
- unique securities: 6
- unique security-date signal events: 12
- integrity findings: 0
- source contract remained frozen
- no future bar altered signal-T candidate state
- all fills were observed opens inside the frozen 0%-5% buy zone
- R2/R3 confirmations preceded fills

Artifact: `e36-breakout-execution-diagnostic-34786603831`
Artifact SHA-256: `d8c3063fbadf595429bc999db7b50f7a62d0fd693fdfaf27297f74d6b66f59a1`

## Execution coverage

- R0: 18 / 138 executed (13.0%)
- R1: 21 / 138 executed (15.2%), +3 incremental candidates vs R0
- R2: 13 / 138 executed (9.4%), +2 incremental candidates vs R0
- R3: 18 / 138 executed (13.0%), +2 incremental candidates vs R0

These are execution diagnostics, not CAN SLIM strategy performance.

## Outcome evidence

Fixed 5/10/20/30-session outcome metrics and 20-session MFE/MAE were computed only after the integrity gate passed, as preregistered.

The candidate-level evidence is highly clustered: 138 candidate records collapse to only 12 security-date signal events. Multiple pattern candidates on the same security/date therefore share the same subsequent market path. Candidate-level means, win rates, and percentiles must not be interpreted as 138 independent trials.

The diagnostic does not provide a governance-quality basis to promote R1, R2, or R3 over R0. In particular:

- R1 increases execution coverage only modestly;
- R2 and R3 select smaller/different subsets and show horizon-dependent outcomes;
- no return statistic overrides the clustering/dependence problem or the absence of a true `CANSLIM_ELIGIBLE` historical source population;
- R3 remains an explicitly non-authoritative +2% research proxy.

## Terminal #36 governance

Canonical `36-execution-entry-v1` remains **FROZEN**:

```text
CANSLIM_ELIGIBLE at T
→ signal known after close T
→ earliest causal fill T+1
→ execute at observed T+1 open iff pivot <= open <= pivot * 1.05
```

R1/R2/R3 remain **RESEARCH-ONLY / NOT PROMOTED**.

#36 historical performance validation of the actionable CAN SLIM entry layer remains blocked until a genuine frozen `CANSLIM_ELIGIBLE` source population exists. That future evidence must be evaluated without retuning the frozen baseline from the breakout-confirmed diagnostic.

Terminal status:

`BASELINE FROZEN / DIAGNOSTIC COMPLETE / PRIMARY PERFORMANCE VALIDATION BLOCKED_ON_ELIGIBLE_POPULATION`
