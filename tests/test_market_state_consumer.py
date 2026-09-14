import hashlib
import json
from datetime import date

import pytest

from canslim_research.market_state_consumer import consume_market_state, entry_permission_for_state


def fixture(state="FOLLOW_THROUGH_CONFIRMED", asof="2026-09-14", classifier="46-market-state-classification-v1"):
    doc = {
        "consumer_version": "50-market-state-consumer-v1",
        "classifier_version": classifier,
        "asof_date": asof,
        "state": state,
        "reason": "fixture",
        "leadership_confirming": None,
        "weakening_confirmed": None,
        "index_evidence": {},
        "source_index_run_id": "index-run-1",
        "source_manifest_key": "market/indexes/runs/index-run-1/manifest.json",
        "source_manifest_sha256": "a" * 64,
        "published_at": "2026-09-15T00:00:00Z",
        "pit_note": "fixture",
    }
    raw = json.dumps(doc, sort_keys=True).encode()
    ptr = {
        "consumer_version": "50-market-state-consumer-v1",
        "run_id": "state-run-1",
        "state_key": "market/state/runs/state-run-1.json",
        "state_sha256": hashlib.sha256(raw).hexdigest(),
        "asof_date": asof,
        "state": state,
        "published_at": "2026-09-15T00:00:00Z",
    }
    return ptr, raw


def test_follow_through_allows_new_buys_under_frozen_45():
    p, raw = fixture()
    x = consume_market_state(pointer=p, state_bytes=raw, decision_session_date=date(2026, 9, 14))
    assert x.M_entry_state == "ALLOW_NEW_BUYS"
    assert x.market_state == "FOLLOW_THROUGH_CONFIRMED"


def test_frozen_45_entry_permissions():
    assert entry_permission_for_state("UPTREND_HEALTHY")[0] == "ALLOW_NEW_BUYS"
    assert entry_permission_for_state("CORRECTION")[0] == "BLOCK_NEW_BUYS"
    assert entry_permission_for_state("RALLY_ATTEMPT")[0] == "BLOCK_NEW_BUYS"
    assert entry_permission_for_state("UPTREND_WEAKENING")[0] == "BLOCK_NEW_BUYS"
    assert entry_permission_for_state("NOT_EVALUABLE")[0] == "NOT_EVALUABLE"


def test_hash_mismatch_fails_closed():
    p, raw = fixture()
    p["state_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="sha256"):
        consume_market_state(pointer=p, state_bytes=raw, decision_session_date=date(2026, 9, 14))


def test_classifier_version_mismatch_fails_closed():
    p, raw = fixture(classifier="wrong")
    with pytest.raises(ValueError, match="classifier"):
        consume_market_state(pointer=p, state_bytes=raw, decision_session_date=date(2026, 9, 14))


def test_future_state_fails_closed():
    p, raw = fixture(asof="2026-09-15")
    with pytest.raises(ValueError, match="future"):
        consume_market_state(pointer=p, state_bytes=raw, decision_session_date=date(2026, 9, 14))


def test_stale_state_fails_closed():
    p, raw = fixture(asof="2026-09-11")
    with pytest.raises(ValueError, match="stale"):
        consume_market_state(pointer=p, state_bytes=raw, decision_session_date=date(2026, 9, 14))
