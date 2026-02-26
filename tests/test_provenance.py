import json
import tempfile
from smart_model_card.provenance import compute_hash, diff_cards, check_fairness_coverage, plausibility_check
from smart_model_card.sections import PerformanceValidation, ValidationDataset, PerformanceMetric


def test_compute_hash_roundtrip():
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write("hello")
        path = f.name
    h = compute_hash(path)
    assert h == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_diff_cards_detects_change(tmp_path):
    old = tmp_path / "old.json"
    new = tmp_path / "new.json"
    old.write_text(json.dumps({"a": 1, "b": {"c": 2}}))
    new.write_text(json.dumps({"a": 1, "b": {"c": 3}}))
    diff = diff_cards(str(old), str(new))
    assert "b.c" in diff
    assert diff["b.c"]["old"] == 2
    assert diff["b.c"]["new"] == 3


def test_fairness_and_plausibility_checks():
    perf = PerformanceValidation(
        validation_datasets=[ValidationDataset("Ext", "Site", "n=10", "external")],
        claimed_metrics=[PerformanceMetric("AUC", 0.9, "claimed", "male")],
        validated_metrics=[PerformanceMetric("AUC", 0.85, "external", "female")],
        calibration_analysis="present",
        fairness_assessment="ok",
        metric_validation_status="External"
    )
    missing = check_fairness_coverage(perf, ["male", "female"])
    assert missing == []
    issues = plausibility_check(perf)
    assert issues == []
