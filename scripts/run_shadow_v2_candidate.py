"""Build read-only CAN SLIM v2 candidate evidence from qualified-only #33 output."""
from __future__ import annotations
import hashlib, io, json, os, sys
from collections import Counter
from pathlib import Path
import boto3, pandas as pd
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from canslim_research.candidate_v2 import CandidateEvidence, DailyBar, PatternAssessment, build_candidate
from canslim_research.candidate_v2_adapters import l_screen_state
from canslim_research.decision_time import regular_close_cutoff
from canslim_research.market_state_consumer import consume_market_state

def env(n):
    v=os.getenv(n)
    if not v: raise RuntimeError(f"missing {n}")
    return v
def raw(s3,b,k): return s3.get_object(Bucket=b,Key=k)["Body"].read()
def js(s3,b,k): return json.loads(raw(s3,b,k))
def add_rs(prices):
    chunks=[]
    for _,g in prices.groupby("security_id",sort=False):
        g=g.sort_values("date").copy()
        for n in (63,126,189,252): g[f"ret_{n}"]=g["adj_close"]/g["adj_close"].shift(n)-1.0
        g["rs_raw"]=.40*g["ret_63"]+.20*g["ret_126"]+.20*g["ret_189"]+.20*g["ret_252"]; chunks.append(g)
    x=pd.concat(chunks,ignore_index=True); x["rs_percentile"]=x.groupby("date")["rs_raw"].rank(pct=True,method="average")*100.0; return x

def main():
    cp=json.loads(Path(env("CANSLIM_V2_WATCHLIST_INPUT")).read_text())
    p33=json.loads(Path(env("CANSLIM_V2_P33_INPUT")).read_text())
    if p33["watchlist_sha256"]!=cp["content_sha256"]: raise RuntimeError("P33_WATCHLIST_LINEAGE_MISMATCH")
    decision=str(cp["lineage"]["decision_date"]); ids=set(cp["qualified_security_ids"])
    s3=boto3.client("s3",endpoint_url=env("R2_ENDPOINT"),region_name="auto",aws_access_key_id=env("R2_ACCESS_KEY_ID"),aws_secret_access_key=env("R2_SECRET_ACCESS_KEY")); bucket=env("R2_BUCKET_NAME")
    rb=raw(s3,bucket,cp["lineage"]["ready_key"])
    if hashlib.sha256(rb).hexdigest()!=cp["lineage"]["ready_sha256"]: raise RuntimeError("READY_SHA256_MISMATCH")
    prices=pd.read_parquet(io.BytesIO(rb)); prices["date"]=pd.to_datetime(prices["date"]).dt.normalize(); prices=add_rs(prices)
    day=prices[prices["date"].eq(pd.Timestamp(decision))][["security_id","rs_percentile"]]; rsmap=dict(zip(day["security_id"].astype(str),day["rs_percentile"]))
    mptr=js(s3,bucket,"market/state/official.json"); mraw=raw(s3,bucket,mptr["state_key"]); m=consume_market_state(pointer=mptr,state_bytes=mraw,decision_session_date=pd.Timestamp(decision).date())
    bars={str(k):[DailyBar(r.date.date().isoformat(),float(r.open),float(r.high),float(r.low),float(r.close),float(r.volume)) for r in g.sort_values("date").itertuples()] for k,g in prices.groupby("security_id") if str(k) in ids}
    wl={str(x["security_id"]):x for x in cp["rows"]}
    outputs=[]
    for rr in p33["records"]:
        p=PatternAssessment.from_mapping(rr); sid=p.security_id
        if sid not in ids: raise RuntimeError("NON_QUALIFIED_PATTERN_LEAKAGE")
        rs=rsmap.get(sid); l,_=l_screen_state(None if rs is None or pd.isna(rs) else float(rs))
        w=wl[sid]
        ev=CandidateEvidence(C_screen_state=w["C_state"],A_screen_state=w["A_state"],L_individual_leadership_state=l,M_entry_state=m.M_entry_state,I_evidence_state="NOT_EVALUABLE",N_catalyst_state="NOT_IMPLEMENTED",industry_evidence_state="NOT_IMPLEMENTED",rs_rating_proxy_percentile=None if rs is None or pd.isna(rs) else float(rs),M_market_state=m.market_state)
        cand=build_candidate(p,bars[sid],ev); outputs.append({name:getattr(cand,name) for name in cand.__dataclass_fields__})
    stages=Counter(x["candidate_stage"] for x in outputs)
    out={"decision_date":decision,"watchlist_sha256":cp["content_sha256"],"oneil_repo_sha":p33["oneil_repo_sha"],"market_state_key":mptr["state_key"],"market_state_sha256":hashlib.sha256(mraw).hexdigest(),"market_state":m.market_state,"M_entry_state":m.M_entry_state,"qualified_security_ids":sorted(ids),"candidate_count":len(outputs),"stage_counts":dict(stages),"records":outputs}
    target=Path(os.getenv("CANSLIM_V2_CANDIDATE_OUTPUT","shadow-v2-candidates.json")); target.write_text(json.dumps(out,default=str,sort_keys=True))
    print(json.dumps({"decision_date":decision,"market_state":m.market_state,"M_entry_state":m.M_entry_state,"qualified":sorted(ids),"stages":dict(stages)}))
if __name__=="__main__": main()
