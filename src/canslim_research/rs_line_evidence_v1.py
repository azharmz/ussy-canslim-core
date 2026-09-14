"""Minimum reproducible CAN SLIM RS-line evidence vs canonical S&P 500.

Evidence-only. This module does not reproduce IBD RS Rating and does not emit
#51 leadership_confirming / weakening_confirmed booleans.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

VERSION = "54-rs-line-evidence-v1"
BENCHMARK_ID = "SP500"


@dataclass(frozen=True, slots=True)
class RSLineObservation:
    session_date: str
    stock_price: float
    benchmark_price: float


@dataclass(frozen=True, slots=True)
class RSLineEvidenceResult:
    asof_date: str
    state: str
    latest_rs_line: float | None
    previous_rs_line: float | None
    direction_vs_prior: str | None
    at_input_window_high: bool | None
    new_input_window_high: bool | None
    observation_count: int
    benchmark_id: str
    input_window_id: str | None
    stock_source_provenance: str | None
    benchmark_source_provenance: str | None
    reason: str
    version: str = VERSION


def _not_evaluable(
    *,
    asof_date: str,
    observations: Sequence[RSLineObservation],
    benchmark_id: str,
    input_window_id: str | None,
    stock_source_provenance: str | None,
    benchmark_source_provenance: str | None,
    reason: str,
) -> RSLineEvidenceResult:
    return RSLineEvidenceResult(
        asof_date=asof_date,
        state="NOT_EVALUABLE",
        latest_rs_line=None,
        previous_rs_line=None,
        direction_vs_prior=None,
        at_input_window_high=None,
        new_input_window_high=None,
        observation_count=len(observations),
        benchmark_id=benchmark_id,
        input_window_id=input_window_id,
        stock_source_provenance=stock_source_provenance,
        benchmark_source_provenance=benchmark_source_provenance,
        reason=reason,
    )


def evaluate_rs_line(
    observations: Sequence[RSLineObservation],
    *,
    asof_date: str,
    benchmark_id: str = BENCHMARK_ID,
    input_window_id: str | None,
    stock_source_provenance: str | None,
    benchmark_source_provenance: str | None,
) -> RSLineEvidenceResult:
    """Evaluate aligned PIT stock/S&P-500 relative-strength line evidence."""
    if benchmark_id != BENCHMARK_ID:
        return _not_evaluable(
            asof_date=asof_date,
            observations=observations,
            benchmark_id=benchmark_id,
            input_window_id=input_window_id,
            stock_source_provenance=stock_source_provenance,
            benchmark_source_provenance=benchmark_source_provenance,
            reason="NONCANONICAL_BENCHMARK",
        )
    if not input_window_id:
        return _not_evaluable(
            asof_date=asof_date,
            observations=observations,
            benchmark_id=benchmark_id,
            input_window_id=input_window_id,
            stock_source_provenance=stock_source_provenance,
            benchmark_source_provenance=benchmark_source_provenance,
            reason="INPUT_WINDOW_ID_MISSING",
        )
    if not stock_source_provenance or not benchmark_source_provenance:
        return _not_evaluable(
            asof_date=asof_date,
            observations=observations,
            benchmark_id=benchmark_id,
            input_window_id=input_window_id,
            stock_source_provenance=stock_source_provenance,
            benchmark_source_provenance=benchmark_source_provenance,
            reason="SOURCE_PROVENANCE_MISSING",
        )
    if len(observations) < 2:
        return _not_evaluable(
            asof_date=asof_date,
            observations=observations,
            benchmark_id=benchmark_id,
            input_window_id=input_window_id,
            stock_source_provenance=stock_source_provenance,
            benchmark_source_provenance=benchmark_source_provenance,
            reason="INSUFFICIENT_ALIGNED_OBSERVATIONS",
        )

    dates = [row.session_date for row in observations]
    if len(set(dates)) != len(dates):
        reason = "DUPLICATE_SESSION_DATE"
    elif dates != sorted(dates):
        reason = "NONMONOTONIC_SESSION_DATES"
    elif dates[-1] != asof_date:
        reason = "ASOF_DATE_NOT_FINAL_OBSERVATION"
    else:
        reason = ""
    if reason:
        return _not_evaluable(
            asof_date=asof_date,
            observations=observations,
            benchmark_id=benchmark_id,
            input_window_id=input_window_id,
            stock_source_provenance=stock_source_provenance,
            benchmark_source_provenance=benchmark_source_provenance,
            reason=reason,
        )

    rs_values: list[float] = []
    for row in observations:
        stock = float(row.stock_price)
        benchmark = float(row.benchmark_price)
        if not isfinite(stock) or not isfinite(benchmark) or stock <= 0 or benchmark <= 0:
            return _not_evaluable(
                asof_date=asof_date,
                observations=observations,
                benchmark_id=benchmark_id,
                input_window_id=input_window_id,
                stock_source_provenance=stock_source_provenance,
                benchmark_source_provenance=benchmark_source_provenance,
                reason="INVALID_NONPOSITIVE_OR_NONFINITE_PRICE",
            )
        rs_values.append(stock / benchmark)

    latest = rs_values[-1]
    previous = rs_values[-2]
    if latest > previous:
        direction = "RISING"
    elif latest < previous:
        direction = "FALLING"
    else:
        direction = "FLAT"

    prior_max = max(rs_values[:-1])
    return RSLineEvidenceResult(
        asof_date=asof_date,
        state="EVALUABLE",
        latest_rs_line=latest,
        previous_rs_line=previous,
        direction_vs_prior=direction,
        at_input_window_high=latest >= prior_max,
        new_input_window_high=latest > prior_max,
        observation_count=len(observations),
        benchmark_id=benchmark_id,
        input_window_id=input_window_id,
        stock_source_provenance=stock_source_provenance,
        benchmark_source_provenance=benchmark_source_provenance,
        reason="RS_LINE_EVALUATED",
    )
