from __future__ import annotations

import json
import os
from pathlib import Path

import boto3

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "bt1-market-input-readiness"


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"missing {name}")
    return value


def client():
    return boto3.client(
        "s3", endpoint_url=env("R2_ENDPOINT"),
        aws_access_key_id=env("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=env("R2_SECRET_ACCESS_KEY"), region_name="auto")


def objects(s3, bucket: str) -> list[dict]:
    out = []
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket):
        out.extend(page.get("Contents", []))
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = client(); bucket = env("R2_BUCKET_NAME")
    objs = objects(s3, bucket)

    # Frozen #47 permits only the actual major-index identities. ETF proxies are
    # deliberately reported separately and can never make BT1-M READY.
    canonical_tokens = {
        "NASDAQ_COMPOSITE": ("nasdaq_composite", "nasdaq-composite", "^ixic", "ixic"),
        "SP500": ("sp500", "sp_500", "sp-500", "s&p500", "^gspc", "gspc"),
        "DJIA": ("djia", "dow_jones", "dow-jones", "^dji"),
    }
    etf_tokens = ("spy", "qqq", "dia")

    canonical = {k: [] for k in canonical_tokens}
    etf_like = []
    market_like = []
    for obj in objs:
        key = str(obj["Key"])
        low = key.lower()
        if any(tok in low for toks in canonical_tokens.values() for tok in toks):
            for index_id, toks in canonical_tokens.items():
                if any(tok in low for tok in toks):
                    canonical[index_id].append({"key": key, "bytes": int(obj.get("Size", 0))})
        if any(tok in low for tok in etf_tokens):
            etf_like.append({"key": key, "bytes": int(obj.get("Size", 0))})
        if any(tok in low for tok in ("market", "index", "benchmark")):
            market_like.append({"key": key, "bytes": int(obj.get("Size", 0))})

    counts = {k: len(v) for k, v in canonical.items()}
    summary = {
        "audit": "BT1_MARKET_INPUT_READINESS_V1",
        "strategy_returns_inspected": False,
        "frozen_input_contract": "47-market-input-data-contract-v1",
        "canonical_index_ids": ["NASDAQ_COMPOSITE", "SP500", "DJIA"],
        "etf_substitution_forbidden": True,
        "canonical_match_counts": counts,
        "canonical_matches": canonical,
        "etf_like_objects": etf_like,
        "market_or_index_like_objects": market_like,
        "historical_m_replay_ready": all(counts[x] > 0 for x in counts),
        "note": "Filename/key inventory only. A positive match still requires schema/provenance/coverage validation before historical M replay is authorized.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
