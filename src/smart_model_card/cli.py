"""
Command-line interface for smart-model-card.

Provides:
- validate: validate a model card JSON against the published schema (and optionally jsonschema)
- export: convert a model card JSON to HTML/Markdown using built-in exporters
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from smart_model_card.schema import get_model_card_json_schema
from smart_model_card.exporters import JSONExporter, MarkdownExporter, HTMLExporter
from smart_model_card.model_card import ModelCard
from smart_model_card.sections import (
    ModelDetails,
    IntendedUse,
    DataFactors,
    FeaturesOutputs,
    PerformanceValidation,
    Methodology,
    AdditionalInfo,
    Annotation,
    SourceDataset,
    InputFeature,
    OutputFeature,
    ValidationDataset,
    PerformanceMetric
)
from smart_model_card.provenance import (
    compute_hash,
    diff_cards,
)
from smart_model_card.integrations import performance_from_dict
from smart_model_card.interactive import interactive_create_model_card


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open() as f:
        return json.load(f)


def _validate_with_schema(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    schema = get_model_card_json_schema()
    try:
        import jsonschema

        validator = jsonschema.Draft7Validator(schema)
        for err in validator.iter_errors(data):
            errors.append(f"{'/'.join([str(p) for p in err.path]) or 'root'}: {err.message}")
    except ImportError:
        required = schema.get("required", [])
        for key in required:
            if key not in data:
                errors.append(f"root: missing required section '{key}' (install jsonschema for full validation)")
    return errors


def cmd_validate(args: argparse.Namespace) -> int:
    data = _load_json(Path(args.input))
    errors = _validate_with_schema(data)
    if errors:
        print("Validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Validation passed")
    return 0


def cmd_annotate(args: argparse.Namespace) -> int:
    path = Path(args.input)
    data = _load_json(path)
    notes = data.get("Notes", [])
    new_note = Annotation(author=args.author, note=args.note).to_dict()
    notes.append(new_note)
    data["Notes"] = notes
    path.write_text(json.dumps(data, indent=2))
    print(f"Added note by {args.author}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    data = _load_json(Path(args.input))
    fmt = args.format.lower()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        if args.public:
            df = data.get("3. Data & Factors", {})
            for k in ["De-id Report URI", "De-id Report Hash"]:
                df.pop(k, None)
            data["3. Data & Factors"] = df
        JSONExporter.export_from_dict(data, output)
    elif fmt in ("md", "markdown"):
        md_content = MarkdownExporter._dict_to_markdown(data if not args.public else _strip_public(data))  # type: ignore[attr-defined]
        output.write_text(md_content)
    elif fmt == "html":
        model_name = data.get("1. Model Details", {}).get("Model Name", "Model")
        html_content = HTMLExporter._generate_html(data if not args.public else _strip_public(data), model_name)  # type: ignore[attr-defined]
        output.write_text(html_content)
    else:
        print(f"Unsupported format: {fmt}")
        return 1

    print(f"Exported {fmt.upper()} to {output}")
    return 0


def _strip_public(data: Dict[str, Any]) -> Dict[str, Any]:
    sanitized = json.loads(json.dumps(data))
    df = sanitized.get("3. Data & Factors", {})
    for k in ["De-id Report URI", "De-id Report Hash"]:
        df.pop(k, None)
    sanitized["3. Data & Factors"] = df
    return sanitized


def cmd_hash(args: argparse.Namespace) -> int:
    hashes = {}
    for label, path in [("card", args.card), ("artifact", args.artifact), ("manifest", args.manifest)]:
        if path:
            hashes[label] = compute_hash(path)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(hashes, f, indent=2)
    else:
        print(json.dumps(hashes, indent=2))
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    changes = diff_cards(args.old, args.new)
    if not changes:
        print("No differences.")
        return 0
    print(json.dumps(changes, indent=2))
    return 1 if args.fail_on_diff else 0


def cmd_create(args: argparse.Namespace) -> int:
    """Scaffold a model card with placeholder content and write JSON."""
    card = ModelCard()
    card.set_model_details(ModelDetails(
        model_name=args.model_name or "Your Model Name",
        version="0.1.0",
        developer_organization="Your Organization",
        release_date="2025-01-01",
        description="Short description of the model and clinical context",
        clinical_function="decision_support",
        algorithms_used="Model family or architecture",
        licensing="MIT",
        support_contact="support@example.com"
    ))
    card.set_intended_use(IntendedUse(
        primary_intended_users="Clinicians",
        clinical_indications="Clinical conditions for which this model is intended",
        patient_target_group="Target population (age, condition, setting)",
        intended_use_environment="hospital_outpatient",
        contraindications="Contraindications or none",
        out_of_scope_applications="Explicitly unsupported uses",
        warnings="Key warnings to users"
    ))
    card.set_data_factors(DataFactors(
        source_datasets=[SourceDataset(
            name="Dataset name",
            origin="EHR / Registry / Trial",
            size=1000,
            collection_period="2020-2024",
            population_characteristics="Population characteristics"
        )],
        data_distribution_summary="Describe key demographics/clinical variables",
        data_representativeness="Representativeness vs target deployment",
        data_governance="IRB/ethics, consent, de-ID"
    ))
    card.set_features_outputs(FeaturesOutputs(
        input_features=[
            InputFeature("age", "numeric", True, "Demographics", "18-100", "years")
        ],
        output_features=[
            OutputFeature("risk_score", "probability", "probability", "0.0-1.0")
        ],
        feature_type_distribution="1 numeric",
        uncertainty_quantification="Prediction intervals / calibration method",
        output_interpretability="How to interpret outputs in workflow"
    ))
    card.set_performance_validation(PerformanceValidation(
        validation_datasets=[
            ValidationDataset("Internal holdout", "Your institution", "n=1000", "internal")
        ],
        claimed_metrics=[PerformanceMetric("AUC", 0.8, "claimed")],
        validated_metrics=[PerformanceMetric("AUC", 0.8, "internal")],
        calibration_analysis="Calibration method/results",
        fairness_assessment="Subgroup performance summary",
        metric_validation_status="Claimed/internal/external as applicable"
    ))
    card.set_methodology(Methodology(
        model_development_workflow="Data prep -> split -> train -> validate -> explainability",
        training_procedure="Algorithm + objective + optimizer + hardware",
        data_preprocessing="Imputation, normalization, leakage controls",
        synthetic_data_usage="None or describe",
        explainable_ai_method="SHAP/LIME/etc.",
        global_vs_local_interpretability="Global, local, or both"
    ))
    card.set_additional_info(AdditionalInfo(
        benefit_risk_summary="Summarize benefits vs risks",
        post_market_surveillance_plan="How you will monitor performance post-deployment",
        ethical_considerations="Ethical risks and mitigations",
        caveats_limitations="Known limitations",
        recommendations_for_safe_use="Guidance for safe use",
        explainability_recommendations="How to present explanations",
        supporting_documents=[]
    ))

    try:
        card.validate()
    except Exception as exc:  # pragma: no cover - should not fail with placeholders
        print(f"Generated card failed validation: {exc}")
        return 1

    out_path = Path(args.output)
    JSONExporter.export(card, str(out_path))
    print(f"Scaffolded model card JSON at {out_path}")
    return 0


def cmd_interactive(args: argparse.Namespace) -> int:
    """Launch interactive model card creation wizard"""
    try:
        from smart_model_card.interactive import run_interactive_wizard
        exported_files = run_interactive_wizard(
            template=getattr(args, "template", None),
            load_path=getattr(args, "load", None),
            jurisdiction=getattr(args, "jurisdiction", None),
        )
        return 0
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="smart-model-card", description="Smart Model Card CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="Validate a model card JSON file")
    p_validate.add_argument("input", help="Path to model card JSON")
    p_validate.set_defaults(func=cmd_validate)

    p_export = sub.add_parser("export", help="Export a model card JSON to HTML/Markdown/JSON")
    p_export.add_argument("input", help="Path to model card JSON")
    p_export.add_argument("--format", "-f", choices=["json", "html", "md", "markdown"], required=True, help="Output format")
    p_export.add_argument("--output", "-o", required=True, help="Output file path")
    p_export.add_argument("--public", action="store_true", help="Strip internal-only fields (de-id report URIs/hashes)")
    p_export.set_defaults(func=cmd_export)

    p_create = sub.add_parser("create", help="Scaffold a model card JSON with placeholders")
    p_create.add_argument("--model-name", help="Model name to prefill", default=None)
    p_create.add_argument("--output", "-o", required=True, help="Output JSON path")
    p_create.set_defaults(func=cmd_create)

    p_hash = sub.add_parser("hash", help="Compute SHA-256 of card/artifact/manifest")
    p_hash.add_argument("--card", help="Path to model card JSON")
    p_hash.add_argument("--artifact", help="Path to model artifact (optional)")
    p_hash.add_argument("--manifest", help="Path to data manifest (optional)")
    p_hash.add_argument("--output", help="Optional output JSON for hashes")
    p_hash.set_defaults(func=cmd_hash)

    p_diff = sub.add_parser("diff", help="Diff two model card JSON files")
    p_diff.add_argument("old", help="Old card JSON")
    p_diff.add_argument("new", help="New card JSON")
    p_diff.add_argument("--fail-on-diff", action="store_true", help="Exit 1 if differences found")
    p_diff.set_defaults(func=cmd_diff)

    p_annotate = sub.add_parser("annotate", help="Append a note/comment to a model card JSON")
    p_annotate.add_argument("input", help="Model card JSON path to modify")
    p_annotate.add_argument("--author", required=True, help="Author of the note")
    p_annotate.add_argument("--note", required=True, help="Note text")
    p_annotate.set_defaults(func=cmd_annotate)

    p_interactive = sub.add_parser("interactive", help="Interactive guided model card creation")
    p_interactive.add_argument("--template", "-t", help="Start Quick Start with a template ID (e.g., copd_risk_predictor, screening_tool)")
    p_interactive.add_argument("--load", "-l", help="Start Load & Edit mode with an existing JSON file path")
    p_interactive.add_argument("--jurisdiction", "-j", choices=["eu", "us", "both"], help="Auto-fill regulatory classifications for jurisdiction")
    p_interactive.set_defaults(func=cmd_interactive)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
