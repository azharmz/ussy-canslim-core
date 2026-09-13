# #35 Historical Corpus Freeze

Date: 2026-09-13
Status: **FROZEN FOR V35-D**

Canonical run: `34763920536` — SUCCESS.

Head commit: `a160087f43bae93e8dc4e67804ec046bb4b579ca`.

Artifact: `v35-historical-pool-34763920536`.
Artifact digest: `sha256:d101325bdd43ed7a9ae3730c8ea871e51ccd8608f63e7a373cc6ce1766b691f7`.

Historical pool:
- 1,300 history objects available;
- deterministic 20-security compute frame;
- 20 preregistered quarter-end anchors from 2021Q1 through 2025Q4;
- 300-bar morphology window;
- 265,642 generated candidate observations;
- no future-performance fields used.

V35-A/B/C result:
- finding count: `0`;
- canonical workflow is self-validating and fails on any semantic finding.

Frozen audit manifest:
- 60 cases total;
- 20 RECOGNIZED;
- 20 AMBIGUOUS;
- 20 REJECTED;
- all four production core patterns represented;
- chronology coverage includes NO_CROSS, ALREADY_CROSSED, FIRST_CROSS;
- volume coverage includes NOT_EVALUABLE, <1.40x, >=1.40x;
- gap-through-pivot represented.

Manifest SHA-256:
`8fcbb6345d97354043e036e21aee852999fed4402343321f02f8e51225d11628`

Summary SHA-256:
`8a21948ef4c64355e7f256e7b675bb610aef06382c321b296434248887e52c48`

Validation findings file SHA-256:
`f8462cdad3c9b9fb34ca593266b8d3bf195307e07df40495a4aa0c34d565739f`

This freeze does not validate trading performance and does not reopen #33 or #34. V35-D may now open as a manual/independent chart-semantic audit against these frozen case IDs.