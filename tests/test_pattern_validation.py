from canslim_research.pattern_validation import MorphologyLabel, evaluate_morphology_labels


def _label(label_id, adjudication="POSITIVE", pattern_type="DOUBLE_BOTTOM"):
    return MorphologyLabel.from_dict(
        {
            "label_id": label_id,
            "security_id": "SEC1",
            "ticker": "XYZ",
            "pattern_type": pattern_type,
            "start_date_min": "2023-07-01",
            "start_date_max": "2023-07-10",
            "end_date_min": "2023-08-20",
            "end_date_max": "2023-09-15",
            "adjudication": adjudication,
        }
    )


def _lineage(lineage_id="L1", pattern_type="DOUBLE_BOTTOM", start="2023-07-05", end="2023-09-01"):
    return {
        "lineage_id": lineage_id,
        "security_id": "SEC1",
        "pattern_type": pattern_type,
        "base_start_date": start,
        "last_supported_date": end,
    }


def test_positive_label_match_is_true_positive():
    result = evaluate_morphology_labels([_label("P1")], [_lineage()])
    assert result["tp"] == 1
    assert result["fn"] == 0
    assert result["recall_on_positive_labels"] == 1.0
    assert result["unadjudicated_lineage_count"] == 0


def test_positive_label_without_match_is_false_negative():
    result = evaluate_morphology_labels([_label("P1")], [_lineage(pattern_type="FLAT_BASE")])
    assert result["tp"] == 0
    assert result["fn"] == 1
    assert result["recall_on_positive_labels"] == 0.0
    assert result["unadjudicated_lineage_count"] == 1


def test_negative_label_match_is_false_positive():
    result = evaluate_morphology_labels([_label("N1", adjudication="NEGATIVE")], [_lineage()])
    assert result["fp"] == 1
    assert result["tn"] == 0
    assert result["precision_on_adjudicated_windows"] == 0.0


def test_negative_label_without_match_is_true_negative():
    result = evaluate_morphology_labels([_label("N1", adjudication="NEGATIVE")], [])
    assert result["fp"] == 0
    assert result["tn"] == 1


def test_unlabelled_detector_output_is_not_automatically_false_positive():
    result = evaluate_morphology_labels([_label("P1")], [_lineage(), _lineage("L2", start="2023-01-01", end="2023-03-01")])
    assert result["tp"] == 1
    assert result["fp"] == 0
    assert result["unadjudicated_lineage_ids"] == ["L2"]


def test_label_rejects_unsupported_pattern_type():
    try:
        MorphologyLabel.from_dict(
            {
                "label_id": "BAD",
                "security_id": "SEC1",
                "ticker": "XYZ",
                "pattern_type": "ASCENDING_BASE",
                "start_date_min": "2023-01-01",
                "start_date_max": "2023-01-02",
                "end_date_min": "2023-02-01",
                "end_date_max": "2023-02-02",
            }
        )
    except ValueError as exc:
        assert "unsupported morphology label" in str(exc)
    else:
        raise AssertionError("expected unsupported pattern type to fail")
