from datetime import date

import pytest

from canslim_research.execution_entry_v1 import (
    ExecutionState,
    decide_t1_open_execution,
    validate_execution_decision,
)


T = date(2025, 1, 2)
T1 = date(2025, 1, 3)


def _d(**kwargs):
    base = dict(
        candidate_id="c1",
        security_id="s1",
        signal_date=T,
        candidate_stage="CANSLIM_ELIGIBLE",
        pivot_level=100.0,
        next_session_date=T1,
        next_open=100.0,
        prior_close=99.0,
        source_candidate_version="34-candidate-generator-v0.2",
    )
    base.update(kwargs)
    return decide_t1_open_execution(**base)


def test_open_exactly_at_pivot_executes():
    d = _d(next_open=100.0)
    assert d.execution_state == ExecutionState.EXECUTED_T1_OPEN
    assert d.fill_price == 100.0
    assert validate_execution_decision(d) == []


def test_open_just_above_pivot_executes():
    d = _d(next_open=100.01)
    assert d.execution_state == ExecutionState.EXECUTED_T1_OPEN
    assert d.fill_price == 100.01
    assert validate_execution_decision(d) == []


def test_open_exactly_five_percent_executes():
    d = _d(next_open=105.0)
    assert d.execution_state == ExecutionState.EXECUTED_T1_OPEN
    assert d.fill_price == 105.0
    assert validate_execution_decision(d) == []


def test_open_above_five_percent_is_not_chased():
    d = _d(next_open=105.01)
    assert d.execution_state == ExecutionState.MISSED_EXTENDED_AT_OPEN
    assert d.fill_price is None
    assert validate_execution_decision(d) == []


def test_gap_within_buy_zone_executes_at_observed_open():
    d = _d(next_open=103.0, prior_close=99.0)
    assert d.execution_state == ExecutionState.EXECUTED_T1_OPEN
    assert d.gap_above_pivot is True
    assert d.fill_price == 103.0
    assert validate_execution_decision(d) == []


def test_open_below_pivot_has_no_fill():
    d = _d(next_open=99.5)
    assert d.execution_state == ExecutionState.BELOW_PIVOT_AT_OPEN
    assert d.fill_price is None
    assert validate_execution_decision(d) == []


def test_no_next_session_bar():
    d = _d(next_session_date=None, next_open=None)
    assert d.execution_state == ExecutionState.NO_NEXT_SESSION_BAR
    assert d.fill_price is None
    assert validate_execution_decision(d) == []


def test_noneligible_candidate_never_executes():
    d = _d(candidate_stage="BREAKOUT_CONFIRMED", next_open=101.0)
    assert d.execution_state == ExecutionState.NOT_ENTRY_ELIGIBLE
    assert d.fill_price is None
    assert validate_execution_decision(d) == []


def test_stop_reference_uses_actual_fill_not_pivot():
    d = _d(next_open=103.0)
    assert d.initial_stop_reference == 103.0
    assert d.practical_loss_trigger_price == pytest.approx(95.79)
    assert d.legacy_hard_loss_ceiling_price == pytest.approx(94.76)
    assert validate_execution_decision(d) == []


def test_profit_zone_uses_pivot_not_fill():
    d = _d(next_open=103.0)
    assert d.normal_profit_zone_low == pytest.approx(120.0)
    assert d.normal_profit_zone_high == pytest.approx(125.0)
    assert validate_execution_decision(d) == []


def test_noncausal_next_session_date_rejected():
    with pytest.raises(ValueError, match="strictly after"):
        _d(next_session_date=T)
