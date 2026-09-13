import pytest

from canslim_research.weekly_10w_v1 import DailyBar, aggregate_completed_weeks, evaluate_weekly_10w, validate_weekly_10w


def b(d, o=100, h=101, l=99, c=100, v=100):
    return DailyBar(d, o, h, l, c, v)


def test_current_iso_week_is_excluded():
    bars = [
        b("2026-09-07", c=100),
        b("2026-09-11", c=101),
        b("2026-09-14", c=102),
    ]
    weeks = aggregate_completed_weeks(bars)
    assert len(weeks) == 1
    assert weeks[0].last_date == "2026-09-11"


def test_holiday_short_week_is_valid_completed_week():
    bars = [b("2026-09-08"), b("2026-09-09"), b("2026-09-11"), b("2026-09-14")]
    weeks = aggregate_completed_weeks(bars)
    assert weeks[0].session_count == 3


def test_weekly_ohlcv_aggregation():
    bars = [
        b("2026-09-07", o=10, h=12, l=9, c=11, v=100),
        b("2026-09-08", o=11, h=14, l=10, c=13, v=200),
        b("2026-09-11", o=13, h=15, l=8, c=12, v=300),
        b("2026-09-14"),
    ]
    w = aggregate_completed_weeks(bars)[0]
    assert w.open == 10
    assert w.high == 15
    assert w.low == 8
    assert w.close == 12
    assert w.volume == 600


def test_missing_component_volume_makes_week_volume_none():
    bars = [b("2026-09-07", v=100), b("2026-09-08", v=None), b("2026-09-14")]
    assert aggregate_completed_weeks(bars)[0].volume is None


def build_one_bar_per_week(start_dates, closes, volumes=None):
    if volumes is None:
        volumes = [100] * len(start_dates)
    return [b(d, c=c, v=v) for d, c, v in zip(start_dates, closes, volumes)]


def test_fewer_than_10_completed_weeks_not_evaluable():
    dates = [f"2026-0{m}-02" for m in range(1, 9)]
    # use explicit weekly-separated dates instead to avoid month quirks
    bars = [b("2026-06-01"), b("2026-06-08"), b("2026-06-15"), b("2026-06-22"), b("2026-06-29"), b("2026-07-06"), b("2026-07-13"), b("2026-07-20"), b("2026-07-27")]
    bars += [b("2026-08-03")]
    s = evaluate_weekly_10w(candidate_id="c", security_id="s", bars_through_asof=bars)
    assert s.completed_week_count == 9
    assert s.ma10w is None
    assert s.break_10w_state == "NOT_EVALUABLE"


def test_ten_week_ma_uses_completed_week_closes_only():
    dates = ["2026-06-01","2026-06-08","2026-06-15","2026-06-22","2026-06-29","2026-07-06","2026-07-13","2026-07-20","2026-07-27","2026-08-03","2026-08-10"]
    bars = build_one_bar_per_week(dates, list(range(1, 12)))
    s = evaluate_weekly_10w(candidate_id="c", security_id="s", bars_through_asof=bars)
    assert s.completed_week_count == 10
    assert s.ma10w == pytest.approx(5.5)
    assert s.week_close == 10


def test_equality_to_ma_is_not_break():
    dates = ["2026-06-01","2026-06-08","2026-06-15","2026-06-22","2026-06-29","2026-07-06","2026-07-13","2026-07-20","2026-07-27","2026-08-03","2026-08-10"]
    bars = build_one_bar_per_week(dates, [100]*11)
    s = evaluate_weekly_10w(candidate_id="c", security_id="s", bars_through_asof=bars)
    assert s.ma10w == 100
    assert s.break_10w_state == "FALSE"


def test_weekly_volume_ratio_excludes_latest_completed_week():
    dates = ["2026-05-25","2026-06-01","2026-06-08","2026-06-15","2026-06-22","2026-06-29","2026-07-06","2026-07-13","2026-07-20","2026-07-27","2026-08-03","2026-08-10"]
    bars = build_one_bar_per_week(dates, [100]*12, [100]*10 + [140, 100])
    s = evaluate_weekly_10w(candidate_id="c", security_id="s", bars_through_asof=bars)
    assert s.completed_week_count == 11
    assert s.week_volume_ratio_10 == pytest.approx(1.40)


def test_first_break_chronology():
    dates = ["2026-05-18","2026-05-25","2026-06-01","2026-06-08","2026-06-15","2026-06-22","2026-06-29","2026-07-06","2026-07-13","2026-07-20","2026-07-27","2026-08-03","2026-08-10"]
    closes = [100]*11 + [90, 100]
    bars = build_one_bar_per_week(dates, closes)
    s = evaluate_weekly_10w(candidate_id="c", security_id="s", bars_through_asof=bars)
    assert s.break_10w_state == "TRUE"
    assert s.prior_completed_week_break_10w_state == "FALSE"
    assert s.first_break_10w_observed_state == "TRUE"


def test_no_ma50_identity_and_no_sell_action_promotion():
    dates = ["2026-05-25","2026-06-01","2026-06-08","2026-06-15","2026-06-22","2026-06-29","2026-07-06","2026-07-13","2026-07-20","2026-07-27","2026-08-03"]
    bars = build_one_bar_per_week(dates, [100]*11)
    s = evaluate_weekly_10w(candidate_id="c", security_id="s", bars_through_asof=bars)
    assert s.weekly_aggregation_version == "39-weekly-10w-evidence-v1"
    assert s.action_promotion_state == "EVIDENCE_ONLY_NO_CANONICAL_SELL_ACTION"
    assert validate_weekly_10w(s) == []
