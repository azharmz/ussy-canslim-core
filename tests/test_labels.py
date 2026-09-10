from src.canslim_research.labels import a_label, c_label


def test_c_pass_boundary():
    assert c_label(0.25, 0.25).value is True


def test_c_fail_one_leg():
    assert c_label(0.40, 0.24).value is False


def test_c_missing_is_not_zero():
    r = c_label(None, 0.50)
    assert r.value is None
    assert r.state == "NOT_EVALUABLE"


def test_a_pass_three_years():
    assert a_label([0.25, 0.30, 0.40]).value is True


def test_a_fail_one_year():
    assert a_label([0.25, 0.24, 0.40]).value is False


def test_a_undefined_is_not_zero():
    assert a_label([0.30, None, 0.40]).value is None
