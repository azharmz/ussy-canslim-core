from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from canslim_research.pattern_engine_v02 import (  # noqa: E402
    PATTERN_ENGINE_VERSION,
    detect_patterns_v02,
    prior_uptrend_state_v02,
)


def _row(day: int, close: float) -> dict:
    close = float(close)
    return {
        "date": (date(2022, 1, 1) + timedelta(days=day)).isoformat(),
        "open": close,
        "high": close * 1.005,
        "low": close * 0.995,
        "close": close,
        "volume": 1_000_000,
    }


def test_prior_uptrend_v02_uses_trailing_low_to_base_start_high():
    prior = [_row(i, 70 + 0.20 * i) for i in range(120)]
    prior[20]["low"] = 60.0
    base_start = _row(120, 90.0)
    rows = prior + [base_start]
    assert prior_uptrend_state_v02(rows, 120) == "PASS"


def test_prior_uptrend_v02_fails_closed_without_120_completed_sessions():
    rows = [_row(i, 100.0) for i in range(120)]
    assert prior_uptrend_state_v02(rows, 119) == "NOT_EVALUABLE"


def _flat_fixture():
    prefix = []
    for i in range(125):
        close = 70.0 + i * 0.25
        prefix.append(_row(i, close))
    # Ensure the trailing window contains a low far enough below the base start
    # to satisfy the source-grounded 30% prior-advance rule.
    prefix[20]["low"] = 55.0
    flat = [100, 99, 101, 100, 98, 99, 100, 97, 98, 99, 100, 98, 99, 101, 100,
            99, 98, 100, 99, 101, 100, 99, 98, 100, 99]
    return prefix + [_row(125 + i, value) for i, value in enumerate(flat)]


def test_v02_candidate_stamp_is_versioned():
    candidates = detect_patterns_v02(_flat_fixture())
    flat_candidates = [item for item in candidates if item.pattern_type == "FLAT_BASE"]
    assert flat_candidates
    assert all(item.pattern_engine_version == PATTERN_ENGINE_VERSION for item in flat_candidates)


def test_flat_breakout_day_new_high_does_not_redefine_structural_pivot():
    rows = _flat_fixture()
    # Append a recognition/breakout session only modestly above the prior high,
    # so it remains inside the preregistered 4% containment allowance. v0.1
    # would have persisted this breakout-day high as the pivot.
    breakout = _row(len(rows), 103.0)
    breakout["high"] = 103.4
    breakout["low"] = 102.0
    breakout["open"] = 102.5
    breakout["close"] = 103.0
    rows.append(breakout)

    candidates = detect_patterns_v02(rows)
    ending_on_breakout = [
        item for item in candidates
        if item.pattern_type == "FLAT_BASE" and item.base_end_or_breakout_ready_date == breakout["date"]
    ]
    assert ending_on_breakout
    candidate = max(ending_on_breakout, key=lambda item: item.confidence)
    assert candidate.pivot_source_date != breakout["date"]
    assert candidate.pivot_level < breakout["high"]
    assert candidate.landmarks["flat_left_high"]["date"] == candidate.pivot_source_date
