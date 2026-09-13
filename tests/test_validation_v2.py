from dataclasses import replace

from canslim_research.candidate_v2 import CandidateEvidence, DailyBar, PatternAssessment, build_candidate
from canslim_research.validation_v2 import audit_candidate_record


def pattern(status="RECOGNIZED"):
    return PatternAssessment.from_mapping({
        "assessment_id": "a1",
        "output_schema_version": "oneil-pattern-output-v2",
        "engine_version": "33-core-p8-frozen-v1",
        "labelled_validation_status": "P8_CONDITIONAL_PASS_FROZEN",
        "security_id": "s1",
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
        "pivot_source_date": "2026-07-01",
        "pivot_level": 100.0,
        "depth_pct": 10.0,
        "detector_faults": [],
        "detector_contract_version": "flat-base-v2",
    })


def bars(volume=150.0):
    rows = [DailyBar(f"2026-07-{i+1:02d}", 90, 95, 89, 94, 100.0) for i in range(50)]
    rows.append(DailyBar("2026-09-11", 99, 102, 98, 101, volume))
    return rows


def evidence():
    return CandidateEvidence("PASS", "PASS", "PASS", "ALLOW_NEW_BUYS")


def test_valid_eligible_record_has_no_findings():
    record = build_candidate(pattern(), bars(), evidence())
    assert record.candidate_stage == "CANSLIM_ELIGIBLE"
    assert audit_candidate_record(record) == ()


def test_validation_catches_status_promotion():
    record = build_candidate(pattern("AMBIGUOUS"), bars(), evidence())
    bad = replace(record, candidate_stage="CANSLIM_ELIGIBLE")
    codes = {x.code for x in audit_candidate_record(bad)}
    assert "STATUS_PROMOTION" in codes
    assert "ELIGIBILITY_GATE_INVALID" in codes


def test_validation_catches_invalid_volume_confirmation():
    record = build_candidate(pattern(), bars(120.0), evidence())
    bad = replace(record, candidate_stage="BREAKOUT_CONFIRMED", volume_confirmation_state="CONFIRMED_ON_BREAKOUT", volume_ratio=1.20, volume_confirmation_date=record.breakout_date)
    codes = {x.code for x in audit_candidate_record(bad)}
    assert "VOLUME_CONFIRMATION_INVALID" in codes


def test_validation_catches_recounted_prior_breakout():
    record = build_candidate(pattern(), bars(), evidence())
    bad = replace(record, prior_cross_after_structure=True, pivot_crossed_intraday=True)
    codes = {x.code for x in audit_candidate_record(bad)}
    assert "REPEATED_BREAKOUT_RECOUNT" in codes
