from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from .pattern_validation import IMPLEMENTED_PATTERN_TYPES, MorphologyLabel


LABEL_PACK_VERSION = "p8-morphology-label-pack-v0.1"


@dataclass(frozen=True)
class LabelPackSummary:
    label_pack_version: str
    label_count: int
    security_count: int
    positive_count: int
    negative_count: int
    positive_pattern_counts: dict[str, int]
    negative_pattern_counts: dict[str, int]
    missing_positive_patterns: list[str]
    missing_negative_patterns: list[str]
    duplicate_label_ids: list[str]
    ready_for_broader_development_validation: bool
    readiness_reasons: list[str]

    def to_dict(self) -> dict:
        return {
            "label_pack_version": self.label_pack_version,
            "label_count": self.label_count,
            "security_count": self.security_count,
            "positive_count": self.positive_count,
            "negative_count": self.negative_count,
            "positive_pattern_counts": dict(self.positive_pattern_counts),
            "negative_pattern_counts": dict(self.negative_pattern_counts),
            "missing_positive_patterns": list(self.missing_positive_patterns),
            "missing_negative_patterns": list(self.missing_negative_patterns),
            "duplicate_label_ids": list(self.duplicate_label_ids),
            "ready_for_broader_development_validation": self.ready_for_broader_development_validation,
            "readiness_reasons": list(self.readiness_reasons),
        }


def _duplicates(values: Iterable[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def summarize_label_pack(labels: Sequence[MorphologyLabel]) -> LabelPackSummary:
    pattern_types = sorted(IMPLEMENTED_PATTERN_TYPES)
    positive = Counter(label.pattern_type for label in labels if label.adjudication == "POSITIVE")
    negative = Counter(label.pattern_type for label in labels if label.adjudication == "NEGATIVE")
    security_ids = {label.security_id for label in labels}
    duplicate_ids = _duplicates(label.label_id for label in labels)
    missing_positive = [pattern for pattern in pattern_types if positive.get(pattern, 0) == 0]
    missing_negative = [pattern for pattern in pattern_types if negative.get(pattern, 0) == 0]

    reasons: list[str] = []
    if len(security_ids) < 2:
        reasons.append("label pack must span at least two securities")
    if missing_positive:
        reasons.append("positive labels must cover all implemented core pattern types")
    if missing_negative:
        reasons.append("negative labels must cover all implemented core pattern types")
    if duplicate_ids:
        reasons.append("label_id values must be unique")

    return LabelPackSummary(
        label_pack_version=LABEL_PACK_VERSION,
        label_count=len(labels),
        security_count=len(security_ids),
        positive_count=sum(positive.values()),
        negative_count=sum(negative.values()),
        positive_pattern_counts={pattern: positive.get(pattern, 0) for pattern in pattern_types},
        negative_pattern_counts={pattern: negative.get(pattern, 0) for pattern in pattern_types},
        missing_positive_patterns=missing_positive,
        missing_negative_patterns=missing_negative,
        duplicate_label_ids=duplicate_ids,
        ready_for_broader_development_validation=not reasons,
        readiness_reasons=reasons,
    )


def parse_label_pack(payload: Mapping[str, object] | Sequence[Mapping[str, object]]) -> tuple[list[MorphologyLabel], LabelPackSummary]:
    if isinstance(payload, Mapping):
        raw_labels = payload.get("labels")
        if not isinstance(raw_labels, list):
            raise ValueError("label pack object must contain a labels list")
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes)):
        raw_labels = list(payload)
    else:
        raise ValueError("label pack must be an object with labels or a label list")

    labels: list[MorphologyLabel] = []
    for index, row in enumerate(raw_labels):
        if not isinstance(row, Mapping):
            raise ValueError(f"label pack row {index} must be an object")
        labels.append(MorphologyLabel.from_dict(row))

    return labels, summarize_label_pack(labels)
