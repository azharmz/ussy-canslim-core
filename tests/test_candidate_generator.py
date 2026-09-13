from canslim_research.candidate_generator import DailyBar, generate_candidate


def pattern(status="RECOGNIZED", pattern_type="FLAT_BASE", pivot=100.0):
    return {
        "base_id": "b1",
        "pattern_type": pattern_type,
        "status": status,
        "pivot_level": pivot,
        "fault_flags": ["EXAMPLE_FAULT"] if status == "AMBIGUOUS" else [],
        "pattern_engine_version": "33-core-p8-frozen-v1",
    }


def test_ambiguous_pattern_is_preserved_not_promoted():
    out = generate_candidate(pattern(status="AMBIGUOUS"), DailyBar(99, 102, 98, 101, 200), [100] * 50)
    assert out["candidate_stage"] == "NOT_EVALUABLE"
    assert out["status"] == "AMBIGUOUS"
    assert out["fault_flags"] == ["EXAMPLE_FAULT"]
    assert "PATTERN_AMBIGUOUS" in out["eligibility_reason_codes"]


def test_pivot_cross_is_distinct_from_close_hold():
    out = generate_candidate(pattern(), DailyBar(99, 101, 98, 99.5, 100), [100] * 50)
    assert out["candidate_stage"] == "PIVOT_CROSSED"
    assert out["pivot_crossed_intraday"] is True
    assert out["close_above_pivot"] is False


def test_breakout_volume_uses_prior_50_only():
    out = generate_candidate(pattern(), DailyBar(100, 103, 99, 102, 140), [100] * 50)
    assert out["volume_avg_50_prior"] == 100
    assert out["volume_ratio"] == 1.4
    assert out["volume_confirmation_state"] == "CONFIRMED_ON_BREAKOUT"
    assert out["candidate_stage"] == "BREAKOUT_CONFIRMED"


def test_full_minimum_contract_reaches_canslim_eligible():
    out = generate_candidate(
        pattern(), DailyBar(100, 103, 99, 102, 150), [100] * 50,
        C_screen_state="PASS", A_screen_state="PASS",
        L_individual_leadership_state="STRONG", M_entry_state="ALLOW_NEW_BUYS",
    )
    assert out["candidate_stage"] == "CANSLIM_ELIGIBLE"


def test_advanced_pattern_cannot_enter_frozen_core_path():
    out = generate_candidate(pattern(pattern_type="ASCENDING_BASE"), DailyBar(100, 103, 99, 102, 150), [100] * 50)
    assert out["candidate_stage"] == "NOT_EVALUABLE"
    assert "PATTERN_OUTSIDE_FROZEN_CORE" in out["eligibility_reason_codes"]


def test_rejects_noncanonical_pattern_engine():
    p = pattern()
    p["pattern_engine_version"] = "legacy-parent-engine"
    try:
        generate_candidate(p, DailyBar(100, 103, 99, 102, 150), [100] * 50)
    except ValueError as exc:
        assert "unsupported pattern engine" in str(exc)
    else:
        raise AssertionError("legacy engine must be rejected")
