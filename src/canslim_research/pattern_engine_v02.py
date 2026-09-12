from __future__ import annotations

from typing import Any, Iterable, Sequence

from . import pattern_engine as v01


PATTERN_ENGINE_VERSION = "p8-v0.3-development-flat-pivot-correction"
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


def _correct_flat_pivot_to_left_side_high(
    candidate: v01.PatternCandidate,
    rows: Sequence[dict[str, Any]],
    date_to_index: dict[str, int],
) -> None:
    """Persist the flat-base pivot from the established left-side high.

    A flat-base buy point is derived from the prior/base high that price must
    clear. If the recognition window includes the breakout session, that day's
    new high must not redefine the structural pivot. v0.1 used the maximum high
    over the entire rolling window; v0.3 preserves its preregistered geometry
    gates but corrects the persisted landmark to the same left-side zone already
    used by the flat-base containment test.
    """
    if candidate.pattern_type != "FLAT_BASE":
        return
    start = date_to_index[candidate.base_start_date]
    end = date_to_index[candidate.base_end_or_breakout_ready_date]
    duration = end - start + 1
    first_third_end = start + max(2, duration // 3)
    left_high_index = v01._argmax(rows, "high", start, first_third_end)
    left_high = v01._price(rows[left_high_index], "high")
    candidate.pivot_level = round(left_high, 8)
    candidate.pivot_landmark_type = "flat_left_high"
    candidate.pivot_source_date = v01._date(rows[left_high_index])
    candidate.landmarks["flat_left_high"] = {
        "date": candidate.pivot_source_date,
        "price": left_high,
    }


def detect_patterns_v02(
    raw_rows: Iterable[dict[str, Any]],
    policy: v01.EnginePolicy = v01.DEFAULT_POLICY,
    *,
    min_confidence: float = 0.75,
) -> list[v01.PatternCandidate]:
    """Run v0.1 morphology with versioned P8 DEVELOPMENT corrections.

    v0.1 detector functions reference their module-level `prior_uptrend_state`.
    This adapter temporarily replaces that dependency for one deterministic
    call, then restores it. After detection, flat-base candidates retain the
    preregistered geometry gates but persist their pivot from the established
    left-side high rather than an optional breakout-day new high.
    """

    materialized = list(raw_rows)
    rows = v01.normalize_rows(materialized)
    date_to_index = {v01._date(row): index for index, row in enumerate(rows)}

    original = v01.prior_uptrend_state

    def _adapter(rows_arg, base_start, _policy=policy):
        return prior_uptrend_state_v02(rows_arg, base_start)

    v01.prior_uptrend_state = _adapter
    try:
        candidates = v01.detect_patterns(materialized, policy=policy, min_confidence=min_confidence)
    finally:
        v01.prior_uptrend_state = original

    for candidate in candidates:
        _correct_flat_pivot_to_left_side_high(candidate, rows, date_to_index)
        candidate.pattern_engine_version = PATTERN_ENGINE_VERSION
    return candidates
