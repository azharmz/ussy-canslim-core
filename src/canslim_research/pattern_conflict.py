from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
import hashlib
from itertools import combinations
from typing import Iterable

from .pattern_identity import BaseIdentity
from .pattern_lineage import BaseLineage


CONFLICT_LAYER_VERSION = "p8-conflict-v0.1"


@dataclass
class PatternConflict:
    conflict_id: str
    security_id: str
    left_lineage_id: str
    right_lineage_id: str
    left_pattern_type: str
    right_pattern_type: str
    relationship: str
    resolution_state: str
    rationale: list[str]
    conflict_layer_version: str = CONFLICT_LAYER_VERSION

    def to_dict(self) -> dict:
        return asdict(self)


def _identity_map(identities: Iterable[BaseIdentity]) -> dict[str, BaseIdentity]:
    return {item.base_id: item for item in identities}


def _representative(lineage: BaseLineage, identities: dict[str, BaseIdentity]) -> BaseIdentity:
    try:
        return identities[lineage.representative_base_id]
    except KeyError as exc:
        raise ValueError(f"missing representative base identity: {lineage.representative_base_id}") from exc


def _pivot(identity: BaseIdentity) -> tuple[str | None, float | None]:
    raw_date = identity.representative.get("pivot_source_date")
    raw_price = identity.representative.get("pivot_level")
    pivot_date = str(raw_date)[:10] if raw_date else None
    try:
        pivot_price = float(raw_price)
    except (TypeError, ValueError):
        pivot_price = None
    return pivot_date, pivot_price


def _days_between(left: str, right: str) -> int:
    return abs((date.fromisoformat(left[:10]) - date.fromisoformat(right[:10])).days)


def _intervals_overlap(left: BaseLineage, right: BaseLineage) -> bool:
    return max(left.first_recognized_date, right.first_recognized_date) <= min(
        left.last_supported_date, right.last_supported_date
    )


def _pivot_close(left: BaseIdentity, right: BaseIdentity) -> bool:
    left_date, left_price = _pivot(left)
    right_date, right_price = _pivot(right)
    if not left_date or not right_date or left_price is None or right_price is None:
        return False
    if _days_between(left_date, right_date) > 5:
        return False
    if left_price <= 0 or right_price <= 0:
        return False
    return abs(left_price / right_price - 1.0) <= 0.03


def _cup_root(identity: BaseIdentity) -> tuple[str | None, str | None]:
    landmarks = identity.representative.get("landmarks", {})
    if not isinstance(landmarks, dict):
        return None, None
    left_peak = landmarks.get("left_peak", {})
    cup_low = landmarks.get("cup_low", {})
    if not isinstance(left_peak, dict) or not isinstance(cup_low, dict):
        return None, None
    return (
        str(left_peak.get("date"))[:10] if left_peak.get("date") else None,
        str(cup_low.get("date"))[:10] if cup_low.get("date") else None,
    )


def _stable_conflict_id(left: BaseLineage, right: BaseLineage, relationship: str) -> str:
    lineage_ids = sorted((left.lineage_id, right.lineage_id))
    payload = "|".join((left.security_id, *lineage_ids, relationship)).encode("utf-8")
    return "conflict_" + hashlib.sha256(payload).hexdigest()[:16]


def _classify(
    left: BaseLineage,
    right: BaseLineage,
    left_identity: BaseIdentity,
    right_identity: BaseIdentity,
) -> tuple[str, str, list[str]] | None:
    pair = {left.pattern_type, right.pattern_type}

    if pair == {"CUP_WITH_HANDLE", "CUP_WITHOUT_HANDLE"}:
        if _cup_root(left_identity) == _cup_root(right_identity) and all(_cup_root(left_identity)):
            return (
                "CUP_FAMILY_HIERARCHY",
                "UNRESOLVED_EXPLICIT_HIERARCHY",
                [
                    "shared left_peak and cup_low identify one cup root",
                    "handle/no-handle variants remain separately observable; no silent winner is selected",
                ],
            )
        return None

    if _intervals_overlap(left, right) and _pivot_close(left_identity, right_identity):
        return (
            "OVERLAPPING_MORPHOLOGY",
            "UNRESOLVED",
            [
                "recognition-support intervals overlap",
                "pattern-specific pivots are temporally and numerically close",
                "both pattern labels are retained for later adjudication",
            ],
        )

    return None


def detect_pattern_conflicts(
    lineages: Iterable[BaseLineage], identities: Iterable[BaseIdentity]
) -> list[PatternConflict]:
    lineage_items = list(lineages)
    by_base_id = _identity_map(identities)
    conflicts: list[PatternConflict] = []

    for left, right in combinations(lineage_items, 2):
        if left.security_id != right.security_id or left.pattern_type == right.pattern_type:
            continue
        left_identity = _representative(left, by_base_id)
        right_identity = _representative(right, by_base_id)
        classified = _classify(left, right, left_identity, right_identity)
        if classified is None:
            continue
        relationship, resolution_state, rationale = classified
        first, second = sorted((left, right), key=lambda item: item.lineage_id)
        conflicts.append(
            PatternConflict(
                conflict_id=_stable_conflict_id(first, second, relationship),
                security_id=first.security_id,
                left_lineage_id=first.lineage_id,
                right_lineage_id=second.lineage_id,
                left_pattern_type=first.pattern_type,
                right_pattern_type=second.pattern_type,
                relationship=relationship,
                resolution_state=resolution_state,
                rationale=rationale,
            )
        )

    return sorted(conflicts, key=lambda item: item.conflict_id)
