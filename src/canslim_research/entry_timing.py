"""Pre-specified causal entry-timing variants for CAN SLIM daily-EOD research.

These rules compare how a T0 EOD breakout signal is translated into an
executable fill. They are not claims about literal discretionary O'Neil
execution. Every fill occurs only after the information needed for that rule
was available.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

BUY_ZONE_MAX = 0.05
RETEST_NEAR_PIVOT_MAX = 0.02
MAX_ENTRY_DELAY = 3


@dataclass(frozen=True)
class TimingDecision:
    accepted: bool
    reason: str
    entry_offset: Optional[int]
    entry_price: Optional[float]
    confirmation_offset: Optional[int] = None


def _valid_open(pivot: float, price: float) -> bool:
    return pivot < price <= pivot * (1.0 + BUY_ZONE_MAX)


def x1_immediate(*, pivot: float, opens: Sequence[float]) -> TimingDecision:
    """Enter T+1 open if still inside the 0-5% buy zone."""
    if len(opens) < 1:
        return TimingDecision(False, "NO_T1_BAR", None, None)
    price = float(opens[0])
    if price <= pivot:
        return TimingDecision(False, "T1_AT_OR_BELOW_PIVOT", None, None)
    if price > pivot * (1.0 + BUY_ZONE_MAX):
        return TimingDecision(False, "T1_ABOVE_BUY_ZONE", None, None)
    return TimingDecision(True, "X1_T1_OPEN", 1, price)


def x2_first_valid(*, pivot: float, opens: Sequence[float]) -> TimingDecision:
    """Take the first valid open from T+1 through T+3."""
    for offset, raw in enumerate(opens[:MAX_ENTRY_DELAY], start=1):
        price = float(raw)
        if _valid_open(pivot, price):
            return TimingDecision(True, "X2_FIRST_VALID_OPEN", offset, price)
    return TimingDecision(False, "NO_VALID_OPEN_T1_T3", None, None)


def x3_pivot_hold(
    *, pivot: float, opens: Sequence[float], lows: Sequence[float], closes: Sequence[float]
) -> TimingDecision:
    """Require a full daily hold above pivot, then enter next open by T+3.

    Confirmation may occur on T+1 or T+2. A hold requires the entire daily bar
    to stay above pivot (low > pivot), with the close still no more than 5%
    above pivot. The confirmation day's close is only known after that close,
    so entry is at the following open.
    """
    max_confirm = min(2, len(closes), len(lows))
    for i in range(max_confirm):
        confirm_offset = i + 1
        if float(lows[i]) > pivot and pivot < float(closes[i]) <= pivot * (1.0 + BUY_ZONE_MAX):
            entry_index = i + 1
            entry_offset = confirm_offset + 1
            if entry_offset <= MAX_ENTRY_DELAY and entry_index < len(opens):
                price = float(opens[entry_index])
                if _valid_open(pivot, price):
                    return TimingDecision(True, "X3_PIVOT_HOLD", entry_offset, price, confirm_offset)
            return TimingDecision(False, "HOLD_CONFIRMED_BUT_NEXT_OPEN_INVALID", None, None, confirm_offset)
    return TimingDecision(False, "NO_PIVOT_HOLD_CONFIRMATION", None, None)


def x4_retest_hold(
    *, pivot: float, opens: Sequence[float], lows: Sequence[float], closes: Sequence[float]
) -> TimingDecision:
    """Require a near-pivot retest and close back above pivot, then enter next open.

    Quantitative proxy: on T+1 or T+2 the session low reaches within +2% of the
    pivot (or below it), while the close finishes above pivot and no more than
    5% above pivot. Entry occurs only at the next open and must itself remain
    inside the buy zone. The +2% retest band is pre-specified for this basis
    test and must not be tuned from the result.
    """
    max_confirm = min(2, len(closes), len(lows))
    for i in range(max_confirm):
        confirm_offset = i + 1
        near_pivot = float(lows[i]) <= pivot * (1.0 + RETEST_NEAR_PIVOT_MAX)
        close_holds = pivot < float(closes[i]) <= pivot * (1.0 + BUY_ZONE_MAX)
        if near_pivot and close_holds:
            entry_index = i + 1
            entry_offset = confirm_offset + 1
            if entry_offset <= MAX_ENTRY_DELAY and entry_index < len(opens):
                price = float(opens[entry_index])
                if _valid_open(pivot, price):
                    return TimingDecision(True, "X4_RETEST_HOLD", entry_offset, price, confirm_offset)
            return TimingDecision(False, "RETEST_CONFIRMED_BUT_NEXT_OPEN_INVALID", None, None, confirm_offset)
    return TimingDecision(False, "NO_RETEST_HOLD_CONFIRMATION", None, None)
