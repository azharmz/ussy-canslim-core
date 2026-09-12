from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from canslim_research.pattern_identity import BaseIdentity  # noqa: E402
from canslim_research.pattern_lineage import cluster_base_lineages  # noqa: E402


def _identity(
    *,
    base_id: str,
    pattern_type: str = "FLAT_BASE",
    pivot_date: str = "2023-07-19",
    pivot_price: float = 465.67,
    low_date: str = "2023-08-18",
    first_recognized: str = "2023-08-18",
    last_supported: str = "2023-08-28",
    confidence: float = 0.82,
    state: str = "PASS",
) -> BaseIdentity:
    if pattern_type == "FLAT_BASE":
        landmarks = {
            "flat_left_high": {"date": pivot_date, "price": pivot_price},
            "base_low": {"date": low_date, "price": 418.51},
        }
        signature = [f"flat_left_high:{pivot_date}", f"base_low:{low_date}"]
    else:
        landmarks = {
            "first_bottom": {"date": "2023-06-27", "price": 416.87},
            "middle_peak": {"date": "2023-07-19", "price": 465.67},
            "second_bottom": {"date": low_date, "price": 418.51},
        }
        signature = [
            "first_bottom:2023-06-27",
            "middle_peak:2023-07-19",
            f"second_bottom:{low_date}",
        ]
    return BaseIdentity(
        base_id=base_id,
        security_id="US8716071076",
        pattern_type=pattern_type,
        structural_signature=signature,
        first_recognized_date=first_recognized,
        last_supported_date=last_supported,
        member_window_count=3,
        pattern_evidence_state=state,
        confidence=confidence,
        representative={
            "pattern_type": pattern_type,
            "pivot_level": pivot_price,
            "pivot_source_date": pivot_date,
            "landmarks": landmarks,
        },
        recognition_dates=[first_recognized, last_supported],
        pattern_engine_version="test",
    )


def test_flat_base_low_evolution_collapses_under_same_pivot_anchor():
    items = [
        _identity(base_id="a", low_date="2023-08-11"),
        _identity(base_id="b", low_date="2023-08-17"),
        _identity(base_id="c", low_date="2023-08-18"),
    ]
    lineages = cluster_base_lineages(items)
    assert len(lineages) == 1
    assert lineages[0].member_identity_count == 3
    assert lineages[0].member_base_ids == ["a", "b", "c"]


def test_flat_base_adjacent_pivot_dates_merge_only_when_price_is_close():
    close = [
        _identity(base_id="a", pivot_date="2023-07-17", pivot_price=462.85),
        _identity(base_id="b", pivot_date="2023-07-19", pivot_price=465.67),
    ]
    far_price = _identity(base_id="c", pivot_date="2023-07-18", pivot_price=500.0)
    assert len(cluster_base_lineages(close)) == 1
    assert len(cluster_base_lineages(close + [far_price])) == 2


def test_lineage_id_is_prefix_stable_when_higher_confidence_member_arrives_later():
    early = _identity(
        base_id="early",
        pivot_date="2023-07-17",
        pivot_price=462.85,
        first_recognized="2023-07-17",
        last_supported="2023-07-17",
        confidence=0.80,
    )
    later = _identity(
        base_id="later",
        pivot_date="2023-07-19",
        pivot_price=465.67,
        first_recognized="2023-08-18",
        last_supported="2023-09-01",
        confidence=0.90,
    )
    prefix = cluster_base_lineages([early])[0]
    full = cluster_base_lineages([early, later])[0]
    assert prefix.lineage_id == full.lineage_id
    assert full.representative_base_id == "later"
    assert full.anchor_signature == ["flat_left_high:2023-07-17"]


def test_double_bottom_second_low_can_evolve_without_creating_new_lineage():
    items = [
        _identity(base_id="a", pattern_type="DOUBLE_BOTTOM", low_date="2023-08-08"),
        _identity(base_id="b", pattern_type="DOUBLE_BOTTOM", low_date="2023-08-11"),
        _identity(base_id="c", pattern_type="DOUBLE_BOTTOM", low_date="2023-08-18"),
    ]
    lineages = cluster_base_lineages(items)
    assert len(lineages) == 1
    assert lineages[0].anchor_signature == [
        "first_bottom:2023-06-27",
        "middle_peak:2023-07-19",
    ]


def test_pattern_types_do_not_merge_at_lineage_stage():
    flat = _identity(base_id="flat", pattern_type="FLAT_BASE")
    db = _identity(base_id="db", pattern_type="DOUBLE_BOTTOM")
    lineages = cluster_base_lineages([flat, db])
    assert len(lineages) == 2
    assert {item.pattern_type for item in lineages} == {"FLAT_BASE", "DOUBLE_BOTTOM"}


def test_ambiguity_propagates_to_lineage():
    items = [
        _identity(base_id="a", state="PASS"),
        _identity(base_id="b", low_date="2023-08-17", state="AMBIGUOUS"),
    ]
    lineage = cluster_base_lineages(items)[0]
    assert lineage.pattern_evidence_state == "AMBIGUOUS"
