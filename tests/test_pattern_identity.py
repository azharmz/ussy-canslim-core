from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from canslim_research.pattern_engine import PatternCandidate  # noqa: E402
from canslim_research.pattern_identity import cluster_base_identities  # noqa: E402


def _candidate(*, end: str, duration: int, confidence: float = 0.8, pattern_type: str = "DOUBLE_BOTTOM"):
    if pattern_type == "DOUBLE_BOTTOM":
        landmarks = {
            "first_bottom": {"date": "2023-06-27", "price": 416.87},
            "middle_peak": {"date": "2023-07-19", "price": 465.67},
            "second_bottom": {"date": "2023-08-18", "price": 418.51},
        }
        pivot_type = "middle_peak"
        pivot_date = "2023-07-19"
    else:
        landmarks = {
            "flat_left_high": {"date": "2023-07-19", "price": 465.67},
            "base_low": {"date": "2023-08-18", "price": 418.51},
        }
        pivot_type = "flat_left_high"
        pivot_date = "2023-07-19"
    return PatternCandidate(
        pattern_type=pattern_type,
        pattern_evidence_state="PASS",
        confidence=confidence,
        base_start_date="2023-06-02",
        base_end_or_breakout_ready_date=end,
        base_duration_sessions=duration,
        base_depth_pct=0.12,
        prior_uptrend_state="PASS",
        pivot_level=465.67,
        pivot_landmark_type=pivot_type,
        pivot_source_date=pivot_date,
        landmarks=landmarks,
    )


def test_same_landmarks_collapse_rolling_windows_to_one_base():
    candidates = [
        _candidate(end="2023-08-28", duration=60),
        _candidate(end="2023-09-05", duration=65),
        _candidate(end="2023-09-12", duration=70),
    ]
    identities = cluster_base_identities(candidates, security_id="US8716071076")
    assert len(identities) == 1
    base = identities[0]
    assert base.member_window_count == 3
    assert base.first_recognized_date == "2023-08-28"
    assert base.last_supported_date == "2023-09-12"
    assert base.recognition_dates == ["2023-08-28", "2023-09-05", "2023-09-12"]


def test_base_id_is_stable_across_input_order():
    a = _candidate(end="2023-08-28", duration=60)
    b = _candidate(end="2023-09-05", duration=65)
    first = cluster_base_identities([a, b], security_id="US8716071076")[0]
    second = cluster_base_identities([b, a], security_id="US8716071076")[0]
    assert first.base_id == second.base_id
    assert first.structural_signature == second.structural_signature


def test_different_pattern_type_remains_separate_identity_even_on_same_dates():
    db = _candidate(end="2023-08-28", duration=60, pattern_type="DOUBLE_BOTTOM")
    flat = _candidate(end="2023-08-28", duration=35, pattern_type="FLAT_BASE")
    identities = cluster_base_identities([db, flat], security_id="US8716071076")
    assert len(identities) == 2
    assert {item.pattern_type for item in identities} == {"DOUBLE_BOTTOM", "FLAT_BASE"}


def test_representative_prefers_highest_confidence_then_longer_window():
    candidates = [
        _candidate(end="2023-08-28", duration=60, confidence=0.82),
        _candidate(end="2023-09-05", duration=65, confidence=0.88),
        _candidate(end="2023-09-12", duration=70, confidence=0.88),
    ]
    base = cluster_base_identities(candidates, security_id="US8716071076")[0]
    assert base.confidence == 0.88
    assert base.representative["base_duration_sessions"] == 70


def test_security_id_is_part_of_stable_identity():
    candidate = _candidate(end="2023-08-28", duration=60)
    left = cluster_base_identities([candidate], security_id="SEC-A")[0]
    right = cluster_base_identities([candidate], security_id="SEC-B")[0]
    assert left.base_id != right.base_id
