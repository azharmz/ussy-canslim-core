from datetime import datetime, timezone

import pandas as pd

from canslim_research.institutional_pit import resolve_institutional_pit

SID = "US0378331005"
CUSIP = "037833100"
CUTOFF = datetime(2026, 9, 14, 20, 0, tzinfo=timezone.utc)


def live(accepted="2026-08-14T20:00:00+00:00", count=120):
    return pd.DataFrame([{
        "security_id": SID,
        "period_of_report": "2026-06-30",
        "I_manager_count": count,
        "I_available_at": accepted,
    }])


def history(count=100):
    return pd.DataFrame([
        {"available_on": "2026-05-16", "period_of_report": "2026-03-31", "cusip": CUSIP, "I_manager_count": count},
        {"available_on": "2026-08-16", "period_of_report": "2026-06-30", "cusip": CUSIP, "I_manager_count": 999},
    ])


def uncertainty(count=0):
    return pd.DataFrame([{
        "available_on": "2026-05-17",
        "period_of_report": "2026-03-31",
        "cusip": CUSIP,
        "I_uncertain_manager_count": count,
    }])


def test_rising_fund_count_is_positive():
    r = resolve_institutional_pit(
        security_id=SID, decision_cutoff=CUTOFF, live_state=live(),
        history_events=history(), uncertainty_events=uncertainty(0))
    assert r.state == "POSITIVE"
    assert r.fund_count_latest == 120
    assert r.fund_count_prior == 100
    assert r.latest_period == "2026-06-30"
    assert r.prior_period == "2026-03-31"


def test_live_filing_after_cutoff_fails_closed():
    r = resolve_institutional_pit(
        security_id=SID, decision_cutoff=CUTOFF,
        live_state=live("2026-09-14T20:00:01+00:00"),
        history_events=history(), uncertainty_events=uncertainty(0))
    assert r.state == "NOT_EVALUABLE"
    assert r.reason == "I_LIVE_NOT_AVAILABLE_ASOF"


def test_prior_period_must_be_available_by_cutoff():
    h = history()
    h.loc[h["period_of_report"].eq("2026-03-31"), "available_on"] = "2026-09-15"
    r = resolve_institutional_pit(
        security_id=SID, decision_cutoff=CUTOFF, live_state=live(),
        history_events=h, uncertainty_events=uncertainty(0))
    assert r.state == "NOT_EVALUABLE"
    assert r.reason == "I_PRIOR_PERIOD_NOT_AVAILABLE"


def test_uncertain_prior_lineage_fails_closed():
    r = resolve_institutional_pit(
        security_id=SID, decision_cutoff=CUTOFF, live_state=live(),
        history_events=history(), uncertainty_events=uncertainty(1))
    assert r.state == "NOT_EVALUABLE"
    assert r.reason == "I_PRIOR_PERIOD_LINEAGE_UNCERTAIN"


def test_non_us_identity_fails_closed():
    r = resolve_institutional_pit(
        security_id="CA1234567890", decision_cutoff=CUTOFF, live_state=live(),
        history_events=history(), uncertainty_events=uncertainty(0))
    assert r.state == "NOT_EVALUABLE"
    assert r.reason == "I_IDENTITY_NOT_DETERMINISTIC"


def test_flat_and_falling_are_not_positive():
    flat = resolve_institutional_pit(
        security_id=SID, decision_cutoff=CUTOFF, live_state=live(count=100),
        history_events=history(count=100), uncertainty_events=uncertainty(0))
    falling = resolve_institutional_pit(
        security_id=SID, decision_cutoff=CUTOFF, live_state=live(count=90),
        history_events=history(count=100), uncertainty_events=uncertainty(0))
    assert flat.state == "NEUTRAL"
    assert falling.state == "NEGATIVE"
