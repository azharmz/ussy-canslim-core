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


## Untouched validation result

Actions run: `35515149758`.

- NVDA: oracle 184.48; nearest adjusted-basis pivot 184.0287 (-0.245%). Source-aligned practical-near. Open-right-edge = 7 trading weeks, depth 11.06%. Frozen state AMBIGUOUS:WIDE_LOOSE; R2-D candidate = **RECOGNIZED**.
- EME: oracle 667.64; nearest pivot 666.3181 (-0.198%). Source-aligned practical-near. Open-right-edge = 10 trading weeks, depth 11.73%. Frozen state AMBIGUOUS:WIDE_LOOSE; R2-D candidate = **RECOGNIZED**.
- IBKR: oracle 73.35; nearest pivot 73.0410 (-0.421%). Source-aligned practical-near. Open-right-edge = 6 trading weeks / 23 sessions, depth 12.54%. Frozen state REJECTED:TOO_SHORT+WIDE_LOOSE; R2-D candidate = **RECOGNIZED**. This independently validates the 5-trading-week vs 25-session correction.
- VEEV: oracle 291.69; nearest engine pivot 258.93 (-11.23%). **UPSTREAM PIVOT/BOUNDARY MISS**; morphology not scored.

### Validation conclusion

Among the three untouched cases with source-aligned practical-near pivot reconstruction, R2-D candidate semantics recognize **3/3** source-labelled Flat Bases. The fourth case is an upstream reconstruction miss and is excluded from morphology scoring by the preregistered contract.

This is a clean untouched validation pass for the narrow morphology-state question, but it is not sufficient by itself for production promotion. It does not validate upstream landmark/pivot recall and it does not establish a quantitative tightness-quality gate.

Next gate: implement the frozen R2-D semantics as a research candidate in the engine repository, then run regression across all four core pattern families before any production-contract decision.
