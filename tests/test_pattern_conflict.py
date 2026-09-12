from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from canslim_research.pattern_conflict import detect_pattern_conflicts  # noqa: E402
from canslim_research.pattern_identity import BaseIdentity  # noqa: E402
from canslim_research.pattern_lineage import BaseLineage  # noqa: E402


def _identity(
    *,
    base_id: str,
    pattern_type: str,
    pivot_date: str,
    pivot_level: float,
    landmarks: dict,
) -> BaseIdentity:
    return BaseIdentity(
        base_id=base_id,
        security_id="SEC",
        pattern_type=pattern_type,
        structural_signature=[f"{pattern_type}:{base_id}"],
        first_recognized_date="2023-08-01",
        last_supported_date="2023-09-01",
        member_window_count=1,
        pattern_evidence_state="PASS",
        confidence=0.85,
        representative={
            "pattern_type": pattern_type,
            "pivot_source_date": pivot_date,
            "pivot_level": pivot_level,
            "landmarks": landmarks,
        },
        recognition_dates=["2023-08-01"],
        pattern_engine_version="test",
    )


def _lineage(*, lineage_id: str, base_id: str, pattern_type: str, start="2023-08-01", end="2023-09-01"):
    return BaseLineage(
        lineage_id=lineage_id,
        security_id="SEC",
        pattern_type=pattern_type,
        anchor_signature=[lineage_id],
        member_base_ids=[base_id],
        first_recognized_date=start,
        last_supported_date=end,
        member_identity_count=1,
        pattern_evidence_state="PASS",
        confidence=0.85,
        representative_base_id=base_id,
    )


def test_flat_and_double_bottom_overlap_is_explicit_not_silently_resolved():
    flat_id = _identity(
        base_id="flat",
        pattern_type="FLAT_BASE",
        pivot_date="2023-07-19",
        pivot_level=465.67,
        landmarks={"flat_left_high": {"date": "2023-07-19", "price": 465.67}},
    )
    db_id = _identity(
        base_id="db",
        pattern_type="DOUBLE_BOTTOM",
        pivot_date="2023-07-19",
        pivot_level=465.67,
        landmarks={
            "first_bottom": {"date": "2023-06-27", "price": 416.87},
            "middle_peak": {"date": "2023-07-19", "price": 465.67},
            "second_bottom": {"date": "2023-08-18", "price": 418.51},
        },
    )
    conflicts = detect_pattern_conflicts(
        [
            _lineage(lineage_id="flat-lineage", base_id="flat", pattern_type="FLAT_BASE"),
            _lineage(lineage_id="db-lineage", base_id="db", pattern_type="DOUBLE_BOTTOM"),
        ],
        [flat_id, db_id],
    )
    assert len(conflicts) == 1
    conflict = conflicts[0]
    assert conflict.relationship == "OVERLAPPING_MORPHOLOGY"
    assert conflict.resolution_state == "UNRESOLVED"


def test_nonoverlapping_support_intervals_do_not_conflict():
    flat_id = _identity(
        base_id="flat",
        pattern_type="FLAT_BASE",
        pivot_date="2023-07-19",
        pivot_level=465.67,
        landmarks={},
    )
    db_id = _identity(
        base_id="db",
        pattern_type="DOUBLE_BOTTOM",
        pivot_date="2023-07-19",
        pivot_level=465.67,
        landmarks={},
    )
    conflicts = detect_pattern_conflicts(
        [
            _lineage(lineage_id="flat-lineage", base_id="flat", pattern_type="FLAT_BASE", start="2023-07-01", end="2023-07-15"),
            _lineage(lineage_id="db-lineage", base_id="db", pattern_type="DOUBLE_BOTTOM", start="2023-08-01", end="2023-09-01"),
        ],
        [flat_id, db_id],
    )
    assert conflicts == []


def test_cup_handle_and_no_handle_share_explicit_hierarchy_without_winner():
    root = {
        "left_peak": {"date": "2023-01-10", "price": 100.0},
        "cup_low": {"date": "2023-02-10", "price": 75.0},
    }
    no_handle = _identity(
        base_id="cup",
        pattern_type="CUP_WITHOUT_HANDLE",
        pivot_date="2023-01-10",
        pivot_level=100.0,
        landmarks={**root, "right_side_high": {"date": "2023-03-10", "price": 99.0}},
    )
    with_handle = _identity(
        base_id="cwh",
        pattern_type="CUP_WITH_HANDLE",
        pivot_date="2023-03-15",
        pivot_level=98.0,
        landmarks={
            **root,
            "right_side_high": {"date": "2023-03-10", "price": 99.0},
            "handle_high": {"date": "2023-03-15", "price": 98.0},
            "handle_low": {"date": "2023-03-17", "price": 94.0},
        },
    )
    conflicts = detect_pattern_conflicts(
        [
            _lineage(lineage_id="cup-lineage", base_id="cup", pattern_type="CUP_WITHOUT_HANDLE"),
            _lineage(lineage_id="cwh-lineage", base_id="cwh", pattern_type="CUP_WITH_HANDLE"),
        ],
        [no_handle, with_handle],
    )
    assert len(conflicts) == 1
    assert conflicts[0].relationship == "CUP_FAMILY_HIERARCHY"
    assert conflicts[0].resolution_state == "UNRESOLVED_EXPLICIT_HIERARCHY"
