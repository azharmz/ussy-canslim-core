from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
from typing import Iterable

from .pattern_engine import PatternCandidate


BASE_IDENTITY_VERSION = "p8-base-id-v0.1"


@dataclass
class BaseIdentity:
    base_id: str
    security_id: str
    pattern_type: str
    structural_signature: list[str]
    first_recognized_date: str
    last_supported_date: str
    member_window_count: int
    pattern_evidence_state: str
    confidence: float
    representative: dict
    recognition_dates: list[str]
    pattern_engine_version: str
    base_identity_version: str = BASE_IDENTITY_VERSION

    def to_dict(self) -> dict:
        return asdict(self)


def _landmark_date(candidate: PatternCandidate, name: str) -> str | None:
    value = candidate.landmarks.get(name)
    if not isinstance(value, dict):
        return None
    date = value.get("date")
    return str(date) if date else None


def structural_signature(candidate: PatternCandidate) -> tuple[str, ...]:
    """Return the pattern-specific landmark identity for one rolling window.

    This intentionally ignores rolling start/end boundaries. Two windows that
    point to the same structural landmarks are observations of one base, not
    separate bases.
    """

    names_by_pattern = {
        "DOUBLE_BOTTOM": ("first_bottom", "middle_peak", "second_bottom"),
        "FLAT_BASE": ("flat_left_high", "base_low"),
        "CUP_WITH_HANDLE": ("left_peak", "cup_low", "right_side_high", "handle_high", "handle_low"),
        "CUP_WITHOUT_HANDLE": ("left_peak", "cup_low", "right_side_high"),
    }
    names = names_by_pattern.get(candidate.pattern_type, ())
    values = [f"{name}:{_landmark_date(candidate, name)}" for name in names if _landmark_date(candidate, name)]
    if values:
        return tuple(values)
    return (
        f"pivot:{candidate.pivot_source_date}",
        f"start:{candidate.base_start_date}",
        f"end:{candidate.base_end_or_breakout_ready_date}",
    )


def _stable_base_id(security_id: str, pattern_type: str, signature: tuple[str, ...]) -> str:
    payload = "|".join((security_id, pattern_type, *signature)).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()[:16]
    return f"base_{digest}"


def _representative(candidates: list[PatternCandidate]) -> PatternCandidate:
    # Highest confidence first. For ties, prefer the longest observed support
    # window, then the earliest start date for deterministic stability.
    return sorted(
        candidates,
        key=lambda c: (-c.confidence, -c.base_duration_sessions, c.base_start_date, c.base_end_or_breakout_ready_date),
    )[0]


def cluster_base_identities(
    candidates: Iterable[PatternCandidate], *, security_id: str
) -> list[BaseIdentity]:
    if not security_id:
        raise ValueError("security_id is required for stable base identity")

    grouped: dict[tuple[str, tuple[str, ...]], list[PatternCandidate]] = {}
    for candidate in candidates:
        signature = structural_signature(candidate)
        grouped.setdefault((candidate.pattern_type, signature), []).append(candidate)

    identities: list[BaseIdentity] = []
    for (pattern_type, signature), members in grouped.items():
        representative = _representative(members)
        recognition_dates = sorted({member.base_end_or_breakout_ready_date for member in members})
        states = {member.pattern_evidence_state for member in members}
        evidence_state = "AMBIGUOUS" if "AMBIGUOUS" in states else "PASS"
        identities.append(
            BaseIdentity(
                base_id=_stable_base_id(security_id, pattern_type, signature),
                security_id=security_id,
                pattern_type=pattern_type,
                structural_signature=list(signature),
                first_recognized_date=recognition_dates[0],
                last_supported_date=recognition_dates[-1],
                member_window_count=len(members),
                pattern_evidence_state=evidence_state,
                confidence=representative.confidence,
                representative=representative.to_dict(),
                recognition_dates=recognition_dates,
                pattern_engine_version=representative.pattern_engine_version,
            )
        )

    return sorted(
        identities,
        key=lambda item: (item.first_recognized_date, item.pattern_type, item.base_id),
    )
