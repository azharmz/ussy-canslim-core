from canslim_research.candidate_v2 import (
    CandidateEvidence,
    DailyBar,
    PatternAssessment,
    build_candidate,
)
from canslim_research.candidate_v2_adapters import (
    AnnualEpsObservation,
    a_screen_state,
    c_screen_state,
    institutional_state,
    l_screen_state,
    m_entry_state,
)


def pattern_row(status="RECOGNIZED", pivot=100.0):
    return {
        "assessment_id": "a1",
        "output_schema_version": "oneil-pattern-output-v2",
        "engine_version": "33-core-p8-frozen-v1",
        "labelled_validation_status": "P8_CONDITIONAL_PASS_FROZEN",
        "security_id": "sec1",
        "ticker": "TEST",
        "asof_date": "2026-09-11",
        "candidate_id": "c1",
        "base_id": "b1",
        "lineage_id": "l1",
        "pattern": "FLAT_BASE",
        "normalized_status": status,
        "native_state": f"FLAT_BASE_{status}",
        "candidate_semantics": "RIGHT_EDGE_OBSERVATION",
        "structural_signature": ["LEFT_HIGH:2026-07-01"],
        "structural_start": "2026-07-01",
        "structural_end": "2026-09-11",
        "pivot_source_date": "2026-07-01" if pivot is not None else None,
        "pivot_level": pivot,
        "depth_pct": 10.0,
        "detector_faults": ["EXAMPLE_FAULT"] if status == "AMBIGUOUS" else [],
        "detector_contract_version": "flat-base-v2",
    }


def bars(breakout_volume=150.0):
    rows = []
    for i in range(50):
        rows.append(DailyBar(f"2026-07-{i+1:02d}", 90, 95, 89, 94, 100.0))
    rows.append(DailyBar("2026-09-11", 99, 102, 98, 101, breakout_volume))
    return rows


def evidence(**overrides):
    values = dict(
        C_screen_state="PASS",
        A_screen_state="PASS",
        L_individual_leadership_state="PASS",
        M_entry_state="ALLOW_NEW_BUYS",
        N_catalyst_state="NOT_IMPLEMENTED",
        I_evidence_state="POSITIVE",
        rs_rating_proxy_percentile=85.0,
        M_market_state="FOLLOW_THROUGH_CONFIRMED",
    )
    values.update(overrides)
    return CandidateEvidence(**values)


def test_rejects_advanced_pattern_from_frozen_contract():
    row = pattern_row()
    row["pattern"] = "ASCENDING_BASE"
    try:
        PatternAssessment.from_mapping(row)
    except ValueError as exc:
        assert "outside frozen #33 core contract" in str(exc)
    else:
        raise AssertionError("advanced P6 pattern must not enter #34 production consumer")


def test_ambiguous_is_preserved_and_not_promoted():
    pattern = PatternAssessment.from_mapping(pattern_row(status="AMBIGUOUS"))
    result = build_candidate(pattern, bars(), evidence())
    assert result.pattern_status == "AMBIGUOUS"
    assert result.candidate_stage == "NOT_ELIGIBLE"
    assert result.detector_faults == ("EXAMPLE_FAULT",)
    assert "PATTERN_AMBIGUOUS" in result.eligibility_reason_codes


def test_recognized_confirmed_breakout_can_be_eligible_with_all_mandatory_letters():
    pattern = PatternAssessment.from_mapping(pattern_row())
    result = build_candidate(pattern, bars(150.0), evidence())
    assert result.pivot_crossed_intraday is True
    assert result.first_tradeable_daily_bar_crossed_pivot is True
    assert result.breakout_date == "2026-09-11"
    assert result.close_above_pivot is True
    assert result.close_position_quality == 0.75
    assert result.volume_ratio == 1.5
    assert result.volume_confirmation_state == "CONFIRMED_ON_BREAKOUT"
    assert result.volume_confirmation_date == "2026-09-11"
    assert result.N_price_state == "PASS"
    assert result.S_evidence_state == "POSITIVE"
    assert result.I_evidence_state == "POSITIVE"
    assert result.N_catalyst_state == "NOT_IMPLEMENTED"
    assert result.rs_rating_proxy_percentile == 85.0
    assert result.M_market_state == "FOLLOW_THROUGH_CONFIRMED"
    assert result.candidate_stage == "CANSLIM_ELIGIBLE"
    assert result.eligibility_reason_codes == ()


def test_catalyst_not_implemented_is_evidence_only_not_a_mandatory_gate():
    pattern = PatternAssessment.from_mapping(pattern_row())
    result = build_candidate(pattern, bars(), evidence(N_catalyst_state="NOT_IMPLEMENTED"))
    assert result.candidate_stage == "CANSLIM_ELIGIBLE"


def test_institutional_not_evaluable_blocks_full_eligibility():
    pattern = PatternAssessment.from_mapping(pattern_row())
    result = build_candidate(pattern, bars(), evidence(I_evidence_state="NOT_EVALUABLE"))
    assert result.candidate_stage == "BREAKOUT_CONFIRMED"
    assert "I_NOT_PASS:NOT_EVALUABLE" in result.eligibility_reason_codes


