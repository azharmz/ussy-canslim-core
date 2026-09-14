"""Theory-faithful PIT market leadership/weakening evidence boundary v1.

This module deliberately does not discover a leader cohort.  It aggregates already
observed, provenance-bearing broad-market leadership evidence without inventing
quantitative thresholds.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

VERSION = "51-market-leadership-weakening-evidence-v1"


@dataclass(frozen=True)
class LeadershipEvidenceInput:
    asof_date: str
    broad_market_cohort_valid: Optional[bool]
    cohort_definition: Optional[str] = None
    cohort_provenance: Optional[str] = None
    valid_observed_leaders: Optional[int] = None
    leaders_making_new_highs: Optional[bool] = None
    institutional_accumulation_in_leaders: Optional[bool] = None
    majority_leaders_no_longer_making_new_highs: Optional[bool] = None
    institutional_selling_in_leaders: Optional[bool] = None
    source_provenance: Optional[str] = None


@dataclass(frozen=True)
class LeadershipEvidenceResult:
    asof_date: str
    leadership_confirming: Optional[bool]
    weakening_confirmed: Optional[bool]
    leadership_reason: str
    weakening_reason: str
    version: str = VERSION


def _provenance_complete(e: LeadershipEvidenceInput) -> bool:
    return bool(
        e.asof_date
        and e.cohort_definition
        and e.cohort_provenance
        and e.source_provenance
        and e.valid_observed_leaders is not None
        and e.valid_observed_leaders > 0
    )


def evaluate_market_leadership(e: LeadershipEvidenceInput) -> LeadershipEvidenceResult:
    """Return tri-state #46 auxiliary evidence without filling missing channels.

    A restricted/invalid cohort is NOT_EVALUABLE rather than False because it cannot
    answer the broad-market question. Required channel absence is also NOT_EVALUABLE.
    """
    if e.broad_market_cohort_valid is not True or not _provenance_complete(e):
        return LeadershipEvidenceResult(
            e.asof_date,
            None,
            None,
            "NOT_EVALUABLE_BROAD_MARKET_COHORT_OR_PROVENANCE",
            "NOT_EVALUABLE_BROAD_MARKET_COHORT_OR_PROVENANCE",
        )

    if e.leaders_making_new_highs is None or e.institutional_accumulation_in_leaders is None:
        leadership: Optional[bool] = None
        leadership_reason = "NOT_EVALUABLE_REQUIRED_LEADERSHIP_CHANNEL_MISSING"
    else:
        leadership = bool(e.leaders_making_new_highs and e.institutional_accumulation_in_leaders)
        leadership_reason = (
            "LEADERSHIP_CONFIRMED_NEW_HIGHS_AND_INSTITUTIONAL_DEMAND"
            if leadership
            else "LEADERSHIP_NOT_CONFIRMED"
        )

    if (
        e.majority_leaders_no_longer_making_new_highs is None
        or e.institutional_selling_in_leaders is None
    ):
        weakening: Optional[bool] = None
        weakening_reason = "NOT_EVALUABLE_REQUIRED_WEAKENING_CHANNEL_MISSING"
    else:
        weakening = bool(
            e.majority_leaders_no_longer_making_new_highs
            and e.institutional_selling_in_leaders
        )
        weakening_reason = (
            "WEAKENING_CONFIRMED_LEADER_FAILURE_AND_INSTITUTIONAL_SELLING"
            if weakening
            else "WEAKENING_NOT_CONFIRMED"
        )

    return LeadershipEvidenceResult(
        e.asof_date,
        leadership,
        weakening,
        leadership_reason,
        weakening_reason,
    )
