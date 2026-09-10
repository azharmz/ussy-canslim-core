"""Independent CAN SLIM execution/exit baseline v1.

Frozen before trading-performance testing. No TrendFoll ATR/EMA/time-stop rules.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

BUY_ZONE_MAX = 0.05
HARD_STOP_LOSS = 0.07
PROFIT_TARGET_FROM_PIVOT = 0.20


@dataclass(frozen=True)
class EntryDecision:
    accepted: bool
    reason: str
    entry_price: Optional[float]
    hard_stop: Optional[float]
    profit_target: Optional[float]


@dataclass(frozen=True)
class ExitDecision:
    exited: bool
    reason: str
    exit_price: Optional[float]


def entry_decision(*, pivot: Optional[float], h1_open: Optional[float]) -> EntryDecision:
    if pivot is None or h1_open is None or pivot <= 0 or h1_open <= 0:
        return EntryDecision(False, "ENTRY_INPUT_MISSING_OR_INVALID", None, None, None)
    if h1_open <= pivot:
        return EntryDecision(False, "BELOW_PIVOT_AT_FILL", None, None, None)
    if h1_open > pivot * (1.0 + BUY_ZONE_MAX):
        return EntryDecision(False, "ABOVE_BUY_ZONE_AT_FILL", None, None, None)
    entry = float(h1_open)
    return EntryDecision(
        True,
        "ENTRY_ACCEPTED_V1",
        entry,
        entry * (1.0 - HARD_STOP_LOSS),
        float(pivot) * (1.0 + PROFIT_TARGET_FROM_PIVOT),
    )


def resolve_bar_exit(
    *,
    open_price: float,
    high: float,
    low: float,
    hard_stop: float,
    profit_target: float,
) -> ExitDecision:
    """Resolve one daily bar conservatively.

    Gap-through prices use the open. If both stop and target are touched intraday,
    stop-first is assumed because OHLC does not reveal sequence.
    """
    if open_price <= hard_stop:
        return ExitDecision(True, "STOP_GAP_THROUGH", float(open_price))
    if open_price >= profit_target:
        return ExitDecision(True, "TARGET_GAP_THROUGH", float(open_price))
    if low <= hard_stop:
        return ExitDecision(True, "HARD_STOP_7PCT", float(hard_stop))
    if high >= profit_target:
        return ExitDecision(True, "PROFIT_TARGET_20PCT_FROM_PIVOT", float(profit_target))
    return ExitDecision(False, "HOLD", None)