def test_low_volume_cross_remains_pivot_crossed():
    pattern = PatternAssessment.from_mapping(pattern_row())
    result = build_candidate(pattern, bars(120.0), evidence())
    assert result.pivot_crossed_intraday is True
    assert result.volume_confirmation_state == "PENDING_CONFIRMATION"
    assert result.S_evidence_state == "NEUTRAL"
    assert result.candidate_stage == "PIVOT_CROSSED"


def test_prior_breakout_is_not_recounted_at_current_asof():
    row = pattern_row()
    row["structural_end"] = "2026-09-01"
    pattern = PatternAssessment.from_mapping(row)
    series = [DailyBar(f"2026-08-{i+1:02d}", 90, 95, 89, 94, 100.0) for i in range(31)]
    series += [
        DailyBar("2026-09-01", 95, 99, 94, 98, 100.0),
        DailyBar("2026-09-02", 99, 101, 98, 100.5, 150.0),
        DailyBar("2026-09-11", 101, 103, 100, 102, 160.0),
    ]
    result = build_candidate(pattern, series, evidence())
    assert result.prior_cross_after_structure is True
    assert result.pivot_crossed_intraday is False
    assert result.first_tradeable_daily_bar_crossed_pivot is False
    assert result.breakout_date is None
    assert result.candidate_stage == "PIVOT_DEFINED"
    assert "BREAKOUT_ALREADY_OCCURRED" in result.eligibility_reason_codes


def test_failed_mandatory_evidence_does_not_erase_confirmed_breakout():
    pattern = PatternAssessment.from_mapping(pattern_row())
    result = build_candidate(pattern, bars(), evidence(A_screen_state="NOT_EVALUABLE"))
    assert result.volume_confirmation_state == "CONFIRMED_ON_BREAKOUT"
    assert result.candidate_stage == "BREAKOUT_CONFIRMED"
    assert "A_NOT_PASS:NOT_EVALUABLE" in result.eligibility_reason_codes


def test_c_adapter_requires_eps_and_revenue_and_is_pit_safe():
    assert c_screen_state(quarterly_eps_yoy=0.30, quarterly_revenue_yoy=0.35, available_on="2026-08-01", asof_date="2026-09-11")[0] == "PASS"
    assert c_screen_state(quarterly_eps_yoy=0.30, quarterly_revenue_yoy=0.20, available_on="2026-08-01", asof_date="2026-09-11")[0] == "FAIL"
    assert c_screen_state(quarterly_eps_yoy=0.40, quarterly_revenue_yoy=None, available_on="2026-08-01", asof_date="2026-09-11")[0] == "NOT_EVALUABLE"
    assert c_screen_state(quarterly_eps_yoy=0.40, quarterly_revenue_yoy=0.40, available_on="2026-09-12", asof_date="2026-09-11")[0] == "NOT_EVALUABLE"


def test_a_adapter_requires_latest_three_consecutive_annual_eps_yoy_states():
    rows = [
        AnnualEpsObservation(2022, 0.10, "2023-02-15"),
        AnnualEpsObservation(2023, 0.30, "2024-02-15"),
        AnnualEpsObservation(2024, 0.31, "2025-02-15"),
        AnnualEpsObservation(2025, 0.32, "2026-02-15"),
    ]
    state, latest_growth, _ = a_screen_state(rows, asof_date="2026-09-11")
    assert state == "PASS"
    assert latest_growth == 0.32


def test_a_adapter_fails_closed_on_nonconsecutive_fy():
    rows = [
        AnnualEpsObservation(2022, 0.30, "2023-02-15"),
        AnnualEpsObservation(2024, 0.31, "2025-02-15"),
        AnnualEpsObservation(2025, 0.32, "2026-02-15"),
    ]
    state, _, reason = a_screen_state(rows, asof_date="2026-09-11")
    assert state == "NOT_EVALUABLE"
    assert reason == "NON_CONSECUTIVE_ANNUAL_FY"


def test_l_m_and_i_adapters_preserve_theory_roles():
    assert l_screen_state(80.0)[0] == "PASS"
    assert l_screen_state(79.99)[0] == "FAIL"
    assert m_entry_state("CONFIRMED_UPTREND")[0] == "ALLOW_NEW_BUYS"
    assert m_entry_state("UPTREND_UNDER_PRESSURE")[0] == "CAUTION"
    assert m_entry_state("CORRECTION")[0] == "BLOCK_NEW_BUYS"
    assert institutional_state(fund_count_latest=12, fund_count_prior=10, available_on="2026-08-01", asof_date="2026-09-11")[0] == "POSITIVE"
    assert institutional_state(fund_count_latest=8, fund_count_prior=10, available_on="2026-08-01", asof_date="2026-09-11")[0] == "NEGATIVE"
