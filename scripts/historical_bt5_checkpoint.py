"""Historical BT5 checkpoint/resume primitives.

Checkpoint is a recovery boundary, not an authority pointer. Resume is allowed
only when every semantic lineage field matches exactly.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any

BT5_CONTRACT = "HISTORICAL_BT5_COMPONENT_REPLAY_V1"
FROZEN_ONEIL_SHA = "c433cc1e35a5aa32a46f732cd8c5545935e36e40"
CANONICAL_HISTORY_PREFIX = "history/ohlcv/"


@dataclass(frozen=True)
class ReplayLineage:
    experiment_id: str
    runner_commit: str
    source_inventory_sha256: str
    config_sha256: str
    oneil_sha: str = FROZEN_ONEIL_SHA
    contract: str = BT5_CONTRACT
    history_prefix: str = CANONICAL_HISTORY_PREFIX

    @property
    def sha256(self) -> str:
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def config_sha256(config: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(config, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def inventory_sha256(items: list[dict[str, Any]]) -> str:
    canonical = sorted(items, key=lambda x: str(x.get("key")))
    return hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def make_checkpoint(*, lineage: ReplayLineage, completed_work_units: list[str], output_parts: list[dict[str, Any]]) -> dict[str, Any]:
    payload = {
        "contract": BT5_CONTRACT,
        "lineage": asdict(lineage),
        "lineage_sha256": lineage.sha256,
        "completed_work_units": sorted(set(completed_work_units)),
        "output_parts": sorted(output_parts, key=lambda x: str(x.get("key"))),
        "production_eligibility_emitted": False,
        "strategy_returns_computed": False,
        "bt6_t1_open_computed": False,
    }
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    payload["checkpoint_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    return payload


def validate_checkpoint(checkpoint: dict[str, Any], expected: ReplayLineage) -> None:
    if checkpoint.get("contract") != BT5_CONTRACT:
        raise RuntimeError("BT5_CHECKPOINT_CONTRACT_MISMATCH")
    if checkpoint.get("lineage") != asdict(expected) or checkpoint.get("lineage_sha256") != expected.sha256:
        raise RuntimeError("BT5_CHECKPOINT_LINEAGE_MISMATCH")
    if checkpoint.get("production_eligibility_emitted") is not False:
        raise RuntimeError("BT5_CHECKPOINT_FORBIDDEN_ELIGIBILITY")
    if checkpoint.get("strategy_returns_computed") is not False or checkpoint.get("bt6_t1_open_computed") is not False:
        raise RuntimeError("BT5_CHECKPOINT_FORBIDDEN_OUTCOME")
    copy = dict(checkpoint)
    observed = copy.pop("checkpoint_sha256", None)
    expected_hash = hashlib.sha256(json.dumps(copy, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
    if observed != expected_hash:
        raise RuntimeError("BT5_CHECKPOINT_INTEGRITY_FAILURE")
