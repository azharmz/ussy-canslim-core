from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from canslim_research.pattern_engine import (  # noqa: E402
    DEFAULT_POLICY,
    detect_cup_with_handle,
    detect_cup_without_handle,
    detect_double_bottom,
    detect_flat_base,
    detect_patterns,
    normalize_rows,
)


def _rows(closes):
    start = date(2020, 1, 1)
    out = []
    for i, close in enumerate(closes):
        close = float(close)
        out.append(
            {
                "date": (start + timedelta(days=i)).isoformat(),
                "open": close * 0.998,
                "high": close * 1.005,
                "low": close * 0.995,
                "close": close,
                "volume": 1_000_000 + i,
            }
        )
    return out


def _uptrend(n=45, start=70.0, end=100.0):
    step = (end - start) / (n - 1)
    return [start + i * step for i in range(n)]


def test_flat_base_recognizes_shallow_consolidation_and_uses_base_high_pivot():
    prefix = _uptrend()
    flat = [100, 99, 101, 100, 98, 99, 100, 97, 98, 99, 100, 98, 99, 101, 100,
            99, 98, 100, 99, 101, 100, 99, 98, 100, 99]
    rows = normalize_rows(_rows(prefix + flat))
    start = len(prefix)
    end = len(rows) - 1
    candidate = detect_flat_base(rows, start, end)
    assert candidate is not None
    assert candidate.pattern_type == "FLAT_BASE"
    assert candidate.pivot_landmark_type == "flat_left_high"
    assert candidate.base_depth_pct <= DEFAULT_POLICY.flat_max_depth


def test_cup_without_handle_uses_left_peak_as_pivot():
    prefix = _uptrend()
    cup = [100, 99, 97, 94, 90, 86, 82, 79, 77, 76, 76, 77, 78, 80, 82, 85, 88,
           91, 93, 95, 96, 97, 98, 99, 99, 100, 100, 99, 100, 100, 99, 100, 100, 99, 100]
    rows = normalize_rows(_rows(prefix + cup))
    candidate = detect_cup_without_handle(rows, len(prefix), len(rows) - 1)
    assert candidate is not None
    assert candidate.pattern_type == "CUP_WITHOUT_HANDLE"
    assert candidate.pivot_landmark_type == "left_peak"
    assert candidate.landmarks["cup_low"]["price"] < candidate.landmarks["left_peak"]["price"]


def test_cup_with_handle_uses_handle_high_as_pivot():
    prefix = _uptrend()
    cup = [100, 99, 97, 94, 90, 86, 82, 79, 77, 76, 76, 77, 79, 82, 85, 88, 91,
           94, 96, 98, 99, 100, 99, 100, 99, 100, 99, 100, 99, 100, 99, 100, 100, 99, 100]
    handle = [99, 98, 97, 98, 99, 98, 99]
    rows = normalize_rows(_rows(prefix + cup + handle))
    candidate = detect_cup_with_handle(rows, len(prefix), len(rows) - 1)
    assert candidate is not None
    assert candidate.pattern_type == "CUP_WITH_HANDLE"
    assert candidate.pivot_landmark_type == "handle_high"
    assert "handle_high" in candidate.landmarks
    assert "handle_low" in candidate.landmarks


def test_double_bottom_uses_middle_peak_as_pivot():
    prefix = _uptrend()
    pattern = [100, 97, 94, 90, 86, 83, 80, 78, 79, 82, 86, 90, 93, 95, 94, 91, 88,
               84, 81, 78, 77, 78, 81, 84, 88, 91, 94, 96, 97, 98, 99, 99, 100, 99, 100]
    rows = normalize_rows(_rows(prefix + pattern))
    candidate = detect_double_bottom(rows, len(prefix), len(rows) - 1)
    assert candidate is not None
    assert candidate.pattern_type == "DOUBLE_BOTTOM"
    assert candidate.pivot_landmark_type == "middle_peak"
    first = candidate.landmarks["first_bottom"]["price"]
    second = candidate.landmarks["second_bottom"]["price"]
    assert abs(second / first - 1.0) <= DEFAULT_POLICY.double_bottom_low_tolerance


def test_no_named_pattern_is_forced_when_prior_uptrend_is_missing():
    rows = _rows([100.0] * 120)
    candidates = detect_patterns(rows)
    assert candidates == []


def test_bad_ohlc_fails_closed():
    rows = _rows([100, 101, 102])
    rows[1]["high"] = 50
    try:
        normalize_rows(rows)
    except ValueError as exc:
        assert "high below OHLC range" in str(exc)
    else:
        raise AssertionError("invalid OHLC must fail closed")
