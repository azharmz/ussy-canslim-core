from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "sec-edgar-access-probe"
OUT.mkdir(parents=True, exist_ok=True)

USER_AGENT = os.getenv(
    "SEC_USER_AGENT",
    "azharmz ussy-canslim-research 127322848+azharmz@users.noreply.github.com",
)

PROBES = {
    "data_submissions": "https://data.sec.gov/submissions/CIK0001067983.json",
    "archives_master_index": "https://www.sec.gov/Archives/edgar/full-index/2026/QTR2/master.idx",
    "bulk_13f_zip": "https://www.sec.gov/files/structureddata/data/form-13f-data-sets/01mar2026-31may2026_form13f.zip",
}


def probe(name: str, url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Encoding": "identity",
            "Accept": "application/json,text/plain,application/octet-stream,*/*",
        },
    )
    out = {"name": name, "url": url, "ok": False, "status": None, "bytes_sampled": 0, "error": None}
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            out["status"] = int(getattr(resp, "status", 200))
            sample = resp.read(65536)
            out["bytes_sampled"] = len(sample)
            out["content_type"] = resp.headers.get("Content-Type")
            out["ok"] = out["status"] == 200 and len(sample) > 0
    except urllib.error.HTTPError as exc:
        out["status"] = int(exc.code)
        out["error"] = f"HTTPError: {exc.code} {exc.reason}"
    except Exception as exc:  # evidence probe: preserve exact failure class
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def main() -> None:
    rows = [probe(name, url) for name, url in PROBES.items()]
    summary = {
        "experiment": "SEC_EDGAR_ACCESS_PROBE_V1",
        "evidence_class": "INFRASTRUCTURE_CONNECTIVITY_ONLY",
        "strategy_returns_inspected": False,
        "fwd1_modified": False,
        "results": rows,
        "usable_first_party_path": any(r["ok"] for r in rows if r["name"] != "bulk_13f_zip"),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))

    # This probe should succeed as a workflow even if SEC blocks all paths: the
    # result is evidence used to choose the ingestion boundary, not a CI failure.


if __name__ == "__main__":
    main()
