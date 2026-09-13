from __future__ import annotations

import io
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

import boto3
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from canslim_research.execution_entry_variants_v1 import (
    BUY_ZONE_MAX,
    r0_t1_baseline,
    r1_first_valid_open,
    r2_full_pivot_hold,
    r3_retest_reclaim_proxy,
)

OUT = ROOT / 'results' / 'e36-breakout-execution-diagnostic'
HORIZONS = (5, 10, 20, 30)


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f'Missing environment variable {name}')
    return value


def s3_client():
    return boto3.client(
        's3',
        endpoint_url=env('R2_ENDPOINT'),
        aws_access_key_id=env('R2_ACCESS_KEY_ID'),
        aws_secret_access_key=env('R2_SECRET_ACCESS_KEY'),
        region_name='auto',
    )


def load_history(s3, bucket: str, security_id: str) -> pd.DataFrame:
    key = f'backtest/ohlcv/{security_id}.parquet'
    payload = s3.get_object(Bucket=bucket, Key=key)['Body'].read()
    frame = pd.read_parquet(io.BytesIO(payload))
    frame['date'] = pd.to_datetime(frame['date'], errors='raise').dt.normalize()
    return frame.sort_values('date').drop_duplicates('date', keep='last').reset_index(drop=True)


def finite_stats(values: list[float]) -> dict:
    if not values:
        return {'n': 0, 'mean': None, 'median': None, 'win_rate': None, 'p25': None, 'p75': None}
    x = np.asarray(values, dtype=float)
    return {
        'n': int(len(x)),
        'mean': float(np.mean(x)),
        'median': float(np.median(x)),
        'win_rate': float(np.mean(x > 0)),
        'p25': float(np.percentile(x, 25)),
        'p75': float(np.percentile(x, 75)),
    }


