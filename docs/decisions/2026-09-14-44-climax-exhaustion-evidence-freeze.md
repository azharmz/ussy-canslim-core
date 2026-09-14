# #44 Climax / Exhaustion Evidence v1 — Freeze Decision

Date: 2026-09-14
Status: **EVIDENCE LAYER COMPLETE / FROZEN v1**

Contract: `44-climax-exhaustion-evidence-v1`

## Decision

Freeze the reproducible climax/exhaustion evidence layer without promoting a new executable exit.

## Frozen evidence channels

- strict largest close-to-close up-day point gain since breakout;
- strict heaviest daily volume since breakout;
- 7-of-8 completed-session up-day sequence;
- 8-of-10 completed-session up-day sequence;
- raw exhaustion-gap evidence: current low > prior high;
- weekly range and strict largest weekly range since breakout when weekly bars are supplied;
- completed-session/week chronology since breakout;
- explicit prior-advance context state without universal stage/maturity action threshold.

## Context boundary

Authoritative O'Neil material treats climax/exhaustion as contextual after a substantial prior advance. Some exhaustion-gap guidance distinguishes about 18+ weeks from first/second-stage bases versus 12+ weeks from later-stage bases. The current frozen production lineage does not yet supply a canonical base-stage contract suitable for universal action promotion, so #44 remains evidence-only.

## EXH2 independence

EXH2 remains `PRE-REGISTERED / LIVE / ACCUMULATING` as a separate prospective diagnostic based on an exploratory extreme-shock and T+1 rejection mechanism. Its 5.3333% shock boundary is not imported into #44 and #44 must not be represented as EXH2 validation.

## Canonical validation

Workflow: `.github/workflows/44-climax-exhaustion-evidence-v1.yml`

Canonical run:
- run `34797449482`
- job `103833195506`
- commit `4697283dbd57c5cc15b5ac7d718f9d6a551ed85b`
- result: **SUCCESS**
- tests: **10 passed in 0.03s**

## Governance consequence

#44 adds no fourth executable exit channel. #43 lifecycle v2 remains unchanged. Any future climax sell action must start a separately versioned action specification from frozen authoritative evidence and then enter a later lifecycle version only after semantic/causal validation.
