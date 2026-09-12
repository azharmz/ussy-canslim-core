from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Iterable

from .pattern_identity import BaseIdentity
from .pattern_lineage import BaseLineage


LABELLED_EVAL_VERSION = "p8-labelled-eval-v0.1"


@dataclass(frozen=True)
class MorphologyLabel:
    example_id: str
    symbol: str
    pattern: str
    label: str
    window_start: str
    window_end: str
    asof_date: str
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


def evaluate_positive_label(
    label: MorphologyLabel,
    lineages: Iterable[BaseLineage],
    identities: Iterable[BaseIdentity],
    *,
    boundary_tolerance_days: int = 10,
) -> LabelAgreement:
    """Compare an authoritative positive morphology label with frozen detector output.

    This evaluator is morphology-only. It does not inspect post-breakout returns.
    The first version requires the same named pattern plus start/end boundaries
    within a preregistered 10-calendar-day tolerance.
    """

    if label.split != "DEVELOPMENT":
        raise ValueError("labelled evaluator is locked to DEVELOPMENT examples")
    if label.label != "POSITIVE":
        raise ValueError("v0.1 evaluates positive authoritative labels only")

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
            rationale=["frozen detector emitted no lineage with the authoritative pattern label"],
        )

    ranked: list[tuple[int, int, BaseLineage, BaseIdentity]] = []
    for lineage in same_pattern:
        identity = _representative(lineage, bases)
        start = str(identity.representative.get("base_start_date", ""))[:10]
        end = str(identity.representative.get("base_end_or_breakout_ready_date", ""))[:10]
        if not start or not end:
            continue
        ranked.append((_date_distance(start, label.window_start), _date_distance(end, label.window_end), lineage, identity))

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
            rationale=["same-pattern lineage exists but representative structural boundaries are missing"],
        )

    start_error, end_error, lineage, identity = min(
        ranked,
        key=lambda item: (max(item[0], item[1]), item[0] + item[1], -item[2].confidence, item[2].lineage_id),
    )
    if start_error <= boundary_tolerance_days and end_error <= boundary_tolerance_days:
        state = "MATCH"
        rationale = [
            "named pattern agrees with authoritative label",
            f"base start is within {boundary_tolerance_days} calendar days of source anchor",
            f"base end/recognition is within {boundary_tolerance_days} calendar days of source anchor",
        ]
    else:
        state = "BOUNDARY_DISAGREEMENT"
        rationale = [
            "named pattern agrees but structural boundary alignment exceeds preregistered tolerance",
            f"start error={start_error} days; end error={end_error} days",
        ]

    return LabelAgreement(
        example_id=label.example_id,
        expected_pattern=label.pattern,
        split=label.split,
        agreement_state=state,
        matched_lineage_id=lineage.lineage_id,
        matched_base_id=identity.base_id,
        start_error_days=start_error,
        end_error_days=end_error,
        rationale=rationale,
    )
