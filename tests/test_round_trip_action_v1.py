from canslim_research.round_trip_action_v1 import DailyBar, decide_round_trip_action, validate_round_trip_action


def b(d, o, h, l, c): return DailyBar(d, o, h, l, c)

def run(bars):
    return decide_round_trip_action(
        candidate_id="c", security_id="s", entry_date="2026-01-05", fill_price=102,
        pivot_level=100, bars_since_entry=bars, source_entry_version="36-execution-entry-v1")


def test_empty_history_not_evaluable():
    assert run([]).round_trip_state == "NOT_EVALUABLE"


def test_no_double_digit_gain_means_no_action():
    x = run([b("2026-01-05",102,109,101,108), b("2026-01-06",108,109,99,100)])
    assert x.round_trip_state == "NO_ACTION"


def test_exact_10pct_prior_gain_qualifies():
    x = run([b("2026-01-05",102,110,101,109), b("2026-01-06",108,109,98,100), b("2026-01-07",99,100,97,98)])
    assert x.round_trip_state == "ROUND_TRIP_EXIT_REQUIRED"
    assert abs(x.prior_max_gain_from_buy_point_pct - 0.10) < 1e-12


def test_trigger_requires_close_at_or_below_pivot():
    x = run([b("2026-01-05",102,112,101,111), b("2026-01-06",105,106,99,100.01)])
    assert x.round_trip_state == "NO_ACTION"


def test_close_equal_pivot_triggers_after_prior_gain():
    x = run([b("2026-01-05",102,111,101,110), b("2026-01-06",103,104,99,100), b("2026-01-07",99,100,98,99)])
    assert x.trigger_date == "2026-01-06"
    assert x.execution_date == "2026-01-07"
    assert x.execution_price == 99


def test_next_session_open_is_execution_price():
    x = run([b("2026-01-05",102,115,101,114), b("2026-01-06",103,105,98,99), b("2026-01-07",95,98,94,97)])
    assert x.execution_price == 95
    assert x.execution_source == "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_CLOSE"


def test_no_next_bar_is_explicit():
    x = run([b("2026-01-05",102,115,101,114), b("2026-01-06",103,105,98,99)])
    assert x.round_trip_state == "NO_NEXT_SESSION_BAR"
    assert x.execution_date is None


def test_same_bar_first_gain_and_round_trip_is_ambiguous():
    x = run([b("2026-01-05",102,111,98,99), b("2026-01-06",100,101,98,99)])
    assert x.round_trip_state == "AMBIGUOUS_SAME_SESSION"
    assert x.execution_date is None


def test_reference_is_pivot_not_fill():
    x = run([b("2026-01-05",102,110,101,109), b("2026-01-06",103,104,99,100), b("2026-01-07",99,100,98,99)])
    assert x.prior_max_high == 110
    assert abs(x.prior_max_gain_from_buy_point_pct - 0.10) < 1e-12


def test_validator_green_for_actionable_case():
    x = run([b("2026-01-05",102,112,101,111), b("2026-01-06",103,104,98,99), b("2026-01-07",97,99,96,98)])
    assert validate_round_trip_action(x) == []
