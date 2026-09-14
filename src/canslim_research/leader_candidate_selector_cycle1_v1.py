"""Research-only #54 Cycle 1 PIT candidate leader selector.

This module intentionally stops at candidate-cohort construction. It does not
emit #51 leadership_confirming / weakening_confirmed booleans.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

VERSION = "54-cycle1-candidate-leader-selector-v1"
RS_VERSION = "PROJECT_RS_PERCENTILE_252_V1"
WINDOW = 252
RS_THRESHOLD = 80.0
NEAR_HIGH_RATIO = 0.90
BENCHMARK_ID = "SP500"


class CandidateState(str, Enum):
    LEADER_CANDIDATE = "LEADER_CANDIDATE"
    NOT_LEADER_CANDIDATE = "NOT_LEADER_CANDIDATE"
    NOT_EVALUABLE = "NOT_EVALUABLE"


@dataclass(frozen=True)
class MembershipRecord:
    security_id: str
    symbol: str
    is_etf: bool = False
    is_test_issue: bool = False
    membership_pit_valid: bool = True


@dataclass(frozen=True)
class CandidateResult:
    security_id: str
    symbol: str
    state: str
    rs_percentile_252: float | None
    relative_return_252: float | None
    near_high_ratio_252: float | None
    reason: str
    version: str = VERSION
    rs_version: str = RS_VERSION
    benchmark_id: str = BENCHMARK_ID


def _window(values: Sequence[float]) -> tuple[float, ...] | None:
    if len(values) < WINDOW:
        return None
    latest = tuple(float(v) for v in values[-WINDOW:])
    if any(v <= 0 for v in latest):
        return None
    return latest


def _price_return(values: tuple[float, ...]) -> float:
    return values[-1] / values[0] - 1.0


def _percentile_upper_ecdf(value: float, population: Sequence[float]) -> float:
    if not population:
        raise ValueError("population must not be empty")
    return 100.0 * sum(v <= value for v in population) / len(population)


def select_candidate_cohort(
    membership: Sequence[MembershipRecord],
    adjusted_close_by_security: Mapping[str, Sequence[float]],
    benchmark_adjusted_close: Sequence[float],
) -> tuple[CandidateResult, ...]:
    """Evaluate one PIT cross-section using only supplied histories through T.

    Caller owns date alignment/provenance. This function refuses security types
    prohibited by the preregistration and preserves missing data explicitly.
    """
    benchmark = _window(benchmark_adjusted_close)
    if benchmark is None:
        return tuple(
            CandidateResult(
                row.security_id,
                row.symbol,
                CandidateState.NOT_EVALUABLE.value,
                None,
                None,
                None,
                "BENCHMARK_HISTORY_NOT_EVALUABLE",
            )
            for row in membership
        )

    benchmark_return = _price_return(benchmark)
    prepared: dict[str, tuple[float, float]] = {}
    exclusions: dict[str, str] = {}

    for row in membership:
        if not row.membership_pit_valid:
            exclusions[row.security_id] = "MEMBERSHIP_PIT_INVALID"
            continue
        if row.is_etf:
            exclusions[row.security_id] = "ETF_EXCLUDED"
            continue
        if row.is_test_issue:
            exclusions[row.security_id] = "TEST_ISSUE_EXCLUDED"
            continue
        stock = _window(adjusted_close_by_security.get(row.security_id, ()))
        if stock is None:
            exclusions[row.security_id] = "STOCK_HISTORY_NOT_EVALUABLE"
            continue
        stock_return = _price_return(stock)
        relative_return = stock_return - benchmark_return
        high_ratio = stock[-1] / max(stock)
        prepared[row.security_id] = (relative_return, high_ratio)

    population = [relative_return for relative_return, _ in prepared.values()]
    results: list[CandidateResult] = []
    for row in membership:
        if row.security_id in exclusions:
            results.append(
                CandidateResult(
                    row.security_id,
                    row.symbol,
                    CandidateState.NOT_EVALUABLE.value,
                    None,
                    None,
                    None,
                    exclusions[row.security_id],
                )
            )
            continue

        relative_return, high_ratio = prepared[row.security_id]
        percentile = _percentile_upper_ecdf(relative_return, population)
        passes = percentile + 1e-12 >= RS_THRESHOLD and high_ratio + 1e-12 >= NEAR_HIGH_RATIO
        if passes:
            state = CandidateState.LEADER_CANDIDATE.value
            reason = "RS_AND_NEAR_HIGH_PASS"
        else:
            state = CandidateState.NOT_LEADER_CANDIDATE.value
            failures = []
            if percentile + 1e-12 < RS_THRESHOLD:
                failures.append("RS_BELOW_80")
            if high_ratio + 1e-12 < NEAR_HIGH_RATIO:
                failures.append("PRICE_BELOW_90PCT_OF_252_HIGH")
            reason = "+".join(failures)

        results.append(
            CandidateResult(
                row.security_id,
                row.symbol,
                state,
                percentile,
                relative_return,
                high_ratio,
                reason,
            )
        )

    return tuple(results)
