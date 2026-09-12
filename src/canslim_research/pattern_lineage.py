from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
import hashlib
from typing import Iterable

from .pattern_identity import BaseIdentity


BASE_LINEAGE_VERSION = "p8-base-lineage-v0.1"


@dataclass
class BaseLineage:
    lineage_id: str
    security_id: str
    pattern_type: str
    anchor_signature: list[str]
    member_base_ids: list[str]
    first_recognized_date: str
    last_supported_date: str
    member_identity_count: int
    pattern_evidence_state: str
    confidence: float
    representative_base_id: str
    lineage_version: str = BASE_LINEAGE_VERSION

    def to_dict(self) -> dict:
        return asdict(self)


def _landmarks(identity: BaseIdentity) -> dict:
    value = identity.representative.get("landmarks", {})
    return value if isinstance(value, dict) else {}


def _landmark_date(identity: BaseIdentity, name: str) -> str | None:
    value = _landmarks(identity).get(name)
    if not isinstance(value, dict):
        return None
    item = value.get("date")
    return str(item) if item else None


def _landmark_price(identity: BaseIdentity, name: str) -> float | None:
    value = _landmarks(identity).get(name)
    if not isinstance(value, dict):
        return None
    item = value.get("price")
    try:
        return float(item)
    except (TypeError, ValueError):
        return None


def _anchor_names(pattern_type: str) -> tuple[str, ...]:
    return {
        "FLAT_BASE": ("flat_left_high",),
        "DOUBLE_BOTTOM": ("first_bottom", "middle_peak"),
        "CUP_WITHOUT_HANDLE": ("left_peak", "cup_low"),
        "CUP_WITH_HANDLE": ("left_peak", "cup_low"),
    }.get(pattern_type, ())


def anchor_signature(identity: BaseIdentity) -> tuple[str, ...]:
    names = _anchor_names(identity.pattern_type)
    values = [f"{name}:{_landmark_date(identity, name)}" for name in names if _landmark_date(identity, name)]
    return tuple(values) if values else tuple(identity.structural_signature)


def _stable_lineage_id(security_id: str, pattern_type: str, anchor: tuple[str, ...]) -> str:
    payload = "|".join((security_id, pattern_type, *anchor)).encode("utf-8")
    return "lineage_" + hashlib.sha256(payload).hexdigest()[:16]


def _days_between(left: str, right: str) -> int:
    return abs((date.fromisoformat(left[:10]) - date.fromisoformat(right[:10])).days)


def _prices_close(left: float | None, right: float | None, *, tolerance: float = 0.01) -> bool:
    if left is None or right is None or left <= 0 or right <= 0:
        return False
    return abs(left / right - 1.0) <= tolerance


def _same_anchor(identity: BaseIdentity, other: BaseIdentity) -> bool:
    if identity.security_id != other.security_id or identity.pattern_type != other.pattern_type:
        return False

    names = _anchor_names(identity.pattern_type)
    if not names:
        return anchor_signature(identity) == anchor_signature(other)

    # Most patterns require exact root landmarks. Flat bases are allowed a tiny
    # pivot-date drift when the pivot prices are effectively the same; this
    # captures one evolving base whose rolling left-high advances by 1-2 bars.
    if identity.pattern_type == "FLAT_BASE":
        left_date = _landmark_date(identity, "flat_left_high")
        right_date = _landmark_date(other, "flat_left_high")
        if not left_date or not right_date:
            return False
        if left_date == right_date:
            return True
        if _days_between(left_date, right_date) > 4:
            return False
        return _prices_close(
            _landmark_price(identity, "flat_left_high"),
            _landmark_price(other, "flat_left_high"),
            tolerance=0.01,
        )

    return all(_landmark_date(identity, name) == _landmark_date(other, name) for name in names)


def _component_groups(identities: list[BaseIdentity]) -> list[list[BaseIdentity]]:
    remaining = list(identities)
    groups: list[list[BaseIdentity]] = []
    while remaining:
        seed = remaining.pop(0)
        group = [seed]
        changed = True
        while changed:
            changed = False
            for candidate in list(remaining):
                if any(_same_anchor(candidate, member) for member in group):
                    group.append(candidate)
                    remaining.remove(candidate)
                    changed = True
        groups.append(group)
    return groups


def _representative(members: list[BaseIdentity]) -> BaseIdentity:
    return sorted(
        members,
        key=lambda item: (-item.confidence, -item.member_window_count, item.first_recognized_date, item.base_id),
    )[0]


def cluster_base_lineages(identities: Iterable[BaseIdentity]) -> list[BaseLineage]:
    items = list(identities)
    if not items:
        return []

    lineages: list[BaseLineage] = []
    for members in _component_groups(items):
        representative = _representative(members)
        anchor = anchor_signature(representative)
        states = {member.pattern_evidence_state for member in members}
        lineages.append(
            BaseLineage(
                lineage_id=_stable_lineage_id(representative.security_id, representative.pattern_type, anchor),
                security_id=representative.security_id,
                pattern_type=representative.pattern_type,
                anchor_signature=list(anchor),
                member_base_ids=sorted(member.base_id for member in members),
                first_recognized_date=min(member.first_recognized_date for member in members),
                last_supported_date=max(member.last_supported_date for member in members),
                member_identity_count=len(members),
                pattern_evidence_state="AMBIGUOUS" if "AMBIGUOUS" in states else "PASS",
                confidence=representative.confidence,
                representative_base_id=representative.base_id,
            )
        )

    return sorted(lineages, key=lambda item: (item.first_recognized_date, item.pattern_type, item.lineage_id))
