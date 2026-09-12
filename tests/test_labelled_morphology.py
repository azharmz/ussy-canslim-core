from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from canslim_research.labelled_morphology import MorphologyLabel, evaluate_positive_label  # noqa: E402
from canslim_research.pattern_identity import BaseIdentity  # noqa: E402
from canslim_research.pattern_lineage import BaseLineage  # noqa: E402


def _label(split="DEVELOPMENT", *, with_pivot=True):
    return MorphologyLabel(
        example_id="example",
        symbol="SNPS",
        pattern="FLAT_BASE",
        label="POSITIVE",
        window_start="2023-04-04",
        window_end="2023-05-18",
        asof_date="2023-05-18",
        expected_pivot_source_date="2023-04-04" if with_pivot else None,
        expected_pivot_level=392.79 if with_pivot else None,
        provenance="AUTHORITATIVE_SOURCE",
        source_name="IBD",
        source_reference="https://example.test",
        rationale="source anchored",
        split=split,
    )


def _base(
    start="2023-04-05",
    end="2023-05-18",
    *,
    pivot_date="2023-04-04",
    pivot_level=392.79,
    base_id="base",
):
    return BaseIdentity(
        base_id=base_id,
        security_id="SEC",
        pattern_type="FLAT_BASE",
        structural_signature=[f"flat_left_high:{pivot_date}"],
        first_recognized_date=end,
        last_supported_date=end,
        member_window_count=1,
        pattern_evidence_state="PASS",
        confidence=0.9,
        representative={
            "pattern_type": "FLAT_BASE",
            "base_start_date": start,
            "base_end_or_breakout_ready_date": end,
            "pivot_source_date": pivot_date,
            "pivot_level": pivot_level,
            "landmarks": {"flat_left_high": {"date": pivot_date, "price": pivot_level}},
        },
        recognition_dates=[end],
        pattern_engine_version="test",
    )


def _lineage(base_id="base", lineage_id="lineage", confidence=0.9):
    return BaseLineage(
        lineage_id=lineage_id,
        security_id="SEC",
        pattern_type="FLAT_BASE",
        anchor_signature=["flat_left_high:2023-04-04"],
        member_base_ids=[base_id],
        first_recognized_date="2023-05-18",
        last_supported_date="2023-05-18",
        member_identity_count=1,
        pattern_evidence_state="PASS",
        confidence=confidence,
        representative_base_id=base_id,
    )


def test_authoritative_label_matches_pattern_boundaries_and_pivot():
    result = evaluate_positive_label(_label(), [_lineage()], [_base()])
    assert result.agreement_state == "MATCH"
    assert result.start_error_days == 1
    assert result.end_error_days == 0
    assert result.pivot_date_error_days == 0
    assert result.pivot_price_error_pct == 0.0


def test_same_pattern_with_bad_boundary_is_not_called_match():
    result = evaluate_positive_label(_label(), [_lineage()], [_base(start="2023-03-01")])
    assert result.agreement_state == "BOUNDARY_DISAGREEMENT"


def test_same_pattern_and_boundaries_with_wrong_pivot_is_landmark_disagreement():
    result = evaluate_positive_label(
        _label(),
        [_lineage()],
        [_base(pivot_date="2023-05-18", pivot_level=410.91)],
    )
    assert result.agreement_state == "LANDMARK_DISAGREEMENT"
    assert result.pivot_date_error_days > 3
    assert result.pivot_price_error_pct > 0.01


def test_source_pivot_makes_correct_landmark_win_over_exact_terminal_date():
    wrong = _base(
        start="2023-04-04",
        end="2023-05-18",
        pivot_date="2023-05-18",
        pivot_level=410.91,
        base_id="wrong",
    )
    right = _base(
        start="2023-04-04",
        end="2023-05-17",
        pivot_date="2023-04-04",
        pivot_level=392.79,
        base_id="right",
    )
    result = evaluate_positive_label(
        _label(),
        [
            _lineage(base_id="wrong", lineage_id="wrong-lineage", confidence=0.95),
            _lineage(base_id="right", lineage_id="right-lineage", confidence=0.85),
        ],
        [wrong, right],
    )
    assert result.agreement_state == "MATCH"
    assert result.matched_base_id == "right"
    assert result.end_error_days == 1


def test_pivot_is_optional_when_authoritative_source_does_not_supply_it():
    result = evaluate_positive_label(
        _label(with_pivot=False),
        [_lineage()],
        [_base(pivot_date="2023-05-18", pivot_level=410.91)],
    )
    assert result.agreement_state == "MATCH"
    assert result.pivot_date_error_days is None


def test_missing_pattern_is_explicit_miss():
    result = evaluate_positive_label(_label(), [], [])
    assert result.agreement_state == "MISS_PATTERN"


def test_validation_split_is_not_allowed_into_development_evaluator():
    try:
        evaluate_positive_label(_label(split="VALIDATION"), [], [])
    except ValueError as exc:
        assert "DEVELOPMENT" in str(exc)
    else:
        raise AssertionError("VALIDATION label must stay hidden from DEVELOPMENT evaluator")
