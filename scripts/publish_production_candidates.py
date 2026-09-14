from __future__ import annotations

import hashlib
import io
import json
import os
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

import boto3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from canslim_research.candidate_v2 import CandidateEvidence, DailyBar, PatternAssessment, build_candidate
from canslim_research.candidate_v2_adapters import AnnualEpsObservation, a_screen_state, c_screen_state, l_screen_state
from canslim_research.decision_time import regular_close_cutoff
from canslim_research.institutional_pit import resolve_institutional_pit, validate_institutional_pointer
from canslim_research.market_state_consumer import consume_market_state
from oneil_patterns.production.engine import analyze_security
from oneil_patterns.production.runner import run_from_r2

POINTER_KEY = 'canslim/candidates/current.json'
GENERATOR_VERSION = 'canslim-production-candidate-publisher-v1'
ONEIL_REPO_SHA = 'c433cc1e35a5aa32a46f732cd8c5545935e36e40'


def env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f'missing {name}')
    return v


def s3_client():
    return boto3.client('s3', endpoint_url=env('R2_ENDPOINT'), aws_access_key_id=env('R2_ACCESS_KEY_ID'), aws_secret_access_key=env('R2_SECRET_ACCESS_KEY'), region_name='auto')


def raw(s3, bucket: str, key: str) -> bytes:
    return s3.get_object(Bucket=bucket, Key=key)['Body'].read()


def js(s3, bucket: str, key: str) -> dict:
    return json.loads(raw(s3, bucket, key))


def pq(s3, bucket: str, key: str) -> pd.DataFrame:
    return pd.read_parquet(io.BytesIO(raw(s3, bucket, key)))


def csv(s3, bucket: str, key: str) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(raw(s3, bucket, key)), dtype={'security_id':'string','cusip':'string'})


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_sha(obj: dict) -> str:
    return sha256_bytes(json.dumps(obj, sort_keys=True, separators=(',', ':'), default=str).encode())


def latest_ready(s3, bucket: str) -> tuple[date, dict, pd.DataFrame]:
    ptr = js(s3, bucket, 'production/ready/current.json')
    frame = pq(s3, bucket, ptr['parquet_key'])
    asof = pd.to_datetime(frame['date'], errors='raise').dt.date.max()
    frame['date'] = pd.to_datetime(frame['date'], errors='raise').dt.normalize()
    return asof, ptr, frame


def add_rs(prices: pd.DataFrame) -> pd.DataFrame:
    chunks = []
    for _, g in prices.groupby('security_id', sort=False):
        g = g.sort_values('date').copy()
        for n in (63,126,189,252):
            g[f'ret_{n}'] = g['adj_close'] / g['adj_close'].shift(n) - 1.0
        g['rs_raw'] = .40*g['ret_63'] + .20*g['ret_126'] + .20*g['ret_189'] + .20*g['ret_252']
        chunks.append(g)
    x = pd.concat(chunks, ignore_index=True)
    x['rs_percentile'] = x.groupby('date')['rs_raw'].rank(pct=True, method='average') * 100.0
    return x


def symbol_col(df: pd.DataFrame) -> str:
    for c in ('symbol','ticker'):
        if c in df.columns:
            return c
    raise RuntimeError('fundamentals missing symbol/ticker')


def prepare_fundamentals(wide: pd.DataFrame, long: pd.DataFrame):
    w = wide.copy(); sym = symbol_col(w)
    w['accepted_at'] = pd.to_datetime(w['accepted_at'], errors='coerce', utc=True)
    w['fiscal_period_end'] = pd.to_datetime(w['fiscal_period_end'], errors='coerce')
    w['annual_eps_accepted_at'] = pd.to_datetime(w['annual_eps_accepted_at'], errors='coerce', utc=True)

    fy = long.loc[
        long['form'].astype(str).str.upper().isin(['10-K','10-K/A']) & long['accession'].notna() & long['fy'].notna(),
        ['accession','fy']
    ].copy()
    fy['annual_fy'] = pd.to_numeric(fy['fy'], errors='coerce')
    fy = fy.dropna(subset=['annual_fy']).drop_duplicates('accession')

    annual = w[[sym,'annual_eps_accepted_at','annual_eps_source_accession','annual_eps_growth']].copy()
    annual = annual.dropna(subset=[sym,'annual_eps_accepted_at','annual_eps_source_accession'])
    annual = annual.merge(fy[['accession','annual_fy']], left_on='annual_eps_source_accession', right_on='accession', how='left')
    return sym, w, annual


