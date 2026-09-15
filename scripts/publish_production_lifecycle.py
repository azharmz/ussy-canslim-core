from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone

import boto3

from canslim_research.execution_entry_v1 import ExecutionState
from canslim_research.position_lifecycle_v2 import LIFECYCLE_VERSION

POINTER_KEY = "canslim/lifecycle/current.json"
PUBLISHER_VERSION = "canslim-production-lifecycle-publisher-v1"
ENTRY_POINTER_KEY = "canslim/entries/current.json"


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"missing {name}")
    return value


def s3_client():
    return boto3.client("s3", endpoint_url=env("R2_ENDPOINT"), aws_access_key_id=env("R2_ACCESS_KEY_ID"), aws_secret_access_key=env("R2_SECRET_ACCESS_KEY"), region_name="auto")


def raw(s3, bucket: str, key: str) -> bytes:
    return s3.get_object(Bucket=bucket, Key=key)["Body"].read()


def js(s3, bucket: str, key: str) -> dict:
    return json.loads(raw(s3, bucket, key))


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()


def publication_status(entry_count: int) -> str:
    return "BLOCKED_ON_PRODUCTION_ENTRY_POPULATION" if entry_count == 0 else "REQUIRES_POPULATED_LIFECYCLE_ACCEPTANCE"


def is_executable_entry(row: dict) -> bool:
    """Match the frozen #36 execution contract exactly; do not invent aliases."""
    return row.get("execution_state") == ExecutionState.EXECUTED_T1_OPEN.value


def main() -> None:
    s3 = s3_client(); bucket = env("R2_BUCKET_NAME")
    eptr = js(s3, bucket, ENTRY_POINTER_KEY)
    if eptr.get("status") != "READY":
        raise RuntimeError("entry pointer is not READY")
    entry_bytes = raw(s3, bucket, eptr["entries_key"])
    if sha(entry_bytes) != eptr["entries_sha256"]:
        raise RuntimeError("entry artifact hash mismatch")
    rows = [json.loads(line) for line in entry_bytes.splitlines() if line.strip()]
    if len(rows) != int(eptr["entry_decision_count"]):
        raise RuntimeError("entry count mismatch")

    executable = [r for r in rows if is_executable_entry(r)]
    # Governance guard: current Phase-8 plumbing is allowed to publish the truthful
    # empty production state, but must not pretend populated lifecycle acceptance.
    # When a real executable entry appears, fail closed so #37/#40/#42/#43 wiring
    # receives its required production-observation validation before promotion.
    if executable:
        raise RuntimeError("PHASE8_POPULATION_DETECTED: populated Entry->Lifecycle acceptance is required before publication")

    payload = b""
    run_id = os.getenv("GITHUB_RUN_ID", "manual")
    asof = str(eptr["asof_date"])
    prefix = f"canslim/lifecycle/snapshots/{asof}/run-{run_id}"
    lifecycle_key = f"{prefix}/lifecycle.jsonl"
    s3.put_object(Bucket=bucket, Key=lifecycle_key, Body=payload, ContentType="application/x-ndjson")

    status = publication_status(len(executable))
    manifest = {
        "schema_version": 1,
        "type": "canslim_production_lifecycle_manifest",
        "status": status,
        "publisher_version": PUBLISHER_VERSION,
        "publisher_commit": os.getenv("GITHUB_SHA", "unknown"),
        "publisher_run_id": run_id,
        "asof_date": asof,
        "lifecycle_version": LIFECYCLE_VERSION,
        "source_entry_pointer": ENTRY_POINTER_KEY,
        "source_entry_manifest_key": eptr["manifest_key"],
        "source_entry_manifest_sha256": eptr["manifest_sha256"],
        "source_entry_decision_count": len(rows),
        "executable_entry_count": len(executable),
        "lifecycle_record_count": 0,
        "lifecycle_key": lifecycle_key,
        "lifecycle_sha256": sha(payload),
        "production_observation_validation": "BLOCKED_NO_EXECUTABLE_ENTRY",
        "synthetic_population_used": False,
        "strategy_returns_inspected": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    mbytes = canonical(manifest); mkey = f"{prefix}/manifest.json"
    s3.put_object(Bucket=bucket, Key=mkey, Body=mbytes, ContentType="application/json")
    pointer = {
        "schema_version": 1, "type": "canslim_production_lifecycle_pointer", "status": status,
        "asof_date": asof, "snapshot_prefix": prefix, "manifest_key": mkey,
        "manifest_sha256": sha(mbytes), "lifecycle_key": lifecycle_key,
        "lifecycle_sha256": sha(payload), "lifecycle_record_count": 0,
        "executable_entry_count": len(executable), "publisher_run_id": run_id,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    s3.put_object(Bucket=bucket, Key=POINTER_KEY, Body=canonical(pointer), ContentType="application/json")
    print(json.dumps({"pointer": pointer, "validation": "BLOCKED_NO_EXECUTABLE_ENTRY"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
