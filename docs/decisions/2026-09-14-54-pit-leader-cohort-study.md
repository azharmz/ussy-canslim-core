# Decision — #54 PIT Leader-Cohort / Institutional-Demand Evidence Study

Date: 2026-09-14

Status: **PREREGISTERED EVIDENCE STUDY / DETERMINISTIC PRODUCTION SELECTOR NOT YET AUTHORIZED**

## Decision

The project will treat #54 as the research bridge between #53 broad-market PIT membership and #51 market leadership/weakening evidence.

Authoritative O'Neil evidence supports these evidence families for market leaders:

- relative strength / outperformance;
- price leadership and movement to new highs;
- strong price-volume demand / accumulation;
- institutional sponsorship / money moving into leaders;
- later leader failure and institutional selling as weakening evidence.

However, the reviewed authoritative material does not establish one universal public numeric algorithm that can safely classify every #53 member as a general-market leader. Therefore #54 does not authorize a production leader/non-leader selector.

## Implemented boundary

`src/canslim_research/leader_cohort_evidence_v1.py` validates PIT evidence-packet research eligibility only. It explicitly rejects future-return use, restricted-universe substitution and invalid membership chronology. It never emits a leader label.

The semantic tests freeze this anti-leakage boundary.

## Consequence

#53 remains membership-only. #51 remains the governing contract for `leadership_confirming` / `weakening_confirmed`. #50 must continue using `None` when no approved evidence packet exists.

Any later deterministic selector must be preregistered before outcome inspection and pass an untouched validation cycle. Numeric choices unsupported by authoritative evidence are research conventions, not O'Neil facts.
