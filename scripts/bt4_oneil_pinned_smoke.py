from __future__ import annotations

"""Execute the frozen O'Neil production engine on the deterministic BT3 sample.

Research-only BT4 smoke. The workflow must install ussy-oneil-patterns at the
exact frozen SHA before invoking this script. Every security frame is truncated
to decision_date, and the external engine independently rejects future bars.
"""
import argparse
import io
import json
import os
import subprocess
from datetime import date, datetime, timezone

import boto3
import pandas as pd

from oneil_patterns.production.engine import analyze_security
from oneil_patterns.production.output import ENGINE_VERSION, OUTPUT_SCHEMA_VERSION

ONEIL_SHA = "c433cc1e35a5aa32a46f732cd8c5545935e36e40"
CORE_PATTERNS = {"FLAT_BASE", "DOUBLE_BOTTOM", "CUP_WITHOUT_HANDLE", "CUP_WITH_HANDLE"}


def need(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"missing {name}")
    return value


def s3_client():
    return boto3.client(
        "s3", endpoint_url=need("R2_ENDPOINT"), region_name="auto",
        aws_access_key_id=need("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=need("R2_SECRET_ACCESS_KEY"),
    )


def git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def normalize(raw: pd.DataFrame, security_id: str) -> pd.DataFrame:
    f = raw.copy()
    f.columns = [str(c).lower() for c in f.columns]
    date_col = next((c for c in ("date", "session_date", "datetime") if c in f.columns), None)
    if date_col is None:
        raise RuntimeError(f"{security_id}: date unavailable")
    rename = {date_col: "date"}
    aliases = {"adjusted_open":"open", "adjusted_high":"high", "adjusted_low":"low", "adjusted_close":"close", "adjusted_volume":"volume", "adj_close":"close"}
    for src, dst in aliases.items():
        if src in f.columns and dst not in f.columns:
            rename[src] = dst
    f = f.rename(columns=rename)
    required = ["date", "open", "high", "low", "close", "volume"]
    missing = [c for c in required if c not in f.columns]
    if missing:
        raise RuntimeError(f"{security_id}: missing {missing}")
    f = f[required].copy()
    f["date"] = pd.to_datetime(f["date"], utc=True, errors="raise").dt.tz_localize(None)
    for c in ("open", "high", "low", "close", "volume"):
        f[c] = pd.to_numeric(f[c], errors="raise")
    f = f.dropna().sort_values("date").drop_duplicates("date", keep="last")
    f.insert(0, "security_id", security_id)
    f.insert(1, "ticker", security_id)
    return f


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--bt3-manifest", default="bt3-component-smoke-manifest.json")
    p.add_argument("--bt4-manifest", default="bt4-component-event-smoke.json")
    p.add_argument("--output", default="bt4-oneil-pinned-smoke.json")
    args = p.parse_args()
    bt3 = json.load(open(args.bt3_manifest, encoding="utf-8"))
    bt4 = json.load(open(args.bt4_manifest, encoding="utf-8"))
    if bt3.get("oneil_dependency_sha") != ONEIL_SHA or bt4.get("oneil_dependency_sha") != ONEIL_SHA:
        raise RuntimeError("frozen O'Neil SHA mismatch")
    decision_date = date.fromisoformat(bt4["decision_date"])
    keys = bt3["smoke_sample_keys"]
    ids = bt3["smoke_sample_identities"]
    s3 = s3_client(); bucket = need("R2_BUCKET_NAME")
    records = []
    per_security = {}
    for sid, key in zip(ids, keys):
        raw = pd.read_parquet(io.BytesIO(s3.get_object(Bucket=bucket, Key=key)["Body"].read()))
        frame = normalize(raw, sid)
        frame = frame[pd.to_datetime(frame["date"]).dt.date <= decision_date].reset_index(drop=True)
        out = analyze_security(sid, sid, frame, decision_date)
        per_security[sid] = len(out)
        records.extend(out)
    if any(r.output_schema_version != OUTPUT_SCHEMA_VERSION for r in records):
        raise RuntimeError("unexpected O'Neil output schema")
    if any(r.pattern not in CORE_PATTERNS for r in records):
        raise RuntimeError("advanced/non-core pattern escaped frozen scope")
    statuses = {}
    patterns = {}
    for r in records:
        statuses[r.normalized_status] = statuses.get(r.normalized_status, 0) + 1
        patterns[r.pattern] = patterns.get(r.pattern, 0) + 1
    payload = {
        "contract": "BT4_ONEIL_PINNED_EXECUTION_SMOKE_V1",
        "status": "ONEIL_PINNED_EXECUTED",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository_sha": git_sha(),
        "oneil_dependency_sha": ONEIL_SHA,
        "oneil_engine_version": ENGINE_VERSION,
        "oneil_output_schema_version": OUTPUT_SCHEMA_VERSION,
        "decision_date": decision_date.isoformat(),
        "sample_size": len(ids),
        "assessment_count": len(records),
        "pattern_counts": dict(sorted(patterns.items())),
        "normalized_status_counts": dict(sorted(statuses.items())),
        "assessment_counts_by_security": per_security,
        "future_information_used": False,
        "strategy_returns_inspected": False,
        "production_eligibility_emitted": False,
        "N": "NOT_EVALUABLE",
        "S": "NOT_EVALUABLE",
        "M": "NOT_EVALUABLE",
        "next_phase": "BT4_COMPONENT_BOUNDARY_VERDICT",
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    open(args.output, "w", encoding="utf-8").write(text)
    print(text, end="")


if __name__ == "__main__":
    main()
