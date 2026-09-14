"""Point-in-time general-market state classification v1."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Sequence

VERSION = "46-market-state-classification-v1"
FTD_MIN_GAIN_PCT = 1.25
DISTRIBUTION_MAX_RETURN_PCT = -0.20


class MarketState(str, Enum):
    CORRECTION = "CORRECTION"
    RALLY_ATTEMPT = "RALLY_ATTEMPT"
    FOLLOW_THROUGH_CONFIRMED = "FOLLOW_THROUGH_CONFIRMED"
    UPTREND_HEALTHY = "UPTREND_HEALTHY"
    UPTREND_WEAKENING = "UPTREND_WEAKENING"
    NOT_EVALUABLE = "NOT_EVALUABLE"


@dataclass(frozen=True)
class IndexBar:
    date: str
    low: float
    close: float
    volume: Optional[float]


@dataclass(frozen=True)
class IndexEvidence:
    index_id: str
    asof_date: str
    rally_day: Optional[int]
    rally_day1_low: Optional[float]
    follow_through_today: Optional[bool]
    distribution_today: Optional[bool]
    attempt_intact: Optional[bool]


@dataclass(frozen=True)
class MarketClassification:
    asof_date: str
    state: str
    index_evidence: tuple[IndexEvidence, ...]
    leadership_confirming: Optional[bool]
    weakening_confirmed: Optional[bool]
    reason: str
    version: str = VERSION


def _pct_change(current: float, previous: float) -> float:
    return (current / previous - 1.0) * 100.0


def classify_index(index_id: str, bars: Sequence[IndexBar]) -> IndexEvidence:
    if len(bars) < 2:
        date = bars[-1].date if bars else ""
        return IndexEvidence(index_id, date, None, None, None, None, None)

    day1_idx: Optional[int] = None
    day1_low: Optional[float] = None
    for i in range(1, len(bars)):
        b, prev = bars[i], bars[i - 1]
        if day1_idx is None:
            if b.close > prev.close:
                day1_idx, day1_low = i, b.low
            continue
        if b.low < day1_low:  # strict undercut resets the attempt
            day1_idx = None
            day1_low = None
            if b.close > prev.close:
                day1_idx, day1_low = i, b.low

    b, prev = bars[-1], bars[-2]
    distribution: Optional[bool]
    if b.volume is None or prev.volume is None:
        distribution = None
    else:
        distribution = _pct_change(b.close, prev.close) <= DISTRIBUTION_MAX_RETURN_PCT and b.volume > prev.volume

    if day1_idx is None:
        return IndexEvidence(index_id, b.date, None, None, False, distribution, False)

    rally_day = len(bars) - day1_idx
    # Day 1 itself counts as 1, hence index distance + 1.
    rally_day += 1
    ftd: Optional[bool]
    if b.volume is None or prev.volume is None:
        ftd = None if rally_day >= 4 else False
    else:
        ftd = (
            rally_day >= 4
            and _pct_change(b.close, prev.close) >= FTD_MIN_GAIN_PCT
            and b.volume > prev.volume
        )
    return IndexEvidence(index_id, b.date, rally_day, day1_low, ftd, distribution, True)


def classify_market(
    *,
    index_series: dict[str, Sequence[IndexBar]],
    prior_state: str,
    leadership_confirming: Optional[bool] = None,
    weakening_confirmed: Optional[bool] = None,
    correction_reset: bool = False,
) -> MarketClassification:
    evidences = tuple(classify_index(k, v) for k, v in sorted(index_series.items()))
    dates = [e.asof_date for e in evidences if e.asof_date]
    asof = max(dates) if dates else ""
    evaluable = [e for e in evidences if e.attempt_intact is not None]
    if not evaluable:
        return MarketClassification(asof, MarketState.NOT_EVALUABLE.value, evidences,
                                    leadership_confirming, weakening_confirmed,
                                    "NO_EVALUABLE_MAJOR_INDEX")

    if correction_reset:
        return MarketClassification(asof, MarketState.CORRECTION.value, evidences,
                                    leadership_confirming, weakening_confirmed,
                                    "EXPLICIT_CORRECTION_RESET")

    if weakening_confirmed is True and prior_state in {
        MarketState.FOLLOW_THROUGH_CONFIRMED.value,
        MarketState.UPTREND_HEALTHY.value,
        MarketState.UPTREND_WEAKENING.value,
    }:
        return MarketClassification(asof, MarketState.UPTREND_WEAKENING.value, evidences,
                                    leadership_confirming, weakening_confirmed,
                                    "EXPLICIT_WEAKENING_EVIDENCE")

    if any(e.follow_through_today is True for e in evaluable):
        return MarketClassification(asof, MarketState.FOLLOW_THROUGH_CONFIRMED.value, evidences,
                                    leadership_confirming, weakening_confirmed,
                                    "VALID_DAY4_PLUS_FOLLOW_THROUGH")

    if prior_state == MarketState.FOLLOW_THROUGH_CONFIRMED.value and leadership_confirming is True:
        return MarketClassification(asof, MarketState.UPTREND_HEALTHY.value, evidences,
                                    leadership_confirming, weakening_confirmed,
                                    "LEADERSHIP_CONFIRMS_FOLLOW_THROUGH")

    if prior_state in {MarketState.UPTREND_HEALTHY.value, MarketState.UPTREND_WEAKENING.value,
                       MarketState.FOLLOW_THROUGH_CONFIRMED.value}:
        return MarketClassification(asof, prior_state, evidences,
                                    leadership_confirming, weakening_confirmed,
                                    "NO_NEW_STATE_CHANGING_EVIDENCE")

    intact = [e for e in evaluable if e.attempt_intact is True]
    if intact:
        return MarketClassification(asof, MarketState.RALLY_ATTEMPT.value, evidences,
                                    leadership_confirming, weakening_confirmed,
                                    "MAJOR_INDEX_RALLY_ATTEMPT_INTACT")
    return MarketClassification(asof, MarketState.CORRECTION.value, evidences,
                                leadership_confirming, weakening_confirmed,
                                "NO_INTACT_RALLY_ATTEMPT")
