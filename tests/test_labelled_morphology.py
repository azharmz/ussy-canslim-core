from __future__ import annotations
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from canslim_research.labelled_morphology import MorphologyLabel, evaluate_positive_label
from canslim_research.pattern_engine import PatternCandidate
from canslim_research.pattern_identity import BaseIdentity, structural_signature
from canslim_research.pattern_lineage import BaseLineage


def _label(split="DEVELOPMENT", *, with_pivot=True):
    return MorphologyLabel("example", "SNPS", "FLAT_BASE", "POSITIVE", "2023-04-04", "2023-05-18", "2023-05-18", "2023-04-04" if with_pivot else None, 392.79 if with_pivot else None, "AUTHORITATIVE_SOURCE", "IBD", "https://example.test", "source anchored", split)


def _candidate(start="2023-04-04", end="2023-05-17", *, pivot_date="2023-04-04", pivot_level=392.79, confidence=.9):
    return PatternCandidate(
        pattern_type="FLAT_BASE", pattern_evidence_state="PASS", confidence=confidence,
        base_start_date=start, base_end_or_breakout_ready_date=end, base_duration_sessions=31,
        base_depth_pct=.08, prior_uptrend_state="PASS", pivot_level=pivot_level,
        pivot_landmark_type="flat_left_high", pivot_source_date=pivot_date,
        landmarks={"flat_left_high":{"date":pivot_date,"price":pivot_level}, "base_low":{"date":"2023-04-25","price":360.37}},
        pattern_engine_version="test",
    )


def _base(candidate, base_id="base"):
    return BaseIdentity(
        base_id, "SEC", "FLAT_BASE", list(structural_signature(candidate)), candidate.base_end_or_breakout_ready_date,
        candidate.base_end_or_breakout_ready_date, 1, "PASS", candidate.confidence, candidate.to_dict(),
        [candidate.base_end_or_breakout_ready_date], "test",
    )


def _lineage(base_id="base", lineage_id="lineage"):
    return BaseLineage(lineage_id, "SEC", "FLAT_BASE", ["flat_left_high:2023-04-04"], [base_id], "2023-05-17", "2023-05-17", 1, "PASS", .9, base_id)


def _eval(candidate, label=None):
    base=_base(candidate); lineage=_lineage()
    return evaluate_positive_label(label or _label(), [lineage], [base], [candidate])


def test_authoritative_label_matches_emitted_window_boundaries_and_pivot():
    r=_eval(_candidate()); assert r.agreement_state=="MATCH"; assert (r.start_error_days,r.end_error_days,r.pivot_date_error_days,r.pivot_price_error_pct)==(0,1,0,0.0); assert r.matched_base_id=="base"


def test_bad_boundary_is_not_called_match():
    assert _eval(_candidate(start="2023-03-01",end="2023-04-01")).agreement_state=="BOUNDARY_DISAGREEMENT"


def test_good_boundaries_with_wrong_pivot_is_landmark_disagreement():
    assert _eval(_candidate(pivot_date="2023-05-17",pivot_level=410.91)).agreement_state=="LANDMARK_DISAGREEMENT"


def test_exact_raw_window_beats_identity_representative_loss_of_boundaries():
    # Multiple raw windows can collapse to one BaseIdentity. P8 must score the
    # actual emitted windows, not only the identity representative.
    exact=_candidate()
    wrong=_candidate(start="2023-03-17",end="2023-04-24",confidence=.99)
    base=_base(wrong)
    # Force identity to represent the same structural signature as exact/wrong.
    lineage=_lineage(base.base_id)
    r=evaluate_positive_label(_label(), [lineage], [base], [wrong,exact])
    assert r.agreement_state=="MATCH"; assert r.start_error_days==0; assert r.end_error_days==1


def test_boundary_fidelity_beats_perfect_pivot_on_wrong_window():
    wrong=_candidate(start="2023-03-01",end="2023-04-01")
    right=_candidate(start="2023-04-05",end="2023-05-17",pivot_date="2023-04-06",pivot_level=394.0)
    bases=[_base(wrong,"wrong-base"),_base(right,"right-base")]
    lineages=[_lineage("wrong-base","wrong-lineage"),_lineage("right-base","right-lineage")]
    r=evaluate_positive_label(_label(),lineages,bases,[wrong,right]); assert r.agreement_state=="MATCH"; assert r.start_error_days==1; assert r.end_error_days==1


def test_pivot_is_optional_when_source_does_not_supply_it():
    r=_eval(_candidate(pivot_date="2023-05-17",pivot_level=410.91), _label(with_pivot=False)); assert r.agreement_state=="MATCH"; assert r.pivot_date_error_days is None


def test_missing_pattern_is_explicit_miss():
    other=_candidate(); other.pattern_type="DOUBLE_BOTTOM"
    assert evaluate_positive_label(_label(),[],[],[other]).agreement_state=="MISS_PATTERN"


def test_validation_split_is_not_allowed_into_development_evaluator():
    try: evaluate_positive_label(_label(split="VALIDATION"),[],[],[])
    except ValueError as exc: assert "DEVELOPMENT" in str(exc)
    else: raise AssertionError("VALIDATION label must stay hidden from DEVELOPMENT evaluator")
