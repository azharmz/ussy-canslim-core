from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Iterable

from .pattern_engine import PatternCandidate
from .pattern_identity import BaseIdentity, structural_signature
from .pattern_lineage import BaseLineage

LABELLED_EVAL_VERSION = "p8-labelled-eval-v0.6"


@dataclass(frozen=True)
class MorphologyLabel:
    example_id: str
    symbol: str
    pattern: str
    label: str
    window_start: str
    window_end: str | None
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
    boundary_validation_state: str
    pivot_validation_state: str
    matched_raw_candidate: dict | None
    rationale: list[str]
    evaluator_version: str = LABELLED_EVAL_VERSION

    def to_dict(self) -> dict:
        return asdict(self)


def _date_distance(left: str, right: str) -> int:
    return abs((date.fromisoformat(left[:10]) - date.fromisoformat(right[:10])).days)


def _pivot_errors(label: MorphologyLabel, candidate: PatternCandidate) -> tuple[int | None, float | None]:
    if not label.expected_pivot_source_date or label.expected_pivot_level is None:
        return None, None
    if label.expected_pivot_level <= 0:
        raise ValueError("expected pivot level must be positive")
    return (
        _date_distance(candidate.pivot_source_date, label.expected_pivot_source_date),
        abs(float(candidate.pivot_level) / label.expected_pivot_level - 1.0),
    )


def _map_candidate(candidate: PatternCandidate, identities: list[BaseIdentity], lineages: list[BaseLineage]) -> tuple[str | None, str | None]:
    signature = list(structural_signature(candidate))
    identity = next(
        (item for item in identities if item.pattern_type == candidate.pattern_type and item.structural_signature == signature),
        None,
    )
    if identity is None:
        return None, None
    lineage = next((item for item in lineages if identity.base_id in item.member_base_ids), None)
    return (lineage.lineage_id if lineage else None, identity.base_id)


def _no_match(label: MorphologyLabel, state: str, rationale: list[str]) -> LabelAgreement:
    boundary_state = "FULL_SOURCE_ANCHORS" if label.window_end else "START_ONLY_SOURCE_ANCHOR"
    return LabelAgreement(
        label.example_id, label.pattern, label.split, state,
        None, None, None, None, None, None,
        boundary_state, "NOT_EVALUABLE", None, rationale,
    )


