from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta, timezone

import boto3
from botocore.exceptions import ClientError

ROOT = "canslim/candidates/snapshots/"
POINTER_KEY = "canslim/candidates/current.json"
PROTECTED_KEY = "canslim/candidates/protected.json"
RETENTION_DAYS = int(os.getenv("CANSLIM_RETENTION_DAYS", "7"))
KEEP_NEWEST_DATES = int(os.getenv("CANSLIM_RETENTION_KEEP_NEWEST", "2"))


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"missing {name}")
    return value


def client():
    return boto3.client("s3", endpoint_url=env("R2_ENDPOINT"), aws_access_key_id=env("R2_ACCESS_KEY_ID"), aws_secret_access_key=env("R2_SECRET_ACCESS_KEY"), region_name="auto")


def read_json_optional(s3, bucket: str, key: str):
    try:
        return json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") in {"NoSuchKey", "404"}:
            return None
        raise


def snapshot_prefix_from_key(key: str) -> str:
    parts = key.split("/")
    if len(parts) < 6 or "/".join(parts[:3]) != "canslim/candidates/snapshots":
        raise RuntimeError(f"not a candidate snapshot key: {key}")
    return "/".join(parts[:5]) + "/"


def snapshot_date(prefix: str) -> date:
    return date.fromisoformat(prefix.split("/")[3])


def run_id(prefix: str) -> int:
    name = prefix.rstrip("/").split("/")[-1]
    if not name.startswith("run-") or not name[4:].isdigit():
        raise RuntimeError(f"invalid candidate snapshot run prefix: {prefix}")
    return int(name[4:])


def list_snapshot_objects(s3, bucket: str):
    out = []
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=ROOT):
        out.extend(page.get("Contents", []))
    return out


def main() -> None:
    if RETENTION_DAYS < 2:
        raise RuntimeError("retention must be at least 2 days to preserve cross-session handoff safety")
    if KEEP_NEWEST_DATES < 2:
        raise RuntimeError("must protect at least the two newest session dates")

    s3 = client()
    bucket = env("R2_BUCKET_NAME")
    ptr = read_json_optional(s3, bucket, POINTER_KEY)
    if not ptr or ptr.get("status") != "READY":
        raise RuntimeError("current candidate pointer missing/not READY")
    current_prefix = snapshot_prefix_from_key(ptr["candidates_key"])

    objects = list_snapshot_objects(s3, bucket)
    grouped: dict[str, list[dict]] = {}
    for obj in objects:
        prefix = snapshot_prefix_from_key(obj["Key"])
        grouped.setdefault(prefix, []).append(obj)

    protection = read_json_optional(s3, bucket, PROTECTED_KEY) or {}
    explicit_protected = set()
    for prefix in protection.get("snapshot_prefixes", []):
        if not prefix.startswith(ROOT) or not prefix.endswith("/"):
            raise RuntimeError(f"invalid protected snapshot prefix: {prefix}")
        explicit_protected.add(prefix)

    # Production cadence is one canonical Candidate snapshot per as-of/session date.
    # If remediation/reruns created several run-* prefixes for the same date, retain
    # the current pointer when it belongs to that date; otherwise retain the newest
    # run id. Explicitly protected prefixes are never removed.
    by_date: dict[date, list[str]] = {}
    for prefix in grouped:
        by_date.setdefault(snapshot_date(prefix), []).append(prefix)

    canonical_by_date: dict[date, str] = {}
    for d, prefixes in by_date.items():
        if current_prefix in prefixes:
            canonical_by_date[d] = current_prefix
        else:
            canonical_by_date[d] = max(prefixes, key=run_id)

    newest_dates = sorted(by_date, reverse=True)[:KEEP_NEWEST_DATES]
    protected = {current_prefix, *explicit_protected}
    protected.update(canonical_by_date[d] for d in newest_dates)

    today = datetime.now(timezone.utc).date()
    cutoff = today - timedelta(days=RETENTION_DAYS)

    # Same-date non-canonical duplicates are removable immediately, independent of
    # age, because they do not represent a distinct production session. Normal
    # canonical snapshots remain governed by the rolling date retention window.
    duplicate_prefixes = {
        prefix
        for d, prefixes in by_date.items()
        for prefix in prefixes
        if prefix != canonical_by_date[d] and prefix not in protected
    }
    expired_prefixes = {
        prefix
        for prefix in grouped
        if snapshot_date(prefix) < cutoff and prefix not in protected
    }
    delete_prefixes = sorted(duplicate_prefixes | expired_prefixes)

    deleted_objects = 0
    deleted_bytes = 0
    for prefix in delete_prefixes:
        batch = grouped[prefix]
        for start in range(0, len(batch), 1000):
            chunk = batch[start:start + 1000]
            s3.delete_objects(Bucket=bucket, Delete={"Objects": [{"Key": x["Key"]} for x in chunk], "Quiet": True})
        deleted_objects += len(batch)
        deleted_bytes += sum(int(x.get("Size", 0)) for x in batch)
        verify = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1)
        if verify.get("KeyCount", 0):
            raise RuntimeError(f"retention deletion verification failed: {prefix}")

    print(json.dumps({
        "status": "RETENTION_OK",
        "retention_days": RETENTION_DAYS,
        "keep_newest_session_dates": KEEP_NEWEST_DATES,
        "cutoff_exclusive": cutoff.isoformat(),
        "snapshot_count_before": len(grouped),
        "canonical_by_date": {d.isoformat(): canonical_by_date[d] for d in sorted(canonical_by_date)},
        "protected_prefixes": sorted(protected),
        "deleted_duplicate_prefixes": sorted(duplicate_prefixes),
        "deleted_expired_prefixes": sorted(expired_prefixes),
        "deleted_snapshot_prefixes": delete_prefixes,
        "deleted_objects": deleted_objects,
        "deleted_bytes": deleted_bytes,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
