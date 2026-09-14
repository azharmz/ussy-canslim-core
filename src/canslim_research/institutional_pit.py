from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pandas as pd


@dataclass(frozen=True, slots=True)
class InstitutionalPitResult:
    state: str
    reason: str
    fund_count_latest: int | None = None
    fund_count_prior: int | None = None
    latest_period: str | None = None
    prior_period: str | None = None
    latest_available_at: str | None = None
    prior_available_on: str | None = None
    cusip: str | None = None


def _utc(value: object) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        raise ValueError("decision cutoff and exact accepted-at timestamps must be timezone-aware")
    return ts.tz_convert("UTC")


def _cusip9(security_id: str) -> str | None:
    sid = str(security_id).strip().upper()
    if len(sid) == 12 and sid.startswith("US"):
        return sid[2:11]
    return None


def _latest_event_state(events: pd.DataFrame, *, cusip: str, cutoff_date: str) -> pd.DataFrame:
    required = {"available_on", "period_of_report", "cusip", "I_manager_count"}
    missing = required - set(events.columns)
    if missing:
        raise ValueError(f"institutional history event columns missing: {sorted(missing)}")
    x = events[events["cusip"].astype(str).str.upper().eq(cusip)].copy()
    if x.empty:
        return x
    x["_available"] = pd.to_datetime(x["available_on"], errors="coerce").dt.date
    cutoff = pd.Timestamp(cutoff_date).date()
    x = x[x["_available"].notna() & x["_available"].le(cutoff)].copy()
    if x.empty:
        return x
    # Preserve source row order for multiple state changes on one conservative
    # availability date; the upstream event stream is emitted in filing order.
    x["_ordinal"] = range(len(x))
    x = x.sort_values(["period_of_report", "_available", "_ordinal"])
    return x.groupby("period_of_report", as_index=False, sort=False).tail(1)


def _uncertain_periods(events: pd.DataFrame | None, *, cusip: str, cutoff_date: str) -> set[str]:
    if events is None or events.empty:
        return set()
    required = {"available_on", "period_of_report", "cusip", "I_uncertain_manager_count"}
    missing = required - set(events.columns)
    if missing:
        raise ValueError(f"institutional uncertainty event columns missing: {sorted(missing)}")
    x = events[events["cusip"].astype(str).str.upper().eq(cusip)].copy()
    if x.empty:
        return set()
    x["_available"] = pd.to_datetime(x["available_on"], errors="coerce").dt.date
    cutoff = pd.Timestamp(cutoff_date).date()
    x = x[x["_available"].notna() & x["_available"].le(cutoff)].copy()
    if x.empty:
        return set()
    x["_ordinal"] = range(len(x))
    x = x.sort_values(["period_of_report", "_available", "_ordinal"])
    last = x.groupby("period_of_report", as_index=False, sort=False).tail(1)
    return set(last.loc[pd.to_numeric(last["I_uncertain_manager_count"], errors="coerce").fillna(1).gt(0), "period_of_report"].astype(str))


def resolve_institutional_pit(
    *,
    security_id: str,
    decision_cutoff: datetime | pd.Timestamp,
    live_state: pd.DataFrame,
    history_events: pd.DataFrame,
    uncertainty_events: pd.DataFrame | None = None,
) -> InstitutionalPitResult:
    """Resolve stock-level CAN SLIM I without quarter-end leakage.

    Latest-period state comes only from the canonical live exact-accepted_at
    artifact. Prior-period comparison comes from the conservative historical
    state-event stream, filtered to information already available by the same
    decision cutoff. Any unresolved historical uncertainty fails closed.
    """
    cusip = _cusip9(security_id)
    if cusip is None:
        return InstitutionalPitResult("NOT_EVALUABLE", "I_IDENTITY_NOT_DETERMINISTIC")

    required_live = {"security_id", "period_of_report", "I_manager_count", "I_available_at"}
    missing_live = required_live - set(live_state.columns)
    if missing_live:
        raise ValueError(f"institutional live columns missing: {sorted(missing_live)}")

    cutoff = _utc(decision_cutoff)
    live = live_state[live_state["security_id"].astype(str).str.upper().eq(str(security_id).upper())].copy()
    if live.empty:
        return InstitutionalPitResult("NOT_EVALUABLE", "I_LIVE_SECURITY_NOT_FOUND", cusip=cusip)
    live["_accepted"] = pd.to_datetime(live["I_available_at"], errors="coerce", utc=True)
    live = live[live["_accepted"].notna() & live["_accepted"].le(cutoff)].copy()
    if live.empty:
        return InstitutionalPitResult("NOT_EVALUABLE", "I_LIVE_NOT_AVAILABLE_ASOF", cusip=cusip)
    live["_period"] = pd.to_datetime(live["period_of_report"], errors="coerce")
    live = live[live["_period"].notna()].sort_values(["_period", "_accepted"])
    if live.empty:
        return InstitutionalPitResult("NOT_EVALUABLE", "I_LIVE_PERIOD_INVALID", cusip=cusip)
    latest = live.iloc[-1]
    latest_period = pd.Timestamp(latest["_period"]).date().isoformat()
    latest_count = int(latest["I_manager_count"])

    cutoff_date = cutoff.date().isoformat()
    hist = _latest_event_state(history_events, cusip=cusip, cutoff_date=cutoff_date)
    if hist.empty:
        return InstitutionalPitResult(
            "NOT_EVALUABLE", "I_PRIOR_HISTORY_NOT_AVAILABLE",
            fund_count_latest=latest_count, latest_period=latest_period,
            latest_available_at=latest["_accepted"].isoformat(), cusip=cusip,
        )
    hist["_period"] = pd.to_datetime(hist["period_of_report"], errors="coerce")
    hist = hist[hist["_period"].notna() & hist["_period"].lt(pd.Timestamp(latest_period))].sort_values("_period")
    if hist.empty:
        return InstitutionalPitResult(
            "NOT_EVALUABLE", "I_PRIOR_PERIOD_NOT_AVAILABLE",
            fund_count_latest=latest_count, latest_period=latest_period,
            latest_available_at=latest["_accepted"].isoformat(), cusip=cusip,
        )
    prior = hist.iloc[-1]
    prior_period = pd.Timestamp(prior["_period"]).date().isoformat()

    uncertain = _uncertain_periods(uncertainty_events, cusip=cusip, cutoff_date=cutoff_date)
    if prior_period in uncertain:
        return InstitutionalPitResult(
            "NOT_EVALUABLE", "I_PRIOR_PERIOD_LINEAGE_UNCERTAIN",
            fund_count_latest=latest_count, latest_period=latest_period,
            prior_period=prior_period, latest_available_at=latest["_accepted"].isoformat(),
            prior_available_on=str(prior["available_on"]), cusip=cusip,
        )

    prior_count = int(prior["I_manager_count"])
    state = "POSITIVE" if latest_count > prior_count else "NEGATIVE" if latest_count < prior_count else "NEUTRAL"
    return InstitutionalPitResult(
        state, "I_FUND_COUNT_RISING" if state == "POSITIVE" else "I_FUND_COUNT_FALLING" if state == "NEGATIVE" else "I_FUND_COUNT_FLAT",
        fund_count_latest=latest_count, fund_count_prior=prior_count,
        latest_period=latest_period, prior_period=prior_period,
        latest_available_at=latest["_accepted"].isoformat(), prior_available_on=str(prior["available_on"]), cusip=cusip,
    )
