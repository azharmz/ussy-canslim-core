from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Iterable

from .pattern_identity import BaseIdentity
from .pattern_lineage import BaseLineage


LABELLED_EVAL_VERSION = "p8-labelled-eval-v0.3"


@dataclass(frozen=True)
class MorphologyLabel:
    example_id: str
    symbol: str
    pattern: str
    label: str
    window_start: str
    window_end: str
    asof_date: str
    expected_pivot_source_date: str | None
    expected_pivot_level: float | None
    provenance: str
    source_name: str
    source_reference: str
    rationale: str
    split: str


@dataclass
class LabelAgreement:
    example_id: str
    expected_pattern: str
    split: str
    agreement_state: str
    matched_lineage_id: str | None
    matched_base_id: str | None
    start_error_days: int | None
    end_error_days: int | None
    pivot_date_error_days: int | None
    pivot_price_error_pct: float | None
    rationale: list[str]
    evaluator_version: str = LABELLED_EVAL_VERSION

    def to_dict(self) -> dict:
        return asdict(self)


def _date_distance(left: str, right: str) -> int:
    return abs((date.fromisoformat(left[:10]) - date.fromisoformat(right[:10])).days)


def _pivot_errors(label: MorphologyLabel, identity: BaseIdentity) -> tuple[int | None, float | None]:
    if not label.expected_pivot_source_date or label.expected_pivot_level is None:
        return None, None
    raw_date = identity.representative.get("pivot_source_date")
    raw_level = identity.representative.get("pivot_level")
    if not raw_date or raw_level is None:
        return None, None
    try:
        actual_level = float(raw_level)
    except (TypeError, ValueError):
        return None, None
    if label.expected_pivot_level <= 0:
        raise ValueError("expected pivot level must be positive")
    return (
        _date_distance(str(raw_date)[:10], label.expected_pivot_source_date),
        abs(actual_level / label.expected_pivot_level - 1.0),
    )


def _lineage_members(lineage: BaseLineage, bases: dict[str, BaseIdentity]) -> list[BaseIdentity]:
    members: list[BaseIdentity] = []
    for base_id in lineage.member_base_ids:
        try:
            members.append(bases[base_id])
        except KeyError as exc:
            raise ValueError(f"missing lineage member base: {base_id}") from exc
    return members


