from canslim_research.sell_risk_v1 import (
    DailyBar,
    evaluate_sell_risk,
    validate_sell_risk,
)


def b(i, o, h, l, c):
    return DailyBar(f"2026-01-{i:02d}", o, h, l, c, 1000)


def base_eval(bars, *, fill=100.0, pivot=100.0):
    return evaluate_sell_risk(
        candidate_id="c1",
        security_id="s1",
        entry_date="2026-01-01",
        fill_price=fill,
        pivot_level=pivot,
        breakout_date="2026-01-01",
        bars_since_breakout=bars,
        source_entry_version="36-execution-entry-v1",
    )


def test_stop_reference_uses_actual_fill_not_pivot():
    s = base_eval([b(1, 104, 105, 100, 103)], fill=104, pivot=100)
    assert s.practical_loss_trigger_price == 104 * 0.93
    assert s.legacy_hard_loss_ceiling_price == 104 * 0.92
    assert validate_sell_risk(s) == []


def test_gap_through_practical_stop_exits_at_observed_open():
    s = base_eval([b(1, 100, 101, 99, 100), b(2, 90, 92, 89, 91)])
    assert s.sell_action_state == "DEFENSIVE_EXIT_REQUIRED"
    assert s.sell_execution_price == 90
    assert s.sell_execution_source == "DAILY_OHLCV_OPEN_GAP_THROUGH"
    assert s.capital_protection_state == "LEGACY_8PCT_CEILING_BREACHED"


def test_intraday_stop_touch_uses_mechanical_stop_convention():
    s = base_eval([b(1, 100, 101, 92.5, 96)])
    assert s.sell_execution_price == 93
    assert s.sell_execution_source == "DAILY_OHLCV_STOP_CONVENTION"
    assert s.capital_protection_state == "PRACTICAL_7PCT_TRIGGER_REACHED"


def test_profit_zone_is_pivot_referenced_and_not_automatic_exit():
    s = base_eval([b(1, 104, 122, 103, 122)], fill=104, pivot=100)
    assert s.normal_profit_zone_state == "IN_NORMAL_PROFIT_ZONE"
    assert s.sell_action_state == "HOLD"
    assert s.sell_execution_price is None


def test_above_profit_zone_is_not_forced_full_liquidation():
    s = base_eval([b(1, 104, 130, 103, 130)], fill=104, pivot=100)
    assert s.normal_profit_zone_state == "ABOVE_NORMAL_PROFIT_ZONE"
    assert s.sell_action_state == "HOLD"


def test_fast_winner_activates_eight_week_context_before_40_sessions():
    bars = [b(i, 100, 121 if i == 10 else 110, 99, 108) for i in range(1, 16)]
    s = base_eval(bars)
    assert s.reached_20pct_within_first_3_weeks is True
    assert s.eight_week_hold_exception_active is True
    assert s.eight_week_assessment_session == 40


def test_fast_winner_context_expires_at_40_session_assessment_clock():
    bars = []
    for i in range(1, 41):
        day = ((i - 1) % 28) + 1
        bars.append(DailyBar(f"2026-{1 + (i-1)//28:02d}-{day:02d}", 100, 121 if i == 10 else 110, 99, 108, 1000))
    s = base_eval(bars)
    assert s.reached_20pct_within_first_3_weeks is True
    assert s.eight_week_hold_exception_active is False


def test_round_trip_numeric_trigger_is_deliberately_not_invented():
    s = base_eval([b(1, 100, 120, 99, 100)])
    assert s.round_trip_to_buy_point is None
    assert validate_sell_risk(s) == []


def test_climax_is_not_relabelled_from_other_research():
    s = base_eval([b(1, 100, 140, 99, 135)])
    assert s.climax_state == "NOT_IMPLEMENTED_REQUIRES_SEPARATE_AUTHORITATIVE_SPECIFICATION"
    assert validate_sell_risk(s) == []


def test_fell_back_below_pivot_is_evidence_not_automatic_exit_when_stop_not_hit():
    s = base_eval([b(1, 100, 101, 95, 96)], fill=100, pivot=98)
    assert s.fell_back_below_pivot is True
    assert s.sell_action_state == "HOLD"
