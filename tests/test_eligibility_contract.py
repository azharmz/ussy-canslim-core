from canslim_research.eligibility_contract import evaluate_letter_states


def passing_states():
    return {
        "C": "PASS",
        "A": "PASS",
        "N": "PASS",
        "S": "POSITIVE",
        "L": "PASS",
        "I": "POSITIVE",
        "M": "ALLOW_NEW_BUYS",
    }


def test_all_mandatory_letters_pass():
    ok, reasons = evaluate_letter_states(passing_states())
    assert ok is True
    assert reasons == ()


def test_strong_leadership_is_accepted():
    states = passing_states()
    states["L"] = "STRONG"
    ok, reasons = evaluate_letter_states(states)
    assert ok is True
    assert reasons == ()


def test_not_evaluable_mandatory_letter_fails_closed():
    states = passing_states()
    states["I"] = "NOT_EVALUABLE"
    ok, reasons = evaluate_letter_states(states)
    assert ok is False
    assert "I_NOT_PASS:NOT_EVALUABLE" in reasons


def test_not_implemented_mandatory_letter_fails_closed():
    states = passing_states()
    states["N"] = "NOT_IMPLEMENTED"
    ok, reasons = evaluate_letter_states(states)
    assert ok is False
    assert "N_NOT_PASS:NOT_IMPLEMENTED" in reasons


def test_missing_mandatory_letter_fails_closed():
    states = passing_states()
    del states["S"]
    ok, reasons = evaluate_letter_states(states)
    assert ok is False
    assert "S_NOT_PASS:MISSING" in reasons


def test_neutral_supply_demand_is_not_full_pass():
    states = passing_states()
    states["S"] = "NEUTRAL"
    ok, reasons = evaluate_letter_states(states)
    assert ok is False
    assert "S_NOT_PASS:NEUTRAL" in reasons


def test_market_caution_is_not_full_pass():
    states = passing_states()
    states["M"] = "CAUTION"
    ok, reasons = evaluate_letter_states(states)
    assert ok is False
    assert "M_NOT_PASS:CAUTION" in reasons


def test_multiple_failures_are_reported_deterministically():
    states = passing_states()
    states["C"] = "FAIL"
    states["A"] = "NOT_EVALUABLE"
    states["I"] = "NEGATIVE"
    ok, reasons = evaluate_letter_states(states)
    assert ok is False
    assert reasons == (
        "C_NOT_PASS:FAIL",
        "A_NOT_PASS:NOT_EVALUABLE",
        "I_NOT_PASS:NEGATIVE",
    )
