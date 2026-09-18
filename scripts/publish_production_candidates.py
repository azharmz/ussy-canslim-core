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
    target_key = os.getenv('CANSLIM_READY_PARQUET_KEY') or ptr['parquet_key']
    target_payload = raw(s3, bucket, target_key)
    target_sha256 = sha256_bytes(target_payload)
    frame = pd.read_parquet(io.BytesIO(target_payload))
    asof = pd.to_datetime(frame['date'], errors='raise').dt.date.max()
    expected_asof = os.getenv('CANSLIM_READY_ASOF_DATE')
    if expected_asof and asof.isoformat() != expected_asof:
        raise RuntimeError(f'READY_TARGET_DATE_MISMATCH: expected={expected_asof} actual={asof}')
    frame['date'] = pd.to_datetime(frame['date'], errors='raise').dt.normalize()
    source_ptr = dict(ptr)
    source_ptr['source_current_pointer_parquet_key'] = ptr.get('parquet_key')
    source_ptr['source_current_pointer_sha256'] = ptr.get('sha256')
    source_ptr['parquet_key'] = target_key
    source_ptr['sha256'] = target_sha256
    source_ptr['as_of_date'] = asof.isoformat()
    source_ptr['recovery_target'] = target_key != ptr.get('parquet_key')
    return asof, source_ptr, frame


