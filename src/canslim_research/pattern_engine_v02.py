from __future__ import annotations

from typing import Any, Iterable, Sequence

from . import pattern_engine as v01


PATTERN_ENGINE_VERSION = "p8-v0.2-development-authoritative-correction"
PRIOR_UPTREND_LOOKBACK = 120
PRIOR_UPTREND_MIN_GAIN = 0.30


def prior_uptrend_state_v02(
    rows: Sequence[dict[str, Any]],
    base_start: int,
    *,
    lookback: int = PRIOR_UPTREND_LOOKBACK,
    min_gain: float = PRIOR_UPTREND_MIN_GAIN,
) -> str:
    """Theory-faithful DEVELOPMENT prior-advance proxy.

    Search only the 120 completed sessions strictly before the proposed base,
    then measure the advance from the lowest prior low to the base-start high.
    The 30% threshold is source-grounded; the 120-session horizon is a
    versioned research-only operationalization.
    """

    if base_start < lookback:
        return "NOT_EVALUABLE"
    prior = rows[base_start - lookback : base_start]
    origin_low = min(v01._price(row, "low") for row in prior)
    endpoint = v01._price(rows[base_start], "high")
    gain = endpoint / origin_low - 1.0
    return "PASS" if gain >= min_gain else "FAIL"


def detect_patterns_v02(
    raw_rows: Iterable[dict[str, Any]],
    policy: v01.EnginePolicy = v01.DEFAULT_POLICY,
    *,
    min_confidence: float = 0.75,
) -> list[v01.PatternCandidate]:
    """Run v0.1 morphology with the versioned v0.2 prior-uptrend semantics.

    v0.1 detector functions reference their module-level `prior_uptrend_state`.
    This adapter temporarily replaces that dependency for one deterministic
    call, then restores it. Candidate payloads are stamped v0.2 explicitly.
    """

    original = v01.prior_uptrend_state

    def _adapter(rows, base_start, _policy=policy):
        return prior_uptrend_state_v02(rows, base_start)

    v01.prior_uptrend_state = _adapter
    try:
        candidates = v01.detect_patterns(raw_rows, policy=policy, min_confidence=min_confidence)
    finally:
        v01.prior_uptrend_state = original

    for candidate in candidates:
        candidate.pattern_engine_version = PATTERN_ENGINE_VERSION
    return candidates
