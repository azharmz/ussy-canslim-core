"""Publish a fully verified CAN SLIM v2 run without mutating frozen v1 pointers."""
from __future__ import annotations
import hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
import boto3

POINTER_KEY="canslim/v2/current.json"
PUBLISHER_VERSION="canslim-v2-production-publisher-v1"
FILES={
 "watchlist":"shadow-v2-watchlist.json",
 "patterns":"shadow-v2-p33.json",
 "candidates":"shadow-v2-candidates.json",
 "execution":"shadow-v2-execution.json",
 "lifecycle":"shadow-v2-lifecycle.json",
}
def env(n):
 v=os.getenv(n)
 if not v: raise RuntimeError(f"missing {n}")
 return v
def sha(b): return hashlib.sha256(b).hexdigest()
def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":"),default=str).encode()
def load(name):
 p=Path(os.getenv(f"CANSLIM_V2_{name.upper()}_INPUT",FILES[name]))
 b=p.read_bytes(); return b,json.loads(b)
def validate(parts):
 w,p,c,e,l=(parts[x][1] for x in ("watchlist","patterns","candidates","execution","lifecycle"))
 d=str(w["lineage"]["decision_date"])
 if any(str(x.get("decision_date"))!=d for x in (p,c,e,l)): raise RuntimeError("DECISION_DATE_LINEAGE_MISMATCH")
 if p.get("watchlist_sha256")!=w.get("content_sha256") or c.get("watchlist_sha256")!=w.get("content_sha256"): raise RuntimeError("WATCHLIST_LINEAGE_MISMATCH")
 if p.get("oneil_repo_sha")!="3d0b35272d89c5a6f1329e8dea865b3cf7a32b0f": raise RuntimeError("P33_SHA_MISMATCH")
 if c.get("oneil_repo_sha")!=p.get("oneil_repo_sha"): raise RuntimeError("P33_CANDIDATE_LINEAGE_MISMATCH")
 if c.get("eligibility_contract_version")!="canslim-eligibility-contract-v2": raise RuntimeError("ELIGIBILITY_CONTRACT_MISMATCH")
 if e.get("source_candidate_sha256")!=sha(parts["candidates"][0]): raise RuntimeError("EXECUTION_CANDIDATE_LINEAGE_MISMATCH")
 if l.get("source_execution_sha256")!=sha(parts["execution"][0]): raise RuntimeError("LIFECYCLE_EXECUTION_LINEAGE_MISMATCH")
 if e.get("retroactive_entry_allowed") is not False: raise RuntimeError("RETROACTIVE_ENTRY_POLICY_MISMATCH")
 return d
def main():
 parts={k:load(k) for k in FILES}; decision=validate(parts)
 run=os.getenv("GITHUB_RUN_ID","manual"); commit=os.getenv("GITHUB_SHA","unknown")
 prefix=f"canslim/v2/snapshots/{decision}/run-{run}"
 artifacts={k:{"key":f"{prefix}/{k}.json","sha256":sha(v[0]),"size_bytes":len(v[0])} for k,v in parts.items()}
 manifest={"schema_version":1,"type":"canslim_v2_production_manifest","status":"READY","publisher_version":PUBLISHER_VERSION,"decision_date":decision,"publisher_run_id":run,"publisher_commit":commit,"snapshot_prefix":prefix,"oneil_repo_sha":parts["patterns"][1]["oneil_repo_sha"],"pattern_engine_version":"33-core-p8-frozen-v2","watchlist_contract":"canslim-watchlist-contract-v2","eligibility_contract":"canslim-eligibility-contract-v2","production_write":True,"retroactive_entry_allowed":False,"artifacts":artifacts,"created_at":datetime.now(timezone.utc).isoformat()}
 mb=canonical(manifest); mkey=f"{prefix}/manifest.json"
 pointer={"schema_version":1,"type":"canslim_v2_production_pointer","status":"READY","decision_date":decision,"snapshot_prefix":prefix,"manifest_key":mkey,"manifest_sha256":sha(mb),"publisher_run_id":run,"publisher_commit":commit,"previous_pointer":None,"updated_at":datetime.now(timezone.utc).isoformat()}
 dry=os.getenv("CANSLIM_V2_PUBLISH_DRY_RUN","1")!="0"
 if dry:
  print(json.dumps({"status":"DRY_RUN_OK","decision_date":decision,"manifest_sha256":sha(mb),"artifact_count":len(artifacts)},sort_keys=True)); return
 s3=boto3.client("s3",endpoint_url=env("R2_ENDPOINT"),region_name="auto",aws_access_key_id=env("R2_ACCESS_KEY_ID"),aws_secret_access_key=env("R2_SECRET_ACCESS_KEY")); bkt=env("R2_BUCKET_NAME")
 try:
  prev=json.loads(s3.get_object(Bucket=bkt,Key=POINTER_KEY)["Body"].read())
  pointer["previous_pointer"]={"manifest_key":prev.get("manifest_key"),"manifest_sha256":prev.get("manifest_sha256"),"decision_date":prev.get("decision_date")}
 except s3.exceptions.NoSuchKey: pass
 except Exception as ex:
  if "NoSuchKey" not in str(ex): raise
 for k,(raw,_) in parts.items(): s3.put_object(Bucket=bkt,Key=artifacts[k]["key"],Body=raw,ContentType="application/json")
 s3.put_object(Bucket=bkt,Key=mkey,Body=mb,ContentType="application/json")
 # Mutable pointer is deliberately last: incomplete runs can never become canonical.
 pb=canonical(pointer); s3.put_object(Bucket=bkt,Key=POINTER_KEY,Body=pb,ContentType="application/json")
 got=json.loads(s3.get_object(Bucket=bkt,Key=POINTER_KEY)["Body"].read())
 if got.get("manifest_sha256")!=pointer["manifest_sha256"] or got.get("decision_date")!=decision: raise RuntimeError("POINTER_READBACK_MISMATCH")
 print(json.dumps({"status":"PUBLISHED","pointer":POINTER_KEY,"decision_date":decision,"manifest_sha256":pointer["manifest_sha256"]},sort_keys=True))
if __name__=="__main__": main()
