"""CAN SLIM market-exposure action semantics v1."""
from dataclasses import dataclass
from enum import Enum

MARKET_ACTION_VERSION = "45-market-exposure-action-v1"


class ExposureBand(str, Enum):
    E0 = "0-20"
    E1 = "20-40"
    E2 = "40-60"
    E3 = "60-80"
    E4 = "80-100"


class MarketState(str, Enum):
    CORRECTION = "CORRECTION"
    RALLY_ATTEMPT = "RALLY_ATTEMPT"
    FOLLOW_THROUGH_CONFIRMED = "FOLLOW_THROUGH_CONFIRMED"
    UPTREND_HEALTHY = "UPTREND_HEALTHY"
    UPTREND_WEAKENING = "UPTREND_WEAKENING"
    NOT_EVALUABLE = "NOT_EVALUABLE"


class MarketAction(str, Enum):
    HOLD_EXPOSURE = "HOLD_EXPOSURE"
    RAISE_ONE_BAND = "RAISE_ONE_BAND"
    REDUCE_ONE_BAND = "REDUCE_ONE_BAND"
    RESET_TO_E0 = "RESET_TO_E0"
    NOT_EVALUABLE = "NOT_EVALUABLE"


@dataclass(frozen=True)
class MarketExposureDecision:
    asof_date: str
    market_state: str
    prior_exposure_band: str
    action: str
    target_exposure_band: str
    new_entries_allowed: bool
    reason: str
    market_action_version: str = MARKET_ACTION_VERSION


_BANDS = list(ExposureBand)


def decide_market_exposure(*, asof_date: str, market_state: MarketState, prior_band: ExposureBand) -> MarketExposureDecision:
    idx = _BANDS.index(prior_band)

    if market_state == MarketState.NOT_EVALUABLE:
        action = MarketAction.NOT_EVALUABLE
        target = prior_band
        allowed = False
        reason = "MARKET_STATE_NOT_EVALUABLE"
    elif market_state == MarketState.CORRECTION:
        action = MarketAction.RESET_TO_E0 if prior_band != ExposureBand.E0 else MarketAction.HOLD_EXPOSURE
        target = ExposureBand.E0
        allowed = False
        reason = "MARKET_CORRECTION_DEFENSIVE_EXPOSURE"
    elif market_state == MarketState.RALLY_ATTEMPT:
        action = MarketAction.REDUCE_ONE_BAND if idx > 0 else MarketAction.HOLD_EXPOSURE
        target = _BANDS[max(0, idx - 1)] if idx > 0 else ExposureBand.E0
        allowed = False
        reason = "RALLY_ATTEMPT_NOT_YET_CONFIRMED"
    elif market_state == MarketState.FOLLOW_THROUGH_CONFIRMED:
        if prior_band == ExposureBand.E0:
            action = MarketAction.RAISE_ONE_BAND
            target = ExposureBand.E1
        else:
            action = MarketAction.HOLD_EXPOSURE
            target = prior_band
        allowed = True
        reason = "FOLLOW_THROUGH_PERMITS_GRADUAL_REENGAGEMENT"
    elif market_state == MarketState.UPTREND_HEALTHY:
        target = _BANDS[min(4, idx + 1)]
        action = MarketAction.RAISE_ONE_BAND if target != prior_band else MarketAction.HOLD_EXPOSURE
        allowed = True
        reason = "HEALTHY_UPTREND_SUPPORTS_GRADUAL_EXPOSURE_INCREASE"
    elif market_state == MarketState.UPTREND_WEAKENING:
        target = _BANDS[max(0, idx - 1)]
        action = MarketAction.REDUCE_ONE_BAND if target != prior_band else MarketAction.HOLD_EXPOSURE
        allowed = False
        reason = "WEAKENING_UPTREND_CALLS_FOR_DEFENSIVE_EXPOSURE"
    else:
        raise ValueError("unsupported market state")

    return MarketExposureDecision(
        asof_date=asof_date,
        market_state=market_state.value,
        prior_exposure_band=prior_band.value,
        action=action.value,
        target_exposure_band=target.value,
        new_entries_allowed=allowed,
        reason=reason,
    )


def validate_market_exposure_decision(x: MarketExposureDecision) -> list[str]:
    findings = []
    if x.market_action_version != MARKET_ACTION_VERSION:
        findings.append("M45-A_VERSION_MISMATCH")
    valid_bands = {b.value for b in ExposureBand}
    if x.prior_exposure_band not in valid_bands or x.target_exposure_band not in valid_bands:
        findings.append("M45-A_INVALID_BAND")
    if x.market_state in {MarketState.CORRECTION.value, MarketState.RALLY_ATTEMPT.value} and x.new_entries_allowed:
        findings.append("M45-G_ENTRY_GATE_VIOLATION")
    if x.market_state == MarketState.CORRECTION.value and x.target_exposure_band != ExposureBand.E0.value:
        findings.append("M45-B_CORRECTION_NOT_E0")
    return findings
