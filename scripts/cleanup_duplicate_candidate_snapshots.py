#!/usr/bin/env python3
"""Safely identify/delete redundant same-date CAN SLIM Candidate snapshots in R2.

Default mode is DRY RUN. Deletion requires --apply. Protection pointers are
re-read immediately before deletion. Dry-run also reports immutable manifest
fingerprints so redundant same-date snapshots can be audited before apply.
"""
from __future__ import annotations
import argparse, json, os, re
from collections import defaultdict
import boto3

ROOT = "canslim/candidates"
SNAPSHOT_ROOT = f"{ROOT}/snapshots/"
RUN_RE = re.compile(r"^canslim/candidates/snapshots/(\d{4}-\d{2}-\d{2})/(run-(\d+))/")

def client():
    required = ["R2_ACCESS_KEY_ID","R2_SECRET_ACCESS_KEY","R2_ENDPOINT","R2_BUCKET_NAME"]
    missing=[k for k in required if not os.getenv(k)]
    if missing: raise SystemExit(f"Missing R2 configuration: {', '.join(missing)}")
    return boto3.client("s3",endpoint_url=os.environ["R2_ENDPOINT"],aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],region_name="auto"), os.environ["R2_BUCKET_NAME"]

def get_json(s3,bucket,key):
    try: body=s3.get_object(Bucket=bucket,Key=key)["Body"].read()
    except s3.exceptions.NoSuchKey: return None
    return json.loads(body)

def collect_strings(value):
    out=set()
    if isinstance(value,str): out.add(value)
    elif isinstance(value,dict):
        for v in value.values(): out |= collect_strings(v)
    elif isinstance(value,list):
        for v in value: out |= collect_strings(v)
    return out

def pointer_docs(s3,bucket):
    docs={}
    for key in (f"{ROOT}/current.json",f"{ROOT}/protected.json"):
        doc=get_json(s3,bucket,key)
        if doc is not None: docs[key]=doc
    return docs

def protected_prefixes(docs):
    values=set()
    for doc in docs.values(): values |= collect_strings(doc)
    protected=set()
    for value in values:
        m=RUN_RE.search(value if value.endswith("/") else value+"/")
        if m: protected.add(f"{SNAPSHOT_ROOT}{m.group(1)}/{m.group(2)}/")
    return protected

def inventory(s3,bucket):
    runs=defaultdict(lambda:{"bytes":0,"objects":0,"run_id":0,"keys":[]})
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket,Prefix=SNAPSHOT_ROOT):
        for obj in page.get("Contents",[]):
            m=RUN_RE.match(obj["Key"])
            if not m: continue
            prefix=f"{SNAPSHOT_ROOT}{m.group(1)}/{m.group(2)}/"; rec=runs[prefix]
            rec.update(date=m.group(1),run_id=int(m.group(3))); rec["bytes"]+=int(obj.get("Size",0)); rec["objects"]+=1; rec["keys"].append(obj["Key"])
    return runs

def manifest_fingerprint(s3,bucket,rec):
    candidates=[k for k in rec["keys"] if k.endswith("manifest.compacted.json")]
    if not candidates: candidates=[k for k in rec["keys"] if k.endswith("manifest.json")]
    if not candidates: return {"manifest":"MISSING"}
    key=sorted(candidates)[-1]; doc=get_json(s3,bucket,key) or {}
    # Report only deterministic, non-secret integrity/identity fields found anywhere.
    flat={}
    def walk(v,path=""):
        if isinstance(v,dict):
            for k,x in v.items(): walk(x,f"{path}.{k}" if path else k)
        elif isinstance(v,(str,int,float,bool)):
            leaf=path.lower()
            if any(t in leaf for t in ("sha256","hash","row_count","record_count","as_of","contract","schema")):
                flat[path]=v
    walk(doc)
    return {"manifest":key,"fingerprint":flat}

def delete_prefix(s3,bucket,prefix):
    deleted=0
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket,Prefix=prefix):
        keys=[{"Key":x["Key"]} for x in page.get("Contents",[])]
        for i in range(0,len(keys),1000):
            batch=keys[i:i+1000]
            if batch: s3.delete_objects(Bucket=bucket,Delete={"Objects":batch,"Quiet":True}); deleted+=len(batch)
    return deleted

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--apply",action="store_true"); ap.add_argument("--date"); ap.add_argument("--keep-newest",type=int,default=2); args=ap.parse_args()
    if args.keep_newest<1: raise SystemExit("--keep-newest must be >= 1")
    s3,bucket=client(); docs=pointer_docs(s3,bucket); before=protected_prefixes(docs); runs=inventory(s3,bucket); by_date=defaultdict(list)
    for prefix,rec in runs.items():
        if not args.date or rec["date"]==args.date: by_date[rec["date"]].append((prefix,rec))
    victims=[]; print("CAN SLIM duplicate Candidate snapshot cleanup"); print(f"mode={'APPLY' if args.apply else 'DRY-RUN'} keep_newest={args.keep_newest}")
    print("pointer documents present:",", ".join(sorted(docs)) or "NONE")
    print("protected prefixes:")
    for p in sorted(before): print("  KEEP protected",p)
    for date in sorted(by_date):
        items=sorted(by_date[date],key=lambda x:x[1]["run_id"],reverse=True); newest={p for p,_ in items[:args.keep_newest]}; print(f"\n{date}: {len(items)} run snapshot(s)")
        for prefix,rec in items:
            protected=prefix in before; keep=protected or prefix in newest; state="KEEP" if keep else "DELETE"; why="protected" if protected else ("newest" if prefix in newest else "redundant same-date run")
            fp=manifest_fingerprint(s3,bucket,rec)
            print(f"  {state:6} {prefix} objects={rec['objects']} bytes={rec['bytes']} reason={why}")
            print("    integrity=",json.dumps(fp,sort_keys=True,separators=(",",":")))
            if not keep and len(items)>args.keep_newest: victims.append((prefix,rec))
    total=sum(rec["bytes"] for _,rec in victims); print(f"\nplanned_delete_prefixes={len(victims)} planned_reclaim_bytes={total}")
    if not args.apply: print("DRY-RUN ONLY: nothing deleted."); return
    after=protected_prefixes(pointer_docs(s3,bucket))
    if after!=before: raise SystemExit("ABORT: current/protected pointers changed while cleanup was being planned")
    for prefix,_ in victims:
        if prefix in after: raise SystemExit(f"ABORT: planned victim became protected: {prefix}")
    deleted=0
    for prefix,_ in victims: print("Deleting",prefix); deleted+=delete_prefix(s3,bucket,prefix)
    print(f"deleted_objects={deleted} reclaimed_planned_bytes={total}")
if __name__=="__main__": main()
