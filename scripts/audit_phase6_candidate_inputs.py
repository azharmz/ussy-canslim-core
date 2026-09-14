from __future__ import annotations

import io
import json
import os
from pathlib import Path

import boto3
import pandas as pd

OUT = Path('results/remediation-phase6-input-audit')


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f'missing {name}')
    return value


def client():
    return boto3.client(
        's3', endpoint_url=env('R2_ENDPOINT'),
        aws_access_key_id=env('R2_ACCESS_KEY_ID'),
        aws_secret_access_key=env('R2_SECRET_ACCESS_KEY'), region_name='auto')


def raw(s3, bucket, key):
    return s3.get_object(Bucket=bucket, Key=key)['Body'].read()


def js(s3, bucket, key):
    return json.loads(raw(s3, bucket, key))


def pq(s3, bucket, key):
    return pd.read_parquet(io.BytesIO(raw(s3, bucket, key)))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = client(); bucket = env('R2_BUCKET_NAME')
    ptr = js(s3, bucket, 'fundamentals/current.json')
    manifest = js(s3, bucket, ptr['manifest_key'])
    art = manifest['artifacts']
    wide = pq(s3, bucket, art['fundamentals_point_in_time.parquet']['key'])
    long = pq(s3, bucket, art['fundamentals_point_in_time_long.parquet']['key'])

    required_wide = {
        'accepted_at','fiscal_period_end','quarterly_eps_yoy','quarterly_revenue_yoy',
        'annual_eps_accepted_at','annual_eps_source_accession','annual_eps_growth'
    }
    required_long = {'accession','form','fy'}
    missing_wide = sorted(required_wide - set(wide.columns))
    missing_long = sorted(required_long - set(long.columns))
    if missing_wide or missing_long:
        raise RuntimeError(f'fundamental contract missing wide={missing_wide} long={missing_long}')

    accepted = pd.to_datetime(wide['accepted_at'], errors='coerce', utc=True)
    annual_accepted = pd.to_datetime(wide['annual_eps_accepted_at'], errors='coerce', utc=True)
    annual_growth = pd.to_numeric(wide['annual_eps_growth'], errors='coerce')
    q_eps = pd.to_numeric(wide['quarterly_eps_yoy'], errors='coerce')
    q_rev = pd.to_numeric(wide['quarterly_revenue_yoy'], errors='coerce')
    annual_forms = long['form'].astype(str).str.upper().isin(['10-K','10-K/A'])
    fy_bridge = long.loc[annual_forms & long['accession'].notna() & long['fy'].notna(), ['accession','fy']].drop_duplicates()

    summary = {
        'status': 'PASS',
        'fundamentals_manifest_key': ptr['manifest_key'],
        'wide_rows': int(len(wide)),
        'long_rows': int(len(long)),
        'accepted_at_nonnull': int(accepted.notna().sum()),
        'quarterly_eps_yoy_nonnull': int(q_eps.notna().sum()),
        'quarterly_revenue_yoy_nonnull': int(q_rev.notna().sum()),
        'annual_eps_accepted_at_nonnull': int(annual_accepted.notna().sum()),
        'annual_eps_growth_nonnull': int(annual_growth.notna().sum()),
        'annual_accession_fy_bridge_rows': int(len(fy_bridge)),
        'c_requires_eps_and_revenue': True,
        'a_requires_three_consecutive_fy_growth_states': True,
        'strategy_returns_inspected': False,
    }
    for key in ('quarterly_eps_yoy_nonnull','quarterly_revenue_yoy_nonnull','annual_eps_growth_nonnull','annual_accession_fy_bridge_rows'):
        if summary[key] <= 0:
            raise RuntimeError(f'production fundamental input has zero usable rows: {key}')
    (OUT/'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True), encoding='utf-8')
    print(json.dumps(summary, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