def frozen_oneil_ready_dataset(ready_ptr: dict, prices: pd.DataFrame, asof: date) -> ReadyDataset:
    """Adapt canonical READY to the frozen #33 in-memory runner without changing #33."""
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
    fy = long.loc[long['form'].astype(str).str.upper().isin(['10-K','10-K/A']) & long['accession'].notna() & long['fy'].notna(), ['accession','fy']].copy()
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
        latest_period = q['fiscal_period_end'].max(); row = q[q['fiscal_period_end'].eq(latest_period)].sort_values('accepted_at').iloc[-1]
        eps = None if pd.isna(row['quarterly_eps_yoy']) else float(row['quarterly_eps_yoy']); rev = None if pd.isna(row['quarterly_revenue_yoy']) else float(row['quarterly_revenue_yoy'])
        c_state, c_reason = c_screen_state(quarterly_eps_yoy=eps, quarterly_revenue_yoy=rev, available_on=row['accepted_at'].isoformat(), asof_date=cutoff.isoformat())
    a = annual[annual[sym].astype(str).eq(ticker) & annual['annual_eps_accepted_at'].notna() & annual['annual_eps_accepted_at'].le(cutoff)].copy(); observations = []
    if not a.empty:
        a = a.dropna(subset=['annual_fy']).sort_values(['annual_fy','annual_eps_accepted_at']).groupby('annual_fy', as_index=False).tail(1)
        for _, r in a.iterrows(): observations.append(AnnualEpsObservation(int(r['annual_fy']), None if pd.isna(r['annual_eps_growth']) else float(r['annual_eps_growth']), r['annual_eps_accepted_at'].isoformat()))
    a_state, _, a_reason = a_screen_state(observations, asof_date=cutoff.isoformat())
    return c_state, a_state, c_reason, a_reason


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

    # Phase-6 performance remediation: all values below are security/decision-time
    # evidence. Compute them once per security and reuse them across the frozen #33
    # morphology assessments. This changes computation shape only, not semantics.
    log('Preparing security-level caches (bars + C/A/L/I/M evidence)')
    wide_by_ticker = _group(wide, fsym)
    annual_by_ticker = _group(annual, fsym)
    live_by_sid = _group(ilive, 'security_id')
    hist_by_cusip = _group(ihist, 'cusip')
    unc_by_cusip = _group(iunc, 'cusip')
    empty_wide = wide.iloc[0:0]
    empty_annual = annual.iloc[0:0]
    empty_live = ilive.iloc[0:0]
    empty_hist = ihist.iloc[0:0]
    empty_unc = iunc.iloc[0:0]

    security_ticker: dict[str, str] = {}
    for p in patterns:
        security_ticker.setdefault(p.security_id, p.ticker)

    bars_cache: dict[str, list[DailyBar]] = {}
    evidence_cache: dict[str, tuple[CandidateEvidence, str, str, object]] = {}
    for n, (sid, ticker) in enumerate(security_ticker.items(), 1):
        if n == 1 or n % 25 == 0 or n == len(security_ticker):
            log(f'Evidence cache progress: {n:,}/{len(security_ticker):,} security={ticker}')
        g = bysid.get(sid)
        if g is None:
            continue
        bars_cache[sid] = [DailyBar(r.date.date().isoformat(),float(r.open),float(r.high),float(r.low),float(r.close),float(r.volume)) for r in g.itertuples()]
        twide = wide_by_ticker.get(str(ticker).upper(), empty_wide)
        tannual = annual_by_ticker.get(str(ticker).upper(), empty_annual)
        c_state,a_state,c_reason,a_reason = fundamental_states(fsym, twide, tannual, ticker, cutoff, asof.isoformat())
        cusip = _cusip9(sid)
        inst = resolve_institutional_pit(
            security_id=sid,
            decision_cutoff=cutoff,
            live_state=live_by_sid.get(str(sid).upper(), empty_live),
            history_events=hist_by_cusip.get(cusip, empty_hist) if cusip else empty_hist,
            uncertainty_events=unc_by_cusip.get(cusip, empty_unc) if cusip else empty_unc,
        )
        rs=rsmap.get(sid); l_state,_=l_screen_state(None if pd.isna(rs) else float(rs))
        evidence=CandidateEvidence(C_screen_state=c_state,A_screen_state=a_state,L_individual_leadership_state=l_state,M_entry_state=m.M_entry_state,I_evidence_state=inst.state,N_catalyst_state='NOT_IMPLEMENTED',industry_evidence_state='NOT_IMPLEMENTED',rs_rating_proxy_percentile=None if pd.isna(rs) else float(rs),M_market_state=m.market_state)
        evidence_cache[sid] = (evidence, c_reason, a_reason, inst)
    log(f'Security caches COMPLETE: bars={len(bars_cache):,}, evidence={len(evidence_cache):,}')

    outputs=[]; ca_reasons=Counter(); i_reasons=Counter(); total=len(patterns)
    log(f'Building candidates from cached security evidence: total assessments={total:,}')
    for idx,p in enumerate(patterns,1):
        if idx == 1 or idx % 10000 == 0 or idx == total: log(f'Candidate progress: {idx:,}/{total:,} ({idx/max(total,1):.1%}) ticker={p.ticker}')
        bars=bars_cache.get(p.security_id); cached=evidence_cache.get(p.security_id)
        if bars is None or cached is None: continue
        evidence,c_reason,a_reason,inst=cached
        ca_reasons[c_reason]+=1; ca_reasons[a_reason]+=1; i_reasons[inst.reason]+=1
        cand=build_candidate(p,bars,evidence); row={name:getattr(cand,name) for name in cand.__dataclass_fields__}
        row.update({'C_reason':c_reason,'A_reason':a_reason,'I_reason':inst.reason,'I_latest_period':inst.latest_period,'I_prior_period':inst.prior_period,'I_latest_available_at':inst.latest_available_at,'I_prior_available_on':inst.prior_available_on,'M_state_key':m.state_key,'M_state_sha256':m.state_sha256}); outputs.append(row)
    log(f'Candidate build COMPLETE: outputs={len(outputs):,}')

    log('Serializing and uploading immutable candidate/pattern artifacts')
    payload=''.join(json.dumps(x,sort_keys=True,default=str)+'\n' for x in outputs).encode(); pattern_payload=p33.jsonl.encode(); produced=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'); prefix=f'canslim/candidates/snapshots/{asof.isoformat()}/run-{run_id}'; candidate_key=f'{prefix}/candidates.jsonl'; pattern_key=f'{prefix}/patterns.jsonl'
    s3.put_object(Bucket=bucket,Key=candidate_key,Body=payload,ContentType='application/x-ndjson'); s3.put_object(Bucket=bucket,Key=pattern_key,Body=pattern_payload,ContentType='application/x-ndjson')
    log(f'Immutable artifacts uploaded: prefix={prefix}')

    stage_counts=Counter(x['candidate_stage'] for x in outputs)
    manifest={'schema_version':1,'type':'canslim_production_candidate_snapshot','status':'READY','generator_version':GENERATOR_VERSION,'produced_at':produced,'asof_date':asof.isoformat(),'decision_asof_timestamp':cutoff.isoformat(),'snapshot_prefix':prefix,'publisher_run_id':run_id,'publisher_commit':repo_sha,'oneil_repo_sha':ONEIL_REPO_SHA,'pattern_engine_version':'33-core-p8-frozen-v1','pattern_contract':'oneil-pattern-output-v2','candidate_contract':'canslim-candidate-output-v2','eligibility_contract':'canslim-eligibility-contract-v1','ready_pointer':ready_ptr,'fundamentals_manifest_key':fptr['manifest_key'],'fundamentals_manifest_sha256':canonical_sha(fmanifest),'institutional_manifest_key':iptr['manifest_key'],'institutional_manifest_sha256':canonical_sha(imanifest),'institutional_live_source_run_id':str(iptr['live_source_run_id']),'market_state_key':m.state_key,'market_state_sha256':m.state_sha256,'market_classifier_version':m.classifier_version,'market_action_version':m.market_action_version,'candidate_count':len(outputs),'candidate_stage_counts':dict(stage_counts),'ca_reason_counts':dict(ca_reasons),'i_reason_counts':dict(i_reasons),'artifacts':{'candidates.jsonl':{'key':candidate_key,'sha256':sha256_bytes(payload),'size_bytes':len(payload)},'patterns.jsonl':{'key':pattern_key,'sha256':sha256_bytes(pattern_payload),'size_bytes':len(pattern_payload)}},'advanced_patterns_allowed':False,'N_catalyst_state_policy':'EXPLICIT_NOT_IMPLEMENTED_EVIDENCE_ONLY','strategy_returns_inspected':False}
    mbytes=json.dumps(manifest,indent=2,sort_keys=True,default=str).encode(); mkey=f'{prefix}/manifest.json'; s3.put_object(Bucket=bucket,Key=mkey,Body=mbytes,ContentType='application/json')
    log('Manifest uploaded; publishing mutable pointer LAST')
    pointer={'schema_version':1,'type':'canslim_production_candidate_pointer','status':'READY','updated_at':produced,'asof_date':asof.isoformat(),'decision_asof_timestamp':cutoff.isoformat(),'snapshot_prefix':prefix,'manifest_key':mkey,'manifest_sha256':sha256_bytes(mbytes),'candidates_key':candidate_key,'candidates_sha256':sha256_bytes(payload),'candidate_count':len(outputs),'publisher_run_id':run_id,'publisher_commit':repo_sha}
    s3.put_object(Bucket=bucket,Key=POINTER_KEY,Body=json.dumps(pointer,indent=2,sort_keys=True).encode(),ContentType='application/json')
    log(f'DONE pointer={POINTER_KEY}; candidates={len(outputs):,}; stages={dict(stage_counts)}')
    print(json.dumps({'pointer':pointer,'candidate_stage_counts':dict(stage_counts)},indent=2,sort_keys=True), flush=True)

if __name__=='__main__': publish()
