from canslim_research.execution_entry_variants_v1 import (
    r0_t1_baseline,
    r1_first_valid_open,
    r2_full_pivot_hold,
    r3_retest_reclaim_proxy,
)


def test_r0_accepts_exact_pivot_and_5pct_boundary():
    assert r0_t1_baseline(pivot=100.0, opens=[100.0]).executed
    assert r0_t1_baseline(pivot=100.0, opens=[105.0]).executed


def test_r0_rejects_below_and_extended():
    assert not r0_t1_baseline(pivot=100.0, opens=[99.99]).executed
    assert not r0_t1_baseline(pivot=100.0, opens=[105.01]).executed


def test_r1_uses_first_valid_open_only_through_t3():
    d = r1_first_valid_open(pivot=100.0, opens=[106.0, 104.0, 101.0, 100.5])
    assert d.executed and d.entry_offset == 2 and d.entry_price == 104.0
    d2 = r1_first_valid_open(pivot=100.0, opens=[106.0, 107.0, 108.0, 101.0])
    assert not d2.executed


def test_r2_confirmation_close_is_acted_on_next_open():
    d = r2_full_pivot_hold(
        pivot=100.0,
        opens=[101.0, 102.0, 103.0],
        lows=[100.5, 100.8],
        closes=[102.0, 103.0],
    )
    assert d.executed
    assert d.confirmation_offset == 1
    assert d.entry_offset == 2
    assert d.entry_price == 102.0


def test_r2_rejects_next_open_outside_buy_zone():
    d = r2_full_pivot_hold(
        pivot=100.0,
        opens=[101.0, 106.0, 103.0],
        lows=[100.5, 100.8],
        closes=[102.0, 103.0],
    )
    assert not d.executed
    assert d.confirmation_offset == 1


def test_r3_retest_reclaim_uses_next_open():
    d = r3_retest_reclaim_proxy(
        pivot=100.0,
        opens=[104.0, 103.0, 102.0],
        lows=[101.5, 103.0],
        closes=[102.0, 103.5],
    )
    assert d.executed
    assert d.confirmation_offset == 1
    assert d.entry_offset == 2
    assert d.entry_price == 103.0


def test_r3_does_not_use_same_day_close_as_fill():
    d = r3_retest_reclaim_proxy(
        pivot=100.0,
        opens=[104.0],
        lows=[99.0],
        closes=[101.0],
    )
    assert not d.executed
    assert d.confirmation_offset == 1


def test_all_executed_prices_are_observed_opens_inside_zone():
    pivot = 100.0
    decisions = [
        r0_t1_baseline(pivot=pivot, opens=[102.0]),
        r1_first_valid_open(pivot=pivot, opens=[106.0, 103.0, 104.0]),
        r2_full_pivot_hold(
            pivot=pivot,
            opens=[101.0, 103.0, 104.0],
            lows=[100.5, 101.0],
            closes=[102.0, 103.0],
        ),
        r3_retest_reclaim_proxy(
            pivot=pivot,
            opens=[104.0, 102.0, 103.0],
            lows=[101.0, 103.0],
            closes=[102.0, 103.0],
        ),
    ]
    for d in decisions:
        assert d.executed
        assert pivot <= d.entry_price <= pivot * 1.05
        assert d.entry_offset in {1, 2, 3}
