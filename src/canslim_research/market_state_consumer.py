from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date

CONSUMER_VERSION = "50-market-state-consumer-v1"
CLASSIFIER_VERSION = "46-market-state-classification-v1"
MARKET_ACTION_VERSION = "45-market-exposure-action-v1"

_ALLOWED_STATES = {
    "CORRECTION",
    "RALLY_ATTEMPT",
    "FOLLOW_THROUGH_CONFIRMED",
    "UPTREND_HEALTHY",
    "UPTREND_WEAKENING",
    "NOT_EVALUABLE",
}


@dataclass(frozen=True, slots=True)
class CanonicalMarketDecision:
    asof_date: str
    market_state: str
    M_entry_state: str
    reason: str
    state_key: str
    state_sha256: str
    source_index_run_id: str
    source_manifest_key: str
    source_manifest_sha256: str
    consumer_version: str = CONSUMER_VERSION
    classifier_version: str = CLASSIFIER_VERSION
    market_action_version: str = MARKET_ACTION_VERSION


def entry_permission_for_state(state: str) -> tuple[str, str]:
    """Project frozen #45 new-entry permission from the canonical #46 state.

    #45 permits new entries for FOLLOW_THROUGH_CONFIRMED and UPTREND_HEALTHY,
    blocks them for CORRECTION, RALLY_ATTEMPT and UPTREND_WEAKENING, and keeps
    NOT_EVALUABLE explicit/fail-closed.
    """
    if state in {"FOLLOW_THROUGH_CONFIRMED", "UPTREND_HEALTHY"}:
        return "ALLOW_NEW_BUYS", "M45_NEW_ENTRIES_ALLOWED"
    if state in {"CORRECTION", "RALLY_ATTEMPT", "UPTREND_WEAKENING"}:
        return "BLOCK_NEW_BUYS", "M45_NEW_ENTRIES_BLOCKED"
    if state == "NOT_EVALUABLE":
        return "NOT_EVALUABLE", "M45_MARKET_NOT_EVALUABLE"
    raise ValueError(f"unsupported canonical market state: {state!r}")


def consume_market_state(
    *,
    pointer: dict,
    state_bytes: bytes,
    decision_session_date: date,
) -> CanonicalMarketDecision:
    if pointer.get("consumer_version") != CONSUMER_VERSION:
        raise ValueError("market pointer consumer version mismatch")
    required_pointer = {"run_id", "state_key", "state_sha256", "asof_date", "state", "published_at"}
    missing = sorted(k for k in required_pointer if not pointer.get(k))
    if missing:
        raise ValueError(f"market pointer fields missing: {missing}")

    digest = hashlib.sha256(state_bytes).hexdigest()
    if digest != pointer["state_sha256"]:
        raise ValueError("market state object sha256 mismatch")
    state_doc = json.loads(state_bytes)

    if state_doc.get("consumer_version") != CONSUMER_VERSION:
        raise ValueError("market state payload consumer version mismatch")
    if state_doc.get("classifier_version") != CLASSIFIER_VERSION:
        raise ValueError("market state classifier version mismatch")
    for key in ("asof_date", "state", "source_index_run_id", "source_manifest_key", "source_manifest_sha256"):
        if not state_doc.get(key):
            raise ValueError(f"market state payload missing {key}")
    if state_doc["asof_date"] != pointer["asof_date"] or state_doc["state"] != pointer["state"]:
        raise ValueError("market pointer/state payload mismatch")

    state = str(state_doc["state"])
    if state not in _ALLOWED_STATES:
        raise ValueError(f"unsupported market state: {state!r}")
    state_date = date.fromisoformat(str(state_doc["asof_date"]))
    if state_date > decision_session_date:
        raise ValueError("future market state is not allowed")
    # Prospective same-close candidate publication must consume the state for
    # that exact completed trading session. Older state is stale and fails closed.
    if state_date < decision_session_date:
        raise ValueError("stale market state is not allowed for this decision session")

    m_entry, reason = entry_permission_for_state(state)
    return CanonicalMarketDecision(
        asof_date=state_doc["asof_date"],
        market_state=state,
        M_entry_state=m_entry,
        reason=reason,
        state_key=str(pointer["state_key"]),
        state_sha256=digest,
        source_index_run_id=str(state_doc["source_index_run_id"]),
        source_manifest_key=str(state_doc["source_manifest_key"]),
        source_manifest_sha256=str(state_doc["source_manifest_sha256"]),
    )
