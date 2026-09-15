from canslim_research.execution_entry_v1 import ExecutionState
from scripts.publish_production_lifecycle import is_executable_entry, publication_status


def test_zero_population_is_explicitly_blocked():
    assert publication_status(0) == "BLOCKED_ON_PRODUCTION_ENTRY_POPULATION"


def test_population_requires_real_acceptance():
    assert publication_status(1) == "REQUIRES_POPULATED_LIFECYCLE_ACCEPTANCE"


def test_frozen_t1_open_state_is_executable_for_lifecycle_boundary():
    row = {"execution_state": ExecutionState.EXECUTED_T1_OPEN.value}
    assert is_executable_entry(row) is True


def test_legacy_or_invented_executed_alias_is_not_accepted():
    assert is_executable_entry({"execution_state": "EXECUTED"}) is False


def test_non_fill_entry_state_is_not_executable():
    row = {"execution_state": ExecutionState.BELOW_PIVOT_AT_OPEN.value}
    assert is_executable_entry(row) is False
