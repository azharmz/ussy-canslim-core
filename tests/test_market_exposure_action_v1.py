from canslim_research.market_exposure_action_v1 import (
    ExposureBand, MarketState, decide_market_exposure, validate_market_exposure_decision,
)


def d(state, band):
    return decide_market_exposure(asof_date="2026-09-14", market_state=state, prior_band=band)


def test_correction_resets_to_e0_and_blocks_entries():
    x = d(MarketState.CORRECTION, ExposureBand.E4)
    assert x.target_exposure_band == "0-20"
    assert x.action == "RESET_TO_E0"
    assert not x.new_entries_allowed


def test_correction_at_e0_holds():
    x = d(MarketState.CORRECTION, ExposureBand.E0)
    assert x.action == "HOLD_EXPOSURE"


def test_rally_attempt_at_e0_does_not_reenter():
    x = d(MarketState.RALLY_ATTEMPT, ExposureBand.E0)
    assert x.target_exposure_band == "0-20"
    assert not x.new_entries_allowed


def test_rally_attempt_defensively_reduces_nonzero_band():
    x = d(MarketState.RALLY_ATTEMPT, ExposureBand.E2)
    assert x.target_exposure_band == "20-40"
    assert x.action == "REDUCE_ONE_BAND"


def test_follow_through_reenters_one_band_from_e0():
    x = d(MarketState.FOLLOW_THROUGH_CONFIRMED, ExposureBand.E0)
    assert x.target_exposure_band == "20-40"
    assert x.action == "RAISE_ONE_BAND"
    assert x.new_entries_allowed


def test_follow_through_does_not_jump_existing_exposure():
    x = d(MarketState.FOLLOW_THROUGH_CONFIRMED, ExposureBand.E2)
    assert x.target_exposure_band == "40-60"
    assert x.action == "HOLD_EXPOSURE"


def test_healthy_uptrend_raises_at_most_one_band():
    x = d(MarketState.UPTREND_HEALTHY, ExposureBand.E1)
    assert x.target_exposure_band == "40-60"


def test_healthy_uptrend_caps_at_e4():
    x = d(MarketState.UPTREND_HEALTHY, ExposureBand.E4)
    assert x.target_exposure_band == "80-100"
    assert x.action == "HOLD_EXPOSURE"


def test_weakening_reduces_one_band_and_blocks_new_entries():
    x = d(MarketState.UPTREND_WEAKENING, ExposureBand.E3)
    assert x.target_exposure_band == "40-60"
    assert not x.new_entries_allowed


def test_weakening_floors_at_e0():
    x = d(MarketState.UPTREND_WEAKENING, ExposureBand.E0)
    assert x.target_exposure_band == "0-20"


def test_not_evaluable_is_explicit_and_does_not_allow_entries():
    x = d(MarketState.NOT_EVALUABLE, ExposureBand.E2)
    assert x.action == "NOT_EVALUABLE"
    assert x.target_exposure_band == "40-60"
    assert not x.new_entries_allowed


def test_validator_green_on_canonical_decision():
    assert validate_market_exposure_decision(d(MarketState.CORRECTION, ExposureBand.E3)) == []
