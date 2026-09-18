"""Role-aware shadow CAN SLIM v2 eligibility.

Frozen v1 eligibility_contract.py remains untouched.
"""
from __future__ import annotations

from dataclasses import dataclass

ELIGIBILITY_CONTRACT_VERSION = "canslim-eligibility-contract-v2"


@dataclass(frozen=True, slots=True)
class EligibilityV2Input:
    watchlist_state: str
    pattern_state: str
    pivot_defined: bool
    pivot_crossed: bool
    breakout_volume_state: str
    L_individual_state: str
    M_entry_state: str
    N_catalyst_state: str = "NOT_IMPLEMENTED"
    I_evidence_state: str = "NOT_EVALUABLE"
    broader_S_evidence_state: str = "NOT_EVALUABLE"


def evaluate_v2(x: EligibilityV2Input) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []

    if x.watchlist_state != "QUALIFIED":
        reasons.append("WATCHLIST_NOT_QUALIFIED")

    if x.pattern_state == "AMBIGUOUS":
        reasons.append("PATTERN_AMBIGUOUS")
    elif x.pattern_state != "RECOGNIZED":
        reasons.append("PATTERN_NOT_RECOGNIZED")

    if not x.pivot_defined:
        reasons.append("PIVOT_UNDEFINED")
    elif not x.pivot_crossed:
        reasons.append("PIVOT_NOT_CROSSED")

    if x.breakout_volume_state != "CONFIRMED_ON_BREAKOUT":
        reasons.append("BREAKOUT_VOLUME_UNCONFIRMED")

    if x.L_individual_state not in {"PASS", "STRONG"}:
        reasons.append(
            "L_NOT_EVALUABLE"
            if x.L_individual_state == "NOT_EVALUABLE"
            else "L_SCREEN_FAIL"
        )

    if x.M_entry_state != "ALLOW_NEW_BUYS":
        reasons.append(
            "M_NOT_EVALUABLE"
            if x.M_entry_state == "NOT_EVALUABLE"
            else "M_BLOCK_NEW_BUYS"
        )

    # N non-price catalyst, broader S and I are deliberately evidence-only in
    # initial v2. Their states are preserved by the caller, never promoted to
    # an implicit PASS and never converted into v1-style universal vetoes.
    return not reasons, tuple(reasons)
