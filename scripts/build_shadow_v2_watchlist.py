"""Build the real-data CAN SLIM v2 watchlist checkpoint.

Read-only against canonical R2 inputs. The only write is a local JSON checkpoint
(or GitHub artifact when called by CI). It does not invoke #33 or production publishers.
"""
from __future__ import annotations
import hashlib, io, json, os, sys
from pathlib import Path
import boto3, pandas as pd

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from canslim_research.candidate_v2_adapters import AnnualEpsObservation, a_screen_state, c_screen_state
from canslim_research.decision_time import regular_close_cutoff
from canslim_research.watchlist_v2 import WatchlistLineage, build_watchlist
from canslim_research.shadow_v2_pipeline import watchlist_checkpoint_payload

def env(n):
    v=os.getenv(n)
    if not v: raise RuntimeError(f"missing {n}")
    return v

def main():
    s3=boto3.client("s3",endpoint_url=env("R2_ENDPOINT"),region_name="auto",aws_access_key_id=env("R2_ACCESS_KEY_ID"),aws_secret_access_key=env("R2_SECRET_ACCESS_KEY"))
    b=env("R2_BUCKET_NAME")
    def raw(k): return s3.get_object(Bucket=b,Key=k)["Body"].read()
    def js(k): return json.loads(raw(k))
    def pq(k): return pd.read_parquet(io.BytesIO(raw(k)))

    rp=js("production/ready/current.json"); rkey=rp["parquet_key"]; rbytes=raw(rkey); ready=pd.read_parquet(io.BytesIO(rbytes))
    ready["date"]=pd.to_datetime(ready["date"],errors="raise")
    decision=ready["date"].dt.date.max(); cutoff=pd.Timestamp(regular_close_cutoff(decision))
    latest=ready.loc[ready["date"].dt.date.eq(decision)].copy()
    if latest["security_id"].astype(str).duplicated().any(): raise RuntimeError("READY_DUPLICATE_SECURITY_ID_ON_DECISION_DATE")

    fp=js("fundamentals/current.json"); fm=js(fp["manifest_key"]); art=fm["artifacts"]
    wide=pq(art["fundamentals_point_in_time.parquet"]["key"]); long=pq(art["fundamentals_point_in_time_long.parquet"]["key"])
    sym="symbol" if "symbol" in wide.columns else "ticker"
    wide["accepted_at"]=pd.to_datetime(wide["accepted_at"],errors="coerce",utc=True); wide["fiscal_period_end"]=pd.to_datetime(wide["fiscal_period_end"],errors="coerce")
    wide["annual_eps_accepted_at"]=pd.to_datetime(wide["annual_eps_accepted_at"],errors="coerce",utc=True)
    fy=long.loc[long["form"].astype(str).str.upper().isin(["10-K","10-K/A"]) & long["accession"].notna() & long["fy"].notna(),["accession","fy"]].copy()
    fy["annual_fy"]=pd.to_numeric(fy["fy"],errors="coerce"); fy=fy.dropna(subset=["annual_fy"]).drop_duplicates("accession")
    annual=wide[[sym,"annual_eps_accepted_at","annual_eps_source_accession","annual_eps_growth"]].dropna(subset=[sym,"annual_eps_accepted_at","annual_eps_source_accession"]).merge(fy,left_on="annual_eps_source_accession",right_on="accession",how="left")

    def resolve(row):
        ticker=str(row.get("ticker") or row.get("symbol") or "")
        q=wide[wide[sym].astype(str).eq(ticker) & wide["accepted_at"].notna() & wide["accepted_at"].le(cutoff)].copy()
        q=q[q[["quarterly_eps_yoy","quarterly_revenue_yoy"]].notna().any(axis=1)]
        if q.empty: c="NOT_EVALUABLE"
        else:
            lp=q["fiscal_period_end"].max(); z=q[q["fiscal_period_end"].eq(lp)].sort_values("accepted_at").iloc[-1]
            eps=None if pd.isna(z["quarterly_eps_yoy"]) else float(z["quarterly_eps_yoy"]); rev=None if pd.isna(z["quarterly_revenue_yoy"]) else float(z["quarterly_revenue_yoy"])
            c,_=c_screen_state(quarterly_eps_yoy=eps,quarterly_revenue_yoy=rev,available_on=z["accepted_at"].isoformat(),asof_date=cutoff.isoformat())
        a=annual[annual[sym].astype(str).eq(ticker) & annual["annual_eps_accepted_at"].notna() & annual["annual_eps_accepted_at"].le(cutoff)].dropna(subset=["annual_fy"]).copy()
        obs=[]
        if not a.empty:
            a=a.sort_values(["annual_fy","annual_eps_accepted_at"]).groupby("annual_fy",as_index=False).tail(1)
            obs=[AnnualEpsObservation(int(x.annual_fy),None if pd.isna(x.annual_eps_growth) else float(x.annual_eps_growth),x.annual_eps_accepted_at.isoformat()) for x in a.itertuples()]
        aa,_,_=a_screen_state(obs,asof_date=cutoff.isoformat())
        return c,aa

    fidentity=hashlib.sha256(json.dumps(fp,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    lineage=WatchlistLineage(decision.isoformat(),rkey,hashlib.sha256(rbytes).hexdigest(),fidentity)
    rows=latest.to_dict("records"); assessments=build_watchlist(rows,lineage=lineage,state_resolver=resolve)
    out=watchlist_checkpoint_payload(assessments,lineage,producer_commit=os.getenv("GITHUB_SHA","local"),producer_run=os.getenv("GITHUB_RUN_ID","local"))\n    out["qualified_security_ids"]=sorted([sid for sid,a in assessments.items() if a.qualified])
    target=Path(os.getenv("CANSLIM_V2_WATCHLIST_OUTPUT","shadow-v2-watchlist.json")); target.write_text(json.dumps(out,sort_keys=True,indent=2))
    print(json.dumps({"decision_date":decision.isoformat(),"ready_securities":len(assessments),"qualified":out["qualified_count"],"checkpoint":str(target),"sha256":out["content_sha256"]}))

if __name__=="__main__": main()
