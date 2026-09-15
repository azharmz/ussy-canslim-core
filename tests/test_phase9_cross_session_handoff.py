from datetime import date

from scripts.publish_production_entries import resolve_candidate_source


class FakeS3:
    def __init__(self, pointer): self.pointer = pointer
    def get_object(self, Bucket, Key):
        import io, json
        assert Key == "canslim/candidates/current.json"
        return {"Body": io.BytesIO(json.dumps(self.pointer).encode())}


def ptr(asof="2026-09-14"):
    return {"status":"READY","asof_date":asof,"snapshot_prefix":"canslim/candidates/snapshots/2026-09-14/run-x","manifest_key":"m","manifest_sha256":"mh","candidates_key":"c","candidates_sha256":"ch","candidate_count":0}


def test_same_session_candidate_waits_for_t1():
    p, state = resolve_candidate_source(FakeS3(ptr()), "b", date(2026,9,14))
    assert p["asof_date"] == "2026-09-14"
    assert state == "WAITING_FOR_T1_BAR"


def test_prior_session_candidate_is_mature_after_ready_advances():
    p, state = resolve_candidate_source(FakeS3(ptr()), "b", date(2026,9,15))
    assert p["asof_date"] == "2026-09-14"
    assert state == "MATURE"
