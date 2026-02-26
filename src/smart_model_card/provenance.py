"""
Provenance, integrity, and validation helpers.

Includes hashing, diffing, fairness coverage checks, data snapshot manifests,
and optional cosign sign/verify helpers (requires cosign installed).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from smart_model_card.sections import DataFactors, PerformanceValidation


def compute_hash(path: str) -> str:
    """Compute SHA-256 hash of a file (hex)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def create_data_manifest(data_factors: DataFactors, output_path: str) -> Dict[str, Any]:
    """
    Generate a data manifest capturing datasets, concept sets, and a hash.

    Fields:
        datasets: name, origin, size
        concept_sets: name, vocabulary, ids
        hash: SHA-256 of manifest contents
    """
    manifest = {
        "datasets": [
            {"name": ds.name, "origin": ds.origin, "size": ds.size}
            for ds in data_factors.source_datasets
        ],
        "concept_sets": [
            {"name": cs.name, "vocabulary": cs.vocabulary, "ids": cs.concept_ids}
            for cs in (data_factors.concept_sets or [])
        ],
    }
    manifest_path = Path(output_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w") as f:
        json.dump(manifest, f, indent=2)

    manifest["hash"] = compute_hash(str(manifest_path))
    with manifest_path.open("w") as f:
        json.dump(manifest, f, indent=2)
    return manifest


def diff_cards(old_path: str, new_path: str) -> Dict[str, Any]:
    """Compute a shallow diff between two card JSON files."""
    with open(old_path) as f:
        old = json.load(f)
    with open(new_path) as f:
        new = json.load(f)

    def _flatten(d: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for k, v in d.items():
            key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                out.update(_flatten(v, key))
            else:
                out[key] = v
        return out

    fo = _flatten(old)
    fn = _flatten(new)
    keys = set(fo.keys()) | set(fn.keys())
    changes = {}
    for k in sorted(keys):
        vo = fo.get(k, "__MISSING__")
        vn = fn.get(k, "__MISSING__")
        if vo != vn:
            changes[k] = {"old": vo, "new": vn}
    return changes


def check_fairness_coverage(perf: PerformanceValidation, required_subgroups: List[str]) -> List[str]:
    """
    Verify that required subgroups appear in claimed or validated metrics.

    Returns list of missing subgroup labels.
    """
    present = set()
    for m in perf.claimed_metrics + perf.validated_metrics:
        if m.subgroup:
            present.add(str(m.subgroup).lower())
    missing = []
    for sg in required_subgroups:
        if sg.lower() not in present:
            missing.append(sg)
    return missing


def plausibility_check(perf: PerformanceValidation) -> List[str]:
    """
    Simple plausibility checks:
    - probability-like metrics within [0,1]
    - calibration provided when outputs are probability-like
    - external metrics present only if validation_datasets include external
    """
    issues: List[str] = []
    prob_tokens = ["auc", "roc", "pr", "precision", "recall", "specificity", "sensitivity", "f1", "dice", "iou", "brier", "accuracy"]
    has_external = any("external" in (vd.validation_type or "").lower() for vd in perf.validation_datasets)
    for m in perf.claimed_metrics + perf.validated_metrics:
        name_norm = (m.metric_name or "").lower()
        if any(tok in name_norm for tok in prob_tokens):
            if m.value < 0.0 or m.value > 1.0:
                issues.append(f"Metric {m.metric_name} out of [0,1]: {m.value}")
        if "external" in (m.validation_status or "").lower() and not has_external:
            issues.append(f"Metric {m.metric_name} marked external without external dataset declared")
    if perf.calibration_analysis is None:
        issues.append("Calibration analysis missing")
    return issues


