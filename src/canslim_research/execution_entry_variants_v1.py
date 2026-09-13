"""Preregistered #36 causal entry-timing research variants.

This module is downstream research only. It does not modify the frozen
36-execution-entry-v1 baseline or upstream #33/#34/#35 semantics.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

BUY_ZONE_MAX = 0.05
RETEST_NEAR_PIVOT_MAX = 0.02
MAX_DELAY = 3


@dataclass(frozen=True)
class VariantDecision:
    variant: str
    executed: bool
    reason: str
    entry_offset: Optional[int]
    entry_price: Optional[float]
    confirmation_offset: Optional[int] = None


def _valid_open(pivot: float, price: float) -> bool:
    return pivot <= price <= pivot * (1.0 + BUY_ZONE_MAX)


def r0_t1_baseline(*, pivot: float, opens: Sequence[float]) -> VariantDecision:
    if not opens:
        return VariantDecision("E36-R0", False, "NO_T1_BAR", None, None)
    price = float(opens[0])
    if price < pivot:
        return VariantDecision("E36-R0", False, "T1_BELOW_PIVOT", None, None)
    if price > pivot * (1.0 + BUY_ZONE_MAX):
        return VariantDecision("E36-R0", False, "T1_ABOVE_BUY_ZONE", None, None)
    return VariantDecision("E36-R0", True, "T1_OPEN", 1, price)


def r1_first_valid_open(*, pivot: float, opens: Sequence[float]) -> VariantDecision:
    for offset, raw in enumerate(opens[:MAX_DELAY], start=1):
        price = float(raw)
        if _valid_open(pivot, price):
            return VariantDecision("E36-R1", True, "FIRST_VALID_OPEN", offset, price)
    return VariantDecision("E36-R1", False, "NO_VALID_OPEN_T1_T3", None, None)


def r2_full_pivot_hold(
    *, pivot: float, opens: Sequence[float], lows: Sequence[float], closes: Sequence[float]
) -> VariantDecision:
    max_confirm = min(2, len(lows), len(closes))
    for i in range(max_confirm):
        confirm_offset = i + 1
        low = float(lows[i])
        close = float(closes[i])
        if low > pivot and pivot < close <= pivot * (1.0 + BUY_ZONE_MAX):
            entry_offset = confirm_offset + 1
            entry_index = i + 1
            if entry_offset <= MAX_DELAY and entry_index < len(opens):
                price = float(opens[entry_index])
                if _valid_open(pivot, price):
                    return VariantDecision(
                        "E36-R2", True, "PIVOT_HOLD_THEN_NEXT_OPEN",
                        entry_offset, price, confirm_offset
                    )
            return VariantDecision(
                "E36-R2", False, "HOLD_CONFIRMED_NEXT_OPEN_INVALID",
                None, None, confirm_offset
            )
    return VariantDecision("E36-R2", False, "NO_PIVOT_HOLD_CONFIRMATION", None, None)


def r3_retest_reclaim_proxy(
    *, pivot: float, opens: Sequence[float], lows: Sequence[float], closes: Sequence[float]
) -> VariantDecision:
    max_confirm = min(2, len(lows), len(closes))
    for i in range(max_confirm):
        confirm_offset = i + 1
        low = float(lows[i])
        close = float(closes[i])
        near_pivot = low <= pivot * (1.0 + RETEST_NEAR_PIVOT_MAX)
        reclaimed = pivot < close <= pivot * (1.0 + BUY_ZONE_MAX)
        if near_pivot and reclaimed:
            entry_offset = confirm_offset + 1
            entry_index = i + 1
            if entry_offset <= MAX_DELAY and entry_index < len(opens):
                price = float(opens[entry_index])
                if _valid_open(pivot, price):
                    return VariantDecision(
                        "E36-R3", True, "RETEST_RECLAIM_THEN_NEXT_OPEN",
                        entry_offset, price, confirm_offset
                    )
            return VariantDecision(
                "E36-R3", False, "RETEST_CONFIRMED_NEXT_OPEN_INVALID",
                None, None, confirm_offset
            )
    return VariantDecision("E36-R3", False, "NO_RETEST_RECLAIM_CONFIRMATION", None, None)
