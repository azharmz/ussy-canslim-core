# #35 Corpus Sampling v1

Date: 2026-09-13
Status: PREREGISTERED

After historical #33 -> #34 observations are generated, order records deterministically by SHA-256 of:

`corpus-v1|security_id|asof_date|candidate_id`

Selection uses only contemporaneous fields. Future-return or later winner/loser information is excluded.

Across adjacent as-of dates, deduplicate the same lineage by retaining the earliest selected observation unless a later observation represents a different preregistered chronology state.