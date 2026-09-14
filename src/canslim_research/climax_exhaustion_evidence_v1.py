"""Canonical climax/exhaustion evidence layer v1."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Sequence

EVIDENCE_VERSION = "44-climax-exhaustion-evidence-v1"

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
    week_end: str
    high: float
    low: float

@dataclass(frozen=True)
class ClimaxEvidence:
    candidate_id: str
    security_id: str
    breakout_date: str
    asof_date: str
    completed_sessions_since_breakout: int
    daily_point_change: Optional[float]
    is_up_day: Optional[bool]
    largest_up_day_point_gain_since_breakout: Optional[bool]
    heaviest_daily_volume_since_breakout: Optional[bool]
    up_days_last_8: Optional[int]
    up_days_last_10: Optional[int]
    seven_of_eight_up_days: Optional[bool]
    eight_of_ten_up_days: Optional[bool]
    exhaustion_gap_raw: Optional[bool]
    completed_weeks_since_breakout: int
    weekly_range: Optional[float]
    largest_weekly_range_since_breakout: Optional[bool]
    prior_advance_context_state: str
    promotion_state: str
    evidence_version: str


def evaluate_climax_exhaustion_evidence(*, candidate_id: str, security_id: str, breakout_date: str, daily_bars: Sequence[DailyBar], weekly_bars: Sequence[WeeklyBar] = ()) -> ClimaxEvidence:
    bars = sorted((b for b in daily_bars if b.date >= breakout_date), key=lambda b: b.date)
    if not bars:
        raise ValueError("daily_bars must include at least one bar on/after breakout_date")
    cur = bars[-1]
    prior = bars[-2] if len(bars) >= 2 else None
    point_change = None if prior is None else float(cur.close) - float(prior.close)
    is_up = None if point_change is None else point_change > 0
    prior_up_changes = []
    for i in range(1, len(bars)-1):
        change = float(bars[i].close) - float(bars[i-1].close)
        if change > 0:
            prior_up_changes.append(change)
    largest_up = None if point_change is None else (False if point_change <= 0 else all(point_change > x for x in prior_up_changes))
    if cur.volume is None:
        heaviest = None
    else:
        prior_vols = [float(b.volume) for b in bars[:-1] if b.volume is not None]
        heaviest = all(float(cur.volume) > v for v in prior_vols)
    up_flags = [float(bars[i].close) > float(bars[i-1].close) for i in range(1, len(bars))]
    up8 = sum(up_flags[-8:]) if len(up_flags) >= 8 else None
    up10 = sum(up_flags[-10:]) if len(up_flags) >= 10 else None
    gap = None if prior is None else float(cur.low) > float(prior.high)
    weeks = sorted((w for w in weekly_bars if w.week_end >= breakout_date), key=lambda w: w.week_end)
    if weeks:
        wr = float(weeks[-1].high) - float(weeks[-1].low)
        prior_ranges = [float(w.high)-float(w.low) for w in weeks[:-1]]
        largest_wr = all(wr > x for x in prior_ranges)
    else:
        wr = None
        largest_wr = None
    return ClimaxEvidence(candidate_id, security_id, breakout_date, cur.date, len(bars), point_change, is_up, largest_up, heaviest, up8, up10, None if up8 is None else up8 >= 7, None if up10 is None else up10 >= 8, gap, len(weeks), wr, largest_wr, "CONTEXT_RECORDED_NOT_ACTIONABLE", "EVIDENCE_ONLY", EVIDENCE_VERSION)


def validate_climax_exhaustion_evidence(x: ClimaxEvidence) -> list[str]:
    findings = []
    if x.evidence_version != EVIDENCE_VERSION:
        findings.append("C44-A_VERSION_MISMATCH")
    if x.promotion_state != "EVIDENCE_ONLY":
        findings.append("C44-I_UNAUTHORIZED_PROMOTION")
    if x.prior_advance_context_state != "CONTEXT_RECORDED_NOT_ACTIONABLE":
        findings.append("C44-J_CONTEXT_PROMOTION")
    if x.up_days_last_8 is None and x.seven_of_eight_up_days is not None:
        findings.append("C44-H_INVALID_8DAY_HISTORY")
    if x.up_days_last_10 is None and x.eight_of_ten_up_days is not None:
        findings.append("C44-H_INVALID_10DAY_HISTORY")
    return findings
