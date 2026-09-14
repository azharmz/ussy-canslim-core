"""Round-trip sell action v1."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Sequence

ACTION_VERSION = "42-round-trip-sell-action-v1"
SOURCE_SELL_RISK_VERSION = "37-sell-risk-v1"
DOUBLE_DIGIT_GAIN = 0.10
BOUNDARY_EPSILON = 1e-12


class RoundTripState(str, Enum):
    NOT_EVALUABLE = "NOT_EVALUABLE"
    NO_ACTION = "NO_ACTION"
    ROUND_TRIP_EXIT_REQUIRED = "ROUND_TRIP_EXIT_REQUIRED"
    NO_NEXT_SESSION_BAR = "NO_NEXT_SESSION_BAR"
    AMBIGUOUS_SAME_SESSION = "AMBIGUOUS_SAME_SESSION"


@dataclass(frozen=True)
class DailyBar:
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None


@dataclass(frozen=True)
class RoundTripAction:
    candidate_id: str
    security_id: str
    entry_date: str
    fill_price: float
    pivot_level: float
    prior_max_high: Optional[float]
    prior_max_gain_from_buy_point_pct: Optional[float]
    trigger_date: Optional[str]
    trigger_close: Optional[float]
    round_trip_state: str
    execution_date: Optional[str]
    execution_price: Optional[float]
    execution_source: Optional[str]
    source_sell_risk_version: str
    source_entry_version: str
    action_version: str


def _meets_double_digit_gain(high: float, pivot: float) -> bool:
    return high / pivot - 1.0 >= DOUBLE_DIGIT_GAIN - BOUNDARY_EPSILON


def decide_round_trip_action(
    *,
    candidate_id: str,
    security_id: str,
    entry_date: str,
    fill_price: float,
    pivot_level: float,
    bars_since_entry: Sequence[DailyBar],
    source_entry_version: str,
    source_sell_risk_version: str = SOURCE_SELL_RISK_VERSION,
) -> RoundTripAction:
    if fill_price <= 0 or pivot_level <= 0:
        raise ValueError("fill_price and pivot_level must be positive")
    if not bars_since_entry:
        return RoundTripAction(candidate_id, security_id, entry_date, float(fill_price), float(pivot_level),
            None, None, None, None, RoundTripState.NOT_EVALUABLE.value,
            None, None, None, source_sell_risk_version, source_entry_version, ACTION_VERSION)

    prior_high: Optional[float] = None
    for i, bar in enumerate(bars_since_entry):
        if bar.date < entry_date:
            continue
        prior_gain = None if prior_high is None else prior_high / pivot_level - 1.0
        had_double_digit_prior = prior_high is not None and _meets_double_digit_gain(prior_high, pivot_level)

        same_session_first_gain = (
            not had_double_digit_prior
            and _meets_double_digit_gain(float(bar.high), pivot_level)
            and float(bar.close) <= pivot_level
        )
        if same_session_first_gain:
            return RoundTripAction(candidate_id, security_id, entry_date, float(fill_price), float(pivot_level),
                prior_high, prior_gain, bar.date, float(bar.close),
                RoundTripState.AMBIGUOUS_SAME_SESSION.value,
                None, None, None, source_sell_risk_version, source_entry_version, ACTION_VERSION)

        if had_double_digit_prior and float(bar.close) <= pivot_level:
            next_bar = next((b for b in bars_since_entry[i + 1:] if b.date > bar.date), None)
            state = RoundTripState.ROUND_TRIP_EXIT_REQUIRED if next_bar is not None else RoundTripState.NO_NEXT_SESSION_BAR
            return RoundTripAction(candidate_id, security_id, entry_date, float(fill_price), float(pivot_level),
                float(prior_high), float(prior_gain), bar.date, float(bar.close), state.value,
                None if next_bar is None else next_bar.date,
                None if next_bar is None else float(next_bar.open),
                None if next_bar is None else "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_CLOSE",
                source_sell_risk_version, source_entry_version, ACTION_VERSION)

        prior_high = float(bar.high) if prior_high is None else max(prior_high, float(bar.high))

    gain = None if prior_high is None else prior_high / pivot_level - 1.0
    return RoundTripAction(candidate_id, security_id, entry_date, float(fill_price), float(pivot_level),
        prior_high, gain, None, None, RoundTripState.NO_ACTION.value,
        None, None, None, source_sell_risk_version, source_entry_version, ACTION_VERSION)


def validate_round_trip_action(x: RoundTripAction) -> list[str]:
    findings: list[str] = []
    if x.action_version != ACTION_VERSION:
        findings.append("R42-A_VERSION_MISMATCH")
    if x.source_sell_risk_version != SOURCE_SELL_RISK_VERSION:
        findings.append("R42-A_SOURCE_37_MISMATCH")
    if x.round_trip_state == RoundTripState.ROUND_TRIP_EXIT_REQUIRED.value:
        if x.prior_max_gain_from_buy_point_pct is None or x.prior_max_gain_from_buy_point_pct < DOUBLE_DIGIT_GAIN - BOUNDARY_EPSILON:
            findings.append("R42-C_MISSING_PRIOR_DOUBLE_DIGIT_GAIN")
        if x.trigger_close is None or x.trigger_close > x.pivot_level:
            findings.append("R42-D_INVALID_RETURN_TO_BUY_POINT")
        if x.execution_date is None or x.execution_price is None:
            findings.append("R42-F_MISSING_CAUSAL_EXECUTION")
        elif x.trigger_date is not None and not x.execution_date > x.trigger_date:
            findings.append("R42-F_NONCAUSAL_EXECUTION")
        if x.execution_source != "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_CLOSE":
            findings.append("R42-F_INVALID_EXECUTION_SOURCE")
    if x.round_trip_state == RoundTripState.AMBIGUOUS_SAME_SESSION.value and x.execution_date is not None:
        findings.append("R42-E_AMBIGUITY_IMPROPERLY_RESOLVED")
    return findings
