"""Shadow-only CAN SLIM v2 fundamental watchlist contract.

This module is intentionally independent of frozen v1 eligibility/candidate code.
It performs no I/O and never invokes #33.  The caller must persist/checkpoint the
result with the pinned lineage before any expensive morphology work.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

WATCHLIST_CONTRACT_VERSION = "canslim-watchlist-contract-v2"
QUALIFIED = "QUALIFIED"


@dataclass(frozen=True, slots=True)
class WatchlistLineage:
    decision_date: str
    ready_key: str
    ready_sha256: str
    fundamental_source_identity: str


@dataclass(frozen=True, slots=True)
class WatchlistAssessment:
    security_id: str
    symbol_asof: str
    decision_date: str
    watchlist_state: str
    reason_codes: tuple[str, ...]
    C_state: str
    A_state: str
    contract_version: str = WATCHLIST_CONTRACT_VERSION

    @property
    def qualified(self) -> bool:
        return self.watchlist_state == QUALIFIED


def assess_watchlist(
    *,
    security_id: str,
    symbol_asof: str,
    lineage: WatchlistLineage,
    C_state: str,
    A_state: str,
) -> WatchlistAssessment:
    reasons: list[str] = []
    if C_state == "FAIL":
        reasons.append("C_FAIL")
    elif C_state != "PASS":
        reasons.append("C_NOT_EVALUABLE")

    if A_state == "FAIL":
        reasons.append("A_FAIL")
    elif A_state != "PASS":
        reasons.append("A_NOT_EVALUABLE")

    if not reasons:
        state = QUALIFIED
    elif any(r.endswith("NOT_EVALUABLE") for r in reasons):
        state = "INPUT_NOT_EVALUABLE"
    elif "C_FAIL" in reasons:
        state = "C_FAIL"
    else:
        state = "A_FAIL"

    return WatchlistAssessment(
        security_id=str(security_id),
        symbol_asof=str(symbol_asof),
        decision_date=lineage.decision_date,
        watchlist_state=state,
        reason_codes=tuple(reasons),
        C_state=C_state,
        A_state=A_state,
    )


def qualified_security_ids(
    assessments: Mapping[str, WatchlistAssessment],
) -> frozenset[str]:
    return frozenset(
        security_id
        for security_id, assessment in assessments.items()
        if assessment.qualified
    )