def fundamental_states(sym: str, wide: pd.DataFrame, annual: pd.DataFrame, ticker: str, cutoff: pd.Timestamp, asof: str):
    q = wide[wide[sym].astype(str).eq(ticker) & wide['accepted_at'].notna() & wide['accepted_at'].le(cutoff)].copy()
    q = q[q[['quarterly_eps_yoy','quarterly_revenue_yoy']].notna().any(axis=1)]
    if q.empty:
        c_state, c_reason = 'NOT_EVALUABLE', 'C_NOT_PIT_AVAILABLE'
    else:
        latest_period = q['fiscal_period_end'].max()
        row = q[q['fiscal_period_end'].eq(latest_period)].sort_values('accepted_at').iloc[-1]
        eps = None if pd.isna(row['quarterly_eps_yoy']) else float(row['quarterly_eps_yoy'])
        rev = None if pd.isna(row['quarterly_revenue_yoy']) else float(row['quarterly_revenue_yoy'])
        c_state, c_reason = c_screen_state(quarterly_eps_yoy=eps, quarterly_revenue_yoy=rev, available_on=row['accepted_at'].isoformat(), asof_date=cutoff.isoformat())

    a = annual[annual[sym].astype(str).eq(ticker) & annual['annual_eps_accepted_at'].notna() & annual['annual_eps_accepted_at'].le(cutoff)].copy()
    observations = []
    if not a.empty:
        a = a.dropna(subset=['annual_fy']).sort_values(['annual_fy','annual_eps_accepted_at']).groupby('annual_fy', as_index=False).tail(1)
        for _, r in a.iterrows():
            observations.append(AnnualEpsObservation(int(r['annual_fy']), None if pd.isna(r['annual_eps_growth']) else float(r['annual_eps_growth']), r['annual_eps_accepted_at'].isoformat()))
    a_state, _, a_reason = a_screen_state(observations, asof_date=cutoff.isoformat())
    return c_state, a_state, c_reason, a_reason


def load_institutional(s3, bucket: str):
    ptr = js(s3, bucket, 'institutional_sponsorship/current.json')
    manifest = js(s3, bucket, ptr['manifest_key'])
    validate_institutional_pointer(ptr, manifest)
    return ptr, manifest, csv(s3,bucket,ptr['live_sponsorship_mapped_key']), pq(s3,bucket,ptr['history_state_events_key']), pq(s3,bucket,ptr['uncertainty_state_events_key'])


