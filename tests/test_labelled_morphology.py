from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from canslim_research.labelled_morphology import MorphologyLabel, evaluate_positive_label  # noqa: E402
from canslim_research.pattern_identity import BaseIdentity  # noqa: E402
from canslim_research.pattern_lineage import BaseLineage  # noqa: E402


def _label(split="DEVELOPMENT"):
    return MorphologyLabel(
        example_id="example",
        symbol="SNPS",
        pattern="FLAT_BASE",
        label="POSITIVE",
        window_start="2023-04-04",
        window_end="2023-05-18",
        asof_date="2023-05-18",
        provenance="AUTHORITATIVE_SOURCE",
        source_name="IBD",
        source_reference="https://example.test",
        rationale="source anchored",
        split=split,
    )


def _base(start="2023-04-05", end="2023-05-18"):
    return BaseIdentity(
        base_id="base",
        security_id="SEC",
        pattern_type="FLAT_BASE",
        structural_signature=["flat_left_high:2023-04-04"],
        first_recognized_date=end,
        last_supported_date=end,
        member_window_count=1,
        pattern_evidence_state="PASS",
        confidence=0.9,
        representative={
            "pattern_type": "FLAT_BASE",
            "base_start_date": start,
            "base_end_or_breakout_ready_date": end,
            "landmarks": {"flat_left_high": {"date": "2023-04-04", "price": 392.79}},
        },
        recognition_dates=[end],
        pattern_engine_version="test",
    )


def _lineage():
    return BaseLineage(
        lineage_id="lineage",
        security_id="SEC",
        pattern_type="FLAT_BASE",
        anchor_signature=["flat_left_high:2023-04-04"],
        member_base_ids=["base"],
        first_recognized_date="2023-05-18",
        last_supported_date="2023-05-18",
        member_identity_count=1,
        pattern_evidence_state="PASS",
        confidence=0.9,
        representative_base_id="base",
    )


def test_authoritative_label_matches_same_pattern_with_aligned_boundaries():
    result = evaluate_positive_label(_label(), [_lineage()], [_base()])
    assert result.agreement_state == "MATCH"
    assert result.start_error_days == 1
    assert result.end_error_days == 0


def test_same_pattern_with_bad_boundary_is_not_called_match():
    result = evaluate_positive_label(_label(), [_lineage()], [_base(start="2023-03-01")])
    assert result.agreement_state == "BOUNDARY_DISAGREEMENT"


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
