"""Position lifecycle / exit arbiter v1.

Combines frozen #37 and #40 executable exits without changing either source contract.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

LIFECYCLE_VERSION = "41-position-lifecycle-exit-arbiter-v1"
SOURCE_SELL_RISK_VERSION = "37-sell-risk-v1"
SOURCE_TECHNICAL_ACTION_VERSION = "40-technical-deterioration-action-v1"


class LifecycleState(str, Enum):
    NOT_OPENED = "NOT_OPENED"
    OPEN = "OPEN"
    CLOSED_CAPITAL_PROTECTION = "CLOSED_CAPITAL_PROTECTION"
    CLOSED_TECHNICAL_DETERIORATION = "CLOSED_TECHNICAL_DETERIORATION"
    CLOSED_SAME_OPEN_CONVERGENCE = "CLOSED_SAME_OPEN_CONVERGENCE"
    AMBIGUOUS_SAME_SESSION = "AMBIGUOUS_SAME_SESSION"
    NOT_EVALUABLE = "NOT_EVALUABLE"


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
class PositionLifecycle:
    candidate_id: str
    security_id: str
    entry_date: Optional[str]
    fill_price: Optional[float]
    source_entry_version: str
    capital_exit_date: Optional[str]
    capital_exit_price: Optional[float]
    capital_exit_source: Optional[str]
    source_sell_risk_version: str
    technical_exit_date: Optional[str]
    technical_exit_price: Optional[float]
    technical_exit_source: Optional[str]
    source_technical_action_version: str
    lifecycle_state: str
    selected_exit_channel: Optional[str]
    selected_exit_date: Optional[str]
    selected_exit_price: Optional[float]
    selected_exit_source: Optional[str]
    arbitration_reason: str
    lifecycle_version: str


def arbitrate_position_lifecycle(
    *,
    candidate_id: str,
    security_id: str,
    entry_date: Optional[str],
    fill_price: Optional[float],
    source_entry_version: str,
    capital_exit: ExitCandidate,
    technical_exit: ExitCandidate,
) -> PositionLifecycle:
    base = dict(
        candidate_id=candidate_id,
        security_id=security_id,
        entry_date=entry_date,
        fill_price=fill_price,
        source_entry_version=source_entry_version,
        capital_exit_date=capital_exit.execution_date,
        capital_exit_price=capital_exit.execution_price,
        capital_exit_source=capital_exit.execution_source,
        source_sell_risk_version=capital_exit.source_version,
        technical_exit_date=technical_exit.execution_date,
        technical_exit_price=technical_exit.execution_price,
        technical_exit_source=technical_exit.execution_source,
        source_technical_action_version=technical_exit.source_version,
        lifecycle_version=LIFECYCLE_VERSION,
    )

    if entry_date is None or fill_price is None:
        return PositionLifecycle(**base, lifecycle_state=LifecycleState.NOT_OPENED.value,
            selected_exit_channel=None, selected_exit_date=None, selected_exit_price=None,
            selected_exit_source=None, arbitration_reason="NO_EXECUTABLE_ENTRY")
    if fill_price <= 0:
        return PositionLifecycle(**base, lifecycle_state=LifecycleState.NOT_EVALUABLE.value,
            selected_exit_channel=None, selected_exit_date=None, selected_exit_price=None,
            selected_exit_source=None, arbitration_reason="INVALID_FILL_PRICE")

    exits = [x for x in (capital_exit, technical_exit) if x.executable]
    if any(x.execution_date < entry_date for x in exits):
        return PositionLifecycle(**base, lifecycle_state=LifecycleState.NOT_EVALUABLE.value,
            selected_exit_channel=None, selected_exit_date=None, selected_exit_price=None,
            selected_exit_source=None, arbitration_reason="EXIT_PRECEDES_ENTRY")
    if not exits:
        return PositionLifecycle(**base, lifecycle_state=LifecycleState.OPEN.value,
            selected_exit_channel=None, selected_exit_date=None, selected_exit_price=None,
            selected_exit_source=None, arbitration_reason="NO_EXECUTABLE_EXIT_YET")
    if len(exits) == 1:
        x = exits[0]
        state = (LifecycleState.CLOSED_CAPITAL_PROTECTION if x.channel == "CAPITAL_PROTECTION_37"
                 else LifecycleState.CLOSED_TECHNICAL_DETERIORATION)
        return PositionLifecycle(**base, lifecycle_state=state.value, selected_exit_channel=x.channel,
            selected_exit_date=x.execution_date, selected_exit_price=x.execution_price,
            selected_exit_source=x.execution_source, arbitration_reason="ONLY_EXECUTABLE_EXIT")

    c, t = capital_exit, technical_exit
    if c.execution_date < t.execution_date:
        return PositionLifecycle(**base, lifecycle_state=LifecycleState.CLOSED_CAPITAL_PROTECTION.value,
            selected_exit_channel=c.channel, selected_exit_date=c.execution_date,
            selected_exit_price=c.execution_price, selected_exit_source=c.execution_source,
            arbitration_reason="EARLIEST_EXECUTABLE_EXIT")
    if t.execution_date < c.execution_date:
        return PositionLifecycle(**base, lifecycle_state=LifecycleState.CLOSED_TECHNICAL_DETERIORATION.value,
            selected_exit_channel=t.channel, selected_exit_date=t.execution_date,
            selected_exit_price=t.execution_price, selected_exit_source=t.execution_source,
            arbitration_reason="EARLIEST_EXECUTABLE_EXIT")

    # Same completed daily session. #40 is known to execute at observed open.
    tech_at_open = t.execution_source == "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_WEEK"
    capital_at_open = c.execution_source == "DAILY_OHLCV_OPEN_GAP_THROUGH"
    capital_at_stop = c.execution_source == "DAILY_OHLCV_STOP_CONVENTION"

    if tech_at_open and capital_at_open and c.execution_price == t.execution_price:
        return PositionLifecycle(**base, lifecycle_state=LifecycleState.CLOSED_SAME_OPEN_CONVERGENCE.value,
            selected_exit_channel="CAPITAL_PROTECTION_37+TECHNICAL_DETERIORATION_40",
            selected_exit_date=t.execution_date, selected_exit_price=t.execution_price,
            selected_exit_source="SAME_OBSERVED_OPEN", arbitration_reason="SAME_OPEN_CONVERGENCE")
    if tech_at_open and capital_at_stop:
        return PositionLifecycle(**base, lifecycle_state=LifecycleState.CLOSED_TECHNICAL_DETERIORATION.value,
            selected_exit_channel=t.channel, selected_exit_date=t.execution_date,
            selected_exit_price=t.execution_price, selected_exit_source=t.execution_source,
            arbitration_reason="SESSION_OPEN_PRECEDES_INTRADAY_STOP_CONVENTION")

    return PositionLifecycle(**base, lifecycle_state=LifecycleState.AMBIGUOUS_SAME_SESSION.value,
        selected_exit_channel=None, selected_exit_date=None, selected_exit_price=None,
        selected_exit_source=None, arbitration_reason="INTRADAY_ORDER_NOT_ESTABLISHED_BY_FROZEN_CONTRACTS")


def validate_position_lifecycle(x: PositionLifecycle) -> list[str]:
    findings: list[str] = []
    if x.lifecycle_version != LIFECYCLE_VERSION:
        findings.append("L41-A_VERSION_MISMATCH")
    if x.source_sell_risk_version != SOURCE_SELL_RISK_VERSION:
        findings.append("L41-A_SOURCE_37_MISMATCH")
    if x.source_technical_action_version != SOURCE_TECHNICAL_ACTION_VERSION:
        findings.append("L41-A_SOURCE_40_MISMATCH")
    if x.entry_date is None and x.selected_exit_date is not None:
        findings.append("L41-B_EXIT_WITHOUT_ENTRY")
    if x.entry_date and x.selected_exit_date and x.selected_exit_date < x.entry_date:
        findings.append("L41-G_EXIT_PRECEDES_ENTRY")
    if x.lifecycle_state.startswith("CLOSED_"):
        if x.selected_exit_date is None or x.selected_exit_price is None:
            findings.append("L41-H_CLOSED_WITHOUT_SINGLE_EXIT")
    if x.lifecycle_state == LifecycleState.AMBIGUOUS_SAME_SESSION.value and x.selected_exit_date is not None:
        findings.append("L41-F_AMBIGUITY_IMPROPERLY_RESOLVED")
    return findings
