from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
from collections import Counter
from dataclasses import asdict
from datetime import date, datetime, timezone

import boto3
import pandas as pd

from canslim_research.execution_entry_v1 import EXECUTION_VERSION, decide_t1_open_execution, validate_execution_decision

POINTER_KEY = "canslim/entries/current.json"
PUBLISHER_VERSION = "canslim-production-entry-publisher-v3-compressed-source"
CANDIDATE_SCHEMA = "canslim-candidate-output-v2"
CANDIDATE_POINTER_KEY = "canslim/candidates/current.json"


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"missing {name}")
    return value


def s3_client():
    return boto3.client("s3", endpoint_url=env("R2_ENDPOINT"), aws_access_key_id=env("R2_ACCESS_KEY_ID"), aws_secret_access_key=env("R2_SECRET_ACCESS_KEY"), region_name="auto")


def raw(s3, bucket: str, key: str) -> bytes:
    return s3.get_object(Bucket=bucket, Key=key)["Body"].read()


def artifact_bytes(s3, bucket: str, key: str) -> tuple[bytes, bytes]:
    stored = raw(s3, bucket, key)
    logical = gzip.decompress(stored) if key.endswith(".gz") else stored
    return stored, logical


def js(s3, bucket: str, key: str) -> dict:
    return json.loads(raw(s3, bucket, key))


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()


def next_bar(ready: pd.DataFrame, security_id: str, signal_date: date):
    g = ready[(ready["security_id"].astype(str) == security_id) & (ready["date"].dt.date > signal_date)].sort_values("date")
    if g.empty:
        return None, None, None
    row = g.iloc[0]
    prior = ready[(ready["security_id"].astype(str) == security_id) & (ready["date"].dt.date <= signal_date)].sort_values("date")
    prior_close = float(prior.iloc[-1]["adj_close"]) if not prior.empty else None
    return row["date"].date(), float(row["open"]), prior_close


def resolve_candidate_source(s3, bucket: str, ready_max_date: date) -> tuple[dict, str]:
    cptr = js(s3, bucket, CANDIDATE_POINTER_KEY)
    if cptr.get("status") != "READY":
        raise RuntimeError("candidate pointer is not READY")
    signal_date = date.fromisoformat(str(cptr["asof_date"]))
    if ready_max_date <= signal_date:
        return cptr, "WAITING_FOR_T1_BAR"
    return cptr, "MATURE"


