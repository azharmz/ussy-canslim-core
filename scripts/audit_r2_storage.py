from __future__ import annotations

import json
import os
from collections import defaultdict

import boto3

GIB = 1024 ** 3
WARNING_GIB = float(os.getenv("R2_STORAGE_WARNING_GIB", "7"))
HARD_STOP_GIB = float(os.getenv("R2_STORAGE_HARD_STOP_GIB", "9"))


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"missing {name}")
    return value


def client():
    return boto3.client("s3", endpoint_url=env("R2_ENDPOINT"), aws_access_key_id=env("R2_ACCESS_KEY_ID"), aws_secret_access_key=env("R2_SECRET_ACCESS_KEY"), region_name="auto")


def human(n: int) -> str:
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    value = float(n)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}"
        value /= 1024
    raise AssertionError


def main() -> None:
    if WARNING_GIB >= HARD_STOP_GIB:
        raise RuntimeError("warning threshold must be below hard-stop threshold")
    s3 = client()
    bucket = env("R2_BUCKET_NAME")
    by_top: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    by_two: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    total_bytes = 0
    total_objects = 0
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket):
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
        return [{"prefix": p, "objects": v[0], "bytes": v[1], "size": human(v[1])} for p, v in sorted(source.items(), key=lambda item: item[1][1], reverse=True)]

    gib = total_bytes / GIB
    state = "HARD_STOP" if gib >= HARD_STOP_GIB else "WARNING" if gib >= WARNING_GIB else "OK"
    result = {
        "bucket": bucket,
        "total_objects": total_objects,
        "total_bytes": total_bytes,
        "total_size": human(total_bytes),
        "storage_guard": {"state": state, "warning_gib": WARNING_GIB, "hard_stop_gib": HARD_STOP_GIB},
        "top_level": rows(by_top),
        "two_level": rows(by_two),
    }
    print(json.dumps(result, indent=2, sort_keys=False))
    if state == "HARD_STOP":
        raise SystemExit(f"R2 storage hard stop: {gib:.2f} GiB >= {HARD_STOP_GIB:.2f} GiB")


if __name__ == "__main__":
    main()
