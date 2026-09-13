"""Theory-faithful #34 candidate generation from frozen canonical #33 output.

This module deliberately does not reconstruct morphology. It consumes the frozen
#33 production contract and attaches breakout/volume/eligibility state while
preserving ambiguity and detector faults.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

CANDIDATE_GENERATOR_VERSION = "34-candidate-generator-v0.1"
SPEC_VERSION = "theory-faithful-candidate-spec-v1"
ALLOWED_PATTERN_ENGINE = "33-core-p8-frozen-v1"
CORE_PATTERNS = {"FLAT_BASE", "DOUBLE_BOTTOM", "CUP_WITHOUT_HANDLE", "CUP_WITH_HANDLE"}


@dataclass(frozen=True)
class DailyBar:
    open: float
    high: float
    low: float
    close: float
    volume: float


def _mean(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        raise ValueError("empty mean")
    return sum(values) / len(values)


def generate_candidate(
    pattern: Mapping[str, object],
    bar: DailyBar,
    prior_volumes: Sequence[float],
    *,
    C_screen_state: str = "NOT_EVALUABLE",
    A_screen_state: str = "NOT_EVALUABLE",
    L_individual_leadership_state: str = "NOT_EVALUABLE",
    M_entry_state: str = "NOT_EVALUABLE",
) -> dict[str, object]:
    """Attach #34 states to one canonical #33 pattern record.

    `prior_volumes` must contain completed sessions strictly before the evaluated
    bar. The function never changes #33 pattern state or faults.
    """
    engine = pattern.get("pattern_engine_version") or pattern.get("engine_version")
    if engine != ALLOWED_PATTERN_ENGINE:
        raise ValueError(f"unsupported pattern engine: {engine!r}")

    pattern_type = str(pattern.get("pattern_type"))
    pattern_state = str(pattern.get("status") or pattern.get("pattern_evidence_state"))
    pivot = pattern.get("pivot_level")
    reasons: list[str] = []

    if pattern_type not in CORE_PATTERNS:
        stage = "NOT_EVALUABLE"
        reasons.append("PATTERN_OUTSIDE_FROZEN_CORE")
    elif pattern_state != "RECOGNIZED":
        stage = "NOT_EVALUABLE"
        reasons.append(f"PATTERN_{pattern_state}")
    elif pivot is None:
        stage = "BASE_RECOGNIZED"
        reasons.append("PIVOT_NOT_DEFINED")
    else:
        stage = "PIVOT_DEFINED"

    pivot_value = float(pivot) if pivot is not None else None
    crossed = bool(pivot_value is not None and bar.high > pivot_value)
    open_above = bool(pivot_value is not None and bar.open > pivot_value)
    gap_through = bool(pivot_value is not None and bar.low > pivot_value)
    close_above = bool(pivot_value is not None and bar.close > pivot_value)
    extension = ((bar.close / pivot_value) - 1.0) * 100.0 if pivot_value else None

    volume_avg_50_prior = None
    volume_ratio = None
    volume_state = "NOT_EVALUABLE"
    if len(prior_volumes) >= 50:
        volume_avg_50_prior = _mean(prior_volumes[-50:])
        if volume_avg_50_prior > 0:
            volume_ratio = bar.volume / volume_avg_50_prior
            volume_state = "CONFIRMED_ON_BREAKOUT" if crossed and volume_ratio >= 1.40 else (
                "UNCONFIRMED" if crossed else "PENDING_CONFIRMATION"
            )

    if stage == "PIVOT_DEFINED" and crossed:
        stage = "PIVOT_CROSSED"
        if volume_state == "CONFIRMED_ON_BREAKOUT":
            stage = "BREAKOUT_CONFIRMED"
            if (
                C_screen_state == "PASS"
                and A_screen_state == "PASS"
                and L_individual_leadership_state in {"PASS", "STRONG"}
                and M_entry_state == "ALLOW_NEW_BUYS"
            ):
                stage = "CANSLIM_ELIGIBLE"
            else:
                reasons.append("CANSLIM_ELIGIBILITY_INCOMPLETE")

    return {
        **dict(pattern),
        "candidate_stage": stage,
        "pivot_crossed_intraday": crossed,
        "open_above_pivot": open_above,
        "gap_through_pivot": gap_through,
        "close_above_pivot": close_above,
        "extension_from_pivot_pct": extension,
        "within_traditional_buy_zone": bool(extension is not None and 0.0 <= extension <= 5.0),
        "extended_above_traditional_buy_zone": bool(extension is not None and extension > 5.0),
        "volume_avg_50_prior": volume_avg_50_prior,
        "volume_ratio": volume_ratio,
        "volume_confirmation_state": volume_state,
        "C_screen_state": C_screen_state,
        "A_screen_state": A_screen_state,
        "L_individual_leadership_state": L_individual_leadership_state,
        "M_entry_state": M_entry_state,
        "eligibility_reason_codes": reasons,
        "spec_version": SPEC_VERSION,
        "candidate_generator_version": CANDIDATE_GENERATOR_VERSION,
    }