def main() -> None:
    s3 = s3_client(); bucket = env("R2_BUCKET_NAME")
    rptr = js(s3, bucket, "production/ready/current.json")
    ready_bytes = raw(s3, bucket, rptr["parquet_key"])
    expected_ready_sha = rptr.get("parquet_sha256") or rptr.get("sha256")
    if expected_ready_sha and sha(ready_bytes) != expected_ready_sha:
        raise RuntimeError("ready artifact hash mismatch")
    ready = pd.read_parquet(io.BytesIO(ready_bytes)); ready["date"] = pd.to_datetime(ready["date"], errors="raise").dt.normalize(); ready_max_date = ready["date"].max().date()

    cptr, maturity = resolve_candidate_source(s3, bucket, ready_max_date)
    if maturity == "WAITING_FOR_T1_BAR":
        print(json.dumps({"status": maturity, "candidate_asof_date": cptr["asof_date"], "ready_max_date": ready_max_date.isoformat()}, sort_keys=True)); return

    stored, candidate_bytes = artifact_bytes(s3, bucket, cptr["candidates_key"])
    stored_expected = cptr.get("candidates_stored_sha256")
    if stored_expected and sha(stored) != stored_expected:
        raise RuntimeError("candidate stored artifact hash mismatch")
    logical_expected = cptr.get("candidates_logical_sha256") or cptr.get("candidates_sha256")
    if logical_expected and sha(candidate_bytes) != logical_expected:
        raise RuntimeError("candidate logical artifact hash mismatch")
    rows = [json.loads(line) for line in candidate_bytes.splitlines() if line.strip()]
    if len(rows) != int(cptr["candidate_count"]): raise RuntimeError("candidate count mismatch")
    if any(r.get("candidate_output_schema_version") != CANDIDATE_SCHEMA for r in rows): raise RuntimeError("unsupported candidate schema")

    eligible = [r for r in rows if r.get("candidate_stage") == "CANSLIM_ELIGIBLE"]
    decisions = []
    for r in eligible:
        signal = date.fromisoformat(r["asof_date"]); nd, no, pc = next_bar(ready, str(r["security_id"]), signal)
        d = decide_t1_open_execution(candidate_id=str(r["candidate_id"]), security_id=str(r["security_id"]), signal_date=signal, candidate_stage=str(r["candidate_stage"]), pivot_level=r.get("pivot_level"), next_session_date=nd, next_open=no, prior_close=pc, source_candidate_version=str(r.get("candidate_generator_version") or ""))
        findings = validate_execution_decision(d)
        if findings: raise RuntimeError(f"entry contract violation {r['candidate_id']}: {findings}")
        out = asdict(d); out["execution_state"] = d.execution_state.value
        for k, v in list(out.items()):
            if isinstance(v, date): out[k] = v.isoformat()
        decisions.append(out)

    payload = b"".join(canonical(x) + b"\n" for x in decisions); run_id = os.getenv("GITHUB_RUN_ID", "manual"); asof = str(cptr["asof_date"]); prefix = f"canslim/entries/snapshots/{asof}/run-{run_id}"; entries_key = f"{prefix}/entries.jsonl"
    s3.put_object(Bucket=bucket, Key=entries_key, Body=payload, ContentType="application/x-ndjson")
    states = Counter(x["execution_state"] for x in decisions)
    manifest = {"schema_version":1,"type":"canslim_production_entry_manifest","status":"READY","publisher_version":PUBLISHER_VERSION,"publisher_commit":os.getenv("GITHUB_SHA","unknown"),"publisher_run_id":run_id,"asof_date":asof,"execution_version":EXECUTION_VERSION,"source_candidate_pointer":CANDIDATE_POINTER_KEY,"source_candidate_snapshot_prefix":cptr["snapshot_prefix"],"source_candidate_manifest_key":cptr["manifest_key"],"source_candidate_manifest_sha256":cptr["manifest_sha256"],"source_candidate_artifact_key":cptr["candidates_key"],"source_candidate_artifact_sha256":logical_expected,"source_candidate_count":len(rows),"eligible_candidate_count":len(eligible),"entry_decision_count":len(decisions),"execution_state_counts":dict(sorted(states.items())),"ready_pointer":"production/ready/current.json","ready_parquet_key":rptr["parquet_key"],"ready_max_date":ready_max_date.isoformat(),"entries_key":entries_key,"entries_sha256":sha(payload),"cross_session_handoff":"IMMUTABLE_SOURCE_PINNED","strategy_returns_inspected":False,"created_at":datetime.now(timezone.utc).isoformat()}
    mbytes=canonical(manifest); mkey=f"{prefix}/manifest.json"; s3.put_object(Bucket=bucket,Key=mkey,Body=mbytes,ContentType="application/json")
    pointer={"schema_version":1,"type":"canslim_production_entry_pointer","status":"READY","asof_date":asof,"snapshot_prefix":prefix,"manifest_key":mkey,"manifest_sha256":sha(mbytes),"entries_key":entries_key,"entries_sha256":sha(payload),"entry_decision_count":len(decisions),"eligible_candidate_count":len(eligible),"publisher_run_id":run_id,"updated_at":datetime.now(timezone.utc).isoformat()}
    s3.put_object(Bucket=bucket,Key=POINTER_KEY,Body=canonical(pointer),ContentType="application/json")
    print(json.dumps({"pointer":pointer,"execution_state_counts":dict(states)},indent=2,sort_keys=True))

if __name__ == "__main__": main()
