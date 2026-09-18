from canslim_research.historical_l_adapter import evaluate_historical_l_day


def _series(ret: float):
    # 253 observations; deterministic terminal return shape is enough to test
    # the frozen weighted-momentum/ranking adapter.
    values = [100.0] * 253
    values[-1] = 100.0 * (1.0 + ret)
    return values


def test_historical_l_ranks_cross_section_not_pass_subset():
    rows = evaluate_historical_l_day(
        asof_date="2022-01-03",
        adjusted_close_history={
            "A": _series(0.50),
            "B": _series(0.20),
            "C": _series(0.00),
            "D": _series(-0.10),
            "E": _series(-0.20),
        },
    )
    by_id = {r.security_id: r for r in rows}
    assert by_id["A"].rs_percentile == 100.0
    assert by_id["A"].L_state == "PASS"
    assert by_id["E"].rs_percentile == 20.0
    assert by_id["E"].L_state == "FAIL"


def test_historical_l_fails_closed_without_252_day_history():
    rows = evaluate_historical_l_day(
        asof_date="2022-01-03",
        adjusted_close_history={"A": [100.0] * 252},
    )
    assert rows[0].L_state == "NOT_EVALUABLE"
    assert rows[0].rs_percentile is None
