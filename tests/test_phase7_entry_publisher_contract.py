from datetime import date

from canslim_research.execution_entry_v1 import ExecutionState, decide_t1_open_execution, validate_execution_decision


def test_frozen_entry_executes_at_t1_open_inside_buy_zone():
    d = decide_t1_open_execution(candidate_id="c1", security_id="s1", signal_date=date(2026, 9, 14), candidate_stage="CANSLIM_ELIGIBLE", pivot_level=100.0, next_session_date=date(2026, 9, 15), next_open=103.0, prior_close=101.0, source_candidate_version="34-candidate-generator-v0.2")
    assert d.execution_state == ExecutionState.EXECUTED_T1_OPEN
    assert d.fill_price == 103.0
    assert d.initial_stop_reference == 103.0
    assert validate_execution_decision(d) == []


def test_frozen_entry_rejects_extended_open():
    d = decide_t1_open_execution(candidate_id="c1", security_id="s1", signal_date=date(2026, 9, 14), candidate_stage="CANSLIM_ELIGIBLE", pivot_level=100.0, next_session_date=date(2026, 9, 15), next_open=105.01)
    assert d.execution_state == ExecutionState.MISSED_EXTENDED_AT_OPEN
    assert d.fill_price is None
    assert validate_execution_decision(d) == []


def test_noneligible_candidate_cannot_execute():
    d = decide_t1_open_execution(candidate_id="c1", security_id="s1", signal_date=date(2026, 9, 14), candidate_stage="BREAKOUT_CONFIRMED", pivot_level=100.0, next_session_date=date(2026, 9, 15), next_open=101.0)
    assert d.execution_state == ExecutionState.NOT_ENTRY_ELIGIBLE
    assert d.fill_price is None
    assert validate_execution_decision(d) == []


def test_no_future_bar_is_invented():
    d = decide_t1_open_execution(candidate_id="c1", security_id="s1", signal_date=date(2026, 9, 14), candidate_stage="CANSLIM_ELIGIBLE", pivot_level=100.0, next_session_date=None, next_open=None)
    assert d.execution_state == ExecutionState.NO_NEXT_SESSION_BAR
    assert d.fill_price is None
    assert validate_execution_decision(d) == []
