# P8 decision — v0.3 structural identity / lineage audit

Date: 2026-09-13
Scope: #33 O'Neil Pattern Recognition Engine, DEVELOPMENT morphology only

## Question

Did the v0.3 flat-base pivot correction merely change the persisted landmark as intended, or did it silently change raw detector membership / create uncontrolled economic-base fragmentation?

## Method

Run the current v0.3 detector once on SNPS 2023, then keep the exact same 1,387 emitted raw candidate windows. For audit only, project each flat-base candidate back to the legacy v0.2 persisted-pivot convention (full-window maximum high) and recluster structural identities / lineages.

This is not an old-detector rerun and not a performance comparison. Candidate membership is identical by construction; only the persisted flat-base pivot landmark differs.

## Result

- raw candidate windows: **1,387**, unchanged;
- flat-base raw windows: **975**;
- flat windows whose persisted pivot changes under v0.3: **615**;
- legacy identities: **104** total / **60** flat;
- v0.3 identities: **111** total / **67** flat;
- identity delta: **+7**, entirely flat-base;
- legacy lineages: **39** total / **26** flat;
- v0.3 lineages: **38** total / **25** flat;
- lineage delta: **-1**, entirely flat-base.

The assignment transition is not trivial:

- 23 legacy flat identities split across multiple v0.3 identities;
- 18 v0.3 flat identities combine candidate windows that belonged to multiple legacy identities;
- maximum identity split fan-out: 7;
- maximum identity merge fan-in: 5;
- 8 legacy flat lineages split across multiple v0.3 lineages;
- 10 v0.3 flat lineages combine windows from multiple legacy lineages;
- maximum lineage split fan-out: 5;
- maximum lineage merge fan-in: 4.

The authoritative SNPS example remains unchanged at the source-facing level: emitted window `2023-04-04 -> 2023-05-17`, pivot `2023-04-04 @ 392.79000854`, mapped to `base_f4e321a93cf8dce2` / `lineage_dead150a96867922`, and remains a full pivot-validated MATCH against the IBD label.

## Decision

**Do not revert v0.3.** The raw detector population is unchanged and the authoritative SNPS morphology improves/retains source fidelity. The identity increase is an expected consequence of using the actual structural left-side pivot date rather than a later full-window maximum.

However, **do not declare the identity/lineage layer frozen yet.** Aggregate lineage count staying essentially flat (39 -> 38) is reassuring, but the split/merge churn is material. A count-only comparison is insufficient evidence that every economic base is grouped correctly.

Therefore:

1. v0.3 flat-pivot semantics remain active;
2. `base_id` stability is explicitly conditional on the pattern-engine landmark semantics/version — IDs are not promised stable across a semantic detector revision;
3. no BaseIdentity/Lineage algorithm change is made from this single-symbol audit;
4. additional independently labelled DEVELOPMENT examples must be used to judge whether lineage grouping is morphologically defensible across symbols/pattern families;
5. lineage logic may only be revised for morphology/source reasons, never to reduce counts or improve returns;
6. NFLX VALIDATION remains locked until DEVELOPMENT semantics are frozen.

## Reproducibility

Audit runner: `scripts/audit_p8_v03_identity.py`

CI artifact: `p8-v03-identity-audit.json`

Detector: `p8-v0.3-development-flat-pivot-correction`

Identity layer: `p8-base-id-v0.1`

Lineage layer: `p8-base-lineage-v0.2`

No return, CAGR, profit factor, or post-event outcome data was inspected.
