"""Build read-only CAN SLIM v2 candidate evidence from qualified-only #33 output."""
from __future__ import annotations
import hashlib, io, json, os, sys
from datetime import datetime, timezone
from collections import Counter
from pathlib import Path
import boto3, pandas as pd
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from canslim_research.candidate_v2 import CandidateEvidence, DailyBar, PatternAssessment, build_candidate
from canslim_research.candidate_v2_adapters import l_screen_state
from canslim_research.decision_time import regular_close_cutoff
from canslim_research.market_state_consumer import consume_market_state
from canslim_research.institutional_pit import resolve_institutional_pit, validate_institutional_pointer

def env(n):
    v=os.getenv(n)
    if not v: raise RuntimeError(f"missing {n}")
    return v
def raw(s3,b,k): return s3.get_object(Bucket=b,Key=k)["Body"].read()
def pq(s3,b,k): return pd.read_parquet(io.BytesIO(raw(s3,b,k)))
def csv(s3,b,k): return pd.read_csv(io.BytesIO(raw(s3,b,k)),dtype={"security_id":"string","cusip":"string"})
def _cusip9(sid):
    x=str(sid).strip().upper(); return x[2:11] if len(x)==12 and x.startswith("US") else None
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
    iptr=js(s3,bucket,"institutional_sponsorship/current.json"); imanifest=js(s3,bucket,iptr["manifest_key"]); validate_institutional_pointer(iptr,imanifest)
    ilive=csv(s3,bucket,iptr["live_sponsorship_mapped_key"]); ihist=pq(s3,bucket,iptr["history_state_events_key"]); iunc=pq(s3,bucket,iptr["uncertainty_state_events_key"])
    cutoff=pd.Timestamp(regular_close_cutoff(pd.Timestamp(decision).date()))
    def grp(df,col):
        if df.empty: return {}
        z=df.assign(_k=df[col].astype(str).str.upper()); return {str(k):g for k,g in z.groupby("_k",sort=False)}
    live_by_sid=grp(ilive,"security_id"); hist_by_cusip=grp(ihist,"cusip"); unc_by_cusip=grp(iunc,"cusip")
    empty_live=ilive.iloc[0:0]; empty_hist=ihist.iloc[0:0]; empty_unc=iunc.iloc[0:0]
    bars={str(k):[DailyBar(r.date.date().isoformat(),float(r.open),float(r.high),float(r.low),float(r.close),float(r.volume)) for r in g.sort_values("date").itertuples()] for k,g in prices.groupby("security_id") if str(k) in ids}
    wl={str(x["security_id"]):x for x in cp["rows"]}
    outputs=[]
    for rr in p33["records"]:
        p=PatternAssessment.from_mapping(rr); sid=p.security_id
        if sid not in ids: raise RuntimeError("NON_QUALIFIED_PATTERN_LEAKAGE")
        rs=rsmap.get(sid); l,_=l_screen_state(None if rs is None or pd.isna(rs) else float(rs))
        w=wl[sid]; cusip=_cusip9(sid)
        inst=resolve_institutional_pit(security_id=sid,decision_cutoff=cutoff,
            live_state=live_by_sid.get(str(sid).upper(),empty_live),
            history_events=hist_by_cusip.get(cusip,empty_hist) if cusip else empty_hist,
            uncertainty_events=unc_by_cusip.get(cusip,empty_unc) if cusip else empty_unc)
        ev=CandidateEvidence(C_screen_state=w["C_state"],A_screen_state=w["A_state"],L_individual_leadership_state=l,M_entry_state=m.M_entry_state,I_evidence_state=inst.state,N_catalyst_state="NOT_IMPLEMENTED",industry_evidence_state="NOT_IMPLEMENTED",rs_rating_proxy_percentile=None if rs is None or pd.isna(rs) else float(rs),M_market_state=m.market_state)
        cand=build_candidate(p,bars[sid],ev); row={name:getattr(cand,name) for name in cand.__dataclass_fields__}
        row.update({"I_reason":inst.reason,"I_latest_period":inst.latest_period,"I_prior_period":inst.prior_period,"I_latest_available_at":inst.latest_available_at,"I_prior_available_on":inst.prior_available_on}); outputs.append(row)
    stages=Counter(x["candidate_stage"] for x in outputs)
    out={"decision_date":decision,"produced_at":datetime.now(timezone.utc).isoformat(),"watchlist_sha256":cp["content_sha256"],"oneil_repo_sha":p33["oneil_repo_sha"],"market_state_key":mptr["state_key"],"market_state_sha256":hashlib.sha256(mraw).hexdigest(),"market_state":m.market_state,"M_entry_state":m.M_entry_state,"institutional_manifest_key":iptr["manifest_key"],"institutional_manifest_sha256":hashlib.sha256(json.dumps(imanifest,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest(),"institutional_live_source_run_id":str(iptr.get("live_source_run_id","")),"qualified_security_ids":sorted(ids),"candidate_count":len(outputs),"stage_counts":dict(stages),"eligibility_contract_version":"canslim-eligibility-contract-v2","candidate_contract":"canslim-candidate-output-v2","ready_key":cp["lineage"]["ready_key"],"ready_sha256":cp["lineage"]["ready_sha256"],"fundamental_source_identity":cp["lineage"]["fundamental_source_identity"],"watchlist_contract_version":cp["contract_version"],"records":outputs}
    target=Path(os.getenv("CANSLIM_V2_CANDIDATE_OUTPUT","shadow-v2-candidates.json")); target.write_text(json.dumps(out,default=str,sort_keys=True))
    print(json.dumps({"decision_date":decision,"market_state":m.market_state,"M_entry_state":m.M_entry_state,"qualified":sorted(ids),"stages":dict(stages)}))
if __name__=="__main__": main()
