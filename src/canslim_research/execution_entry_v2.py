"""Shadow CAN SLIM v2 adapter for the frozen causal T+1-open execution engine.

Execution mechanics are unchanged; only the accepted upstream candidate-stage
identity is translated explicitly at this boundary.
"""
from __future__ import annotations
from dataclasses import replace
from datetime import date
from typing import Optional
from canslim_research.execution_entry_v1 import (
    ExecutionDecision, ExecutionState, decide_t1_open_execution, validate_execution_decision,
)

V2_ELIGIBLE_STAGE="CANSLIM_V2_ELIGIBLE"
LEGACY_ELIGIBLE_STAGE="CANSLIM_ELIGIBLE"
EXECUTION_V2_ADAPTER_VERSION="canslim-v2-to-36-execution-entry-v1"


def decide_v2_t1_open_execution(*, candidate_id:str, security_id:str, signal_date:date,
    candidate_stage:str, pivot_level:Optional[float], next_session_date:Optional[date],
    next_open:Optional[float], prior_close:Optional[float]=None,
    source_candidate_version:Optional[str]=None) -> ExecutionDecision:
    if candidate_stage != V2_ELIGIBLE_STAGE:
        return decide_t1_open_execution(candidate_id=candidate_id,security_id=security_id,
            signal_date=signal_date,candidate_stage=candidate_stage,pivot_level=pivot_level,
            next_session_date=next_session_date,next_open=next_open,prior_close=prior_close,
            source_candidate_version=source_candidate_version)
    d=decide_t1_open_execution(candidate_id=candidate_id,security_id=security_id,
        signal_date=signal_date,candidate_stage=LEGACY_ELIGIBLE_STAGE,pivot_level=pivot_level,
        next_session_date=next_session_date,next_open=next_open,prior_close=prior_close,
        source_candidate_version=source_candidate_version)
    return replace(d,candidate_stage=V2_ELIGIBLE_STAGE)


def validate_v2_execution_decision(d:ExecutionDecision)->list[str]:
    # Frozen validator expects its historical stage spelling. Translate only
    # for validation; prices, dates, buy zone and execution state are untouched.
    translated=replace(d,candidate_stage=LEGACY_ELIGIBLE_STAGE) if d.candidate_stage==V2_ELIGIBLE_STAGE else d
    return validate_execution_decision(translated)
