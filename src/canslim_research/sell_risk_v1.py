"""Theory-faithful CAN SLIM sell/risk state machine v1.

This module is downstream of frozen #36 entry execution. It separates
O'Neil/CAN SLIM theory semantics from daily-data/backtest execution clocks.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Sequence

SELL_RISK_VERSION = "37-sell-risk-v1"
PRACTICAL_LOSS_TRIGGER = 0.07
LEGACY_HARD_LOSS_CEILING = 0.08
NORMAL_PROFIT_LOW = 0.20
NORMAL_PROFIT_HIGH = 0.25
FAST_WINNER_GAIN = 0.20
FAST_WINNER_WINDOW_SESSIONS = 15
EIGHT_WEEK_ASSESSMENT_SESSIONS = 40


class CapitalProtectionState(str, Enum):
    LOSS_OK = "LOSS_OK"
    PRACTICAL_7PCT_TRIGGER_REACHED = "PRACTICAL_7PCT_TRIGGER_REACHED"
    LEGACY_8PCT_CEILING_BREACHED = "LEGACY_8PCT_CEILING_BREACHED"


class ProfitZoneState(str, Enum):
    BELOW_NORMAL_PROFIT_ZONE = "BELOW_NORMAL_PROFIT_ZONE"
    IN_NORMAL_PROFIT_ZONE = "IN_NORMAL_PROFIT_ZONE"
    ABOVE_NORMAL_PROFIT_ZONE = "ABOVE_NORMAL_PROFIT_ZONE"


class SellActionState(str, Enum):
    HOLD = "HOLD"
    DEFENSIVE_EXIT_REQUIRED = "DEFENSIVE_EXIT_REQUIRED"


@dataclass(frozen=True)
class DailyBar:
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None


@dataclass(frozen=True)
class SellRiskSnapshot:
    candidate_id: str
    security_id: str
    entry_date: str
    fill_price: float
    pivot_level: float
    breakout_date: str
    asof_date: str
    loss_from_fill_pct: float
    practical_loss_trigger_price: float
    legacy_hard_loss_ceiling_price: float
    capital_protection_state: str
    fell_back_below_pivot: bool
    profit_from_buy_point_pct: float
    profit_from_fill_pct: float
    normal_profit_zone_state: str
    reached_20pct_within_first_3_weeks: bool
    eight_week_hold_exception_active: bool
    eight_week_assessment_session: int
    max_gain_from_fill_pct: float
    max_gain_from_buy_point_pct: float
    round_trip_to_buy_point: Optional[bool]
    technical_deterioration_state: str
    climax_state: str
    market_exposure_state: str
    sell_action_state: str
    sell_execution_date: Optional[str]
    sell_execution_price: Optional[float]
    sell_execution_source: Optional[str]
    sell_risk_version: str
    source_entry_version: str


def _profit_zone(pivot: float, price: float) -> ProfitZoneState:
    pct = price / pivot - 1.0
    if pct < NORMAL_PROFIT_LOW:
        return ProfitZoneState.BELOW_NORMAL_PROFIT_ZONE
    if pct <= NORMAL_PROFIT_HIGH:
        return ProfitZoneState.IN_NORMAL_PROFIT_ZONE
    return ProfitZoneState.ABOVE_NORMAL_PROFIT_ZONE


def _capital_state(fill: float, mark: float) -> CapitalProtectionState:
    loss = mark / fill - 1.0
    if loss <= -LEGACY_HARD_LOSS_CEILING:
        return CapitalProtectionState.LEGACY_8PCT_CEILING_BREACHED
    if loss <= -PRACTICAL_LOSS_TRIGGER:
        return CapitalProtectionState.PRACTICAL_7PCT_TRIGGER_REACHED
    return CapitalProtectionState.LOSS_OK


def _defensive_exit(fill_price: float, bar: DailyBar) -> tuple[Optional[float], Optional[str]]:
    """Backtest execution convention for the practical 7% defensive trigger."""
    trigger = fill_price * (1.0 - PRACTICAL_LOSS_TRIGGER)
    if bar.open <= trigger:
        return float(bar.open), "DAILY_OHLCV_OPEN_GAP_THROUGH"
    if bar.low <= trigger:
        return float(trigger), "DAILY_OHLCV_STOP_CONVENTION"
    return None, None


def evaluate_sell_risk(
    *,
    candidate_id: str,
    security_id: str,
    entry_date: str,
    fill_price: float,
    pivot_level: float,
    breakout_date: str,
    bars_since_breakout: Sequence[DailyBar],
    source_entry_version: str,
    market_exposure_state: str = "NOT_IMPLEMENTED",
) -> SellRiskSnapshot:
    if fill_price <= 0 or pivot_level <= 0:
        raise ValueError("fill_price and pivot_level must be positive")
    if not bars_since_breakout:
        raise ValueError("bars_since_breakout must not be empty")

    current = bars_since_breakout[-1]
    highs = [float(x.high) for x in bars_since_breakout]
    max_high = max(highs)

    profit_from_pivot = current.close / pivot_level - 1.0
    profit_from_fill = current.close / fill_price - 1.0
    max_gain_fill = max_high / fill_price - 1.0
    max_gain_pivot = max_high / pivot_level - 1.0

    first_15 = bars_since_breakout[:FAST_WINNER_WINDOW_SESSIONS]
    reached_fast_20 = any(float(x.high) >= pivot_level * (1.0 + FAST_WINNER_GAIN) for x in first_15)
    sessions_elapsed = len(bars_since_breakout)
    eight_week_active = reached_fast_20 and sessions_elapsed < EIGHT_WEEK_ASSESSMENT_SESSIONS

    # #37 v1 deliberately does not invent the theory's missing numeric
    # "meaningful gain" precondition for a canonical round-trip trigger.
    round_trip = None

    exit_price = None
    exit_source = None
    exit_date = None
    for bar in bars_since_breakout:
        if bar.date < entry_date:
            continue
        price, source = _defensive_exit(fill_price, bar)
        if price is not None:
            exit_price = price
            exit_source = source
            exit_date = bar.date
            break

    capital_mark = exit_price if exit_price is not None else float(current.close)
    capital_state = _capital_state(fill_price, capital_mark)
    action = SellActionState.DEFENSIVE_EXIT_REQUIRED if exit_price is not None else SellActionState.HOLD

    return SellRiskSnapshot(
        candidate_id=candidate_id,
        security_id=security_id,
        entry_date=entry_date,
        fill_price=float(fill_price),
        pivot_level=float(pivot_level),
        breakout_date=breakout_date,
        asof_date=current.date,
        loss_from_fill_pct=capital_mark / fill_price - 1.0,
        practical_loss_trigger_price=fill_price * 0.93,
        legacy_hard_loss_ceiling_price=fill_price * 0.92,
        capital_protection_state=capital_state.value,
        fell_back_below_pivot=bool(current.close < pivot_level),
        profit_from_buy_point_pct=profit_from_pivot,
        profit_from_fill_pct=profit_from_fill,
        normal_profit_zone_state=_profit_zone(pivot_level, float(current.close)).value,
        reached_20pct_within_first_3_weeks=reached_fast_20,
        eight_week_hold_exception_active=eight_week_active,
        eight_week_assessment_session=EIGHT_WEEK_ASSESSMENT_SESSIONS,
        max_gain_from_fill_pct=max_gain_fill,
        max_gain_from_buy_point_pct=max_gain_pivot,
        round_trip_to_buy_point=round_trip,
        technical_deterioration_state="EVIDENCE_ONLY_NOT_FULLY_IMPLEMENTED",
        climax_state="NOT_IMPLEMENTED_REQUIRES_SEPARATE_AUTHORITATIVE_SPECIFICATION",
        market_exposure_state=market_exposure_state,
        sell_action_state=action.value,
        sell_execution_date=exit_date,
        sell_execution_price=exit_price,
        sell_execution_source=exit_source,
        sell_risk_version=SELL_RISK_VERSION,
        source_entry_version=source_entry_version,
    )


def validate_sell_risk(snapshot: SellRiskSnapshot) -> list[str]:
    findings: list[str] = []
    if snapshot.practical_loss_trigger_price != snapshot.fill_price * 0.93:
        findings.append("S37-B_STOP_REFERENCE_NOT_ACTUAL_FILL")
    if snapshot.legacy_hard_loss_ceiling_price != snapshot.fill_price * 0.92:
        findings.append("S37-B_LEGACY_CEILING_REFERENCE_NOT_ACTUAL_FILL")
    low = snapshot.pivot_level * 1.20
    high = snapshot.pivot_level * 1.25
    if snapshot.normal_profit_zone_state == ProfitZoneState.IN_NORMAL_PROFIT_ZONE.value:
        mark = snapshot.pivot_level * (1.0 + snapshot.profit_from_buy_point_pct)
        if not low <= mark <= high:
            findings.append("S37-D_PROFIT_ZONE_REFERENCE_INVALID")
    if snapshot.sell_action_state == SellActionState.DEFENSIVE_EXIT_REQUIRED.value:
        if snapshot.sell_execution_price is None or snapshot.sell_execution_date is None:
            findings.append("S37-C_EXIT_REQUIRED_WITHOUT_EXECUTION")
    if snapshot.climax_state != "NOT_IMPLEMENTED_REQUIRES_SEPARATE_AUTHORITATIVE_SPECIFICATION":
        findings.append("S37-G_CLIMAX_BOUNDARY_VIOLATION")
    if snapshot.round_trip_to_buy_point is not None:
        findings.append("S37-G_UNSUPPORTED_ROUND_TRIP_NUMERIC_TRIGGER")
    return findings
