from canslim_research.historical_i_adapter import HistoricalIEvent, resolve_historical_i


def test_historical_i_uses_only_available_events():
    sid = "US58506Q1094"
    events = (
        HistoricalIEvent("58506Q109", "2021-03-31", "2021-05-16", 10),
        HistoricalIEvent("58506Q109", "2021-06-30", "2021-08-16", 12),
    )
    before = resolve_historical_i(security_id=sid, asof_date="2021-07-27", events=events)
    assert before.state == "NOT_EVALUABLE"
    after = resolve_historical_i(security_id=sid, asof_date="2021-08-16", events=events)
    assert after.state == "POSITIVE"
    assert after.latest_count == 12
    assert after.prior_count == 10


def test_historical_i_uncertain_period_fails_closed():
    sid = "US58506Q1094"
    events = (
        HistoricalIEvent("58506Q109", "2021-03-31", "2021-05-16", 10),
        HistoricalIEvent("58506Q109", "2021-06-30", "2021-08-16", 12, uncertain=True),
    )
    row = resolve_historical_i(security_id=sid, asof_date="2021-08-17", events=events)
    assert row.state == "NOT_EVALUABLE"
    assert row.reason == "I_PERIOD_LINEAGE_UNCERTAIN"
