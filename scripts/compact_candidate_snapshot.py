from __future__ import annotations

import gzip
import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone

import boto3

POINTER_KEY = "canslim/candidates/current.json"


def env(name: str) -> str:
    v = os.getenv(name)
    if not v: raise RuntimeError(f"missing {name}")
    return v


def client():
    return boto3.client("s3", endpoint_url=env("R2_ENDPOINT"), aws_access_key_id=env("R2_ACCESS_KEY_ID"), aws_secret_access_key=env("R2_SECRET_ACCESS_KEY"), region_name="auto")


def raw(s3, bucket, key): return s3.get_object(Bucket=bucket, Key=key)["Body"].read()
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def canonical(o): return json.dumps(o, sort_keys=True, separators=(",", ":"), default=str).encode()


def file_sha(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()


def compress_one(s3, bucket: str, key: str) -> dict:
    if key.endswith(".gz"):
        head = s3.head_object(Bucket=bucket, Key=key)
        return {"key": key, "stored_size_bytes": head["ContentLength"], "already_compressed": True}
    gz_key = key + ".gz"
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "source.jsonl"); dst = os.path.join(td, "source.jsonl.gz")
        s3.download_file(bucket, key, src)
        logical_sha = file_sha(src); logical_size = os.path.getsize(src)
        with open(src, "rb") as fin, gzip.open(dst, "wb", compresslevel=6, mtime=0) as fout:
            shutil.copyfileobj(fin, fout, length=8 * 1024 * 1024)
        stored_sha = file_sha(dst); stored_size = os.path.getsize(dst)
        s3.upload_file(dst, bucket, gz_key, ExtraArgs={"ContentType":"application/x-ndjson","ContentEncoding":"gzip"})
        head = s3.head_object(Bucket=bucket, Key=gz_key)
        if head["ContentLength"] != stored_size: raise RuntimeError(f"uploaded size mismatch: {gz_key}")
    return {"key":gz_key,"logical_sha256":logical_sha,"logical_size_bytes":logical_size,"stored_sha256":stored_sha,"stored_size_bytes":stored_size,"compression":"gzip","content_encoding":"gzip","already_compressed":False,"source_key":key}


def main():
    s3=client(); bucket=env("R2_BUCKET_NAME"); ptr=json.loads(raw(s3,bucket,POINTER_KEY)); manifest=json.loads(raw(s3,bucket,ptr["manifest_key"]))
    if ptr.get("status") != "READY": raise RuntimeError("candidate pointer not READY")
    old_candidate=ptr["candidates_key"]; pattern_meta=manifest.get("artifacts",{}).get("patterns.jsonl",{}); old_pattern=pattern_meta.get("key")
    candidate=compress_one(s3,bucket,old_candidate); pattern=compress_one(s3,bucket,old_pattern) if old_pattern else None
    if candidate.get("already_compressed"):
        print(json.dumps({"status":"ALREADY_COMPACT","candidate":candidate},sort_keys=True)); return

    artifacts=manifest.setdefault("artifacts",{})
    artifacts.pop("candidates.jsonl",None); artifacts["candidates.jsonl.gz"]={k:v for k,v in candidate.items() if k not in ("source_key","already_compressed")}
    if pattern:
        artifacts.pop("patterns.jsonl",None); artifacts["patterns.jsonl.gz"]={k:v for k,v in pattern.items() if k not in ("source_key","already_compressed")}
    manifest["storage_contract"]="lossless-gzip-v1"; manifest["compacted_at"]=datetime.now(timezone.utc).isoformat(); manifest["logical_candidate_sha256"]=candidate["logical_sha256"]
    mbytes=json.dumps(manifest,indent=2,sort_keys=True,default=str).encode(); mkey=ptr["manifest_key"]
    s3.put_object(Bucket=bucket,Key=mkey,Body=mbytes,ContentType="application/json")

    ptr.update({"manifest_sha256":sha_bytes(mbytes),"candidates_key":candidate["key"],"candidates_sha256":candidate["logical_sha256"],"candidates_logical_sha256":candidate["logical_sha256"],"candidates_stored_sha256":candidate["stored_sha256"],"candidates_stored_size_bytes":candidate["stored_size_bytes"],"storage_contract":"lossless-gzip-v1","updated_at":datetime.now(timezone.utc).isoformat()})
    s3.put_object(Bucket=bucket,Key=POINTER_KEY,Body=json.dumps(ptr,indent=2,sort_keys=True).encode(),ContentType="application/json")

    # Pointer is switched only after compressed artifacts and manifest are durable.
    # Delete redundant raw payloads last; logical SHA preserves byte-for-byte identity.
    s3.delete_object(Bucket=bucket,Key=old_candidate)
    if old_pattern: s3.delete_object(Bucket=bucket,Key=old_pattern)
    saved=candidate["logical_size_bytes"]-candidate["stored_size_bytes"]
    if pattern: saved += pattern["logical_size_bytes"]-pattern["stored_size_bytes"]
    print(json.dumps({"status":"COMPACTED","candidate":candidate,"pattern":pattern,"bytes_saved":saved},indent=2,sort_keys=True))

if __name__ == "__main__": main()
