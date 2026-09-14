from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

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


def validate_institutional_pointer(pointer: dict, manifest: dict) -> None:
    """Fail closed unless the R2 current pointer resolves to the audited v2 live contract."""
    if pointer.get("schema_version") != 2 or pointer.get("status") != "READY":
        raise ValueError("institutional pointer must be READY schema v2")
    if pointer.get("live_availability") != "exact_edgar_accepted_at":
        raise ValueError("institutional pointer lacks exact accepted_at semantics")
    required = {
        "manifest_key", "snapshot_prefix", "publisher_run_id", "live_source_run_id",
        "live_sponsorship_mapped_key", "live_amendment_lineage_key", "live_summary_key",
        "history_state_events_key", "uncertainty_state_events_key",
    }
    missing = sorted(k for k in required if not pointer.get(k))
    if missing:
        raise ValueError(f"institutional pointer fields missing: {missing}")
    if manifest.get("schema_version") != 2 or manifest.get("status") != "READY":
        raise ValueError("institutional manifest must be READY schema v2")
    if manifest.get("snapshot_prefix") != pointer.get("snapshot_prefix"):
        raise ValueError("institutional pointer/manifest snapshot mismatch")
    if str(manifest.get("publisher_run_id")) != str(pointer.get("publisher_run_id")):
        raise ValueError("institutional pointer/manifest publisher mismatch")
    if str(manifest.get("live_source_run_id")) != str(pointer.get("live_source_run_id")):
        raise ValueError("institutional pointer/manifest live source mismatch")
    semantics = manifest.get("semantics") or {}
    if semantics.get("live_availability") != "exact_edgar_accepted_at":
        raise ValueError("institutional manifest lacks exact accepted_at semantics")
    if semantics.get("live_identity_mapping") != "US_ISIN_BODY_TO_CUSIP9":
        raise ValueError("institutional manifest identity mapping unsupported")
    if semantics.get("quarter_end_used_as_availability") is not False:
        raise ValueError("institutional manifest permits quarter-end availability")
    live_summary = manifest.get("live_summary") or {}
    if live_summary.get("data_gate_pass") is not True:
        raise ValueError("institutional live data gate is not PASS")
    if float(live_summary.get("accepted_at_complete_rate", 0)) != 1.0:
        raise ValueError("institutional live accepted_at completeness is not 100%")
    if int(live_summary.get("ambiguous_lineage_events", 1)) != 0:
        raise ValueError("institutional live amendment lineage is ambiguous")


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
    *, security_id: str, decision_cutoff: datetime | pd.Timestamp,
    live_state: pd.DataFrame, history_events: pd.DataFrame,
    uncertainty_events: pd.DataFrame | None = None,
) -> InstitutionalPitResult:
    """Resolve stock-level CAN SLIM I without quarter-end leakage."""
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
        return InstitutionalPitResult("NOT_EVALUABLE", "I_PRIOR_HISTORY_NOT_AVAILABLE", fund_count_latest=latest_count, latest_period=latest_period, latest_available_at=latest["_accepted"].isoformat(), cusip=cusip)
    hist["_period"] = pd.to_datetime(hist["period_of_report"], errors="coerce")
    hist = hist[hist["_period"].notna() & hist["_period"].lt(pd.Timestamp(latest_period))].sort_values("_period")
    if hist.empty:
        return InstitutionalPitResult("NOT_EVALUABLE", "I_PRIOR_PERIOD_NOT_AVAILABLE", fund_count_latest=latest_count, latest_period=latest_period, latest_available_at=latest["_accepted"].isoformat(), cusip=cusip)
    prior = hist.iloc[-1]
    prior_period = pd.Timestamp(prior["_period"]).date().isoformat()
    uncertain = _uncertain_periods(uncertainty_events, cusip=cusip, cutoff_date=cutoff_date)
    if prior_period in uncertain:
        return InstitutionalPitResult("NOT_EVALUABLE", "I_PRIOR_PERIOD_LINEAGE_UNCERTAIN", fund_count_latest=latest_count, latest_period=latest_period, prior_period=prior_period, latest_available_at=latest["_accepted"].isoformat(), prior_available_on=str(prior["available_on"]), cusip=cusip)
    prior_count = int(prior["I_manager_count"])
    state = "POSITIVE" if latest_count > prior_count else "NEGATIVE" if latest_count < prior_count else "NEUTRAL"
    reason = "I_FUND_COUNT_RISING" if state == "POSITIVE" else "I_FUND_COUNT_FALLING" if state == "NEGATIVE" else "I_FUND_COUNT_FLAT"
    return InstitutionalPitResult(state, reason, fund_count_latest=latest_count, fund_count_prior=prior_count, latest_period=latest_period, prior_period=prior_period, latest_available_at=latest["_accepted"].isoformat(), prior_available_on=str(prior["available_on"]), cusip=cusip)
