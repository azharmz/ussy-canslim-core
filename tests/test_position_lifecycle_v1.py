from canslim_research.position_lifecycle_v1 import (
    ExitCandidate, arbitrate_position_lifecycle, validate_position_lifecycle,
)


def ex(channel, date=None, price=None, source=None, version=None):
    return ExitCandidate(channel, date, price, source, version or (
        "37-sell-risk-v1" if channel == "CAPITAL_PROTECTION_37"
        else "40-technical-deterioration-action-v1"))


def run(capital, technical, entry_date="2026-01-05", fill=100):
    return arbitrate_position_lifecycle(
        candidate_id="c", security_id="s", entry_date=entry_date, fill_price=fill,
        source_entry_version="36-execution-entry-v1", capital_exit=capital, technical_exit=technical)


def none_cap(): return ex("CAPITAL_PROTECTION_37")
def none_tech(): return ex("TECHNICAL_DETERIORATION_40")


def test_no_entry_means_not_opened():
    x = run(none_cap(), none_tech(), entry_date=None, fill=None)
    assert x.lifecycle_state == "NOT_OPENED"
    assert x.selected_exit_date is None


def test_no_exit_keeps_position_open():
    x = run(none_cap(), none_tech())
    assert x.lifecycle_state == "OPEN"


def test_only_capital_exit_closes_once():
    c = ex("CAPITAL_PROTECTION_37", "2026-01-08", 93, "DAILY_OHLCV_STOP_CONVENTION")
    x = run(c, none_tech())
    assert x.lifecycle_state == "CLOSED_CAPITAL_PROTECTION"
    assert x.selected_exit_price == 93


def test_only_technical_exit_closes_once():
    t = ex("TECHNICAL_DETERIORATION_40", "2026-01-12", 110, "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_WEEK")
    x = run(none_cap(), t)
    assert x.lifecycle_state == "CLOSED_TECHNICAL_DETERIORATION"


def test_earlier_capital_exit_wins():
    c = ex("CAPITAL_PROTECTION_37", "2026-01-08", 93, "DAILY_OHLCV_STOP_CONVENTION")
    t = ex("TECHNICAL_DETERIORATION_40", "2026-01-12", 90, "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_WEEK")
    x = run(c, t)
    assert x.selected_exit_channel == "CAPITAL_PROTECTION_37"
    assert x.selected_exit_date == "2026-01-08"


def test_earlier_technical_exit_wins():
    c = ex("CAPITAL_PROTECTION_37", "2026-01-13", 93, "DAILY_OHLCV_STOP_CONVENTION")
    t = ex("TECHNICAL_DETERIORATION_40", "2026-01-12", 96, "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_WEEK")
    x = run(c, t)
    assert x.selected_exit_channel == "TECHNICAL_DETERIORATION_40"


def test_same_observed_open_converges_to_one_exit():
    c = ex("CAPITAL_PROTECTION_37", "2026-01-12", 90, "DAILY_OHLCV_OPEN_GAP_THROUGH")
    t = ex("TECHNICAL_DETERIORATION_40", "2026-01-12", 90, "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_WEEK")
    x = run(c, t)
    assert x.lifecycle_state == "CLOSED_SAME_OPEN_CONVERGENCE"
    assert x.selected_exit_price == 90


def test_same_day_technical_open_precedes_stop_convention():
    c = ex("CAPITAL_PROTECTION_37", "2026-01-12", 93, "DAILY_OHLCV_STOP_CONVENTION")
    t = ex("TECHNICAL_DETERIORATION_40", "2026-01-12", 97, "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_WEEK")
    x = run(c, t)
    assert x.lifecycle_state == "CLOSED_TECHNICAL_DETERIORATION"
    assert x.selected_exit_price == 97


def test_unknown_same_session_order_remains_ambiguous():
    c = ex("CAPITAL_PROTECTION_37", "2026-01-12", 91, "UNKNOWN_SOURCE")
    t = ex("TECHNICAL_DETERIORATION_40", "2026-01-12", 97, "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_WEEK")
    x = run(c, t)
    assert x.lifecycle_state == "AMBIGUOUS_SAME_SESSION"
    assert x.selected_exit_date is None


def test_exit_before_entry_is_not_evaluable():
    c = ex("CAPITAL_PROTECTION_37", "2026-01-02", 93, "DAILY_OHLCV_STOP_CONVENTION")
    x = run(c, none_tech())
    assert x.lifecycle_state == "NOT_EVALUABLE"


def test_validator_green_for_normal_closed_lifecycle():
    c = ex("CAPITAL_PROTECTION_37", "2026-01-08", 93, "DAILY_OHLCV_STOP_CONVENTION")
    assert validate_position_lifecycle(run(c, none_tech())) == []
