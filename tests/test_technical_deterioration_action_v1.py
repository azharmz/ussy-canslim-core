from canslim_research.technical_deterioration_action_v1 import (
    DailyBar,
    WeeklyEvidence,
    decide_technical_deterioration_action,
    validate_action,
)


def w(start, end, close, ma, ratio, volume=1000):
    return WeeklyEvidence(start, end, close, ma, volume, ratio)


def d(date, open_):
    return DailyBar(date, open_, open_, open_, open_, 100)


def decide(weeks, days):
    return decide_technical_deterioration_action(
        candidate_id="c1",
        security_id="s1",
        entry_date="2026-01-02",
        fill_price=100,
        weekly_evidence=weeks,
        daily_bars=days,
    )


def test_close_equal_ma_is_not_actionable():
    a = decide([w("2026-01-05", "2026-01-09", 100, 100, 2.0)], [d("2026-01-12", 95)])
    assert a.action_state == "NO_ACTION"


def test_volume_equal_average_is_not_actionable():
    a = decide([w("2026-01-05", "2026-01-09", 99, 100, 1.0)], [d("2026-01-12", 95)])
    assert a.action_state == "NO_ACTION"


def test_break_with_above_average_volume_triggers():
    a = decide([w("2026-01-05", "2026-01-09", 99, 100, 1.01)], [d("2026-01-12", 95)])
    assert a.action_state == "TECHNICAL_DETERIORATION_EXIT_REQUIRED"
    assert a.execution_date == "2026-01-12"
    assert a.execution_price == 95
    assert validate_action(a) == []


def test_low_volume_break_does_not_consume_later_actionable_break():
    weeks = [
        w("2026-01-05", "2026-01-09", 99, 100, 0.8),
        w("2026-01-12", "2026-01-16", 98, 100, 1.2),
    ]
    a = decide(weeks, [d("2026-01-19", 94)])
    assert a.signal_week_end == "2026-01-16"
    assert a.action_state == "TECHNICAL_DETERIORATION_EXIT_REQUIRED"


def test_missing_evidence_is_not_evaluable_if_nothing_else_available():
    a = decide([w("2026-01-05", "2026-01-09", 99, None, None)], [d("2026-01-12", 95)])
    assert a.action_state == "NOT_EVALUABLE"


def test_missing_next_bar_is_explicit():
    a = decide([w("2026-01-05", "2026-01-09", 99, 100, 1.2)], [])
    assert a.action_state == "NO_NEXT_SESSION_BAR"
    assert a.execution_date is None


def test_execution_uses_first_observed_session_after_week_end():
    days = [d("2026-01-09", 90), d("2026-01-12", 95), d("2026-01-13", 96)]
    a = decide([w("2026-01-05", "2026-01-09", 99, 100, 1.2)], days)
    assert a.execution_date == "2026-01-12"
    assert a.execution_price == 95


def test_no_backdated_fill_into_signal_week():
    days = [d("2026-01-08", 90), d("2026-01-09", 91), d("2026-01-12", 95)]
    a = decide([w("2026-01-05", "2026-01-09", 99, 100, 1.2)], days)
    assert a.execution_date == "2026-01-12"


def test_source_versions_are_frozen():
    a = decide([w("2026-01-05", "2026-01-09", 99, 100, 1.2)], [d("2026-01-12", 95)])
    assert a.source_sell_risk_version == "37-sell-risk-v1"
    assert a.source_daily_deterioration_version == "38-technical-deterioration-evidence-v1"
    assert a.source_weekly_evidence_version == "39-weekly-10w-evidence-v1"


def test_observed_open_source_is_explicit():
    a = decide([w("2026-01-05", "2026-01-09", 99, 100, 1.2)], [d("2026-01-12", 95)])
    assert a.execution_source == "DAILY_OHLCV_NEXT_SESSION_OPEN_AFTER_COMPLETED_WEEK"
