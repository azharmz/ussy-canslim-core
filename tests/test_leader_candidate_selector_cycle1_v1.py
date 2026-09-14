from canslim_research.leader_candidate_selector_cycle1_v1 import (
    BENCHMARK_ID,
    NEAR_HIGH_RATIO,
    RS_THRESHOLD,
    VERSION,
    CandidateState,
    MembershipRecord,
    select_candidate_cohort,
)


def hist(start: float, end: float, n: int = 252):
    step = (end - start) / (n - 1)
    return [start + i * step for i in range(n)]


def test_constants_are_frozen():
    assert VERSION == "54-cycle1-candidate-leader-selector-v1"
    assert BENCHMARK_ID == "SP500"
    assert RS_THRESHOLD == 80.0
    assert NEAR_HIGH_RATIO == 0.90


def test_top_relative_strength_near_high_is_candidate():
    membership = [MembershipRecord(str(i), f"S{i}") for i in range(1, 6)]
    prices = {
        "1": hist(100, 105),
        "2": hist(100, 110),
        "3": hist(100, 115),
        "4": hist(100, 120),
        "5": hist(100, 130),
    }
    out = select_candidate_cohort(membership, prices, hist(100, 105))
    result = {r.security_id: r for r in out}
    assert result["5"].state == CandidateState.LEADER_CANDIDATE.value
    assert result["5"].rs_percentile_252 == 100.0


def test_rs_80_boundary_passes():
    membership = [MembershipRecord(str(i), f"S{i}") for i in range(1, 5 + 1)]
    prices = {str(i): hist(100, 100 + i * 5) for i in range(1, 6)}
    out = select_candidate_cohort(membership, prices, hist(100, 100))
    result = {r.security_id: r for r in out}
    assert result["4"].rs_percentile_252 == 80.0
    assert result["4"].state == CandidateState.LEADER_CANDIDATE.value


def test_below_rs_threshold_fails():
    membership = [MembershipRecord(str(i), f"S{i}") for i in range(1, 6)]
    prices = {str(i): hist(100, 100 + i * 5) for i in range(1, 6)}
    out = select_candidate_cohort(membership, prices, hist(100, 100))
    result = {r.security_id: r for r in out}
    assert result["3"].rs_percentile_252 == 60.0
    assert result["3"].state == CandidateState.NOT_LEADER_CANDIDATE.value
    assert "RS_BELOW_80" in result["3"].reason


def test_near_high_90_boundary_passes():
    membership = [MembershipRecord(str(i), f"S{i}") for i in range(1, 6)]
    prices = {str(i): hist(100, 105 + i * 5) for i in range(1, 6)}
    special = hist(100, 200)
    special[-1] = 180.0
    prices["5"] = special
    out = select_candidate_cohort(membership, prices, hist(100, 100))
    result = {r.security_id: r for r in out}
    assert abs(result["5"].near_high_ratio_252 - 0.9) < 1e-12
    assert result["5"].state == CandidateState.LEADER_CANDIDATE.value


def test_below_near_high_threshold_fails_even_with_top_rs():
    membership = [MembershipRecord(str(i), f"S{i}") for i in range(1, 6)]
    prices = {str(i): hist(100, 105 + i * 5) for i in range(1, 6)}
    special = hist(100, 200)
    special[-1] = 179.0
    prices["5"] = special
    out = select_candidate_cohort(membership, prices, hist(100, 100))
    result = {r.security_id: r for r in out}
    assert result["5"].state == CandidateState.NOT_LEADER_CANDIDATE.value
    assert "PRICE_BELOW_90PCT_OF_252_HIGH" in result["5"].reason


def test_insufficient_stock_history_is_not_evaluable():
    membership = [MembershipRecord("1", "S1")]
    out = select_candidate_cohort(membership, {"1": hist(100, 120, 251)}, hist(100, 105))
    assert out[0].state == CandidateState.NOT_EVALUABLE.value
    assert out[0].reason == "STOCK_HISTORY_NOT_EVALUABLE"


def test_insufficient_benchmark_history_makes_all_not_evaluable():
    membership = [MembershipRecord("1", "S1"), MembershipRecord("2", "S2")]
    prices = {"1": hist(100, 120), "2": hist(100, 130)}
    out = select_candidate_cohort(membership, prices, hist(100, 105, 251))
    assert all(r.state == CandidateState.NOT_EVALUABLE.value for r in out)
    assert all(r.reason == "BENCHMARK_HISTORY_NOT_EVALUABLE" for r in out)


def test_etf_test_issue_and_invalid_membership_are_not_evaluable():
    membership = [
        MembershipRecord("1", "ETF", is_etf=True),
        MembershipRecord("2", "TEST", is_test_issue=True),
        MembershipRecord("3", "BAD", membership_pit_valid=False),
    ]
    prices = {r.security_id: hist(100, 120) for r in membership}
    out = select_candidate_cohort(membership, prices, hist(100, 105))
    reasons = {r.security_id: r.reason for r in out}
    assert reasons == {
        "1": "ETF_EXCLUDED",
        "2": "TEST_ISSUE_EXCLUDED",
        "3": "MEMBERSHIP_PIT_INVALID",
    }


def test_future_values_outside_latest_252_are_not_used():
    membership = [MembershipRecord("1", "S1"), MembershipRecord("2", "S2")]
    # Earlier values differ wildly; only the latest 252 observations define T-window.
    prices_a = [9999.0] + hist(100, 120)
    prices_b = [1.0] + hist(100, 110)
    out = select_candidate_cohort(membership, {"1": prices_a, "2": prices_b}, hist(100, 100))
    result = {r.security_id: r for r in out}
    assert result["1"].relative_return_252 > result["2"].relative_return_252


def test_ties_receive_same_upper_ecdf_percentile():
    membership = [MembershipRecord("1", "A"), MembershipRecord("2", "B")]
    prices = {"1": hist(100, 120), "2": hist(100, 120)}
    out = select_candidate_cohort(membership, prices, hist(100, 100))
    assert out[0].rs_percentile_252 == 100.0
    assert out[1].rs_percentile_252 == 100.0
