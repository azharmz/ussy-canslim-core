# #45 Market Exposure Action v1 — Freeze Decision

Date: 2026-09-14
Status: **IMPLEMENTATION COMPLETE / FROZEN v1**

Contract: `45-market-exposure-action-v1`

## Decision

Freeze the portfolio-level market exposure action semantics as a layer separate from stock-level lifecycle exits.

## Frozen semantics

Exposure bands:
- E0 = 0-20%
- E1 = 20-40%
- E2 = 40-60%
- E3 = 60-80%
- E4 = 80-100%

Transitions:
- `CORRECTION` => target E0, block new entries;
- `RALLY_ATTEMPT` => no bullish re-entry permission; defensive posture remains;
- `FOLLOW_THROUGH_CONFIRMED` from E0 => E1, permitting gradual re-engagement;
- `UPTREND_HEALTHY` => at most one-band increase, capped E4;
- `UPTREND_WEAKENING` => one-band reduction, floored E0;
- `NOT_EVALUABLE` => explicit, no new-entry permission.

#45 does not automatically liquidate individual positions and does not modify #43 stock-level exit arbitration. A later portfolio executor is required to translate a lower target exposure into specific position actions.

## Canonical validation

Workflow: `.github/workflows/45-market-exposure-action-v1.yml`

Canonical run:
- run `34802432732`
- job `103847631050`
- commit `4c1f5cbf536d1d144abcd41360019dab7dfca3b8`
- result: **SUCCESS**
- tests: **12 passed**

## Governance consequence

The CAN SLIM `M` layer now has a frozen portfolio-action vocabulary and causal transition contract. The proprietary/dynamic classification of market health is not reverse-engineered here; upstream market-state evidence remains a separate future specification. No historical performance tuning is authorized.