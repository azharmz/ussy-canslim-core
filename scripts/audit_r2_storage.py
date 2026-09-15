from __future__ import annotations

import json
import os
from collections import defaultdict

import boto3


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


def human(n: int) -> str:
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    value = float(n)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}"
        value /= 1024
    raise AssertionError


def main() -> None:
    s3 = client()
    bucket = env("R2_BUCKET_NAME")
    by_top: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    by_two: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    total_bytes = 0
    total_objects = 0

    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            size = int(obj.get("Size", 0))
            parts = key.split("/")
            top = parts[0] if parts else "(root)"
            two = "/".join(parts[:2]) if len(parts) >= 2 else top
            total_objects += 1
            total_bytes += size
            by_top[top][0] += 1
            by_top[top][1] += size
            by_two[two][0] += 1
            by_two[two][1] += size

    def rows(source):
        return [
            {"prefix": prefix, "objects": values[0], "bytes": values[1], "size": human(values[1])}
            for prefix, values in sorted(source.items(), key=lambda item: item[1][1], reverse=True)
        ]

    result = {
        "bucket": bucket,
        "total_objects": total_objects,
        "total_bytes": total_bytes,
        "total_size": human(total_bytes),
        "top_level": rows(by_top),
        "two_level": rows(by_two),
    }
    print(json.dumps(result, indent=2, sort_keys=False))


if __name__ == "__main__":
    main()
