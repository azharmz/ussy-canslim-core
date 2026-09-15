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
KEEP_NEWEST = int(os.getenv("CANSLIM_RETENTION_KEEP_NEWEST", "2"))


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


def list_snapshot_objects(s3, bucket: str):
    out = []
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=ROOT):
        out.extend(page.get("Contents", []))
    return out


def main() -> None:
    if RETENTION_DAYS < 2:
        raise RuntimeError("retention must be at least 2 days to preserve cross-session handoff safety")
    if KEEP_NEWEST < 2:
        raise RuntimeError("must protect at least the two newest snapshots")

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

    newest = sorted(grouped, key=lambda p: (snapshot_date(p), p), reverse=True)[:KEEP_NEWEST]
    protected = {current_prefix, *newest}
    protection = read_json_optional(s3, bucket, PROTECTED_KEY) or {}
    for prefix in protection.get("snapshot_prefixes", []):
        if not prefix.startswith(ROOT) or not prefix.endswith("/"):
            raise RuntimeError(f"invalid protected snapshot prefix: {prefix}")
        protected.add(prefix)

    today = datetime.now(timezone.utc).date()
    cutoff = today - timedelta(days=RETENTION_DAYS)
    delete_prefixes = [p for p in grouped if snapshot_date(p) < cutoff and p not in protected]
    deleted_objects = 0
    deleted_bytes = 0
    for prefix in sorted(delete_prefixes):
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
        "cutoff_exclusive": cutoff.isoformat(),
        "snapshot_count_before": len(grouped),
        "protected_prefixes": sorted(protected),
        "deleted_snapshot_prefixes": sorted(delete_prefixes),
        "deleted_objects": deleted_objects,
        "deleted_bytes": deleted_bytes,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
