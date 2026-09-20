# Flat Base vNext R2-E — untouched validation registry

Status: **VALIDATION ORACLES FROZEN BEFORE REPLAY**

Freeze date: 2026-09-20

Candidate semantics under test were frozen earlier at commit `b1fc3124cf86df71088196e775783d949c31ea18`.

## Anti-leakage

This cohort excludes all Golden Flat Base, R1-E, R2-A and R2-B symbols/cases. No validation result may be used to change R2-D and then rescored on this cohort.

## Frozen source-backed validation cases

| ID | Symbol | Source as-of | Source evidence | Oracle pivot |
| --- | --- | --- | --- | ---: |
| V01 | VEEV | 2025-07-18 | IBD says VEEV formed a newly formed flat base after its late-May earnings gap; buy point 291.69 | 291.69 |
| V02 | NVDA | 2025-09-26 | IBD/MarketSurge explicitly identifies a flat-base buy point | 184.48 |
| V03 | EME | 2025-10-02 | IBD identifies a second-stage flat base | 667.64 |
| V04 | IBKR | 2025-11-11 | MarketSurge weekly chart identifies a flat base on top of prior cup | 73.35 |

Sources are frozen by article date and quoted pattern/pivot facts. Replay uses only information available through each source as-of.

## Scoring

For each case:
1. compare source oracle pivot to frozen-engine nearest Flat Base pivot, with auditable split-basis normalization when necessary;
2. only source-aligned pivot/boundary cases enter morphology scoring;
3. evaluate explicit distinct trading weeks >=5 and depth <=15%;
4. evaluate R2-D candidate final state without tuning.

Upstream reconstruction misses are reported separately and never counted as morphology failures.
