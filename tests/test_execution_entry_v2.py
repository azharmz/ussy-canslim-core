from datetime import date
from canslim_research.execution_entry_v1 import ExecutionState
from canslim_research.execution_entry_v2 import decide_v2_t1_open_execution, validate_v2_execution_decision

def decide(stage="CANSLIM_V2_ELIGIBLE",open_=102.0):
    return decide_v2_t1_open_execution(candidate_id="c",security_id="s",signal_date=date(2026,9,17),
        candidate_stage=stage,pivot_level=100.0,next_session_date=date(2026,9,18),
        next_open=open_,prior_close=99.0,source_candidate_version="v2")

def test_v2_eligible_executes_at_observed_t1_open_inside_buy_zone():
    d=decide(); assert d.execution_state==ExecutionState.EXECUTED_T1_OPEN
    assert d.fill_price==102.0 and d.fill_date==date(2026,9,18)
    assert d.candidate_stage=="CANSLIM_V2_ELIGIBLE"
    assert validate_v2_execution_decision(d)==[]

def test_v2_eligible_misses_when_t1_open_extended_above_five_percent():
    d=decide(open_=106.0); assert d.execution_state==ExecutionState.MISSED_EXTENDED_AT_OPEN
    assert d.fill_price is None and validate_v2_execution_decision(d)==[]

def test_noneligible_v2_candidate_never_executes():
    d=decide(stage="BREAKOUT_CONFIRMED"); assert d.execution_state==ExecutionState.NOT_ENTRY_ELIGIBLE
    assert d.fill_price is None and validate_v2_execution_decision(d)==[]