def publish():
    s3 = s3_client(); bucket = env('R2_BUCKET_NAME')
    run_id = env('GITHUB_RUN_ID'); repo_sha = env('GITHUB_SHA')
    asof, ready_ptr, prices = latest_ready(s3, bucket)
    cutoff = pd.Timestamp(regular_close_cutoff(asof))

    p33 = run_from_r2(s3, bucket=bucket, asof_date=asof, analyze_security=analyze_security)
    patterns = [PatternAssessment.from_mapping(r.to_dict()) for r in p33.records]

    fptr = js(s3,bucket,'fundamentals/current.json'); fmanifest = js(s3,bucket,fptr['manifest_key']); fart=fmanifest['artifacts']
    wide = pq(s3,bucket,fart['fundamentals_point_in_time.parquet']['key']); long = pq(s3,bucket,fart['fundamentals_point_in_time_long.parquet']['key'])
    fsym, wide, annual = prepare_fundamentals(wide,long)

    iptr, imanifest, ilive, ihist, iunc = load_institutional(s3,bucket)
    mptr = js(s3,bucket,'market/state/official.json'); mraw=raw(s3,bucket,mptr['state_key'])
    m = consume_market_state(pointer=mptr,state_bytes=mraw,decision_session_date=asof)

    prices = add_rs(prices)
    rs_day = prices[prices['date'].eq(pd.Timestamp(asof))][['security_id','rs_percentile']]
    rsmap = dict(zip(rs_day['security_id'].astype(str),rs_day['rs_percentile']))
    bysid = {str(k):g.sort_values('date') for k,g in prices.groupby('security_id')}

    outputs=[]; ca_reasons=Counter(); i_reasons=Counter()
    for p in patterns:
        g=bysid.get(p.security_id)
        if g is None: continue
        bars=[DailyBar(r.date.date().isoformat(),float(r.open),float(r.high),float(r.low),float(r.close),float(r.volume)) for r in g.itertuples()]
        c_state,a_state,c_reason,a_reason=fundamental_states(fsym,wide,annual,p.ticker,cutoff,p.asof_date)
        ca_reasons[c_reason]+=1; ca_reasons[a_reason]+=1
        inst=resolve_institutional_pit(security_id=p.security_id,decision_cutoff=cutoff,live_state=ilive,history_events=ihist,uncertainty_events=iunc)
        i_reasons[inst.reason]+=1
        rs=rsmap.get(p.security_id); l_state,_=l_screen_state(None if pd.isna(rs) else float(rs))
        evidence=CandidateEvidence(
            C_screen_state=c_state,A_screen_state=a_state,L_individual_leadership_state=l_state,
            M_entry_state=m.M_entry_state,I_evidence_state=inst.state,
            N_catalyst_state='NOT_IMPLEMENTED',industry_evidence_state='NOT_IMPLEMENTED',
            rs_rating_proxy_percentile=None if pd.isna(rs) else float(rs),M_market_state=m.market_state)
        cand=build_candidate(p,bars,evidence)
        row={name:getattr(cand,name) for name in cand.__dataclass_fields__}
        row.update({
            'C_reason':c_reason,'A_reason':a_reason,'I_reason':inst.reason,
            'I_latest_period':inst.latest_period,'I_prior_period':inst.prior_period,
            'I_latest_available_at':inst.latest_available_at,'I_prior_available_on':inst.prior_available_on,
            'M_state_key':m.state_key,'M_state_sha256':m.state_sha256,
        })
        outputs.append(row)

    payload=''.join(json.dumps(x,sort_keys=True,default=str)+'\n' for x in outputs).encode()
    pattern_payload=p33.jsonl.encode()
    produced=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    prefix=f'canslim/candidates/snapshots/{asof.isoformat()}/run-{run_id}'
    candidate_key=f'{prefix}/candidates.jsonl'; pattern_key=f'{prefix}/patterns.jsonl'
    s3.put_object(Bucket=bucket,Key=candidate_key,Body=payload,ContentType='application/x-ndjson')
    s3.put_object(Bucket=bucket,Key=pattern_key,Body=pattern_payload,ContentType='application/x-ndjson')

    stage_counts=Counter(x['candidate_stage'] for x in outputs)
    manifest={
        'schema_version':1,'type':'canslim_production_candidate_snapshot','status':'READY',
        'generator_version':GENERATOR_VERSION,'produced_at':produced,'asof_date':asof.isoformat(),
        'decision_asof_timestamp':cutoff.isoformat(),'snapshot_prefix':prefix,
        'publisher_run_id':run_id,'publisher_commit':repo_sha,
        'oneil_repo_sha':ONEIL_REPO_SHA,'pattern_engine_version':'33-core-p8-frozen-v1','pattern_contract':'oneil-pattern-output-v2',
        'candidate_contract':'canslim-candidate-output-v2','eligibility_contract':'canslim-eligibility-contract-v1',
        'ready_pointer':ready_ptr,'fundamentals_manifest_key':fptr['manifest_key'],'fundamentals_manifest_sha256':canonical_sha(fmanifest),
        'institutional_manifest_key':iptr['manifest_key'],'institutional_manifest_sha256':canonical_sha(imanifest),
        'institutional_live_source_run_id':str(iptr['live_source_run_id']),
        'market_state_key':m.state_key,'market_state_sha256':m.state_sha256,'market_classifier_version':m.classifier_version,'market_action_version':m.market_action_version,
        'candidate_count':len(outputs),'candidate_stage_counts':dict(stage_counts),'ca_reason_counts':dict(ca_reasons),'i_reason_counts':dict(i_reasons),
        'artifacts':{
            'candidates.jsonl':{'key':candidate_key,'sha256':sha256_bytes(payload),'size_bytes':len(payload)},
            'patterns.jsonl':{'key':pattern_key,'sha256':sha256_bytes(pattern_payload),'size_bytes':len(pattern_payload)},
        },
        'advanced_patterns_allowed':False,'N_catalyst_state_policy':'EXPLICIT_NOT_IMPLEMENTED_EVIDENCE_ONLY','strategy_returns_inspected':False,
    }
    mbytes=json.dumps(manifest,indent=2,sort_keys=True,default=str).encode(); mkey=f'{prefix}/manifest.json'
    s3.put_object(Bucket=bucket,Key=mkey,Body=mbytes,ContentType='application/json')
    pointer={
        'schema_version':1,'type':'canslim_production_candidate_pointer','status':'READY','updated_at':produced,
        'asof_date':asof.isoformat(),'decision_asof_timestamp':cutoff.isoformat(),'snapshot_prefix':prefix,
        'manifest_key':mkey,'manifest_sha256':sha256_bytes(mbytes),'candidates_key':candidate_key,
        'candidates_sha256':sha256_bytes(payload),'candidate_count':len(outputs),'publisher_run_id':run_id,'publisher_commit':repo_sha,
    }
    s3.put_object(Bucket=bucket,Key=POINTER_KEY,Body=json.dumps(pointer,indent=2,sort_keys=True).encode(),ContentType='application/json')
    print(json.dumps({'pointer':pointer,'candidate_stage_counts':dict(stage_counts)},indent=2,sort_keys=True))

if __name__=='__main__':
    publish()
