from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

ELIGIBILITY_CONTRACT_VERSION = "canslim-eligibility-contract-v1"


@dataclass(frozen=True, slots=True)
class LetterRule:
    letter: str
    mandatory: bool
    accepted_states: frozenset[str]
    not_evaluable_blocks: bool = True
    note: str = ""


RULES: Mapping[str, LetterRule] = {
    "C": LetterRule(
        letter="C",
        mandatory=True,
        accepted_states=frozenset({"PASS"}),
        note="Frozen C-v1: quarterly EPS YoY and revenue YoY must both be evaluable and >=25%.",
    ),
    "A": LetterRule(
        letter="A",
        mandatory=True,
        accepted_states=frozenset({"PASS"}),
        note="Frozen A-v1: latest three consecutive annual EPS YoY states must each be evaluable and >=25%; fallback provenance remains distinct.",
    ),
    "N": LetterRule(
        letter="N",
        mandatory=True,
        accepted_states=frozenset({"PASS"}),
        note="Production N-v1 uses the already-governed price/new-high breakout evidence. Catalyst evidence is separate and must not be invented or implied.",
    ),
    "S": LetterRule(
        letter="S",
        mandatory=True,
        accepted_states=frozenset({"POSITIVE"}),
        note="Production S-v1 is positive breakout supply/demand evidence from the frozen volume-confirmation semantics.",
    ),
    "L": LetterRule(
        letter="L",
        mandatory=True,
        accepted_states=frozenset({"PASS", "STRONG"}),
        note="Frozen individual leadership state.",
    ),
    "I": LetterRule(
        letter="I",
        mandatory=True,
        accepted_states=frozenset({"POSITIVE"}),
        note="Canonical PIT institutional sponsorship must be positive; missing/unwired institutional evidence blocks full eligibility.",
    ),
    "M": LetterRule(
        letter="M",
        mandatory=True,
        accepted_states=frozenset({"ALLOW_NEW_BUYS"}),
        note="Canonical market entry state must allow new buys.",
    ),
}


def evaluate_letter_states(states: Mapping[str, str]) -> tuple[bool, tuple[str, ...]]:
    """Evaluate only the frozen C/A/N/S/L/I/M letter contract.

    This function intentionally does not alter candidate generation. It is the
    Phase-2 frozen contract consumed later by the production eligibility gate.
    Unknown, NOT_EVALUABLE, NOT_IMPLEMENTED, missing, or otherwise unaccepted
    states fail closed for every mandatory letter.
    """
    reasons: list[str] = []
    for letter, rule in RULES.items():
        state = states.get(letter)
        if state not in rule.accepted_states:
            reasons.append(f"{letter}_NOT_PASS:{state if state is not None else 'MISSING'}")
    return not reasons, tuple(reasons)
