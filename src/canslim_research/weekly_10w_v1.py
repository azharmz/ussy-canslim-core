"""Completed-week aggregation and 10-week evidence layer v1."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional, Sequence

WEEKLY_10W_VERSION = "39-weekly-10w-evidence-v1"
SOURCE_TECHNICAL_DETERIORATION_VERSION = "38-technical-deterioration-evidence-v1"
HEAVY_VOLUME_RATIO = 1.40


class EvidenceState(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
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
class WeeklyBar:
    iso_year: int
    iso_week: int
    first_date: str
    last_date: str
    session_count: int
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float]


@dataclass(frozen=True)
class Weekly10wSnapshot:
    candidate_id: str
    security_id: str
    asof_date: str
    latest_completed_iso_year: Optional[int]
    latest_completed_iso_week: Optional[int]
    latest_completed_week_first_date: Optional[str]
    latest_completed_week_last_date: Optional[str]
    latest_completed_week_session_count: Optional[int]
    week_open: Optional[float]
    week_high: Optional[float]
    week_low: Optional[float]
    week_close: Optional[float]
    week_volume: Optional[float]
    completed_week_count: int
    ma10w: Optional[float]
    break_10w_state: str
    prior_completed_week_break_10w_state: str
    first_break_10w_observed_state: str
    week_volume_ratio_10: Optional[float]
    heavy_volume_break_10w_state: str
    weekly_aggregation_version: str
    source_technical_deterioration_version: str
    action_promotion_state: str


def _iso_key(d: str) -> tuple[int, int]:
    iso = date.fromisoformat(d).isocalendar()
    return iso.year, iso.week


def aggregate_completed_weeks(bars: Sequence[DailyBar]) -> list[WeeklyBar]:
    if not bars:
        return []
    ordered = sorted(bars, key=lambda x: x.date)
    current_key = _iso_key(ordered[-1].date)
    grouped: dict[tuple[int, int], list[DailyBar]] = {}
    for bar in ordered:
        grouped.setdefault(_iso_key(bar.date), []).append(bar)

    completed: list[WeeklyBar] = []
    for key in sorted(grouped):
        if key == current_key:
            continue
        group = grouped[key]
        volumes = [x.volume for x in group]
        week_volume = None if any(v is None for v in volumes) else sum(float(v) for v in volumes)
        completed.append(
            WeeklyBar(
                iso_year=key[0],
                iso_week=key[1],
                first_date=group[0].date,
                last_date=group[-1].date,
                session_count=len(group),
                open=float(group[0].open),
                high=max(float(x.high) for x in group),
                low=min(float(x.low) for x in group),
                close=float(group[-1].close),
                volume=week_volume,
            )
        )
    return completed


def _ma10w(weeks: Sequence[WeeklyBar]) -> Optional[float]:
    if len(weeks) < 10:
        return None
    return sum(w.close for w in weeks[-10:]) / 10.0


def _break_state(weeks: Sequence[WeeklyBar]) -> EvidenceState:
    ma = _ma10w(weeks)
    if ma is None:
        return EvidenceState.NOT_EVALUABLE
    return EvidenceState.TRUE if weeks[-1].close < ma else EvidenceState.FALSE


def _weekly_volume_ratio(weeks: Sequence[WeeklyBar]) -> Optional[float]:
    if len(weeks) < 11:
        return None
    current = weeks[-1]
    prior = weeks[-11:-1]
    if current.volume is None or any(w.volume is None for w in prior):
        return None
    denom = sum(float(w.volume) for w in prior) / 10.0
    if denom <= 0:
        return None
    return float(current.volume) / denom


def evaluate_weekly_10w(
    *,
    candidate_id: str,
    security_id: str,
    bars_through_asof: Sequence[DailyBar],
    source_technical_deterioration_version: str = SOURCE_TECHNICAL_DETERIORATION_VERSION,
) -> Weekly10wSnapshot:
    if not bars_through_asof:
        raise ValueError("bars_through_asof must not be empty")
    ordered = sorted(bars_through_asof, key=lambda x: x.date)
    weeks = aggregate_completed_weeks(ordered)

    latest = weeks[-1] if weeks else None
    current_break = _break_state(weeks)
    prior_break = _break_state(weeks[:-1]) if len(weeks) >= 2 else EvidenceState.NOT_EVALUABLE
    if current_break is EvidenceState.NOT_EVALUABLE or prior_break is EvidenceState.NOT_EVALUABLE:
        first_break = EvidenceState.NOT_EVALUABLE
    else:
        first_break = EvidenceState.TRUE if (current_break is EvidenceState.TRUE and prior_break is EvidenceState.FALSE) else EvidenceState.FALSE

    ratio = _weekly_volume_ratio(weeks)
    if current_break is EvidenceState.NOT_EVALUABLE or ratio is None:
        heavy = EvidenceState.NOT_EVALUABLE
    else:
        heavy = EvidenceState.TRUE if (current_break is EvidenceState.TRUE and ratio >= HEAVY_VOLUME_RATIO) else EvidenceState.FALSE

    return Weekly10wSnapshot(
        candidate_id=candidate_id,
        security_id=security_id,
        asof_date=ordered[-1].date,
        latest_completed_iso_year=None if latest is None else latest.iso_year,
        latest_completed_iso_week=None if latest is None else latest.iso_week,
        latest_completed_week_first_date=None if latest is None else latest.first_date,
        latest_completed_week_last_date=None if latest is None else latest.last_date,
        latest_completed_week_session_count=None if latest is None else latest.session_count,
        week_open=None if latest is None else latest.open,
        week_high=None if latest is None else latest.high,
        week_low=None if latest is None else latest.low,
        week_close=None if latest is None else latest.close,
        week_volume=None if latest is None else latest.volume,
        completed_week_count=len(weeks),
        ma10w=_ma10w(weeks),
        break_10w_state=current_break.value,
        prior_completed_week_break_10w_state=prior_break.value,
        first_break_10w_observed_state=first_break.value,
        week_volume_ratio_10=ratio,
        heavy_volume_break_10w_state=heavy.value,
        weekly_aggregation_version=WEEKLY_10W_VERSION,
        source_technical_deterioration_version=source_technical_deterioration_version,
        action_promotion_state="EVIDENCE_ONLY_NO_CANONICAL_SELL_ACTION",
    )


def validate_weekly_10w(snapshot: Weekly10wSnapshot) -> list[str]:
    findings: list[str] = []
    if snapshot.weekly_aggregation_version != WEEKLY_10W_VERSION:
        findings.append("W39-A_VERSION_MISMATCH")
    if snapshot.source_technical_deterioration_version != SOURCE_TECHNICAL_DETERIORATION_VERSION:
        findings.append("W39-A_SOURCE_VERSION_MISMATCH")
    if snapshot.action_promotion_state != "EVIDENCE_ONLY_NO_CANONICAL_SELL_ACTION":
        findings.append("W39-K_UNAUTHORIZED_ACTION_PROMOTION")
    if snapshot.break_10w_state == EvidenceState.TRUE.value and snapshot.ma10w is not None and snapshot.week_close is not None:
        if not snapshot.week_close < snapshot.ma10w:
            findings.append("W39-F_BREAK_BOUNDARY_INVALID")
    return findings