def main() -> None:
    observations_path = Path(os.environ.get('E36_OBSERVATIONS', 'input/v35/observations.jsonl'))
    OUT.mkdir(parents=True, exist_ok=True)

    source: list[dict] = []
    with observations_path.open('r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get('candidate_stage') == 'BREAKOUT_CONFIRMED':
                source.append(row)

    if not source:
        raise RuntimeError('No BREAKOUT_CONFIRMED source records')

    candidate_ids = [str(x['candidate_id']) for x in source]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise RuntimeError('Duplicate candidate_id in diagnostic source')

    s3 = s3_client()
    bucket = env('R2_BUCKET_NAME')
    histories = {sid: load_history(s3, bucket, sid) for sid in sorted({str(x['security_id']) for x in source})}

    variant_fns = {
        'E36-R0': lambda p, o, l, c: r0_t1_baseline(pivot=p, opens=o),
        'E36-R1': lambda p, o, l, c: r1_first_valid_open(pivot=p, opens=o),
        'E36-R2': lambda p, o, l, c: r2_full_pivot_hold(pivot=p, opens=o, lows=l, closes=c),
        'E36-R3': lambda p, o, l, c: r3_retest_reclaim_proxy(pivot=p, opens=o, lows=l, closes=c),
    }

    decisions: list[dict] = []
    findings: list[dict] = []
    contexts: dict[tuple[str, str], tuple[pd.DataFrame, int]] = {}

    for row in source:
        cid = str(row['candidate_id'])
        sid = str(row['security_id'])
        signal = pd.Timestamp(row['asof_date']).normalize()
        breakout = pd.Timestamp(row['breakout_date']).normalize()
        pivot = float(row['pivot_level'])
        if breakout != signal:
            findings.append({'candidate_id': cid, 'variant': 'SOURCE', 'code': 'BREAKOUT_ASOF_MISMATCH'})

        frame = histories[sid]
        future = frame[frame['date'] > signal].reset_index(drop=True)
        if future.empty:
            for variant in variant_fns:
                decisions.append({
                    'candidate_id': cid, 'security_id': sid, 'ticker': row.get('ticker'),
                    'signal_date': signal.date().isoformat(), 'pattern': row.get('pattern'),
                    'variant': variant, 'executed': False, 'reason': 'NO_T1_BAR',
                    'entry_offset': None, 'entry_date': None, 'entry_price': None,
                    'confirmation_offset': None, 'fill_extension_from_pivot': None,
                    'signal_gap_through_pivot': bool(row.get('gap_through_pivot', False)),
                })
            continue

        opens = future['open'].astype(float).head(3).tolist()
        lows = future['low'].astype(float).head(3).tolist()
        closes = future['close'].astype(float).head(3).tolist()

        for variant, fn in variant_fns.items():
            d = fn(pivot, opens, lows, closes)
            rec = {
                'candidate_id': cid, 'security_id': sid, 'ticker': row.get('ticker'),
                'signal_date': signal.date().isoformat(), 'pattern': row.get('pattern'),
                'variant': variant, 'executed': bool(d.executed), 'reason': d.reason,
                'entry_offset': d.entry_offset, 'entry_date': None, 'entry_price': d.entry_price,
                'confirmation_offset': d.confirmation_offset,
                'fill_extension_from_pivot': None,
                'signal_gap_through_pivot': bool(row.get('gap_through_pivot', False)),
            }
            if d.executed:
                off = int(d.entry_offset)
                if off < 1 or off > 3:
                    findings.append({'candidate_id': cid, 'variant': variant, 'code': 'ENTRY_OFFSET_OUT_OF_RANGE'})
                if off > len(future):
                    findings.append({'candidate_id': cid, 'variant': variant, 'code': 'ENTRY_BAR_MISSING'})
                else:
                    observed_open = float(future.iloc[off - 1]['open'])
                    if not np.isclose(float(d.entry_price), observed_open, rtol=0.0, atol=1e-10):
                        findings.append({'candidate_id': cid, 'variant': variant, 'code': 'FILL_NOT_OBSERVED_OPEN'})
                    if not (pivot <= float(d.entry_price) <= pivot * (1.0 + BUY_ZONE_MAX)):
                        findings.append({'candidate_id': cid, 'variant': variant, 'code': 'FILL_OUTSIDE_BUY_ZONE'})
                    if d.confirmation_offset is not None and int(d.confirmation_offset) >= off:
                        findings.append({'candidate_id': cid, 'variant': variant, 'code': 'CONFIRMATION_NOT_BEFORE_FILL'})
                    rec['entry_date'] = future.iloc[off - 1]['date'].date().isoformat()
                    rec['fill_extension_from_pivot'] = float(d.entry_price) / pivot - 1.0
                    contexts[(cid, variant)] = (future, off - 1)
            decisions.append(rec)

    decisions_df = pd.DataFrame(decisions)
    findings_df = pd.DataFrame(findings, columns=['candidate_id', 'variant', 'code'])
    decisions_df.to_csv(OUT / 'execution_decisions.csv', index=False)
    findings_df.to_csv(OUT / 'integrity_findings.csv', index=False)

    if findings:
        summary = {
            'contract': '36-breakout-confirmed-execution-diagnostic-v1',
            'source_count': len(source),
            'integrity_finding_count': len(findings),
            'integrity_finding_counts': dict(Counter(x['code'] for x in findings)),
            'performance_metrics_inspected': False,
            'status': 'FAILED_INTEGRITY_GATE',
        }
        (OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(summary, indent=2))
        raise RuntimeError(f'Integrity gate failed with {len(findings)} findings')

    outcomes: list[dict] = []
    for rec in decisions:
        if not rec['executed']:
            continue
        cid = rec['candidate_id']
        variant = rec['variant']
        future, entry_index = contexts[(cid, variant)]
        fill = float(rec['entry_price'])
        out = {'candidate_id': cid, 'variant': variant}
        for h in HORIZONS:
            target = entry_index + h - 1
            out[f'return_{h}s'] = None if target >= len(future) else float(future.iloc[target]['close']) / fill - 1.0
        end20 = entry_index + 20
        if end20 <= len(future):
            block = future.iloc[entry_index:end20]
            out['mfe_20s'] = float(block['high'].astype(float).max()) / fill - 1.0
            out['mae_20s'] = float(block['low'].astype(float).min()) / fill - 1.0
        else:
            out['mfe_20s'] = None
            out['mae_20s'] = None
        outcomes.append(out)

    outcomes_df = pd.DataFrame(outcomes)
    outcomes_df.to_csv(OUT / 'outcomes.csv', index=False)

    executed_sets = {
        v: set(decisions_df[(decisions_df['variant'] == v) & (decisions_df['executed'] == True)]['candidate_id'])
        for v in variant_fns
    }
    r0_set = executed_sets['E36-R0']
    variants_summary = {}
    for variant in variant_fns:
        vd = decisions_df[decisions_df['variant'] == variant]
        ex = vd[vd['executed'] == True]
        vo = outcomes_df[outcomes_df['variant'] == variant] if not outcomes_df.empty else pd.DataFrame()
        horizon_summary = {}
        for h in HORIZONS:
            col = f'return_{h}s'
            vals = [] if vo.empty else [float(x) for x in vo[col].dropna().tolist()]
            hs = finite_stats(vals)
            hs['censored'] = int(len(ex) - hs['n'])
            horizon_summary[str(h)] = hs
        mfe_vals = [] if vo.empty else [float(x) for x in vo['mfe_20s'].dropna().tolist()]
        mae_vals = [] if vo.empty else [float(x) for x in vo['mae_20s'].dropna().tolist()]
        variants_summary[variant] = {
            'source_count': len(source),
            'executed_count': int(len(ex)),
            'execution_rate': float(len(ex) / len(source)),
            'non_entry_reason_counts': dict(Counter(vd[vd['executed'] == False]['reason'].tolist())),
            'entry_offset_counts': {str(int(k)): int(v) for k, v in ex['entry_offset'].value_counts().sort_index().items()},
            'gap_through_signal_executed_count': int(ex['signal_gap_through_pivot'].sum()),
            'median_fill_extension_from_pivot': None if ex.empty else float(ex['fill_extension_from_pivot'].median()),
            'overlap_with_r0': int(len(executed_sets[variant] & r0_set)),
            'incremental_vs_r0': int(len(executed_sets[variant] - r0_set)),
            'horizons': horizon_summary,
            'mfe_20s': finite_stats(mfe_vals),
            'mae_20s': finite_stats(mae_vals),
        }

    summary = {
        'contract': '36-breakout-confirmed-execution-diagnostic-v1',
        'canonical_v35_run_id': 34763920536,
        'population': 'BREAKOUT_CONFIRMED_ONLY_DIAGNOSTIC',
        'source_count': len(source),
        'unique_securities': len({x['security_id'] for x in source}),
        'integrity_finding_count': 0,
        'performance_metrics_inspected': True,
        'status': 'COMPLETE_DIAGNOSTIC_ONLY',
        'horizon_convention': 'entry session is completed session 1',
        'variants': variants_summary,
        'interpretation_boundary': 'Not CANSLIM-eligible strategy performance; no variant promotion authorized.',
    }
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
