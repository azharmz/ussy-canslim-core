from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Iterable

from .pattern_engine import PatternCandidate
from .pattern_identity import BaseIdentity, structural_signature
from .pattern_lineage import BaseLineage

LABELLED_EVAL_VERSION = "p8-labelled-eval-v0.7"


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
    window_start_precision: str = "DAY"


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


def _start_error(candidate_date: str, label: MorphologyLabel) -> tuple[bool, int]:
    precision = label.window_start_precision.upper()
    if precision == "DAY":
        error = _date_distance(candidate_date, label.window_start)
        return error <= 10, error
    if precision == "MONTH":
        anchor = date.fromisoformat(label.window_start[:10])
        actual = date.fromisoformat(candidate_date[:10])
        same_month = actual.year == anchor.year and actual.month == anchor.month
        # Distance remains diagnostic only; MONTH acceptance is membership in the published month.
        return same_month, _date_distance(candidate_date, label.window_start)
    raise ValueError(f"unsupported window_start_precision: {label.window_start_precision}")


def _pivot_errors(label: MorphologyLabel, candidate: PatternCandidate) -> tuple[int | None, float | None]:
    date_error = _date_distance(candidate.pivot_source_date, label.expected_pivot_source_date) if label.expected_pivot_source_date else None
    price_error = None
    if label.expected_pivot_level is not None:
        if label.expected_pivot_level <= 0:
            raise ValueError("expected pivot level must be positive")
        price_error = abs(float(candidate.pivot_level) / label.expected_pivot_level - 1.0)
    return date_error, price_error


def _map_candidate(candidate: PatternCandidate, identities: list[BaseIdentity], lineages: list[BaseLineage]) -> tuple[str | None, str | None]:
    signature = list(structural_signature(candidate))
    identity = next((item for item in identities if item.pattern_type == candidate.pattern_type and item.structural_signature == signature), None)
    if identity is None:
        return None, None
    lineage = next((item for item in lineages if identity.base_id in item.member_base_ids), None)
    return (lineage.lineage_id if lineage else None, identity.base_id)


def _boundary_state(label: MorphologyLabel) -> str:
    suffix = f"_{label.window_start_precision.upper()}_START"
    return ("FULL_SOURCE_ANCHORS" if label.window_end else "START_ONLY_SOURCE_ANCHOR") + suffix


def _pivot_state(label: MorphologyLabel, date_error: int | None, price_error: float | None) -> str:
    has_date = label.expected_pivot_source_date is not None
    has_price = label.expected_pivot_level is not None
    if not has_date and not has_price:
        return "SOURCE_NOT_PROVIDED"
    if has_date and date_error is None or has_price and price_error is None:
        return "NOT_EVALUABLE"
    if has_date and has_price:
        return "DATE_AND_PRICE_VALIDATED"
    return "DATE_VALIDATED" if has_date else "PRICE_VALIDATED"


