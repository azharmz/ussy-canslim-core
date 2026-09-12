from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Iterable

from .pattern_identity import BaseIdentity
from .pattern_lineage import BaseLineage


LABELLED_EVAL_VERSION = "p8-labelled-eval-v0.2"


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


def _representative(lineage: BaseLineage, bases: dict[str, BaseIdentity]) -> BaseIdentity:
    try:
        return bases[lineage.representative_base_id]
    except KeyError as exc:
        raise ValueError(f"missing representative base: {lineage.representative_base_id}") from exc


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

    Matching requires the same named pattern, aligned structural boundaries and,
    when the source supplies it, an aligned pattern-specific pivot landmark.
    The evaluator is morphology-only and never inspects post-pattern returns.
    """

    if label.split != "DEVELOPMENT":
        raise ValueError("labelled evaluator is locked to DEVELOPMENT examples")
    if label.label != "POSITIVE":
        raise ValueError("v0.2 evaluates positive authoritative labels only")

    bases = {item.base_id: item for item in identities}
    same_pattern = [item for item in lineages if item.pattern_type == label.pattern]
    if not same_pattern:
        return LabelAgreement(
            example_id=label.example_id,
            expected_pattern=label.pattern,
            split=label.split,
            agreement_state="MISS_PATTERN",
            matched_lineage_id=None,
            matched_base_id=None,
            start_error_days=None,
            end_error_days=None,
            pivot_date_error_days=None,
            pivot_price_error_pct=None,
            rationale=["frozen detector emitted no lineage with the authoritative pattern label"],
        )

    ranked: list[tuple[int, float, int, int, BaseLineage, BaseIdentity, int | None, float | None]] = []
    for lineage in same_pattern:
        identity = _representative(lineage, bases)
        start = str(identity.representative.get("base_start_date", ""))[:10]
        end = str(identity.representative.get("base_end_or_breakout_ready_date", ""))[:10]
        if not start or not end:
            continue
        start_error = _date_distance(start, label.window_start)
        end_error = _date_distance(end, label.window_end)
        pivot_date_error, pivot_price_error = _pivot_errors(label, identity)
        # When a source pivot exists, prefer landmark fidelity before a one-bar
        # boundary advantage. This prevents a breakout-day high from winning
        # merely because its terminal date exactly equals the source breakout.
        landmark_date_rank = pivot_date_error if pivot_date_error is not None else 0
        landmark_price_rank = pivot_price_error if pivot_price_error is not None else 0.0
        ranked.append(
            (
                landmark_date_rank,
                landmark_price_rank,
                max(start_error, end_error),
                start_error + end_error,
                lineage,
                identity,
                pivot_date_error,
                pivot_price_error,
            )
        )

    if not ranked:
        return LabelAgreement(
            example_id=label.example_id,
            expected_pattern=label.pattern,
            split=label.split,
            agreement_state="NOT_EVALUABLE",
            matched_lineage_id=None,
            matched_base_id=None,
            start_error_days=None,
            end_error_days=None,
            pivot_date_error_days=None,
            pivot_price_error_pct=None,
            rationale=["same-pattern lineage exists but representative structural boundaries are missing"],
        )

    (
        _,
        _,
        _,
        _,
        lineage,
        identity,
        pivot_date_error,
        pivot_price_error,
    ) = min(
        ranked,
        key=lambda item: (item[0], item[1], item[2], item[3], -item[4].confidence, item[4].lineage_id),
    )
    start = str(identity.representative.get("base_start_date", ""))[:10]
    end = str(identity.representative.get("base_end_or_breakout_ready_date", ""))[:10]
    start_error = _date_distance(start, label.window_start)
    end_error = _date_distance(end, label.window_end)

    boundary_ok = start_error <= boundary_tolerance_days and end_error <= boundary_tolerance_days
    pivot_required = bool(label.expected_pivot_source_date and label.expected_pivot_level is not None)
    pivot_evaluable = pivot_date_error is not None and pivot_price_error is not None
    pivot_ok = (
        not pivot_required
        or (
            pivot_evaluable
            and pivot_date_error <= pivot_date_tolerance_days
            and pivot_price_error <= pivot_price_tolerance_pct
        )
    )

    if not boundary_ok:
        state = "BOUNDARY_DISAGREEMENT"
        rationale = [
            "named pattern agrees but structural boundary alignment exceeds preregistered tolerance",
            f"start error={start_error} days; end error={end_error} days",
        ]
    elif pivot_required and not pivot_evaluable:
        state = "NOT_EVALUABLE"
        rationale = [
            "named pattern and boundaries are evaluable but authoritative pivot comparison is missing detector pivot evidence"
        ]
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
            f"base start is within {boundary_tolerance_days} calendar days of source anchor",
            f"base end/recognition is within {boundary_tolerance_days} calendar days of source anchor",
        ]
        if pivot_required:
            rationale.extend(
                [
                    f"pivot date is within {pivot_date_tolerance_days} calendar days of source anchor",
                    f"pivot price is within {pivot_price_tolerance_pct:.2%} of source anchor",
                ]
            )

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
