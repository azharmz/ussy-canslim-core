"""Point-in-time CAN SLIM C/A label semantics.

Pure functions only. Upstream SEC extraction remains owned by ussy-fundamentals.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

C_THRESHOLD = 0.25
A_THRESHOLD = 0.25


@dataclass(frozen=True)
class LabelResult:
    value: Optional[bool]
    state: str
    reason: str


def c_label(eps_yoy: Optional[float], revenue_yoy: Optional[float], *, data_ready: bool = True) -> LabelResult:
    """C-v1: latest usable quarter EPS YoY >=25% AND revenue YoY >=25%.

    Undefined/missing growth is not coerced to zero.
    """
    if not data_ready:
        return LabelResult(None, "NOT_EVALUABLE", "DATA_NOT_READY")
    if eps_yoy is None:
        return LabelResult(None, "NOT_EVALUABLE", "EPS_YOY_UNDEFINED_OR_MISSING")
    if revenue_yoy is None:
        return LabelResult(None, "NOT_EVALUABLE", "REVENUE_YOY_UNDEFINED_OR_MISSING")
    passed = eps_yoy >= C_THRESHOLD and revenue_yoy >= C_THRESHOLD
    return LabelResult(passed, "PASS" if passed else "FAIL", "C_V1_THRESHOLD")


def a_label(annual_eps_yoy: list[Optional[float]], *, data_ready: bool = True, fallback_3y: bool = False) -> LabelResult:
    """A-v1: three consecutive evaluable annual EPS YoY observations, each >=25%."""
    if not data_ready:
        return LabelResult(None, "NOT_EVALUABLE", "DATA_NOT_READY")
    if len(annual_eps_yoy) < 3:
        return LabelResult(None, "NOT_EVALUABLE", "INSUFFICIENT_ANNUAL_HISTORY")
    latest3 = annual_eps_yoy[-3:]
    if any(x is None for x in latest3):
        return LabelResult(None, "NOT_EVALUABLE", "ANNUAL_GROWTH_UNDEFINED_OR_MISSING")
    passed = all(x >= A_THRESHOLD for x in latest3)  # type: ignore[operator]
    tier = "3Y_FALLBACK" if fallback_3y else "FULL"
    return LabelResult(passed, "PASS" if passed else "FAIL", f"A_V1_THRESHOLD_{tier}")
