from __future__ import annotations

from hashlib import sha256
from typing import Iterable, Mapping

STATUS_QUOTA = {"RECOGNIZED": 20, "AMBIGUOUS": 20, "REJECTED": 20}


def selection_key(row: Mapping[str, object]) -> str:
    material = f"corpus-v1|{row['security_id']}|{row['asof_date']}|{row['candidate_id']}"
    return sha256(material.encode("utf-8")).hexdigest()


def chronology_state(row: Mapping[str, object]) -> str:
    if bool(row.get("prior_cross_after_structure")):
        return "ALREADY_CROSSED"
    if bool(row.get("pivot_crossed_intraday")):
        return "FIRST_CROSS"
    return "NO_CROSS"


def volume_state(row: Mapping[str, object]) -> str:
    value = row.get("volume_ratio")
    if value is None:
        return "NOT_EVALUABLE"
    return "GE_1_40" if float(value) >= 1.40 else "LT_1_40"


def strata(row: Mapping[str, object]) -> tuple[str, ...]:
    return (
        str(row.get("pattern", "UNKNOWN")),
        str(row.get("pattern_status", "UNKNOWN")),
        chronology_state(row),
        volume_state(row),
        f"C_{row.get('C_screen_state', 'UNKNOWN')}",
        f"A_{row.get('A_screen_state', 'UNKNOWN')}",
        f"L_{row.get('L_individual_leadership_state', 'UNKNOWN')}",
        f"M_{row.get('M_entry_state', 'UNKNOWN')}",
        "GAP" if bool(row.get("gap_through_pivot")) else "NO_GAP",
    )


def select_corpus(rows: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    buckets: dict[str, list[Mapping[str, object]]] = {status: [] for status in STATUS_QUOTA}
    for row in rows:
        status = str(row.get("pattern_status", ""))
        if status in buckets:
            buckets[status].append(row)

    selected: list[dict[str, object]] = []
    for status, quota in STATUS_QUOTA.items():
        ordered = sorted(buckets[status], key=selection_key)
        seen_lineage_state: set[tuple[str, str]] = set()
        chosen: list[Mapping[str, object]] = []
        for row in ordered:
            identity = (str(row.get("lineage_id", "")), chronology_state(row))
            if identity in seen_lineage_state:
                continue
            seen_lineage_state.add(identity)
            chosen.append(row)
            if len(chosen) >= quota:
                break
        for row in chosen:
            selected.append({
                "validation_case_id": selection_key(row)[:16],
                "selection_hash": selection_key(row),
                "security_id": row.get("security_id"),
                "ticker": row.get("ticker"),
                "asof_date": row.get("asof_date"),
                "candidate_id": row.get("candidate_id"),
                "base_id": row.get("base_id"),
                "lineage_id": row.get("lineage_id"),
                "pattern": row.get("pattern"),
                "pattern_status": row.get("pattern_status"),
                "strata": list(strata(row)),
            })
    return selected
