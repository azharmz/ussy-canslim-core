from canslim_research.leader_cycle1_data_readiness_v1 import DataReadinessInput, evaluate_cycle1_data_readiness


def test_restricted_ohlcv_blocks_selector():
    r = evaluate_cycle1_data_readiness(DataReadinessInput(8000, 1300, 1200, 1000, "RESTRICTED_USSY_CURRENT", True, True))
    assert r.status == "BLOCKED_ON_BROAD_MARKET_OHLCV"
    assert r.selector_execution_authorized is False


def test_broad_market_pit_allows_selector_when_histories_exist():
    r = evaluate_cycle1_data_readiness(DataReadinessInput(8000, 7600, 7300, 7500, "BROAD_MARKET_PIT", True, True))
    assert r.status == "READY_FOR_PROSPECTIVE_SELECTOR"
    assert r.selector_execution_authorized is True
    assert abs(r.evaluable_coverage - 7300 / 8000) < 1e-12


def test_invalid_membership_is_not_evaluable():
    r = evaluate_cycle1_data_readiness(DataReadinessInput(8000, 7600, 7300, 7500, "BROAD_MARKET_PIT", False, True))
    assert r.status == "NOT_EVALUABLE"
    assert r.reason == "MEMBERSHIP_PIT_INVALID"


def test_invalid_benchmark_is_not_evaluable():
    r = evaluate_cycle1_data_readiness(DataReadinessInput(8000, 7600, 7300, 7500, "BROAD_MARKET_PIT", True, False))
    assert r.status == "NOT_EVALUABLE"
    assert r.reason == "BENCHMARK_PIT_INVALID"


def test_zero_history_blocks_even_with_broad_scope():
    r = evaluate_cycle1_data_readiness(DataReadinessInput(8000, 0, 0, 0, "BROAD_MARKET_PIT", True, True))
    assert r.status == "NOT_EVALUABLE"
    assert r.reason == "NO_252_BAR_BROAD_MARKET_HISTORIES"


def test_empty_membership_is_not_evaluable():
    r = evaluate_cycle1_data_readiness(DataReadinessInput(0, 100, 100, 100, "BROAD_MARKET_PIT", True, True))
    assert r.status == "NOT_EVALUABLE"
