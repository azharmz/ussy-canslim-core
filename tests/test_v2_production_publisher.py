import hashlib,json,runpy
from pathlib import Path
import pytest

def _write(tmp,name,obj):
 p=tmp/name; p.write_text(json.dumps(obj,sort_keys=True)); return p
def test_v2_publisher_dry_run_and_lineage(monkeypatch,tmp_path,capsys):
 w={"lineage":{"decision_date":"2026-09-18"},"content_sha256":"w"}
 p={"decision_date":"2026-09-18","watchlist_sha256":"w","oneil_repo_sha":"3d0b35272d89c5a6f1329e8dea865b3cf7a32b0f"}
 c={"decision_date":"2026-09-18","watchlist_sha256":"w","oneil_repo_sha":p["oneil_repo_sha"],"eligibility_contract_version":"canslim-eligibility-contract-v2"}
 cb=json.dumps(c,sort_keys=True).encode()
 e={"decision_date":"2026-09-18","source_candidate_sha256":hashlib.sha256(cb).hexdigest(),"retroactive_entry_allowed":False}
 eb=json.dumps(e,sort_keys=True).encode()
 l={"decision_date":"2026-09-18","source_execution_sha256":hashlib.sha256(eb).hexdigest()}
 for key,obj in [("WATCHLIST",w),("PATTERNS",p),("CANDIDATES",c),("EXECUTION",e),("LIFECYCLE",l)]:
  path=_write(tmp_path,key.lower()+".json",obj); monkeypatch.setenv("CANSLIM_V2_"+key+"_INPUT",str(path))
 monkeypatch.setenv("CANSLIM_V2_PUBLISH_DRY_RUN","1")
 runpy.run_path("scripts/publish_v2_production.py",run_name="__main__")
 assert "DRY_RUN_OK" in capsys.readouterr().out

def test_v2_publisher_fails_closed_on_mixed_p33(monkeypatch,tmp_path):
 w={"lineage":{"decision_date":"2026-09-18"},"content_sha256":"w"}
 p={"decision_date":"2026-09-18","watchlist_sha256":"w","oneil_repo_sha":"wrong"}
 c={"decision_date":"2026-09-18","watchlist_sha256":"w","oneil_repo_sha":"wrong","eligibility_contract_version":"canslim-eligibility-contract-v2"}
 e={"decision_date":"2026-09-18","source_candidate_sha256":"x","retroactive_entry_allowed":False}
 l={"decision_date":"2026-09-18","source_execution_sha256":"y"}
 for key,obj in [("WATCHLIST",w),("PATTERNS",p),("CANDIDATES",c),("EXECUTION",e),("LIFECYCLE",l)]:
  path=_write(tmp_path,key.lower()+".json",obj); monkeypatch.setenv("CANSLIM_V2_"+key+"_INPUT",str(path))
 monkeypatch.setenv("CANSLIM_V2_PUBLISH_DRY_RUN","1")
 with pytest.raises(RuntimeError,match="P33_SHA_MISMATCH"): runpy.run_path("scripts/publish_v2_production.py",run_name="__main__")
