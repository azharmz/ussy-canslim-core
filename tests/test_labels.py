from src.canslim_research.labels import a_label, c_label


def test_c_pass_boundary():
    r = c_label(0.25, 0.25)
    assert r.value is True
    assert r.state == "PASS"


def test_c_fail_eps_leg():
    r = c_label(0.24, 0.40)
    assert r.value is False
    assert r.state == "FAIL"


def test_c_fail_revenue_leg():
    r = c_label(0.40, 0.24)
    assert r.value is False
    assert r.state == "FAIL"


def test_c_missing_eps_is_not_zero():
    r = c_label(None, 0.50)
    assert r.value is None
    assert r.state == "NOT_EVALUABLE"
    assert r.reason == "EPS_YOY_UNDEFINED_OR_MISSING"


def test_c_missing_revenue_is_not_eps_only_pass():
    r = c_label(0.50, None)
    assert r.value is None
    assert r.state == "NOT_EVALUABLE"
    assert r.reason == "REVENUE_YOY_UNDEFINED_OR_MISSING"


def test_c_both_missing_not_evaluable():
    r = c_label(None, None)
    assert r.value is None
    assert r.state == "NOT_EVALUABLE"


def test_c_data_not_ready_precedes_threshold_evaluation():
    r = c_label(0.50, 0.50, data_ready=False)
    assert r.value is None
    assert r.state == "NOT_EVALUABLE"
    assert r.reason == "DATA_NOT_READY"


def test_a_pass_three_years():
    assert a_label([0.25, 0.30, 0.40]).value is True


def test_a_fail_one_year():
    assert a_label([0.25, 0.24, 0.40]).value is False


def test_a_undefined_is_not_zero():
    assert a_label([0.30, None, 0.40]).value is None
