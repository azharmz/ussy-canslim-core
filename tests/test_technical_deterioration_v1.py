import pytest

from canslim_research.technical_deterioration_v1 import (
    DailyBar,
    evaluate_technical_deterioration,
    validate_technical_deterioration,
)


def bar(i, close, volume=100.0):
    return DailyBar(str(i), close, close, close, close, volume)


def eval_bars(bars, **kwargs):
    return evaluate_technical_deterioration(
        candidate_id="c1",
        security_id="s1",
        breakout_date="0",
        entry_date="1",
        fill_price=100,
        pivot_level=99,
        bars_through_asof=bars,
        **kwargs,
    )


def test_insufficient_history_is_not_evaluable():
    s = eval_bars([bar(i, 100 + i) for i in range(9)])
    assert s.ma10 is None
    assert s.break_10d_state == "NOT_EVALUABLE"
    assert s.break_50d_state == "NOT_EVALUABLE"
    assert s.volume_ratio_50 is None


def test_ma10_uses_current_and_prior_nine_completed_closes():
    bars = [bar(i, float(i)) for i in range(1, 11)]
    s = eval_bars(bars)
    assert s.ma10 == pytest.approx(5.5)


def test_equality_to_ma_is_not_a_break():
    bars = [bar(i, 100) for i in range(10)]
    s = eval_bars(bars)
    assert s.ma10 == 100
    assert s.break_10d_state == "FALSE"


def test_close_below_ma_is_break():
    bars = [bar(i, 100) for i in range(9)] + [bar(10, 90)]
    s = eval_bars(bars)
    assert s.break_10d_state == "TRUE"


def test_volume_ratio_excludes_current_session():
    bars = [bar(i, 100, 100) for i in range(50)] + [bar(50, 90, 140)]
    s = eval_bars(bars)
    assert s.volume_ratio_50 == pytest.approx(1.40)


def test_heavy_break_requires_break_and_ratio_at_least_140():
    bars = [bar(i, 100, 100) for i in range(50)] + [bar(50, 90, 140)]
    s = eval_bars(bars)
    assert s.break_50d_state == "TRUE"
    assert s.heavy_volume_break_50d_state == "TRUE"


def test_heavy_break_false_when_price_does_not_break():
    bars = [bar(i, 100, 100) for i in range(50)] + [bar(50, 101, 200)]
    s = eval_bars(bars)
    assert s.break_50d_state == "FALSE"
    assert s.heavy_volume_break_50d_state == "FALSE"


def test_missing_volume_makes_heavy_state_not_evaluable():
    bars = [bar(i, 100, 100) for i in range(50)] + [bar(50, 90, None)]
    s = eval_bars(bars)
    assert s.break_50d_state == "TRUE"
    assert s.heavy_volume_break_50d_state == "NOT_EVALUABLE"


def test_first_down_session_can_be_current_largest_observation():
    bars = [bar(0, 100, 100), bar(1, 101, 100), bar(2, 99, 120)]
    s = eval_bars(bars)
    assert s.down_session is True
    assert s.largest_down_volume_since_breakout is True
    assert s.down_session_observation_count == 1


def test_pivot_and_fill_references_are_separate():
    s = eval_bars([bar(0, 100), bar(1, 98)])
    assert s.fell_back_below_pivot is True
    assert s.loss_from_fill_pct == pytest.approx(-0.02)


def test_weekly_rule_is_explicitly_not_implemented():
    s = eval_bars([bar(i, 100) for i in range(51)])
    assert s.break_10w_state == "NOT_IMPLEMENTED_REQUIRES_WEEKLY_AGGREGATION_SPEC"


def test_no_new_sell_action_is_promoted():
    s = eval_bars([bar(i, 100, 100) for i in range(50)] + [bar(50, 90, 200)])
    assert s.action_promotion_state == "EVIDENCE_ONLY_NO_CANONICAL_SELL_ACTION"
    assert validate_technical_deterioration(s) == []
