from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from canslim_research.morphology_label_pack import parse_label_pack  # noqa: E402


def _row(label_id: str, security_id: str, pattern_type: str, adjudication: str) -> dict:
    return {
        "label_id": label_id,
        "security_id": security_id,
        "ticker": security_id,
        "pattern_type": pattern_type,
        "start_date_min": "2023-01-01",
        "start_date_max": "2023-01-10",
        "end_date_min": "2023-02-01",
        "end_date_max": "2023-02-10",
        "adjudication": adjudication,
    }


def _complete_rows() -> list[dict]:
    patterns = ["CUP_WITH_HANDLE", "CUP_WITHOUT_HANDLE", "DOUBLE_BOTTOM", "FLAT_BASE"]
    rows = []
    for index, pattern in enumerate(patterns):
        security_id = "SEC-A" if index % 2 == 0 else "SEC-B"
        rows.append(_row(f"P-{index}", security_id, pattern, "POSITIVE"))
        rows.append(_row(f"N-{index}", security_id, pattern, "NEGATIVE"))
    return rows


def test_complete_label_pack_is_ready():
    labels, summary = parse_label_pack({"labels": _complete_rows()})
    assert len(labels) == 8
    assert summary.security_count == 2
    assert summary.ready_for_broader_development_validation is True
    assert summary.readiness_reasons == []


def test_missing_pattern_coverage_blocks_readiness():
    rows = _complete_rows()
    rows = [row for row in rows if row["pattern_type"] != "FLAT_BASE"]
    _, summary = parse_label_pack({"labels": rows})
    assert summary.ready_for_broader_development_validation is False
    assert summary.missing_positive_patterns == ["FLAT_BASE"]
    assert summary.missing_negative_patterns == ["FLAT_BASE"]


def test_single_security_blocks_readiness_even_with_pattern_coverage():
    rows = _complete_rows()
    for row in rows:
        row["security_id"] = "SEC-A"
    _, summary = parse_label_pack({"labels": rows})
    assert summary.ready_for_broader_development_validation is False
    assert "label pack must span at least two securities" in summary.readiness_reasons


def test_duplicate_label_id_blocks_readiness():
    rows = _complete_rows()
    rows[1]["label_id"] = rows[0]["label_id"]
    _, summary = parse_label_pack({"labels": rows})
    assert summary.ready_for_broader_development_validation is False
    assert summary.duplicate_label_ids == [rows[0]["label_id"]]


def test_label_pack_requires_labels_list():
    try:
        parse_label_pack({"not_labels": []})
    except ValueError as exc:
        assert "labels list" in str(exc)
    else:
        raise AssertionError("expected invalid label pack to fail")
