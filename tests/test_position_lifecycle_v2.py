from canslim_research.position_lifecycle_v2 import (
    ExitCandidate, arbitrate_position_lifecycle_v2, validate_position_lifecycle_v2,
)


def ex(channel, date=None, price=None, source=None, version=None):
    defaults = {
        "CAPITAL_PROTECTION_37": "37-sell-risk-v1",
        "TECHNICAL_DETERIORATION_40": "40-technical-deterioration-action-v1",
        "ROUND_TRIP_42": "42-round-trip-sell-action-v1",
    }
    return ExitCandidate(channel, date, price, source, version or defaults[channel])


def none_cap(): return ex("CAPITAL_PROTECTION_37")
def none_tech(): return ex("TECHNICAL_DETERIORATION_40")
def none_rt(): return ex("ROUND_TRIP_42")


def run(c=None, t=None, r=None, entry_date="2026-01-05", fill=100):
    return arbitrate_position_lifecycle_v2(
        candidate_id="c", security_id="s", entry_date=entry_date, fill_price=fill,
        source_entry_version="36-execution-entry-v1",
        capital_exit=c or none_cap(), technical_exit=t or none_tech(), round_trip_exit=r or none_rt())


def test_no_entry_not_opened():
    x = run(entry_date=None, fill=None)
    assert x.lifecycle_state == "NOT_OPENED"


def test_no_exit_open():
    assert run().lifecycle_state == "OPEN"


def test_round_trip_only_closes_round_trip():
    r = ex("ROUND_TRIP_42", "2026-01-12", 101, "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_CLOSE")
    x = run(r=r)
    assert x.lifecycle_state == "CLOSED_ROUND_TRIP"
    assert x.selected_exit_channel == "ROUND_TRIP_42"


def test_earliest_of_three_wins():
    c = ex("CAPITAL_PROTECTION_37", "2026-01-15", 93, "DAILY_OHLCV_STOP_CONVENTION")
    t = ex("TECHNICAL_DETERIORATION_40", "2026-01-13", 96, "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_WEEK")
    r = ex("ROUND_TRIP_42", "2026-01-12", 101, "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_CLOSE")
    x = run(c,t,r)
    assert x.lifecycle_state == "CLOSED_ROUND_TRIP"
    assert x.selected_exit_date == "2026-01-12"


def test_technical_and_roundtrip_same_open_converge():
    t = ex("TECHNICAL_DETERIORATION_40", "2026-01-12", 95, "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_WEEK")
    r = ex("ROUND_TRIP_42", "2026-01-12", 95, "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_CLOSE")
    x = run(t=t,r=r)
    assert x.lifecycle_state == "CLOSED_OPEN_CONVERGENCE"
    assert set(x.converged_channels) == {"TECHNICAL_DETERIORATION_40", "ROUND_TRIP_42"}


def test_three_way_same_open_converges_once():
    c = ex("CAPITAL_PROTECTION_37", "2026-01-12", 90, "DAILY_OHLCV_OPEN_GAP_THROUGH")
    t = ex("TECHNICAL_DETERIORATION_40", "2026-01-12", 90, "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_WEEK")
    r = ex("ROUND_TRIP_42", "2026-01-12", 90, "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_CLOSE")
    x = run(c,t,r)
    assert x.lifecycle_state == "CLOSED_OPEN_CONVERGENCE"
    assert x.selected_exit_price == 90
    assert len(x.converged_channels) == 3


def test_roundtrip_open_precedes_same_day_stop():
    c = ex("CAPITAL_PROTECTION_37", "2026-01-12", 93, "DAILY_OHLCV_STOP_CONVENTION")
    r = ex("ROUND_TRIP_42", "2026-01-12", 98, "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_CLOSE")
    x = run(c=c,r=r)
    assert x.lifecycle_state == "CLOSED_ROUND_TRIP"
    assert x.selected_exit_price == 98


def test_conflicting_open_prices_not_evaluable():
    t = ex("TECHNICAL_DETERIORATION_40", "2026-01-12", 96, "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_WEEK")
    r = ex("ROUND_TRIP_42", "2026-01-12", 97, "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_CLOSE")
    x = run(t=t,r=r)
    assert x.lifecycle_state == "NOT_EVALUABLE_SOURCE_CONFLICT"
    assert x.selected_exit_date is None


def test_unknown_same_day_order_ambiguous():
    c = ex("CAPITAL_PROTECTION_37", "2026-01-12", 93, "UNKNOWN")
    r = ex("ROUND_TRIP_42", "2026-01-12", 98, "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_CLOSE")
    x = run(c=c,r=r)
    assert x.lifecycle_state == "AMBIGUOUS_SAME_SESSION"


def test_exit_before_entry_not_evaluable():
    r = ex("ROUND_TRIP_42", "2026-01-02", 98, "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_CLOSE")
    assert run(r=r).lifecycle_state == "NOT_EVALUABLE"


def test_validator_green_normal_case():
    r = ex("ROUND_TRIP_42", "2026-01-12", 101, "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_CLOSE")
    assert validate_position_lifecycle_v2(run(r=r)) == []
