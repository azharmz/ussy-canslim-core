from canslim_research.candidate_v2 import (
    CandidateEvidence,
    DailyBar,
    PatternAssessment,
    build_candidate,
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


def evidence():
    return CandidateEvidence("PASS", "PASS", "PASS", "ALLOW_NEW_BUYS")


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


def test_recognized_confirmed_breakout_can_be_eligible():
    pattern = PatternAssessment.from_mapping(pattern_row())
    result = build_candidate(pattern, bars(150.0), evidence())
    assert result.pivot_crossed_intraday is True
    assert result.close_above_pivot is True
    assert result.volume_ratio == 1.5
    assert result.volume_confirmation_state == "CONFIRMED_ON_BREAKOUT"
    assert result.candidate_stage == "CANSLIM_ELIGIBLE"


def test_low_volume_cross_remains_pivot_crossed():
    pattern = PatternAssessment.from_mapping(pattern_row())
    result = build_candidate(pattern, bars(120.0), evidence())
    assert result.pivot_crossed_intraday is True
    assert result.volume_confirmation_state == "PENDING_CONFIRMATION"
    assert result.candidate_stage == "PIVOT_CROSSED"


def test_failed_core_evidence_does_not_erase_confirmed_breakout():
    pattern = PatternAssessment.from_mapping(pattern_row())
    ev = CandidateEvidence("PASS", "NOT_EVALUABLE", "PASS", "ALLOW_NEW_BUYS")
    result = build_candidate(pattern, bars(), ev)
    assert result.volume_confirmation_state == "CONFIRMED_ON_BREAKOUT"
    assert result.candidate_stage == "BREAKOUT_CONFIRMED"
    assert "A_CORE_NOT_PASS" in result.eligibility_reason_codes
