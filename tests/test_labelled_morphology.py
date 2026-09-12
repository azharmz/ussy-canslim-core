from __future__ import annotations
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from canslim_research.labelled_morphology import MorphologyLabel, evaluate_positive_label
from canslim_research.pattern_identity import BaseIdentity
from canslim_research.pattern_lineage import BaseLineage


def _label(split="DEVELOPMENT", *, with_pivot=True):
    return MorphologyLabel("example", "SNPS", "FLAT_BASE", "POSITIVE", "2023-04-04", "2023-05-18", "2023-05-18", "2023-04-04" if with_pivot else None, 392.79 if with_pivot else None, "AUTHORITATIVE_SOURCE", "IBD", "https://example.test", "source anchored", split)


def _base(start="2023-04-05", end="2023-05-18", *, pivot_date="2023-04-04", pivot_level=392.79, base_id="base", confidence=.9):
    return BaseIdentity(base_id, "SEC", "FLAT_BASE", [f"flat_left_high:{pivot_date}"], end, end, 1, "PASS", confidence, {"pattern_type":"FLAT_BASE","base_start_date":start,"base_end_or_breakout_ready_date":end,"pivot_source_date":pivot_date,"pivot_level":pivot_level,"landmarks":{"flat_left_high":{"date":pivot_date,"price":pivot_level}}}, [end], "test")


def _lineage(member_ids=("base",), representative="base", lineage_id="lineage", confidence=.9):
    return BaseLineage(lineage_id, "SEC", "FLAT_BASE", ["flat_left_high:2023-04-04"], list(member_ids), "2023-05-18", "2023-05-18", len(member_ids), "PASS", confidence, representative)


def test_authoritative_label_matches_pattern_boundaries_and_pivot():
    r=evaluate_positive_label(_label(),[_lineage()],[_base()]); assert r.agreement_state=="MATCH"; assert (r.start_error_days,r.end_error_days,r.pivot_date_error_days,r.pivot_price_error_pct)==(1,0,0,0.0)


def test_same_pattern_with_bad_boundary_is_not_called_match():
    assert evaluate_positive_label(_label(),[_lineage()],[_base(start="2023-03-01")]).agreement_state=="BOUNDARY_DISAGREEMENT"


def test_same_pattern_and_boundaries_with_wrong_pivot_is_landmark_disagreement():
    r=evaluate_positive_label(_label(),[_lineage()],[_base(pivot_date="2023-05-18",pivot_level=410.91)]); assert r.agreement_state=="LANDMARK_DISAGREEMENT"


def test_lineage_member_can_match_when_confidence_representative_has_wrong_boundaries():
    # This is the SNPS failure mode: lineage representative is useful for production
    # summarization, but another already-emitted identity is the faithful source window.
    rep=_base(start="2023-03-17",end="2023-04-24",base_id="rep",confidence=.99)
    member=_base(start="2023-04-05",end="2023-05-17",base_id="member",confidence=.80)
    lineage=_lineage(("rep","member"),representative="rep")
    r=evaluate_positive_label(_label(),[lineage],[rep,member])
    assert r.agreement_state=="MATCH"; assert r.matched_base_id=="member"; assert r.start_error_days==1; assert r.end_error_days==1


def test_boundary_fidelity_beats_perfect_pivot_on_wrong_window():
    wrong=_base(start="2023-03-01",end="2023-04-01",base_id="wrong",confidence=.99)
    right=_base(start="2023-04-05",end="2023-05-17",pivot_date="2023-04-06",pivot_level=394.0,base_id="right",confidence=.8)
    lineage=_lineage(("wrong","right"),representative="wrong")
    r=evaluate_positive_label(_label(),[lineage],[wrong,right]); assert r.agreement_state=="MATCH"; assert r.matched_base_id=="right"


def test_pivot_is_optional_when_authoritative_source_does_not_supply_it():
    r=evaluate_positive_label(_label(with_pivot=False),[_lineage()],[_base(pivot_date="2023-05-18",pivot_level=410.91)]); assert r.agreement_state=="MATCH"; assert r.pivot_date_error_days is None


def test_missing_pattern_is_explicit_miss():
    assert evaluate_positive_label(_label(),[],[]).agreement_state=="MISS_PATTERN"


def test_validation_split_is_not_allowed_into_development_evaluator():
    try: evaluate_positive_label(_label(split="VALIDATION"),[],[])
    except ValueError as exc: assert "DEVELOPMENT" in str(exc)
    else: raise AssertionError("VALIDATION label must stay hidden from DEVELOPMENT evaluator")
