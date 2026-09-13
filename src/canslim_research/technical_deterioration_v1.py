"""Theory-faithful technical-deterioration evidence layer v1.

Evidence only: this module does not promote a new canonical sell action.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Sequence

TECHNICAL_DETERIORATION_VERSION = "38-technical-deterioration-evidence-v1"
SOURCE_SELL_RISK_VERSION = "37-sell-risk-v1"
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
class TechnicalDeteriorationSnapshot:
    candidate_id: str
    security_id: str
    breakout_date: str
    entry_date: str
    fill_price: float
    pivot_level: float
    asof_date: str
    close: float
    volume: Optional[float]
    ma10: Optional[float]
    ma21: Optional[float]
    ma50: Optional[float]
    break_10d_state: str
    break_21d_state: str
    break_50d_state: str
    break_10w_state: str
    volume_ratio_50: Optional[float]
    heavy_volume_break_10d_state: str
    heavy_volume_break_21d_state: str
    heavy_volume_break_50d_state: str
    down_session: Optional[bool]
    largest_down_volume_since_breakout: Optional[bool]
    down_session_observation_count: int
    fell_back_below_pivot: bool
    loss_from_fill_pct: float
    technical_deterioration_version: str
    source_sell_risk_version: str
    action_promotion_state: str


def _ma(bars: Sequence[DailyBar], window: int) -> Optional[float]:
    if len(bars) < window:
        return None
    return sum(float(x.close) for x in bars[-window:]) / window


def _break_state(close: float, ma: Optional[float]) -> EvidenceState:
    if ma is None:
        return EvidenceState.NOT_EVALUABLE
    return EvidenceState.TRUE if close < ma else EvidenceState.FALSE


def _volume_ratio_prior50(bars: Sequence[DailyBar]) -> Optional[float]:
    if len(bars) < 51:
        return None
    current = bars[-1]
    prior = bars[-51:-1]
    if current.volume is None or any(x.volume is None for x in prior):
        return None
    denom = sum(float(x.volume) for x in prior) / 50.0
    if denom <= 0:
        return None
    return float(current.volume) / denom


def _heavy_state(break_state: EvidenceState, ratio: Optional[float]) -> EvidenceState:
    if break_state is EvidenceState.NOT_EVALUABLE or ratio is None:
        return EvidenceState.NOT_EVALUABLE
    return EvidenceState.TRUE if (break_state is EvidenceState.TRUE and ratio >= HEAVY_VOLUME_RATIO) else EvidenceState.FALSE


def _down_volume_state(bars: Sequence[DailyBar]) -> tuple[Optional[bool], Optional[bool], int]:
    if len(bars) < 2:
        return None, None, 0
    current = bars[-1]
    prior_close = float(bars[-2].close)
    down = float(current.close) < prior_close
    prior_down_volumes: list[float] = []
    for i in range(1, len(bars) - 1):
        bar = bars[i]
        if float(bar.close) < float(bars[i - 1].close) and bar.volume is not None:
            prior_down_volumes.append(float(bar.volume))
    observation_count = len(prior_down_volumes) + (1 if down and current.volume is not None else 0)
    if not down:
        return False, False, observation_count
    if current.volume is None:
        return True, None, observation_count
    if not prior_down_volumes:
        return True, True, observation_count
    return True, float(current.volume) >= max(prior_down_volumes), observation_count


def evaluate_technical_deterioration(
    *,
    candidate_id: str,
    security_id: str,
    breakout_date: str,
    entry_date: str,
    fill_price: float,
    pivot_level: float,
    bars_through_asof: Sequence[DailyBar],
    source_sell_risk_version: str = SOURCE_SELL_RISK_VERSION,
) -> TechnicalDeteriorationSnapshot:
    if fill_price <= 0 or pivot_level <= 0:
        raise ValueError("fill_price and pivot_level must be positive")
    if not bars_through_asof:
        raise ValueError("bars_through_asof must not be empty")

    current = bars_through_asof[-1]
    ma10 = _ma(bars_through_asof, 10)
    ma21 = _ma(bars_through_asof, 21)
    ma50 = _ma(bars_through_asof, 50)
    b10 = _break_state(float(current.close), ma10)
    b21 = _break_state(float(current.close), ma21)
    b50 = _break_state(float(current.close), ma50)
    ratio = _volume_ratio_prior50(bars_through_asof)
    down, largest_down, down_count = _down_volume_state(bars_through_asof)

    return TechnicalDeteriorationSnapshot(
        candidate_id=candidate_id,
        security_id=security_id,
        breakout_date=breakout_date,
        entry_date=entry_date,
        fill_price=float(fill_price),
        pivot_level=float(pivot_level),
        asof_date=current.date,
        close=float(current.close),
        volume=None if current.volume is None else float(current.volume),
        ma10=ma10,
        ma21=ma21,
        ma50=ma50,
        break_10d_state=b10.value,
        break_21d_state=b21.value,
        break_50d_state=b50.value,
        break_10w_state="NOT_IMPLEMENTED_REQUIRES_WEEKLY_AGGREGATION_SPEC",
        volume_ratio_50=ratio,
        heavy_volume_break_10d_state=_heavy_state(b10, ratio).value,
        heavy_volume_break_21d_state=_heavy_state(b21, ratio).value,
        heavy_volume_break_50d_state=_heavy_state(b50, ratio).value,
        down_session=down,
        largest_down_volume_since_breakout=largest_down,
        down_session_observation_count=down_count,
        fell_back_below_pivot=float(current.close) < pivot_level,
        loss_from_fill_pct=float(current.close) / fill_price - 1.0,
        technical_deterioration_version=TECHNICAL_DETERIORATION_VERSION,
        source_sell_risk_version=source_sell_risk_version,
        action_promotion_state="EVIDENCE_ONLY_NO_CANONICAL_SELL_ACTION",
    )


def validate_technical_deterioration(snapshot: TechnicalDeteriorationSnapshot) -> list[str]:
    findings: list[str] = []
    if snapshot.technical_deterioration_version != TECHNICAL_DETERIORATION_VERSION:
        findings.append("T38-A_VERSION_MISMATCH")
    if snapshot.source_sell_risk_version != SOURCE_SELL_RISK_VERSION:
        findings.append("T38-A_SOURCE_VERSION_MISMATCH")
    if snapshot.break_10w_state != "NOT_IMPLEMENTED_REQUIRES_WEEKLY_AGGREGATION_SPEC":
        findings.append("T38-I_WEEKLY_BOUNDARY_VIOLATION")
    if snapshot.action_promotion_state != "EVIDENCE_ONLY_NO_CANONICAL_SELL_ACTION":
        findings.append("T38-J_UNAUTHORIZED_ACTION_PROMOTION")
    if snapshot.break_10d_state == EvidenceState.TRUE.value and snapshot.ma10 is not None and not snapshot.close < snapshot.ma10:
        findings.append("T38-C_10D_BREAK_BOUNDARY_INVALID")
    if snapshot.break_21d_state == EvidenceState.TRUE.value and snapshot.ma21 is not None and not snapshot.close < snapshot.ma21:
        findings.append("T38-C_21D_BREAK_BOUNDARY_INVALID")
    if snapshot.break_50d_state == EvidenceState.TRUE.value and snapshot.ma50 is not None and not snapshot.close < snapshot.ma50:
        findings.append("T38-C_50D_BREAK_BOUNDARY_INVALID")
    return findings
