"""Position lifecycle / exit arbiter v2.

Integrates frozen #37, #40 and #42 executable exits without changing upstream semantics.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Sequence

LIFECYCLE_VERSION = "43-position-lifecycle-exit-arbiter-v2"
SOURCE_SELL_RISK_VERSION = "37-sell-risk-v1"
SOURCE_TECHNICAL_ACTION_VERSION = "40-technical-deterioration-action-v1"
SOURCE_ROUND_TRIP_ACTION_VERSION = "42-round-trip-sell-action-v1"

OPEN_SOURCES = {
    "DAILY_OHLCV_OPEN_GAP_THROUGH",
    "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_WEEK",
    "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_CLOSE",
}
STOP_SOURCE = "DAILY_OHLCV_STOP_CONVENTION"


class LifecycleState(str, Enum):
    NOT_OPENED = "NOT_OPENED"
    OPEN = "OPEN"
    CLOSED_CAPITAL_PROTECTION = "CLOSED_CAPITAL_PROTECTION"
    CLOSED_TECHNICAL_DETERIORATION = "CLOSED_TECHNICAL_DETERIORATION"
    CLOSED_ROUND_TRIP = "CLOSED_ROUND_TRIP"
    CLOSED_OPEN_CONVERGENCE = "CLOSED_OPEN_CONVERGENCE"
    AMBIGUOUS_SAME_SESSION = "AMBIGUOUS_SAME_SESSION"
    NOT_EVALUABLE = "NOT_EVALUABLE"
    NOT_EVALUABLE_SOURCE_CONFLICT = "NOT_EVALUABLE_SOURCE_CONFLICT"


@dataclass(frozen=True)
class ExitCandidate:
    channel: str
    execution_date: Optional[str]
    execution_price: Optional[float]
    execution_source: Optional[str]
    source_version: str

    @property
    def executable(self) -> bool:
        return self.execution_date is not None and self.execution_price is not None


@dataclass(frozen=True)
class PositionLifecycleV2:
    candidate_id: str
    security_id: str
    entry_date: Optional[str]
    fill_price: Optional[float]
    source_entry_version: str
    source_sell_risk_version: str
    source_technical_action_version: str
    source_round_trip_action_version: str
    lifecycle_state: str
    selected_exit_channel: Optional[str]
    selected_exit_date: Optional[str]
    selected_exit_price: Optional[float]
    selected_exit_source: Optional[str]
    converged_channels: tuple[str, ...]
    arbitration_reason: str
    lifecycle_version: str


def _closed_state(channel: str) -> LifecycleState:
    if channel == "CAPITAL_PROTECTION_37":
        return LifecycleState.CLOSED_CAPITAL_PROTECTION
    if channel == "TECHNICAL_DETERIORATION_40":
        return LifecycleState.CLOSED_TECHNICAL_DETERIORATION
    if channel == "ROUND_TRIP_42":
        return LifecycleState.CLOSED_ROUND_TRIP
    raise ValueError(f"unsupported channel: {channel}")


def arbitrate_position_lifecycle_v2(
    *,
    candidate_id: str,
    security_id: str,
    entry_date: Optional[str],
    fill_price: Optional[float],
    source_entry_version: str,
    capital_exit: ExitCandidate,
    technical_exit: ExitCandidate,
    round_trip_exit: ExitCandidate,
) -> PositionLifecycleV2:
    base = dict(
        candidate_id=candidate_id,
        security_id=security_id,
        entry_date=entry_date,
        fill_price=fill_price,
        source_entry_version=source_entry_version,
        source_sell_risk_version=capital_exit.source_version,
        source_technical_action_version=technical_exit.source_version,
        source_round_trip_action_version=round_trip_exit.source_version,
        lifecycle_version=LIFECYCLE_VERSION,
    )

    if entry_date is None or fill_price is None:
        return PositionLifecycleV2(**base, lifecycle_state=LifecycleState.NOT_OPENED.value,
            selected_exit_channel=None, selected_exit_date=None, selected_exit_price=None,
            selected_exit_source=None, converged_channels=(), arbitration_reason="NO_EXECUTABLE_ENTRY")
    if fill_price <= 0:
        return PositionLifecycleV2(**base, lifecycle_state=LifecycleState.NOT_EVALUABLE.value,
            selected_exit_channel=None, selected_exit_date=None, selected_exit_price=None,
            selected_exit_source=None, converged_channels=(), arbitration_reason="INVALID_FILL_PRICE")

    candidates = [capital_exit, technical_exit, round_trip_exit]
    exits = [x for x in candidates if x.executable]
    if any(x.execution_date < entry_date for x in exits):
        return PositionLifecycleV2(**base, lifecycle_state=LifecycleState.NOT_EVALUABLE.value,
            selected_exit_channel=None, selected_exit_date=None, selected_exit_price=None,
            selected_exit_source=None, converged_channels=(), arbitration_reason="EXIT_PRECEDES_ENTRY")
    if not exits:
        return PositionLifecycleV2(**base, lifecycle_state=LifecycleState.OPEN.value,
            selected_exit_channel=None, selected_exit_date=None, selected_exit_price=None,
            selected_exit_source=None, converged_channels=(), arbitration_reason="NO_EXECUTABLE_EXIT_YET")

    earliest_date = min(x.execution_date for x in exits)
    same_day = [x for x in exits if x.execution_date == earliest_date]
    if len(same_day) == 1:
        x = same_day[0]
        return PositionLifecycleV2(**base, lifecycle_state=_closed_state(x.channel).value,
            selected_exit_channel=x.channel, selected_exit_date=x.execution_date,
            selected_exit_price=x.execution_price, selected_exit_source=x.execution_source,
            converged_channels=(x.channel,), arbitration_reason="EARLIEST_EXECUTABLE_EXIT")

    open_exits = [x for x in same_day if x.execution_source in OPEN_SOURCES]
    stop_exits = [x for x in same_day if x.execution_source == STOP_SOURCE]
    unknown_exits = [x for x in same_day if x.execution_source not in OPEN_SOURCES and x.execution_source != STOP_SOURCE]

    if open_exits:
        prices = {float(x.execution_price) for x in open_exits}
        if len(prices) > 1:
            return PositionLifecycleV2(**base, lifecycle_state=LifecycleState.NOT_EVALUABLE_SOURCE_CONFLICT.value,
                selected_exit_channel=None, selected_exit_date=None, selected_exit_price=None,
                selected_exit_source=None, converged_channels=tuple(sorted(x.channel for x in open_exits)),
                arbitration_reason="SAME_OBSERVED_OPEN_HAS_CONFLICTING_PRICES")
        if unknown_exits:
            return PositionLifecycleV2(**base, lifecycle_state=LifecycleState.AMBIGUOUS_SAME_SESSION.value,
                selected_exit_channel=None, selected_exit_date=None, selected_exit_price=None,
                selected_exit_source=None, converged_channels=(),
                arbitration_reason="UNKNOWN_SAME_SESSION_ORDERING")
        channels = tuple(sorted(x.channel for x in open_exits))
        price = float(open_exits[0].execution_price)
        if len(open_exits) >= 2:
            return PositionLifecycleV2(**base, lifecycle_state=LifecycleState.CLOSED_OPEN_CONVERGENCE.value,
                selected_exit_channel="+".join(channels), selected_exit_date=earliest_date,
                selected_exit_price=price, selected_exit_source="SAME_OBSERVED_OPEN",
                converged_channels=channels, arbitration_reason="SAME_OPEN_CONVERGENCE")
        # One open exit and one/more stop-convention exits: open occurs first.
        x = open_exits[0]
        return PositionLifecycleV2(**base, lifecycle_state=_closed_state(x.channel).value,
            selected_exit_channel=x.channel, selected_exit_date=x.execution_date,
            selected_exit_price=x.execution_price, selected_exit_source=x.execution_source,
            converged_channels=(x.channel,), arbitration_reason="SESSION_OPEN_PRECEDES_INTRADAY_STOP_CONVENTION")

    # Multiple same-day non-open candidates cannot be causally ordered from daily OHLCV.
    return PositionLifecycleV2(**base, lifecycle_state=LifecycleState.AMBIGUOUS_SAME_SESSION.value,
        selected_exit_channel=None, selected_exit_date=None, selected_exit_price=None,
        selected_exit_source=None, converged_channels=(),
        arbitration_reason="INTRADAY_ORDER_NOT_ESTABLISHED_BY_FROZEN_CONTRACTS")


def validate_position_lifecycle_v2(x: PositionLifecycleV2) -> list[str]:
    findings: list[str] = []
    if x.lifecycle_version != LIFECYCLE_VERSION:
        findings.append("L43-A_VERSION_MISMATCH")
    if x.source_sell_risk_version != SOURCE_SELL_RISK_VERSION:
        findings.append("L43-A_SOURCE_37_MISMATCH")
    if x.source_technical_action_version != SOURCE_TECHNICAL_ACTION_VERSION:
        findings.append("L43-A_SOURCE_40_MISMATCH")
    if x.source_round_trip_action_version != SOURCE_ROUND_TRIP_ACTION_VERSION:
        findings.append("L43-A_SOURCE_42_MISMATCH")
    if x.entry_date is None and x.selected_exit_date is not None:
        findings.append("L43-B_EXIT_WITHOUT_ENTRY")
    if x.entry_date and x.selected_exit_date and x.selected_exit_date < x.entry_date:
        findings.append("L43-H_EXIT_PRECEDES_ENTRY")
    if x.lifecycle_state.startswith("CLOSED_"):
        if x.selected_exit_date is None or x.selected_exit_price is None:
            findings.append("L43-I_CLOSED_WITHOUT_SINGLE_EXIT")
    if x.lifecycle_state in {
        LifecycleState.AMBIGUOUS_SAME_SESSION.value,
        LifecycleState.NOT_EVALUABLE_SOURCE_CONFLICT.value,
    } and x.selected_exit_date is not None:
        findings.append("L43-FG_UNSUPPORTED_RESOLUTION")
    return findings
