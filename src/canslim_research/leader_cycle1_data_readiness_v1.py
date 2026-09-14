"""Pure readiness gate for #54 Cycle 1 candidate-leader validation."""
from __future__ import annotations

from dataclasses import dataclass

VERSION = "54-cycle1-data-readiness-v1"


@dataclass(frozen=True)
class DataReadinessInput:
    broad_membership_count: int
    ohlcv_security_count: int
    ohlcv_with_252_bars: int
    exact_symbol_overlap: int
    ohlcv_scope: str
    membership_pit_valid: bool
    benchmark_pit_valid: bool


@dataclass(frozen=True)
class DataReadinessResult:
    status: str
    reason: str
    selector_execution_authorized: bool
    overlap_coverage: float
    evaluable_coverage: float
    version: str = VERSION


def evaluate_cycle1_data_readiness(e: DataReadinessInput) -> DataReadinessResult:
    if e.broad_membership_count <= 0:
        return DataReadinessResult("NOT_EVALUABLE", "EMPTY_BROAD_MEMBERSHIP", False, 0.0, 0.0)
    overlap = e.exact_symbol_overlap / e.broad_membership_count
    evaluable = e.ohlcv_with_252_bars / e.broad_membership_count
    if not e.membership_pit_valid:
        return DataReadinessResult("NOT_EVALUABLE", "MEMBERSHIP_PIT_INVALID", False, overlap, evaluable)
    if not e.benchmark_pit_valid:
        return DataReadinessResult("NOT_EVALUABLE", "BENCHMARK_PIT_INVALID", False, overlap, evaluable)
    if e.ohlcv_scope != "BROAD_MARKET_PIT":
        return DataReadinessResult(
            "BLOCKED_ON_BROAD_MARKET_OHLCV",
            "RESTRICTED_OR_NON_BROAD_OHLCV_CANNOT_DEFINE_BROAD_MARKET_RS_PERCENTILES",
            False,
            overlap,
            evaluable,
        )
    if e.ohlcv_with_252_bars <= 0:
        return DataReadinessResult("NOT_EVALUABLE", "NO_252_BAR_BROAD_MARKET_HISTORIES", False, overlap, evaluable)
    return DataReadinessResult("READY_FOR_PROSPECTIVE_SELECTOR", "PIT_BROAD_MARKET_INPUTS_AVAILABLE", True, overlap, evaluable)
