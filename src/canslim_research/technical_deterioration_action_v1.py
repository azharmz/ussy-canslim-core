"""Canonical technical-deterioration action v1.

Promotes one frozen weekly 10-week evidence condition into a causal sell action.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Sequence

ACTION_VERSION = "40-technical-deterioration-action-v1"
SOURCE_SELL_RISK_VERSION = "37-sell-risk-v1"
SOURCE_DAILY_DETERIORATION_VERSION = "38-technical-deterioration-evidence-v1"
SOURCE_WEEKLY_EVIDENCE_VERSION = "39-weekly-10w-evidence-v1"


class ActionState(str, Enum):
    NO_ACTION = "NO_ACTION"
    TECHNICAL_DETERIORATION_EXIT_REQUIRED = "TECHNICAL_DETERIORATION_EXIT_REQUIRED"
    NO_NEXT_SESSION_BAR = "NO_NEXT_SESSION_BAR"
    NOT_EVALUABLE = "NOT_EVALUABLE"


@dataclass(frozen=True)
class DailyBar:
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None


@dataclass(frozen=True)
class WeeklyEvidence:
    week_start: str
    week_end: str
    close: float
    ma10w: Optional[float]
    volume: Optional[float]
    volume_ratio_prior10: Optional[float]


@dataclass(frozen=True)
class TechnicalDeteriorationAction:
    candidate_id: str
    security_id: str
    entry_date: str
    fill_price: float
    source_sell_risk_version: str
    source_daily_deterioration_version: str
    source_weekly_evidence_version: str
    signal_week_start: Optional[str]
    signal_week_end: Optional[str]
    signal_week_close: Optional[float]
    signal_week_ma10w: Optional[float]
    signal_week_volume: Optional[float]
    signal_week_volume_ratio_prior10: Optional[float]
    action_state: str
    execution_date: Optional[str]
    execution_price: Optional[float]
    execution_source: Optional[str]
    action_version: str


def is_actionable_week(week: WeeklyEvidence) -> Optional[bool]:
    if week.ma10w is None or week.volume_ratio_prior10 is None:
        return None
    return week.close < week.ma10w and week.volume_ratio_prior10 > 1.0


def decide_technical_deterioration_action(
    *,
    candidate_id: str,
    security_id: str,
    entry_date: str,
    fill_price: float,
    weekly_evidence: Sequence[WeeklyEvidence],
    daily_bars: Sequence[DailyBar],
    source_sell_risk_version: str = SOURCE_SELL_RISK_VERSION,
    source_daily_deterioration_version: str = SOURCE_DAILY_DETERIORATION_VERSION,
    source_weekly_evidence_version: str = SOURCE_WEEKLY_EVIDENCE_VERSION,
) -> TechnicalDeteriorationAction:
    if fill_price <= 0:
        raise ValueError("fill_price must be positive")

    signal = None
    saw_evaluable = False
    for week in weekly_evidence:
        actionable = is_actionable_week(week)
        if actionable is None:
            continue
        saw_evaluable = True
        if actionable:
            signal = week
            break

    if signal is None:
        state = ActionState.NO_ACTION if saw_evaluable else ActionState.NOT_EVALUABLE
        return TechnicalDeteriorationAction(
            candidate_id, security_id, entry_date, float(fill_price),
            source_sell_risk_version, source_daily_deterioration_version,
            source_weekly_evidence_version,
            None, None, None, None, None, None,
            state.value, None, None, None, ACTION_VERSION,
        )

    next_bar = next((b for b in daily_bars if b.date > signal.week_end), None)
    if next_bar is None:
        return TechnicalDeteriorationAction(
            candidate_id, security_id, entry_date, float(fill_price),
            source_sell_risk_version, source_daily_deterioration_version,
            source_weekly_evidence_version,
            signal.week_start, signal.week_end, float(signal.close),
            None if signal.ma10w is None else float(signal.ma10w),
            None if signal.volume is None else float(signal.volume),
            None if signal.volume_ratio_prior10 is None else float(signal.volume_ratio_prior10),
            ActionState.NO_NEXT_SESSION_BAR.value,
            None, None, None, ACTION_VERSION,
        )

    return TechnicalDeteriorationAction(
        candidate_id, security_id, entry_date, float(fill_price),
        source_sell_risk_version, source_daily_deterioration_version,
        source_weekly_evidence_version,
        signal.week_start, signal.week_end, float(signal.close),
        None if signal.ma10w is None else float(signal.ma10w),
        None if signal.volume is None else float(signal.volume),
        None if signal.volume_ratio_prior10 is None else float(signal.volume_ratio_prior10),
        ActionState.TECHNICAL_DETERIORATION_EXIT_REQUIRED.value,
        next_bar.date, float(next_bar.open),
        "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_WEEK",
        ACTION_VERSION,
    )


def validate_action(action: TechnicalDeteriorationAction) -> list[str]:
    findings: list[str] = []
    if action.action_version != ACTION_VERSION:
        findings.append("A40-A_VERSION_MISMATCH")
    if action.source_sell_risk_version != SOURCE_SELL_RISK_VERSION:
        findings.append("A40-A_SOURCE_37_MISMATCH")
    if action.source_daily_deterioration_version != SOURCE_DAILY_DETERIORATION_VERSION:
        findings.append("A40-A_SOURCE_38_MISMATCH")
    if action.source_weekly_evidence_version != SOURCE_WEEKLY_EVIDENCE_VERSION:
        findings.append("A40-A_SOURCE_39_MISMATCH")
    if action.action_state == ActionState.TECHNICAL_DETERIORATION_EXIT_REQUIRED.value:
        if action.signal_week_end is None or action.execution_date is None:
            findings.append("A40-G_MISSING_DATES")
        elif not action.execution_date > action.signal_week_end:
            findings.append("A40-G_NONCAUSAL_EXECUTION")
        if action.execution_price is None or action.execution_source != "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_WEEK":
            findings.append("A40-H_INVALID_EXECUTION")
        if action.signal_week_close is None or action.signal_week_ma10w is None or not action.signal_week_close < action.signal_week_ma10w:
            findings.append("A40-B_INVALID_PRICE_TRIGGER")
        if action.signal_week_volume_ratio_prior10 is None or not action.signal_week_volume_ratio_prior10 > 1.0:
            findings.append("A40-C_INVALID_VOLUME_TRIGGER")
    return findings
