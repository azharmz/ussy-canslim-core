from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import time
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
from oneil_patterns.data.r2_ready import ReadyDataset, REQUIRED_COLUMNS
from oneil_patterns.production.engine import analyze_security
from oneil_patterns.production.runner import run_ready_dataset

POINTER_KEY = 'canslim/candidates/current.json'
GENERATOR_VERSION = 'canslim-production-candidate-publisher-v1'
ONEIL_REPO_SHA = 'c433cc1e35a5aa32a46f732cd8c5545935e36e40'
START = time.monotonic()


def log(message: str) -> None:
    print(f'[phase6 +{time.monotonic()-START:8.1f}s] {message}', flush=True)


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


def frozen_oneil_ready_dataset(ready_ptr: dict, prices: pd.DataFrame, asof: date) -> ReadyDataset:
    """Adapt the governed READY pointer to the frozen #33 in-memory runner.

    The frozen O'Neil R2 loader owns an older upstream manifest schema.  Do not
    loosen or mutate that frozen consumer.  Phase9 already loads the canonical
    READY parquet from its current pointer; this adapter validates the exact
    frozen engine input columns/chronology and then invokes run_ready_dataset,
    preserving the frozen analyzer and PIT cutoff while avoiding a second
    schema-specific R2 load.
    """
    missing = set(REQUIRED_COLUMNS) - set(prices.columns)
    if missing:
        raise RuntimeError(f'READY_COMPAT_MISSING_COLUMNS:{sorted(missing)}')
    frame = prices.loc[:, REQUIRED_COLUMNS].copy()
    frame['date'] = pd.to_datetime(frame['date'], errors='raise').dt.normalize()
    if frame['date'].isna().any():
        raise RuntimeError('READY_COMPAT_NULL_DATE')
    if frame.duplicated(['security_id', 'date']).any():
        raise RuntimeError('READY_COMPAT_DUPLICATE_SECURITY_DATE')
    frame = frame.loc[frame['date'].dt.date <= asof].sort_values(['security_id', 'date']).reset_index(drop=True)
    backwards = frame.groupby('security_id', sort=False)['date'].apply(lambda s: not s.is_monotonic_increasing)
    if backwards.any():
        raise RuntimeError('READY_COMPAT_NONMONOTONIC_SECURITY_HISTORY')
    source_manifest = {
        'compat_contract': 'PHASE9_READY_TO_FROZEN_ONEIL_V1',
        'ready_pointer_sha256': canonical_sha(ready_ptr),
        'parquet_key': ready_ptr.get('parquet_key'),
        'asof_date': asof.isoformat(),
        'rows': len(frame),
        'security_ids': sorted(frame['security_id'].astype(str).unique().tolist()),
    }
    return ReadyDataset(frame=frame, manifest=source_manifest)


def add_rs(prices: pd.DataFrame) -> pd.DataFrame:
    p=prices.sort_values(['security_id','date']).copy(); p['close63']=p.groupby('security_id')['close'].shift(63); p['rs63']=p['close']/p['close63']-1
    p['rs_percentile']=p.groupby('date')['rs63'].rank(pct=True)*100.0
    return p


def prepare_fundamentals(wide: pd.DataFrame, long: pd.DataFrame):
    sym='ticker' if 'ticker' in wide.columns else 'symbol'
    w=wide.copy(); w[sym]=w[sym].astype(str).str.upper(); w['accepted_at']=pd.to_datetime(w['accepted_at'],utc=True,errors='coerce')
    l=long.copy(); l['symbol']=l['symbol'].astype(str).str.upper(); l['accepted_at']=pd.to_datetime(l['accepted_at'],utc=True,errors='coerce')
    annual=l[l['period_type'].eq('FY') & l['metric'].eq('eps')].copy(); annual['fy']=annual['fiscal_year'].astype('Int64')
    return sym,w,annual


def load_institutional(s3, bucket: str):
    ptr = js(s3, bucket, 'institutional_sponsorship/current.json'); manifest = js(s3, bucket, ptr['manifest_key']); validate_institutional_pointer(ptr, manifest)
    return ptr, manifest, csv(s3,bucket,ptr['live_sponsorship_mapped_key']), pq(s3,bucket,ptr['history_state_events_key']), pq(s3,bucket,ptr['uncertainty_state_events_key'])