def _no_match(label: MorphologyLabel, state: str, rationale: list[str]) -> LabelAgreement:
    return LabelAgreement(label.example_id, label.pattern, label.split, state, None, None, None, None, None, None, _boundary_state(label), "NOT_EVALUABLE", None, rationale)


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
    """Validate source-published morphology dimensions against raw detector windows.

    Source dimensions are scored only at the precision actually published. DAY starts
    use the preregistered day tolerance; MONTH starts require the emitted start to fall
    inside that calendar month. Pivot date and pivot price are independent dimensions:
    a source may publish one without the other. Missing dimensions remain unscored.
    """
    if label.split != "DEVELOPMENT":
        raise ValueError("labelled evaluator is locked to DEVELOPMENT examples")
    if label.label != "POSITIVE":
        raise ValueError("v0.7 evaluates positive authoritative labels only")
    if not label.window_start:
        raise ValueError("v0.7 requires at least a source-anchored window_start")
    if label.window_start_precision.upper() not in {"DAY", "MONTH"}:
        raise ValueError("window_start_precision must be DAY or MONTH")

    identities_list, lineages_list = list(identities), list(lineages)
    same_pattern = [item for item in candidates if item.pattern_type == label.pattern]
    if not same_pattern:
        return _no_match(label, "MISS_PATTERN", ["frozen detector emitted no raw window with the authoritative pattern label"])

    end_required = bool(label.window_end)
    pivot_date_required = label.expected_pivot_source_date is not None
    pivot_price_required = label.expected_pivot_level is not None
    ranked = []
    for candidate in same_pattern:
        if label.window_start_precision.upper() == "DAY":
            start_error = _date_distance(candidate.base_start_date, label.window_start)
            start_ok = start_error <= boundary_tolerance_days
        else:
            start_ok, start_error = _start_error(candidate.base_start_date, label)
        end_error = _date_distance(candidate.base_end_or_breakout_ready_date, label.window_end) if end_required else None
        end_ok = end_error <= boundary_tolerance_days if end_error is not None else True
        pivot_date_error, pivot_price_error = _pivot_errors(label, candidate)
        pivot_date_ok = not pivot_date_required or (pivot_date_error is not None and pivot_date_error <= pivot_date_tolerance_days)
        pivot_price_ok = not pivot_price_required or (pivot_price_error is not None and pivot_price_error <= pivot_price_tolerance_pct)
        boundary_ok, pivot_ok = start_ok and end_ok, pivot_date_ok and pivot_price_ok
        ranked.append((0 if boundary_ok else 1, 0 if pivot_ok else 1, start_error + (end_error or 0), pivot_date_error if pivot_date_error is not None else 10**9, pivot_price_error if pivot_price_error is not None else float("inf"), -candidate.confidence, candidate.base_start_date, candidate.base_end_or_breakout_ready_date, candidate, start_error, end_error, pivot_date_error, pivot_price_error))

    chosen = min(ranked, key=lambda item: item[:8])
    candidate = chosen[8]
    start_error, end_error, pivot_date_error, pivot_price_error = chosen[9:13]
    if label.window_start_precision.upper() == "DAY":
        start_ok = start_error <= boundary_tolerance_days
    else:
        start_ok, _ = _start_error(candidate.base_start_date, label)
    end_ok = end_error <= boundary_tolerance_days if end_error is not None else True
    pivot_date_ok = not pivot_date_required or (pivot_date_error is not None and pivot_date_error <= pivot_date_tolerance_days)
    pivot_price_ok = not pivot_price_required or (pivot_price_error is not None and pivot_price_error <= pivot_price_tolerance_pct)
    boundary_ok, pivot_ok = start_ok and end_ok, pivot_date_ok and pivot_price_ok
    lineage_id, base_id = _map_candidate(candidate, identities_list, lineages_list)
    pivot_validation_state = _pivot_state(label, pivot_date_error, pivot_price_error)

    if not boundary_ok:
        state = "BOUNDARY_DISAGREEMENT"
        rationale = ["named pattern agrees but no emitted window aligns with all source-provided boundary anchors at their published precision", f"best emitted start={candidate.base_start_date}; source start anchor={label.window_start} ({label.window_start_precision.upper()})"]
    elif not pivot_ok:
        state = "LANDMARK_DISAGREEMENT"
        details = []
        if pivot_date_required: details.append(f"pivot date error={pivot_date_error} days")
        if pivot_price_required: details.append(f"pivot price error={pivot_price_error:.6f}")
        rationale = ["named pattern and source-provided boundaries agree but a source-provided pivot dimension does not", "; ".join(details)]
    else:
        state = "MATCH"
        rationale = ["named pattern agrees with authoritative label", "the matched window was emitted by the frozen detector and maps to a stable structural identity"]
        if label.window_start_precision.upper() == "MONTH":
            rationale.append(f"emitted base start falls inside the source-published month {label.window_start[:7]}")
        else:
            rationale.append(f"base start is within {boundary_tolerance_days} calendar days of source anchor")
        rationale.append(f"base end/recognition is within {boundary_tolerance_days} calendar days of source anchor" if end_required else "source does not publish an exact base-end boundary; end fidelity is not scored")
        if pivot_date_required: rationale.append(f"pivot date is within {pivot_date_tolerance_days} calendar days of source anchor")
        else: rationale.append("source does not publish a detector-comparable pivot date; pivot-date fidelity is not scored")
        if pivot_price_required: rationale.append(f"pivot price is within {pivot_price_tolerance_pct:.2%} of source anchor")
        else: rationale.append("source does not publish a detector-comparable pivot price; pivot-price fidelity is not scored")

    return LabelAgreement(label.example_id, label.pattern, label.split, state, lineage_id, base_id, start_error, end_error, pivot_date_error, round(pivot_price_error, 8) if pivot_price_error is not None else None, _boundary_state(label), pivot_validation_state, candidate.to_dict(), rationale)
