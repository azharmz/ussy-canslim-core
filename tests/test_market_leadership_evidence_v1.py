from canslim_research.market_leadership_evidence_v1 import (
    VERSION,
    LeadershipEvidenceInput,
    evaluate_market_leadership,
)


def packet(**kwargs):
    base = dict(
        asof_date="2026-09-11",
        broad_market_cohort_valid=True,
        cohort_definition="PIT broad-market leader cohort v1",
        cohort_provenance="cohort-run-1",
        valid_observed_leaders=25,
        leaders_making_new_highs=True,
        institutional_accumulation_in_leaders=True,
        majority_leaders_no_longer_making_new_highs=False,
        institutional_selling_in_leaders=False,
        source_provenance="source-run-1",
    )
    base.update(kwargs)
    return LeadershipEvidenceInput(**base)


def test_version_is_frozen():
    assert VERSION == "51-market-leadership-weakening-evidence-v1"


def test_joint_positive_leadership_confirms():
    r = evaluate_market_leadership(packet())
    assert r.leadership_confirming is True
    assert r.weakening_confirmed is False


def test_new_highs_without_institutional_demand_does_not_confirm():
    r = evaluate_market_leadership(packet(institutional_accumulation_in_leaders=False))
    assert r.leadership_confirming is False


def test_institutional_demand_without_new_highs_does_not_confirm():
    r = evaluate_market_leadership(packet(leaders_making_new_highs=False))
    assert r.leadership_confirming is False


def test_joint_leader_failure_and_selling_confirms_weakening():
    r = evaluate_market_leadership(packet(
        leaders_making_new_highs=False,
        institutional_accumulation_in_leaders=False,
        majority_leaders_no_longer_making_new_highs=True,
        institutional_selling_in_leaders=True,
    ))
    assert r.weakening_confirmed is True


def test_leader_failure_without_selling_does_not_confirm_weakening():
    r = evaluate_market_leadership(packet(
        majority_leaders_no_longer_making_new_highs=True,
        institutional_selling_in_leaders=False,
    ))
    assert r.weakening_confirmed is False


def test_missing_leadership_channel_is_not_evaluable():
    r = evaluate_market_leadership(packet(leaders_making_new_highs=None))
    assert r.leadership_confirming is None
    assert r.weakening_confirmed is False


def test_missing_weakening_channel_is_not_evaluable():
    r = evaluate_market_leadership(packet(institutional_selling_in_leaders=None))
    assert r.weakening_confirmed is None
    assert r.leadership_confirming is True


def test_invalid_broad_market_cohort_makes_both_not_evaluable():
    r = evaluate_market_leadership(packet(broad_market_cohort_valid=False))
    assert r.leadership_confirming is None
    assert r.weakening_confirmed is None


def test_missing_provenance_makes_both_not_evaluable():
    r = evaluate_market_leadership(packet(source_provenance=None))
    assert r.leadership_confirming is None
    assert r.weakening_confirmed is None


def test_zero_observed_leaders_is_not_evaluable():
    r = evaluate_market_leadership(packet(valid_observed_leaders=0))
    assert r.leadership_confirming is None
    assert r.weakening_confirmed is None
