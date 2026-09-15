#!/usr/bin/env python3
"""Safely identify/delete redundant same-date CAN SLIM Candidate snapshots in R2.

Default mode is DRY RUN. A snapshot is eligible only when all are true:
- it is under canslim/candidates/snapshots/YYYY-MM-DD/run-*/
- another snapshot exists for the same as-of date
- it is not referenced by current.json or protected.json
- it is not one of the newest KEEP_NEWEST runs for that date

Deletion requires --apply. The script re-reads protection pointers immediately
before deletion and aborts if the protected set changed after planning.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from collections import defaultdict

import boto3

ROOT = "canslim/candidates"
SNAPSHOT_ROOT = f"{ROOT}/snapshots/"
RUN_RE = re.compile(r"^canslim/candidates/snapshots/(\d{4}-\d{2}-\d{2})/(run-(\d+))/")


def client():
    required = ["R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_ENDPOINT", "R2_BUCKET_NAME"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise SystemExit(f"Missing R2 configuration: {', '.join(missing)}")
    return boto3.client(
        "s3",
        endpoint_url=os.environ["R2_ENDPOINT"],
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
    ), os.environ["R2_BUCKET_NAME"]


def get_json(s3, bucket, key):
    try:
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    except s3.exceptions.NoSuchKey:
        return None
    return json.loads(body)


def collect_strings(value):
    out = set()
    if isinstance(value, str):
        out.add(value)
    elif isinstance(value, dict):
        for v in value.values():
            out |= collect_strings(v)
    elif isinstance(value, list):
        for v in value:
            out |= collect_strings(v)
    return out


def protected_prefixes(s3, bucket):
    values = set()
    for key in (f"{ROOT}/current.json", f"{ROOT}/protected.json"):
        doc = get_json(s3, bucket, key)
        if doc is not None:
            values |= collect_strings(doc)
    protected = set()
    for value in values:
        m = RUN_RE.search(value if value.endswith("/") else value + "/")
        if m:
            protected.add(f"{SNAPSHOT_ROOT}{m.group(1)}/{m.group(2)}/")
    return protected


def inventory(s3, bucket):
    runs = defaultdict(lambda: {"bytes": 0, "objects": 0, "run_id": 0})
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=SNAPSHOT_ROOT):
        for obj in page.get("Contents", []):
            m = RUN_RE.match(obj["Key"])
            if not m:
                continue
            prefix = f"{SNAPSHOT_ROOT}{m.group(1)}/{m.group(2)}/"
            rec = runs[prefix]
            rec["date"] = m.group(1)
            rec["run_id"] = int(m.group(3))
            rec["bytes"] += int(obj.get("Size", 0))
            rec["objects"] += 1
    return runs


def delete_prefix(s3, bucket, prefix):
    paginator = s3.get_paginator("list_objects_v2")
    deleted = 0
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        keys = [{"Key": x["Key"]} for x in page.get("Contents", [])]
        for i in range(0, len(keys), 1000):
            batch = keys[i:i+1000]
            if batch:
                s3.delete_objects(Bucket=bucket, Delete={"Objects": batch, "Quiet": True})
                deleted += len(batch)
    return deleted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually delete eligible prefixes")
    ap.add_argument("--date", help="limit cleanup to one YYYY-MM-DD as-of date")
    ap.add_argument("--keep-newest", type=int, default=2, help="minimum newest runs to keep per date")
    args = ap.parse_args()
    if args.keep_newest < 1:
        raise SystemExit("--keep-newest must be >= 1")

    s3, bucket = client()
    before_protected = protected_prefixes(s3, bucket)
    runs = inventory(s3, bucket)
    by_date = defaultdict(list)
    for prefix, rec in runs.items():
        if not args.date or rec["date"] == args.date:
            by_date[rec["date"]].append((prefix, rec))

    victims = []
    print("CAN SLIM duplicate Candidate snapshot cleanup")
    print(f"mode={'APPLY' if args.apply else 'DRY-RUN'} keep_newest={args.keep_newest}")
    print("protected prefixes:")
    for p in sorted(before_protected):
        print(f"  KEEP protected {p}")

    for date in sorted(by_date):
        items = sorted(by_date[date], key=lambda x: x[1]["run_id"], reverse=True)
        newest = {p for p, _ in items[:args.keep_newest]}
        print(f"\n{date}: {len(items)} run snapshot(s)")
        for prefix, rec in items:
            protected = prefix in before_protected
            keep = protected or prefix in newest
            state = "KEEP" if keep else "DELETE"
            why = "protected" if protected else ("newest" if prefix in newest else "redundant same-date run")
            print(f"  {state:6} {prefix} objects={rec['objects']} bytes={rec['bytes']} reason={why}")
            if not keep and len(items) > args.keep_newest:
                victims.append((prefix, rec))

    total = sum(rec["bytes"] for _, rec in victims)
    print(f"\nplanned_delete_prefixes={len(victims)} planned_reclaim_bytes={total}")
    if not args.apply:
        print("DRY-RUN ONLY: nothing deleted. Re-run with --apply after reviewing this plan.")
        return

    after_protected = protected_prefixes(s3, bucket)
    if after_protected != before_protected:
        raise SystemExit("ABORT: current/protected pointers changed while cleanup was being planned")
    for prefix, _ in victims:
        if prefix in after_protected:
            raise SystemExit(f"ABORT: planned victim became protected: {prefix}")

    deleted = 0
    for prefix, _ in victims:
        print(f"Deleting {prefix}")
        deleted += delete_prefix(s3, bucket, prefix)
    print(f"deleted_objects={deleted} reclaimed_planned_bytes={total}")


if __name__ == "__main__":
    main()