def _group(df: pd.DataFrame, column: str) -> dict[str, pd.DataFrame]:
    if df.empty:
        return {}
    keys = df[column].astype(str).str.upper()
    return {str(k).upper(): g for k, g in df.assign(_cache_key=keys).groupby('_cache_key', sort=False)}


def _cusip9(security_id: str) -> str | None:
    sid = str(security_id).strip().upper()
    return sid[2:11] if len(sid) == 12 and sid.startswith('US') else None


def publish():
    log('START publisher')
    s3 = s3_client(); bucket = env('R2_BUCKET_NAME'); run_id = env('GITHUB_RUN_ID'); repo_sha = env('GITHUB_SHA')
    log('Loading canonical ready dataset for as-of discovery')
    asof, ready_ptr, prices = latest_ready(s3, bucket); cutoff = pd.Timestamp(regular_close_cutoff(asof))
    log(f'Ready loaded: rows={len(prices):,}, securities={prices.security_id.nunique():,}, asof={asof}')

    scan_count = 0
    def observed_analyzer(security_id, ticker, frame, scan_asof):
        nonlocal scan_count
        scan_count += 1
        if scan_count == 1 or scan_count % 25 == 0:
            log(f'#33 scan progress: securities={scan_count:,}; current={ticker}; bars={len(frame):,}')
        return analyze_security(security_id, ticker, frame, scan_asof)

    log('Running frozen #33 pattern engine (canonical READY via compatibility adapter)')
    oneil_ready = frozen_oneil_ready_dataset(ready_ptr, prices, asof)
    p33 = run_ready_dataset(oneil_ready, asof_date=asof, analyze_security=observed_analyzer)
    patterns = [PatternAssessment.from_mapping(r.to_dict()) for r in p33.records]
    log(f'#33 COMPLETE: scanned={scan_count:,}, assessments={len(patterns):,}')

    log('Loading fundamentals PIT artifacts')
    fptr = js(s3,bucket,'fundamentals/current.json'); fmanifest = js(s3,bucket,fptr['manifest_key']); fart=fmanifest['artifacts']
    wide = pq(s3,bucket,fart['fundamentals_point_in_time.parquet']['key']); long = pq(s3,bucket,fart['fundamentals_point_in_time_long.parquet']['key']); fsym, wide, annual = prepare_fundamentals(wide,long)
    log(f'Fundamentals loaded: wide={len(wide):,}, long={len(long):,}, annual={len(annual):,}')

    log('Loading institutional PIT artifacts')
    iptr, imanifest, ilive, ihist, iunc = load_institutional(s3,bucket)
    log(f'Institutional loaded: live={len(ilive):,}, history={len(ihist):,}, uncertainty={len(iunc):,}')
    log('Loading canonical M state')
    mptr = js(s3,bucket,'market/state/official.json'); mraw=raw(s3,bucket,mptr['state_key']); m = consume_market_state(pointer=mptr,state_bytes=mraw,decision_session_date=asof)
    log(f'M loaded: market_state={m.market_state}, entry_state={m.M_entry_state}')

    log('Computing RS percentiles')
    prices = add_rs(prices); rs_day = prices[prices['date'].eq(pd.Timestamp(asof))][['security_id','rs_percentile']]; rsmap = dict(zip(rs_day['security_id'].astype(str),rs_day['rs_percentile'])); bysid = {str(k):g.sort_values('date') for k,g in prices.groupby('security_id')}
    log(f'RS COMPLETE: asof securities={len(rsmap):,}')

    log('Preparing security-level caches (bars + C/A/L/I/M evidence)')
    wide_by_ticker = _group(wide, fsym)
    annual_by_ticker = _group(annual, fsym)
    live_by_sid = _group(ilive, 'security_id')
    hist_by_cusip = _group(ihist, 'cusip')
    uncertainty_by_cusip = _group(iunc, 'cusip')
    evidence_cache = {}
    for cache_i, (sid, bars) in enumerate(bysid.items(), 1):
        ticker = str(bars.iloc[-1]['ticker']).upper()
        wf = wide_by_ticker.get(ticker, wide.iloc[0:0])
        af = annual_by_ticker.get(ticker, annual.iloc[0:0])
        cstate = c_screen_state(wf, cutoff)
        aobs=[]
        for _,r in af[af['accepted_at'].le(cutoff)].sort_values('fy').iterrows():
            growth = None if pd.isna(r.get('yoy_growth')) else float(r['yoy_growth'])
            aobs.append(AnnualEpsObservation(int(r['fy']), growth, str(r.get('missing_reason') or '')))
        astate=a_screen_state(aobs)
        lstate=l_screen_state(float(rsmap.get(sid,float('nan')))) if pd.notna(rsmap.get(sid)) else l_screen_state(float('nan'))
        cusip = _cusip9(sid)
        ires=resolve_institutional_pit(decision_time=cutoff.to_pydatetime(),security_id=sid,cusip=cusip,live_sponsorship_mapped=live_by_sid.get(sid, ilive.iloc[0:0]),history_state_events=hist_by_cusip.get(cusip, ihist.iloc[0:0]) if cusip else ihist.iloc[0:0],uncertainty_state_events=uncertainty_by_cusip.get(cusip, iunc.iloc[0:0]) if cusip else iunc.iloc[0:0])
        evidence_cache[sid]=(ticker,cstate,astate,lstate,ires)
        if cache_i == 1 or cache_i % 100 == 0:
            log(f'Evidence cache progress: {cache_i:,}/{len(bysid):,}')
    log(f'Evidence caches COMPLETE: securities={len(evidence_cache):,}')

    out=[]; stages=Counter()
    log(f'Building candidates from assessments={len(patterns):,}')
    for i,pat in enumerate(patterns,1):
        sid=pat.security_id; bars=bysid.get(sid)
        if bars is None or bars.empty: continue
        ticker,cstate,astate,lstate,ires=evidence_cache[sid]
        p=bars.iloc[-1]
        evidence=CandidateEvidence(c_state=cstate,a_state=astate,l_state=lstate,i_state=ires.state,m_state=m.M_entry_state)
        cand=build_candidate(pattern=pat,evidence=evidence,bar=DailyBar(asof,float(p['open']),float(p['high']),float(p['low']),float(p['close']),float(p['volume'])))
        rec=cand.to_dict(); rec['ticker']=ticker; out.append(rec); stages[rec['candidate_stage']]+=1
        if i == 1 or i % 100000 == 0:
            log(f'Candidate build progress: {i:,}/{len(patterns):,}')
    log(f'Candidate build COMPLETE: records={len(out):,}, stages={dict(stages)}')

    body=('\n'.join(json.dumps(r,sort_keys=True,separators=(',',':'),default=str) for r in out)+'\n').encode() if out else b''
    digest=sha256_bytes(body); prefix=f'canslim/candidates/snapshots/{asof.isoformat()}/run-{run_id}'
    manifest={'schema_version':1,'generator_version':GENERATOR_VERSION,'oneil_repo_sha':ONEIL_REPO_SHA,'repo_sha':repo_sha,'run_id':run_id,'asof_date':asof.isoformat(),'source_ready_pointer_sha256':canonical_sha(ready_ptr),'record_count':len(out),'stage_counts':dict(stages),'candidates_sha256':digest,'candidates_key':f'{prefix}/candidates.jsonl','created_at':datetime.now(timezone.utc).isoformat()}
    s3.put_object(Bucket=bucket,Key=manifest['candidates_key'],Body=body,ContentType='application/x-ndjson')
    mbody=json.dumps(manifest,sort_keys=True,separators=(',',':')).encode(); msha=sha256_bytes(mbody); mkey=f'{prefix}/manifest.json'; s3.put_object(Bucket=bucket,Key=mkey,Body=mbody,ContentType='application/json')
    pointer={'schema_version':1,'type':'canslim_production_candidate_pointer','status':'READY','asof_date':asof.isoformat(),'snapshot_prefix':prefix,'candidates_key':manifest['candidates_key'],'candidates_sha256':digest,'manifest_key':mkey,'manifest_sha256':msha,'record_count':len(out),'stage_counts':dict(stages),'updated_at':datetime.now(timezone.utc).isoformat()}
    s3.put_object(Bucket=bucket,Key=POINTER_KEY,Body=json.dumps(pointer,sort_keys=True,separators=(',',':')).encode(),ContentType='application/json')
    log(f'PUBLISHED pointer={POINTER_KEY} asof={asof} records={len(out):,}')
    print(json.dumps({'pointer':pointer,'manifest':manifest},indent=2,sort_keys=True))

if __name__=='__main__': publish()
