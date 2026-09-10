from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from canslim_research.technical import (  # noqa: E402
    consolidation_pivot,
    is_distribution_day,
    is_follow_through_day,
    l_label,
    m_label,
    n_price_label,
    price_guardrail,
    rs_proxy_raw,
    s_label,
)


def test_price_floor_boundary():
    assert price_guardrail(15.0).state == "PASS"
    assert price_guardrail(14.99).state == "FAIL"


def test_n_buy_zone_boundary():
    assert n_price_label(close=105.0, pivot=100.0, base_depth=0.20).state == "PASS"
    assert n_price_label(close=105.01, pivot=100.0, base_depth=0.20).state == "FAIL"
    assert n_price_label(close=101.0, pivot=100.0, base_depth=0.41).reason == "BASE_TOO_DEEP"


def test_consolidation_uses_35_sessions():
    highs = [100.0] * 35
    lows = [80.0] * 35
    pivot, depth = consolidation_pivot(highs, lows)
    assert pivot == 100.0
    assert round(depth, 4) == 0.20


def test_s_volume_boundary():
    assert s_label(volume=1_400_000, avg_volume_50=1_000_000).state == "PASS"
    assert s_label(volume=1_399_999, avg_volume_50=1_000_000).state == "FAIL"


def test_rs_proxy_and_threshold():
    score = rs_proxy_raw(return_63d=0.4, return_126d=0.3, return_189d=0.2, return_252d=0.1)
    assert round(score, 4) == 0.28
    assert l_label(80.0).state == "PASS"
    assert l_label(79.99).state == "FAIL"


def test_distribution_and_follow_through_boundaries():
    assert is_distribution_day(daily_return=-0.002, volume=110, previous_volume=100)
    assert not is_distribution_day(daily_return=-0.0019, volume=110, previous_volume=100)
    assert is_follow_through_day(rally_day_number=4, daily_return=0.01, volume=110, previous_volume=100)
    assert not is_follow_through_day(rally_day_number=3, daily_return=0.02, volume=110, previous_volume=100)


def test_m_gate():
    assert m_label(spy_confirmed=True, qqq_confirmed=False, spy_distribution_count=2, qqq_distribution_count=3).state == "PASS"
    assert m_label(spy_confirmed=True, qqq_confirmed=True, spy_distribution_count=6, qqq_distribution_count=1).reason == "DISTRIBUTION_CLUSTER"
