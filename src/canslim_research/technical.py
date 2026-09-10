"""Independent CAN SLIM technical baseline v1.

Transparent quantitative proxies for N/S/L/M. These are not proprietary IBD
ratings or pattern-recognition algorithms.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

PRICE_FLOOR = 15.0
BUY_ZONE_MAX = 0.05
VOLUME_RATIO_MIN = 1.40
RS_PERCENTILE_MIN = 80.0
FTD_RETURN_MIN = 0.01
DISTRIBUTION_RETURN_MAX = -0.002
DISTRIBUTION_BLOCK_COUNT = 6
DISTRIBUTION_WINDOW = 25
BASE_LOOKBACK = 35
BASE_DEPTH_MAX = 0.40


@dataclass(frozen=True)
class TechnicalResult:
    value: Optional[bool]
    state: str
    reason: str


def price_guardrail(close: Optional[float]) -> TechnicalResult:
    if close is None:
        return TechnicalResult(None, "NOT_EVALUABLE", "PRICE_MISSING")
    passed = close >= PRICE_FLOOR
    return TechnicalResult(passed, "PASS" if passed else "FAIL", "PRICE_FLOOR_15")


def n_price_label(*, close: Optional[float], pivot: Optional[float], base_depth: Optional[float]) -> TechnicalResult:
    """N-price v1: breakout above pivot, within 5% buy zone, base depth <=40%."""
    if close is None or pivot is None or base_depth is None or pivot <= 0:
        return TechnicalResult(None, "NOT_EVALUABLE", "N_INPUT_MISSING")
    if base_depth > BASE_DEPTH_MAX:
        return TechnicalResult(False, "FAIL", "BASE_TOO_DEEP")
    if close <= pivot:
        return TechnicalResult(False, "FAIL", "NO_BREAKOUT")
    if close > pivot * (1.0 + BUY_ZONE_MAX):
        return TechnicalResult(False, "FAIL", "ABOVE_5PCT_BUY_ZONE")
    return TechnicalResult(True, "PASS", "N_PRICE_V1")


def consolidation_pivot(highs: list[float], lows: list[float]) -> tuple[Optional[float], Optional[float]]:
    """Generic 7-week consolidation proxy using the prior 35 sessions.

    Returns (pivot, depth). The signal day itself must not be included by callers.
    """
    if len(highs) < BASE_LOOKBACK or len(lows) < BASE_LOOKBACK:
        return None, None
    h = highs[-BASE_LOOKBACK:]
    l = lows[-BASE_LOOKBACK:]
    pivot = max(h)
    base_low = min(l)
    if pivot <= 0:
        return None, None
    return float(pivot), float((pivot - base_low) / pivot)


def s_label(*, volume: Optional[float], avg_volume_50: Optional[float]) -> TechnicalResult:
    if volume is None or avg_volume_50 is None or avg_volume_50 <= 0:
        return TechnicalResult(None, "NOT_EVALUABLE", "VOLUME_INPUT_MISSING")
    ratio = volume / avg_volume_50
    passed = ratio >= VOLUME_RATIO_MIN
    return TechnicalResult(passed, "PASS" if passed else "FAIL", "BREAKOUT_VOLUME_1P40X")


def rs_proxy_raw(*, return_63d: Optional[float], return_126d: Optional[float], return_189d: Optional[float], return_252d: Optional[float]) -> Optional[float]:
    vals = [return_63d, return_126d, return_189d, return_252d]
    if any(v is None for v in vals):
        return None
    return 0.40 * float(return_63d) + 0.20 * float(return_126d) + 0.20 * float(return_189d) + 0.20 * float(return_252d)


def l_label(rs_percentile: Optional[float]) -> TechnicalResult:
    if rs_percentile is None:
        return TechnicalResult(None, "NOT_EVALUABLE", "RS_PERCENTILE_MISSING")
    passed = rs_percentile >= RS_PERCENTILE_MIN
    return TechnicalResult(passed, "PASS" if passed else "FAIL", "RS_PROXY_PCTL_80")


def is_distribution_day(*, daily_return: Optional[float], volume: Optional[float], previous_volume: Optional[float]) -> bool:
    if daily_return is None or volume is None or previous_volume is None:
        return False
    return daily_return <= DISTRIBUTION_RETURN_MAX and volume > previous_volume


def is_follow_through_day(*, rally_day_number: int, daily_return: Optional[float], volume: Optional[float], previous_volume: Optional[float]) -> bool:
    if rally_day_number < 4 or daily_return is None or volume is None or previous_volume is None:
        return False
    return daily_return >= FTD_RETURN_MIN and volume > previous_volume


def m_label(*, spy_confirmed: bool, qqq_confirmed: bool, spy_distribution_count: int, qqq_distribution_count: int) -> TechnicalResult:
    if max(spy_distribution_count, qqq_distribution_count) >= DISTRIBUTION_BLOCK_COUNT:
        return TechnicalResult(False, "FAIL", "DISTRIBUTION_CLUSTER")
    passed = spy_confirmed or qqq_confirmed
    return TechnicalResult(passed, "PASS" if passed else "FAIL", "FTD_PROXY_ACTIVE" if passed else "NO_ACTIVE_FTD_PROXY")


def technical_candidate(*, price: TechnicalResult, n: TechnicalResult, s: TechnicalResult, l: TechnicalResult, m: TechnicalResult) -> TechnicalResult:
    components = [price, n, s, l, m]
    if any(x.value is None for x in components):
        return TechnicalResult(None, "NOT_EVALUABLE", "TECHNICAL_COMPONENT_NOT_EVALUABLE")
    passed = all(bool(x.value) for x in components)
    return TechnicalResult(passed, "PASS" if passed else "FAIL", "TECHNICAL_BASELINE_V1")
