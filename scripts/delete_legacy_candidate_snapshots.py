from __future__ import annotations

import json
import os

import boto3

# One-shot cleanup explicitly approved for the two superseded raw snapshots.
TARGET_PREFIXES = (
    "canslim/candidates/snapshots/2026-09-14/run-34918297690/",
    "canslim/candidates/snapshots/2026-09-14/run-34929485939/",
)
POINTER_KEY = "canslim/candidates/current.json"


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"missing {name}")
    return value


def client():
    return boto3.client(
        "s3",
        endpoint_url=env("R2_ENDPOINT"),
        aws_access_key_id=env("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=env("R2_SECRET_ACCESS_KEY"),
        region_name="auto",
    )


def main() -> None:
    s3 = client()
    bucket = env("R2_BUCKET_NAME")
    pointer = json.loads(s3.get_object(Bucket=bucket, Key=POINTER_KEY)["Body"].read())
    current_prefix = pointer.get("snapshot_prefix", "").rstrip("/") + "/"

    if current_prefix in TARGET_PREFIXES:
        raise RuntimeError(f"refusing to delete current candidate snapshot: {current_prefix}")

    summary = []
    for prefix in TARGET_PREFIXES:
        paginator = s3.get_paginator("list_objects_v2")
        keys = []
        total_bytes = 0
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                keys.append(obj["Key"])
                total_bytes += int(obj.get("Size", 0))

        for start in range(0, len(keys), 1000):
            batch = keys[start : start + 1000]
            response = s3.delete_objects(
                Bucket=bucket,
                Delete={"Objects": [{"Key": key} for key in batch], "Quiet": False},
            )
            errors = response.get("Errors", [])
            if errors:
                raise RuntimeError(f"delete errors for {prefix}: {errors}")

        remaining = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1).get("KeyCount", 0)
        if remaining:
            raise RuntimeError(f"snapshot prefix not empty after deletion: {prefix}")

        summary.append({"prefix": prefix, "objects_deleted": len(keys), "bytes_deleted": total_bytes})

    print(json.dumps({"status": "DELETED", "snapshots": summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
