"""Theory-faithful #36 execution/entry contract v1.

This module translates an already-frozen #34 candidate into a causal daily-EOD
T+1-open execution decision. It does not recompute pattern, pivot, breakout,
volume, CAN SLIM qualification, or validation semantics.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional

EXECUTION_VERSION = "36-execution-entry-v1"
BUY_ZONE_MAX_EXTENSION = 0.05
PRACTICAL_LOSS_TRIGGER = 0.07
LEGACY_HARD_LOSS_CEILING = 0.08
NORMAL_PROFIT_ZONE_LOW = 0.20
NORMAL_PROFIT_ZONE_HIGH = 0.25


class ExecutionState(str, Enum):
    NOT_ENTRY_ELIGIBLE = "NOT_ENTRY_ELIGIBLE"
    NO_NEXT_SESSION_BAR = "NO_NEXT_SESSION_BAR"
    EXECUTED_T1_OPEN = "EXECUTED_T1_OPEN"
    MISSED_EXTENDED_AT_OPEN = "MISSED_EXTENDED_AT_OPEN"
    BELOW_PIVOT_AT_OPEN = "BELOW_PIVOT_AT_OPEN"
    NOT_EVALUABLE = "NOT_EVALUABLE"


@dataclass(frozen=True)
class ExecutionDecision:
    candidate_id: str
    security_id: str
    signal_date: date
    candidate_stage: str
    pivot_level: Optional[float]
    next_session_date: Optional[date]
    next_open: Optional[float]
    buy_zone_floor: Optional[float]
    buy_zone_ceiling: Optional[float]
    open_extension_pct: Optional[float]
    gap_above_pivot: Optional[bool]
    execution_state: ExecutionState
    fill_date: Optional[date]
    fill_price: Optional[float]
    fill_source: Optional[str]
    initial_stop_reference: Optional[float]
    practical_loss_trigger_price: Optional[float]
    legacy_hard_loss_ceiling_price: Optional[float]
    normal_profit_zone_low: Optional[float]
    normal_profit_zone_high: Optional[float]
    execution_version: str = EXECUTION_VERSION
    source_candidate_version: Optional[str] = None


def decide_t1_open_execution(
    *,
    candidate_id: str,
    security_id: str,
    signal_date: date,
    candidate_stage: str,
    pivot_level: Optional[float],
    next_session_date: Optional[date],
    next_open: Optional[float],
    prior_close: Optional[float] = None,
    source_candidate_version: Optional[str] = None,
) -> ExecutionDecision:
    """Apply the frozen #36 v1 causal T+1-open execution contract.

    Only CANSLIM_ELIGIBLE candidates may execute. A valid canonical fill is the
    observed next-session open, provided it lies from the structural pivot
    through +5% inclusive. No later/retest fill is inferred here.
    """
    common = dict(
        candidate_id=candidate_id,
        security_id=security_id,
        signal_date=signal_date,
        candidate_stage=candidate_stage,
        pivot_level=pivot_level,
        next_session_date=next_session_date,
        next_open=next_open,
        execution_version=EXECUTION_VERSION,
        source_candidate_version=source_candidate_version,
    )

    if candidate_stage != "CANSLIM_ELIGIBLE":
        return ExecutionDecision(
            **common,
            buy_zone_floor=None,
            buy_zone_ceiling=None,
            open_extension_pct=None,
            gap_above_pivot=None,
            execution_state=ExecutionState.NOT_ENTRY_ELIGIBLE,
            fill_date=None,
            fill_price=None,
            fill_source=None,
            initial_stop_reference=None,
            practical_loss_trigger_price=None,
            legacy_hard_loss_ceiling_price=None,
            normal_profit_zone_low=None,
            normal_profit_zone_high=None,
        )

    if pivot_level is None or pivot_level <= 0:
        return ExecutionDecision(
            **common,
            buy_zone_floor=None,
            buy_zone_ceiling=None,
            open_extension_pct=None,
            gap_above_pivot=None,
            execution_state=ExecutionState.NOT_EVALUABLE,
            fill_date=None,
            fill_price=None,
            fill_source=None,
            initial_stop_reference=None,
            practical_loss_trigger_price=None,
            legacy_hard_loss_ceiling_price=None,
            normal_profit_zone_low=None,
            normal_profit_zone_high=None,
        )

    floor = float(pivot_level)
    ceiling = floor * (1.0 + BUY_ZONE_MAX_EXTENSION)
    profit_low = floor * (1.0 + NORMAL_PROFIT_ZONE_LOW)
    profit_high = floor * (1.0 + NORMAL_PROFIT_ZONE_HIGH)

    if next_session_date is None or next_open is None:
        return ExecutionDecision(
            **common,
            buy_zone_floor=floor,
            buy_zone_ceiling=ceiling,
            open_extension_pct=None,
            gap_above_pivot=None,
            execution_state=ExecutionState.NO_NEXT_SESSION_BAR,
            fill_date=None,
            fill_price=None,
            fill_source=None,
            initial_stop_reference=None,
            practical_loss_trigger_price=None,
            legacy_hard_loss_ceiling_price=None,
            normal_profit_zone_low=profit_low,
            normal_profit_zone_high=profit_high,
        )

    if next_session_date <= signal_date:
        raise ValueError("next_session_date must be strictly after signal_date")

    open_price = float(next_open)
    if open_price <= 0:
        return ExecutionDecision(
            **common,
            buy_zone_floor=floor,
            buy_zone_ceiling=ceiling,
            open_extension_pct=None,
            gap_above_pivot=None,
            execution_state=ExecutionState.NOT_EVALUABLE,
            fill_date=None,
            fill_price=None,
            fill_source=None,
            initial_stop_reference=None,
            practical_loss_trigger_price=None,
            legacy_hard_loss_ceiling_price=None,
            normal_profit_zone_low=profit_low,
            normal_profit_zone_high=profit_high,
        )

    extension = open_price / floor - 1.0
    gap_above_pivot = bool(open_price > floor and (prior_close is None or open_price > float(prior_close)))

    if open_price < floor:
        state = ExecutionState.BELOW_PIVOT_AT_OPEN
        fill_price = None
    elif open_price > ceiling:
        state = ExecutionState.MISSED_EXTENDED_AT_OPEN
        fill_price = None
    else:
        state = ExecutionState.EXECUTED_T1_OPEN
        fill_price = open_price

    if fill_price is None:
        return ExecutionDecision(
            **common,
            buy_zone_floor=floor,
            buy_zone_ceiling=ceiling,
            open_extension_pct=extension,
            gap_above_pivot=gap_above_pivot,
            execution_state=state,
            fill_date=None,
            fill_price=None,
            fill_source=None,
            initial_stop_reference=None,
            practical_loss_trigger_price=None,
            legacy_hard_loss_ceiling_price=None,
            normal_profit_zone_low=profit_low,
            normal_profit_zone_high=profit_high,
        )

    return ExecutionDecision(
        **common,
        buy_zone_floor=floor,
        buy_zone_ceiling=ceiling,
        open_extension_pct=extension,
        gap_above_pivot=gap_above_pivot,
        execution_state=state,
        fill_date=next_session_date,
        fill_price=fill_price,
        fill_source="DAILY_OHLCV_OPEN",
        initial_stop_reference=fill_price,
        practical_loss_trigger_price=fill_price * (1.0 - PRACTICAL_LOSS_TRIGGER),
        legacy_hard_loss_ceiling_price=fill_price * (1.0 - LEGACY_HARD_LOSS_CEILING),
        normal_profit_zone_low=profit_low,
        normal_profit_zone_high=profit_high,
    )


def validate_execution_decision(decision: ExecutionDecision) -> list[str]:
    """Return semantic findings for the frozen #36 v1 contract."""
    findings: list[str] = []

    if decision.execution_state == ExecutionState.EXECUTED_T1_OPEN:
        if decision.candidate_stage != "CANSLIM_ELIGIBLE":
            findings.append("EXECUTED_WITHOUT_CANSLIM_ELIGIBLE")
        if decision.fill_date is None or decision.fill_date <= decision.signal_date:
            findings.append("NON_CAUSAL_FILL_DATE")
        if decision.fill_price is None or decision.next_open is None or decision.fill_price != decision.next_open:
            findings.append("FILL_NOT_OBSERVED_T1_OPEN")
        if (
            decision.fill_price is None
            or decision.buy_zone_floor is None
            or decision.buy_zone_ceiling is None
            or not (decision.buy_zone_floor <= decision.fill_price <= decision.buy_zone_ceiling)
        ):
            findings.append("FILL_OUTSIDE_BUY_ZONE")
        if decision.initial_stop_reference != decision.fill_price:
            findings.append("STOP_REFERENCE_NOT_ACTUAL_FILL")

    if decision.execution_state in {
        ExecutionState.MISSED_EXTENDED_AT_OPEN,
        ExecutionState.BELOW_PIVOT_AT_OPEN,
        ExecutionState.NOT_ENTRY_ELIGIBLE,
    } and decision.fill_price is not None:
        findings.append("NON_EXECUTED_STATE_HAS_FILL")

    if decision.pivot_level is not None:
        expected_low = decision.pivot_level * 1.20
        expected_high = decision.pivot_level * 1.25
        if decision.normal_profit_zone_low is not None and abs(decision.normal_profit_zone_low - expected_low) > 1e-9:
            findings.append("PROFIT_ZONE_LOW_NOT_PIVOT_REFERENCED")
        if decision.normal_profit_zone_high is not None and abs(decision.normal_profit_zone_high - expected_high) > 1e-9:
            findings.append("PROFIT_ZONE_HIGH_NOT_PIVOT_REFERENCED")

    return findings
