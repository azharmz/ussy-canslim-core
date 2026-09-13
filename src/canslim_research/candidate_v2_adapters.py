"""Theory-faithful evidence adapters for CAN SLIM candidate generator #34.

These adapters translate already-PIT-safe upstream facts into the explicit states
required by frozen #32. They do not fetch data and do not reinterpret #33
morphology. Missing/non-PIT-safe evidence stays NOT_EVALUABLE.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

from canslim_research.candidate_v2 import CandidateEvidence


@dataclass(frozen=True, slots=True)
class AnnualEpsObservation:
    fiscal_year: int
    eps: float | None
    available_on: str


@dataclass(frozen=True, slots=True)
class EvidenceAdapterResult:
    evidence: CandidateEvidence
    rs_rating_proxy_percentile: float | None
    annual_eps_growth_measure: float | None
    reason_codes: tuple[str, ...]


def c_screen_state(*, quarterly_eps_yoy: float | None, available_on: str | None, asof_date: str) -> tuple[str, str]:
    if available_on is None or available_on > asof_date:
        return "NOT_EVALUABLE", "C_NOT_PIT_AVAILABLE"
    if quarterly_eps_yoy is None or not isfinite(float(quarterly_eps_yoy)):
        return "NOT_EVALUABLE", "C_EPS_YOY_UNDEFINED"
    return ("PASS", "C_EPS_YOY_GE_25") if float(quarterly_eps_yoy) >= 0.25 else ("FAIL", "C_EPS_YOY_LT_25")


def annual_eps_cagr(observations: Sequence[AnnualEpsObservation], *, asof_date: str) -> float | None:
    """Latest three-year-span EPS CAGR using four consecutive PIT-available FY values."""
    usable = sorted(
        (x for x in observations if x.available_on <= asof_date and x.eps is not None),
        key=lambda x: x.fiscal_year,
    )
    if len(usable) < 4:
        return None
    window = usable[-4:]
    years = [x.fiscal_year for x in window]
    if years != list(range(years[0], years[0] + 4)):
        return None
    first, last = window[0], window[-1]
    if float(first.eps) <= 0 or float(last.eps) <= 0:
        return None
    return (float(last.eps) / float(first.eps)) ** (1.0 / 3.0) - 1.0


def a_screen_state(observations: Sequence[AnnualEpsObservation], *, asof_date: str) -> tuple[str, float | None, str]:
    growth = annual_eps_cagr(observations, asof_date=asof_date)
    if growth is None or not isfinite(growth):
        return "NOT_EVALUABLE", None, "A_3Y_EPS_CAGR_NOT_EVALUABLE"
    return ("PASS", growth, "A_3Y_EPS_CAGR_GE_25") if growth >= 0.25 else ("FAIL", growth, "A_3Y_EPS_CAGR_LT_25")


def l_screen_state(rs_rating_proxy_percentile: float | None) -> tuple[str, str]:
    if rs_rating_proxy_percentile is None or not isfinite(float(rs_rating_proxy_percentile)):
        return "NOT_EVALUABLE", "L_RS_PERCENTILE_MISSING"
    value = float(rs_rating_proxy_percentile)
    if not 0.0 <= value <= 100.0:
        raise ValueError("RS percentile must be within [0, 100]")
    return ("PASS", "L_RS_PERCENTILE_GE_80") if value >= 80.0 else ("FAIL", "L_RS_PERCENTILE_LT_80")


def m_entry_state(market_state: str | None) -> tuple[str, str]:
    mapping = {
        "CONFIRMED_UPTREND": ("ALLOW_NEW_BUYS", "M_CONFIRMED_UPTREND"),
        "UPTREND_UNDER_PRESSURE": ("CAUTION", "M_UPTREND_UNDER_PRESSURE"),
        "CORRECTION": ("BLOCK_NEW_BUYS", "M_CORRECTION"),
        "UNKNOWN": ("NOT_EVALUABLE", "M_UNKNOWN"),
        None: ("NOT_EVALUABLE", "M_MISSING"),
    }
    if market_state not in mapping:
        raise ValueError(f"unsupported M market state: {market_state!r}")
    return mapping[market_state]


def institutional_state(*, fund_count_latest: int | None, fund_count_prior: int | None, available_on: str | None, asof_date: str) -> tuple[str, str]:
    if available_on is None or available_on > asof_date or fund_count_latest is None or fund_count_prior is None:
        return "NOT_EVALUABLE", "I_NOT_PIT_EVALUABLE"
    delta = int(fund_count_latest) - int(fund_count_prior)
    if delta > 0:
        return "POSITIVE", "I_FUND_COUNT_RISING"
    if delta < 0:
        return "NEGATIVE", "I_FUND_COUNT_FALLING"
    return "NEUTRAL", "I_FUND_COUNT_FLAT"


def build_candidate_evidence(
    *,
    asof_date: str,
    quarterly_eps_yoy: float | None,
    quarterly_available_on: str | None,
    annual_eps: Sequence[AnnualEpsObservation],
    rs_rating_proxy_percentile: float | None,
    market_state: str | None,
    fund_count_latest: int | None = None,
    fund_count_prior: int | None = None,
    institutional_available_on: str | None = None,
    n_price_state: str = "NOT_EVALUABLE",
    n_catalyst_state: str = "NOT_IMPLEMENTED",
    s_evidence_state: str = "NOT_EVALUABLE",
    industry_evidence_state: str = "NOT_IMPLEMENTED",
) -> EvidenceAdapterResult:
    c_state, c_reason = c_screen_state(
        quarterly_eps_yoy=quarterly_eps_yoy,
        available_on=quarterly_available_on,
        asof_date=asof_date,
    )
    a_state, a_growth, a_reason = a_screen_state(annual_eps, asof_date=asof_date)
    l_state, l_reason = l_screen_state(rs_rating_proxy_percentile)
    m_state, m_reason = m_entry_state(market_state)
    i_state, i_reason = institutional_state(
        fund_count_latest=fund_count_latest,
        fund_count_prior=fund_count_prior,
        available_on=institutional_available_on,
        asof_date=asof_date,
    )
    return EvidenceAdapterResult(
        evidence=CandidateEvidence(
            C_screen_state=c_state,
            A_screen_state=a_state,
            L_individual_leadership_state=l_state,
            M_entry_state=m_state,
            N_price_state=n_price_state,
            N_catalyst_state=n_catalyst_state,
            S_evidence_state=s_evidence_state,
            I_evidence_state=i_state,
            industry_evidence_state=industry_evidence_state,
        ),
        rs_rating_proxy_percentile=rs_rating_proxy_percentile,
        annual_eps_growth_measure=a_growth,
        reason_codes=(c_reason, a_reason, l_reason, m_reason, i_reason),
    )
