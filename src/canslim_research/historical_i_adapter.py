from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from canslim_research.candidate_v2_adapters import institutional_state

VERSION = "fa-first-historical-i-adapter-v0.1"


@dataclass(frozen=True, slots=True)
class HistoricalIEvent:
    cusip: str
    period_of_report: str
    available_on: str
    manager_count: int
    uncertain: bool = False


@dataclass(frozen=True, slots=True)
class HistoricalIDecision:
    security_id: str
    asof_date: str
    state: str
    reason: str
    latest_period: str | None
    prior_period: str | None
    latest_count: int | None
    prior_count: int | None
    latest_available_on: str | None
    version: str = VERSION


def cusip9(security_id: str) -> str | None:
    sid = str(security_id).strip().upper()
    return sid[2:11] if len(sid) == 12 and sid.startswith("US") else None


def resolve_historical_i(
    *,
    security_id: str,
    asof_date: str,
    events: Sequence[HistoricalIEvent],
) -> HistoricalIDecision:
    """Resolve frozen historical I from conservative PIT event states only."""
    cusip = cusip9(security_id)
    if cusip is None:
        return HistoricalIDecision(security_id, asof_date, "NOT_EVALUABLE", "I_IDENTITY_NOT_DETERMINISTIC", None, None, None, None, None)

    usable = [e for e in events if e.cusip.upper() == cusip and e.available_on <= asof_date]
    if not usable:
        return HistoricalIDecision(security_id, asof_date, "NOT_EVALUABLE", "I_HISTORY_NOT_AVAILABLE_ASOF", None, None, None, None, None)

    # Last available state for each report period, matching the canonical
    # amendment-aware historical event stream.
    by_period: dict[str, HistoricalIEvent] = {}
    for event in sorted(usable, key=lambda e: (e.period_of_report, e.available_on)):
        by_period[event.period_of_report] = event
    periods = sorted(by_period)
    if len(periods) < 2:
        latest = by_period[periods[-1]]
        return HistoricalIDecision(security_id, asof_date, "NOT_EVALUABLE", "I_PRIOR_PERIOD_NOT_AVAILABLE", latest.period_of_report, None, latest.manager_count, None, latest.available_on)

    latest = by_period[periods[-1]]
    prior = by_period[periods[-2]]
    if latest.uncertain or prior.uncertain:
        return HistoricalIDecision(security_id, asof_date, "NOT_EVALUABLE", "I_PERIOD_LINEAGE_UNCERTAIN", latest.period_of_report, prior.period_of_report, latest.manager_count, prior.manager_count, latest.available_on)

    state, reason = institutional_state(
        fund_count_latest=latest.manager_count,
        fund_count_prior=prior.manager_count,
        available_on=latest.available_on,
        asof_date=asof_date,
    )
    return HistoricalIDecision(security_id, asof_date, state, reason, latest.period_of_report, prior.period_of_report, latest.manager_count, prior.manager_count, latest.available_on)
