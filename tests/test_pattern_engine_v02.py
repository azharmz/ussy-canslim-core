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


def test_v02_candidate_stamp_is_versioned():
    prefix = []
    for i in range(125):
        close = 70.0 + i * 0.25
        prefix.append(_row(i, close))
    # Ensure the trailing window contains a low far enough below the base start
    # to satisfy the source-grounded 30% prior-advance rule.
    prefix[20]["low"] = 55.0
    flat = [100, 99, 101, 100, 98, 99, 100, 97, 98, 99, 100, 98, 99, 101, 100,
            99, 98, 100, 99, 101, 100, 99, 98, 100, 99]
    rows = prefix + [_row(125 + i, value) for i, value in enumerate(flat)]
    candidates = detect_patterns_v02(rows)
    flat_candidates = [item for item in candidates if item.pattern_type == "FLAT_BASE"]
    assert flat_candidates
    assert all(item.pattern_engine_version == PATTERN_ENGINE_VERSION for item in flat_candidates)