def evaluate_positive_label(
    label: MorphologyLabel,
    lineages: Iterable[BaseLineage],
    identities: Iterable[BaseIdentity],
    candidates: Iterable[PatternCandidate],
    *,
    boundary_tolerance_days: int = 10,
    pivot_date_tolerance_days: int = 3,
    pivot_price_tolerance_pct: float = 0.01,
) -> LabelAgreement:
    """Validate a frozen positive label against windows actually emitted by the detector.

    Identity/lineage objects deliberately summarize many rolling windows and can
    discard their individual start/end boundaries. P8 therefore scores the raw
    emitted windows, then maps the selected window back to its stable base_id and
    lineage for audit. No synthetic window is created and no outcome data is used.

    Authoritative sources do not always publish both base boundaries and a pivot.
    Missing source dimensions are represented explicitly rather than invented.
    An example with a source-anchored start but no exact end can therefore test
    pattern/start/pivot fidelity while reporting START_ONLY_SOURCE_ANCHOR. Such a
    MATCH is not equivalent to a full-boundary MATCH.
    """
    if label.split != "DEVELOPMENT":
        raise ValueError("labelled evaluator is locked to DEVELOPMENT examples")
    if label.label != "POSITIVE":
        raise ValueError("v0.6 evaluates positive authoritative labels only")
    if not label.window_start:
        raise ValueError("v0.6 requires at least a source-anchored window_start")

    identities_list = list(identities)
    lineages_list = list(lineages)
    same_pattern = [item for item in candidates if item.pattern_type == label.pattern]
    if not same_pattern:
        return _no_match(label, "MISS_PATTERN", ["frozen detector emitted no raw window with the authoritative pattern label"])

    end_required = bool(label.window_end)
    boundary_validation_state = "FULL_SOURCE_ANCHORS" if end_required else "START_ONLY_SOURCE_ANCHOR"
    pivot_required = bool(label.expected_pivot_source_date and label.expected_pivot_level is not None)
    ranked = []
    for candidate in same_pattern:
        start_error = _date_distance(candidate.base_start_date, label.window_start)
        end_error = _date_distance(candidate.base_end_or_breakout_ready_date, label.window_end) if end_required else None
        pivot_date_error, pivot_price_error = _pivot_errors(label, candidate)
        start_ok = start_error <= boundary_tolerance_days
        end_ok = (end_error <= boundary_tolerance_days) if end_error is not None else True
        boundary_ok = start_ok and end_ok
        pivot_evaluable = pivot_date_error is not None and pivot_price_error is not None
        pivot_ok = not pivot_required or (pivot_evaluable and pivot_date_error <= pivot_date_tolerance_days and pivot_price_error <= pivot_price_tolerance_pct)
        boundary_max_error = max(start_error, end_error or 0)
        boundary_total_error = start_error + (end_error or 0)
        ranked.append((
            0 if boundary_ok else 1,
            0 if pivot_ok else 1,
            boundary_max_error,
            boundary_total_error,
            pivot_date_error if pivot_date_error is not None else 10**9,
            pivot_price_error if pivot_price_error is not None else float("inf"),
            -candidate.confidence,
            candidate.base_start_date,
            candidate.base_end_or_breakout_ready_date,
            candidate,
            start_error,
            end_error,
            pivot_date_error,
            pivot_price_error,
        ))

    chosen = min(ranked, key=lambda item: item[:9])
    candidate = chosen[9]
    start_error, end_error = chosen[10], chosen[11]
    pivot_date_error, pivot_price_error = chosen[12], chosen[13]
    start_ok = start_error <= boundary_tolerance_days
    end_ok = (end_error <= boundary_tolerance_days) if end_error is not None else True
    boundary_ok = start_ok and end_ok
    pivot_evaluable = pivot_date_error is not None and pivot_price_error is not None
    pivot_ok = not pivot_required or (pivot_evaluable and pivot_date_error <= pivot_date_tolerance_days and pivot_price_error <= pivot_price_tolerance_pct)
    lineage_id, base_id = _map_candidate(candidate, identities_list, lineages_list)
    pivot_validation_state = "VALIDATED" if pivot_required and pivot_evaluable else ("SOURCE_NOT_PROVIDED" if not pivot_required else "NOT_EVALUABLE")

    if not boundary_ok:
        state = "BOUNDARY_DISAGREEMENT"
        rationale = ["named pattern agrees but no emitted window aligns with all source-provided boundary anchors within the preregistered tolerance", f"best emitted window start error={start_error} days" + (f"; end error={end_error} days" if end_error is not None else "")]
    elif pivot_required and not pivot_evaluable:
        state = "NOT_EVALUABLE"
        rationale = ["source-provided boundary anchors agree but authoritative pivot comparison lacks detector pivot evidence"]
    elif not pivot_ok:
        state = "LANDMARK_DISAGREEMENT"
        rationale = ["named pattern and source-provided boundaries agree but the pattern-specific pivot does not", f"pivot date error={pivot_date_error} days; pivot price error={pivot_price_error:.6f}"]
    else:
        state = "MATCH"
        rationale = [
            "named pattern agrees with authoritative label",
            "the matched window was emitted by the frozen detector and maps to a stable structural identity",
            f"base start is within {boundary_tolerance_days} calendar days of source anchor",
        ]
        if end_required:
            rationale += [f"base end/recognition is within {boundary_tolerance_days} calendar days of source anchor"]
        else:
            rationale += ["source does not publish an exact base-end boundary; end fidelity is not scored"]
        if pivot_required:
            rationale += [f"pivot date is within {pivot_date_tolerance_days} calendar days of source anchor", f"pivot price is within {pivot_price_tolerance_pct:.2%} of source anchor"]
        else:
            rationale += ["source does not provide a detector-comparable structural pivot; pivot fidelity is not scored"]

    return LabelAgreement(
        label.example_id,
        label.pattern,
        label.split,
        state,
        lineage_id,
        base_id,
        start_error,
        end_error,
        pivot_date_error,
        round(pivot_price_error, 8) if pivot_price_error is not None else None,
        boundary_validation_state,
        pivot_validation_state,
        candidate.to_dict(),
        rationale,
    )