def evaluate_positive_label(
    label: MorphologyLabel,
    lineages: Iterable[BaseLineage],
    identities: Iterable[BaseIdentity],
    *,
    boundary_tolerance_days: int = 10,
    pivot_date_tolerance_days: int = 3,
    pivot_price_tolerance_pct: float = 0.01,
) -> LabelAgreement:
    """Compare an authoritative positive morphology label with frozen detector output.

    A lineage is a structural family, not a single immutable window. Authoritative
    comparison therefore evaluates every identity belonging to each same-pattern
    lineage and selects the member with best joint structural fidelity. This does
    not alter detector output and never inspects post-pattern returns.
    """
    if label.split != "DEVELOPMENT":
        raise ValueError("labelled evaluator is locked to DEVELOPMENT examples")
    if label.label != "POSITIVE":
        raise ValueError("v0.3 evaluates positive authoritative labels only")

    bases = {item.base_id: item for item in identities}
    same_pattern = [item for item in lineages if item.pattern_type == label.pattern]
    if not same_pattern:
        return LabelAgreement(
            label.example_id, label.pattern, label.split, "MISS_PATTERN", None, None,
            None, None, None, None,
            ["frozen detector emitted no lineage with the authoritative pattern label"],
        )

    # rank = boundary pass first, then landmark pass, then joint error. This avoids
    # choosing a perfect pivot attached to a structurally wrong base window.
    ranked = []
    pivot_required = bool(label.expected_pivot_source_date and label.expected_pivot_level is not None)
    for lineage in same_pattern:
        for identity in _lineage_members(lineage, bases):
            start = str(identity.representative.get("base_start_date", ""))[:10]
            end = str(identity.representative.get("base_end_or_breakout_ready_date", ""))[:10]
            if not start or not end:
                continue
            start_error = _date_distance(start, label.window_start)
            end_error = _date_distance(end, label.window_end)
            pivot_date_error, pivot_price_error = _pivot_errors(label, identity)
            boundary_ok = start_error <= boundary_tolerance_days and end_error <= boundary_tolerance_days
            pivot_evaluable = pivot_date_error is not None and pivot_price_error is not None
            pivot_ok = (
                not pivot_required
                or (pivot_evaluable and pivot_date_error <= pivot_date_tolerance_days
                    and pivot_price_error <= pivot_price_tolerance_pct)
            )
            ranked.append((
                0 if boundary_ok else 1,
                0 if pivot_ok else 1,
                max(start_error, end_error),
                start_error + end_error,
                pivot_date_error if pivot_date_error is not None else 10**9,
                pivot_price_error if pivot_price_error is not None else float("inf"),
                -identity.confidence,
                lineage.lineage_id,
                identity.base_id,
                lineage,
                identity,
                start_error,
                end_error,
                pivot_date_error,
                pivot_price_error,
            ))

    if not ranked:
        return LabelAgreement(
            label.example_id, label.pattern, label.split, "NOT_EVALUABLE", None, None,
            None, None, None, None,
            ["same-pattern lineage exists but no member has structural boundaries"],
        )

    chosen = min(ranked, key=lambda x: x[:9])
    lineage, identity = chosen[9], chosen[10]
    start_error, end_error = chosen[11], chosen[12]
    pivot_date_error, pivot_price_error = chosen[13], chosen[14]
    boundary_ok = start_error <= boundary_tolerance_days and end_error <= boundary_tolerance_days
    pivot_evaluable = pivot_date_error is not None and pivot_price_error is not None
    pivot_ok = (
        not pivot_required
        or (pivot_evaluable and pivot_date_error <= pivot_date_tolerance_days
            and pivot_price_error <= pivot_price_tolerance_pct)
    )

    if not boundary_ok:
        state = "BOUNDARY_DISAGREEMENT"
        rationale = [
            "named pattern agrees but no member of the structural lineage aligns within the preregistered boundary tolerance",
            f"best member start error={start_error} days; end error={end_error} days",
        ]
    elif pivot_required and not pivot_evaluable:
        state = "NOT_EVALUABLE"
        rationale = ["boundaries agree but authoritative pivot comparison lacks detector pivot evidence"]
    elif not pivot_ok:
        state = "LANDMARK_DISAGREEMENT"
        rationale = [
            "named pattern and structural boundaries agree but the pattern-specific pivot does not",
            f"pivot date error={pivot_date_error} days; pivot price error={pivot_price_error:.6f}",
        ]
    else:
        state = "MATCH"
        rationale = [
            "named pattern agrees with authoritative label",
            "matched identity is a member of the detector's structural lineage rather than an evaluator-created base",
            f"base start is within {boundary_tolerance_days} calendar days of source anchor",
            f"base end/recognition is within {boundary_tolerance_days} calendar days of source anchor",
        ]
        if pivot_required:
            rationale.extend([
                f"pivot date is within {pivot_date_tolerance_days} calendar days of source anchor",
                f"pivot price is within {pivot_price_tolerance_pct:.2%} of source anchor",
            ])

    return LabelAgreement(
        example_id=label.example_id,
        expected_pattern=label.pattern,
        split=label.split,
        agreement_state=state,
        matched_lineage_id=lineage.lineage_id,
        matched_base_id=identity.base_id,
        start_error_days=start_error,
        end_error_days=end_error,
        pivot_date_error_days=pivot_date_error,
        pivot_price_error_pct=round(pivot_price_error, 8) if pivot_price_error is not None else None,
        rationale=rationale,
    )
