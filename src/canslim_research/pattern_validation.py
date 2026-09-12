"""Independent morphology-label validation for Stage #33 pattern lineages.

This module deliberately evaluates detector output against human/externally adjudicated
morphology labels only. It does not consume returns or downstream trade outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, Mapping, Sequence

MORPHOLOGY_VALIDATION_VERSION = "p8-morphology-validation-v0.1"
IMPLEMENTED_PATTERN_TYPES = frozenset(
    {"CUP_WITH_HANDLE", "CUP_WITHOUT_HANDLE", "DOUBLE_BOTTOM", "FLAT_BASE"}
)


@dataclass(frozen=True)
class MorphologyLabel:
    label_id: str
    security_id: str
    ticker: str
    pattern_type: str
    start_date_min: str
    start_date_max: str
    end_date_min: str
    end_date_max: str
    adjudication: str = "POSITIVE"
    notes: str = ""

    @classmethod
    def from_dict(cls, row: Mapping[str, object]) -> "MorphologyLabel":
        required = (
            "label_id",
            "security_id",
            "ticker",
            "pattern_type",
            "start_date_min",
            "start_date_max",
            "end_date_min",
            "end_date_max",
        )
        missing = [key for key in required if not row.get(key)]
        if missing:
            raise ValueError(f"morphology label missing required fields: {', '.join(missing)}")
        pattern_type = str(row["pattern_type"])
        if pattern_type not in IMPLEMENTED_PATTERN_TYPES:
            raise ValueError(f"unsupported morphology label pattern_type={pattern_type}")
        adjudication = str(row.get("adjudication", "POSITIVE")).upper()
        if adjudication not in {"POSITIVE", "NEGATIVE"}:
            raise ValueError("adjudication must be POSITIVE or NEGATIVE")
        label = cls(
            label_id=str(row["label_id"]),
            security_id=str(row["security_id"]),
            ticker=str(row["ticker"]).upper(),
            pattern_type=pattern_type,
            start_date_min=str(row["start_date_min"]),
            start_date_max=str(row["start_date_max"]),
            end_date_min=str(row["end_date_min"]),
            end_date_max=str(row["end_date_max"]),
            adjudication=adjudication,
            notes=str(row.get("notes", "")),
        )
        for value in (
            label.start_date_min,
            label.start_date_max,
            label.end_date_min,
            label.end_date_max,
        ):
            date.fromisoformat(value)
        if label.start_date_min > label.start_date_max:
            raise ValueError(f"label {label.label_id}: invalid start-date range")
        if label.end_date_min > label.end_date_max:
            raise ValueError(f"label {label.label_id}: invalid end-date range")
        return label


def _overlaps(a_min: str, a_max: str, b_min: str, b_max: str) -> bool:
    return max(a_min, b_min) <= min(a_max, b_max)


def _lineage_matches_label(lineage: Mapping[str, object], label: MorphologyLabel) -> bool:
    if str(lineage.get("security_id", "")) != label.security_id:
        return False
    if str(lineage.get("pattern_type", "")) != label.pattern_type:
        return False
    start = str(lineage.get("base_start_date", ""))
    end = str(lineage.get("last_supported_date", lineage.get("base_end_or_breakout_ready_date", "")))
    if not start or not end:
        return False
    return _overlaps(start, start, label.start_date_min, label.start_date_max) and _overlaps(
        end, end, label.end_date_min, label.end_date_max
    )


def evaluate_morphology_labels(
    labels: Sequence[MorphologyLabel],
    lineages: Iterable[Mapping[str, object]],
) -> dict:
    """Compare independently adjudicated labels with detector lineages.

    Positive labels yield TP/FN. Negative labels define forbidden morphology windows and
    yield TN/FP. Detector lineages not covered by any label are reported as UNADJUDICATED,
    not silently counted as false positives.
    """

    lineage_rows = [dict(row) for row in lineages]
    matched_lineage_ids: set[str] = set()
    outcomes: list[dict] = []
    tp = fn = tn = fp = 0

    for label in labels:
        matches = [row for row in lineage_rows if _lineage_matches_label(row, label)]
        lineage_ids = [str(row.get("lineage_id", "")) for row in matches]
        matched_lineage_ids.update(lineage_id for lineage_id in lineage_ids if lineage_id)
        if label.adjudication == "POSITIVE":
            outcome = "TP" if matches else "FN"
            tp += bool(matches)
            fn += not bool(matches)
        else:
            outcome = "FP" if matches else "TN"
            fp += bool(matches)
            tn += not bool(matches)
        outcomes.append(
            {
                "label_id": label.label_id,
                "adjudication": label.adjudication,
                "pattern_type": label.pattern_type,
                "outcome": outcome,
                "matched_lineage_ids": lineage_ids,
            }
        )

    unadjudicated = [
        row for row in lineage_rows if str(row.get("lineage_id", "")) not in matched_lineage_ids
    ]
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None

    return {
        "validation_version": MORPHOLOGY_VALIDATION_VERSION,
        "label_count": len(labels),
        "positive_label_count": sum(label.adjudication == "POSITIVE" for label in labels),
        "negative_label_count": sum(label.adjudication == "NEGATIVE" for label in labels),
        "tp": tp,
        "fn": fn,
        "tn": tn,
        "fp": fp,
        "precision_on_adjudicated_windows": precision,
        "recall_on_positive_labels": recall,
        "unadjudicated_lineage_count": len(unadjudicated),
        "unadjudicated_lineage_ids": [str(row.get("lineage_id", "")) for row in unadjudicated],
        "label_outcomes": outcomes,
        "guardrail": "Unlabelled detector output is UNADJUDICATED, never automatically FP.",
    }
