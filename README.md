# SMART Model Card

A Python package for creating structured model cards (documentation) for medical AI models. Fills in a 7-section template, exports to JSON/HTML/Markdown, and can pull dataset info from OMOP CDM sources.

## What This Package Does

- Provides a **7-section template** for documenting a medical AI model (what it does, what data it uses, how it performs, etc.)
- Offers **5 pre-filled templates** for common use cases (risk prediction, screening, diagnostics, triage, monitoring) so you don't start from scratch
- Exports to **HTML** (interactive, with tables and charts), **JSON** (machine-readable), and **Markdown**
- Can **pull dataset information from OMOP CDM** via WebAPI to auto-fill the data section
- Supports **round-trip editing**: export to JSON, reload, modify, re-export
- Includes a **CLI** and an **interactive wizard** for step-by-step creation

## Installation

```bash
pip install smart-model-card
```

From source:

```bash
git clone https://github.com/ankurlohachab/smart-model-card.git
cd smart-model-card
pip install -e .
```

Optional extras:

```bash
pip install smart-model-card[omop]    # OMOP CDM integration + charts
pip install smart-model-card[viz]     # Matplotlib charts only
pip install smart-model-card[dev]     # pytest, black, flake8
pip install smart-model-card[all]     # Everything
```

**Requirements**: Python >= 3.8, requests >= 2.25.0

## Quick Start

### Create a Model Card in 5 Lines

```python
from smart_model_card import quick_card

card = quick_card(
    model_name="COPD Risk Predictor",
    description="Predicts 30-day COPD exacerbation risk from EHR data",
    developer="University Hospital Research Lab",
    contact="ai-team@hospital.org",
    template="copd_risk_predictor",
)

card.to_dict()
```

This fills all 7 sections with template defaults. You should review and replace the placeholder values with your actual model details.

### Override Defaults

```python
card = quick_card(
    model_name="My Screening Model",
    description="Screens for early-stage disease X",
    developer="My Hospital",
    contact="team@hospital.org",
    template="screening_tool",
    algorithms_used="Custom Neural Network",
    version="2.5.0",
    intended_use__contraindications="Not for pediatric use",
    methodology__training_procedure="10-fold CV with early stopping",
)
```

Flat kwargs override `model_details` fields. Use `section__field` syntax for other sections.

## Interactive Wizard

```bash
smart-model-card interactive
```

Three modes:

| Mode | What It Does | Questions |
|------|-------------|-----------|
| **Quick Start** | Pick a template, fill in key details | ~8 |
| **Full Wizard** | Walk through all 7 sections step by step | ~40 |
| **Load & Edit** | Load an existing JSON card, modify specific sections | Variable |

```bash
smart-model-card interactive --template copd_risk_predictor
smart-model-card interactive --load existing_card.json
```

## Programmatic Usage

```python
from smart_model_card import (
    ModelCard, ModelDetails, IntendedUse, DataFactors,
    FeaturesOutputs, PerformanceValidation, Methodology, AdditionalInfo,
    SourceDataset, InputFeature, OutputFeature, ValidationDataset, PerformanceMetric,
)
from smart_model_card.exporters import HTMLExporter, JSONExporter

card = ModelCard()

card.set_model_details(ModelDetails(
    model_name="Diabetes Risk Model",
    version="2.1.0",
    developer_organization="University Hospital Research Lab",
    release_date="2025-01-15",
    description="Predicts 5-year diabetes risk using EHR data",
    clinical_function="decision_support",
    algorithms_used="XGBoost Classifier",
    licensing="MIT",
    support_contact="ai-team@hospital.org",
))

card.set_intended_use(IntendedUse(
    primary_intended_users="Primary care physicians",
    clinical_indications="Patients aged 40-75 with pre-diabetes indicators",
    patient_target_group="Adults with BMI > 25 and family history of diabetes",
    intended_use_environment="hospital_outpatient",
    contraindications="Not for type 1 diabetes screening",
    warnings="Does not replace clinical judgment",
))

card.set_data_factors(DataFactors(
    source_datasets=[
        SourceDataset("Hospital EHR Database", "Academic Medical Center",
                      15000, "2018-2023", "Adult patients, 45% female, mean age 62")
    ],
    data_distribution_summary="Balanced dataset with 30% positive cases",
    data_representativeness="Representative of urban academic hospital population",
    data_governance="IRB-approved data access",
))

card.set_features_outputs(FeaturesOutputs(
    input_features=[
        InputFeature("age", "numeric", True, "Demographics", "18-100", "years"),
        InputFeature("bmi", "numeric", True, "Anthropometrics", "15-60", "kg/m2"),
        InputFeature("hba1c", "numeric", True, "Laboratory", "4.0-14.0", "%"),
    ],
    output_features=[
        OutputFeature("risk_score", "probability", "probability", "0.0-1.0"),
    ],
    feature_type_distribution="3 numeric features",
    uncertainty_quantification="Bootstrap 95% confidence intervals",
    output_interpretability="SHAP values for individual predictions",
))

card.set_performance_validation(PerformanceValidation(
    validation_datasets=[
        ValidationDataset("Internal Holdout", "Same Institution", "n=3000", "internal"),
    ],
    claimed_metrics=[PerformanceMetric("AUC", 0.82, "claimed")],
    validated_metrics=[PerformanceMetric("AUC", 0.80, "internal")],
    calibration_analysis="Hosmer-Lemeshow test p=0.45",
    fairness_assessment="AUC within 0.03 across sex and age subgroups",
    metric_validation_status="Internal validation complete",
))

card.set_methodology(Methodology(
    model_development_workflow="Data extraction, preprocessing, training, validation",
    training_procedure="5-fold stratified cross-validation with early stopping",
    data_preprocessing="Missing value imputation (MICE), feature normalization",
    explainable_ai_method="SHAP TreeExplainer",
    global_vs_local_interpretability="Global feature importance and local explanations",
))

card.set_additional_info(AdditionalInfo(
    benefit_risk_summary="Early risk identification enables preventive intervention",
    ethical_considerations="Potential bias in underrepresented populations",
    caveats_limitations="Not validated for patients under 18",
    recommendations_for_safe_use="Use as decision support; clinical judgment required",
    post_market_surveillance_plan="Quarterly performance monitoring",
))

HTMLExporter.export(card, "model_card.html")
JSONExporter.export(card, "model_card.json")
```

### Field Options

**`clinical_function`**: `diagnosis`, `screening`, `triage`, `monitoring`, `decision_support`, `workflow_support`, `other`

**`intended_use_environment`**: `hospital_inpatient`, `hospital_outpatient`, `emergency`, `telemedicine`, `research`, `home`, `other`

## Templates

Five pre-filled templates for common use cases:

| Template ID | Type | Example Use |
|-------------|------|-------------|
| `copd_risk_predictor` | Risk prediction | COPD exacerbation risk from EHR |
| `screening_tool` | Screening | Population screening with labs |
| `diagnostic_classifier` | Diagnostics | Image-based diagnostic classification |
| `triage_model` | Triage | Emergency triage with vitals |
| `monitoring_model` | Monitoring | Continuous monitoring with time-series |

Templates fill all 7 sections with placeholder content. Replace with your actual values.

```python
from smart_model_card import TEMPLATES

for tid, tmpl in TEMPLATES.items():
    print(f"{tid}: {tmpl['name']}")
```

## Save, Reload, Edit

```python
from smart_model_card import ModelCard
from smart_model_card.exporters import JSONExporter

JSONExporter.export(card, "card.json")

reloaded = ModelCard.from_json("card.json")
reloaded.model_details.model_name = "Updated Name"
JSONExporter.export(reloaded, "card_v2.json")
```

Also works from a dictionary:

```python
import json

with open("card.json") as f:
    data = json.load(f)

card = ModelCard.from_dict(data)
```

## OMOP CDM Integration

If your training data lives in an OMOP CDM, the package can pull cohort and dataset information directly:

```python
from smart_model_card.integrations import OMOPIntegration

with OMOPIntegration(
    webapi_url="https://atlas.yourorg.org/WebAPI",
    source_key="YOUR_CDM_SOURCE"
) as omop:
    cohort_data = omop.get_cohort_with_reports(
        cohort_id=168,
        include_heracles=True,
    )

card.set_data_factors(cohort_data["data_factors"])
```

This fetches cohort definitions, concept sets, and Heracles characterization reports (demographics, conditions, drugs, procedures) from an OHDSI ATLAS instance and uses them to fill the Data & Factors section of your model card.

Requires `pip install smart-model-card[omop]`.

## Export Formats

```python
from smart_model_card.exporters import HTMLExporter, JSONExporter, MarkdownExporter

HTMLExporter.export(card, "card.html")
JSONExporter.export(card, "card.json")
MarkdownExporter.export(card, "card.md")
```

- **HTML**: Interactive page with collapsible sections, searchable tables, CSV download, demographic charts (from OMOP data), text zoom, print layout
- **JSON**: Structured output following the 7-section schema
- **Markdown**: Plain text, good for version control diffs

`JSONExporter.export(card, "card_public.json", public=True)` strips internal fields (de-identification report URIs) for sharing.

## CLI Reference

```bash
smart-model-card interactive                          # Launch wizard
smart-model-card interactive --template screening_tool # Quick start with template
smart-model-card interactive --load card.json          # Edit existing card

smart-model-card create --model-name "MyModel" -o scaffold.json  # Generate placeholder JSON
smart-model-card validate card.json                               # Check against schema

smart-model-card export card.json -f html -o card.html   # Export to HTML
smart-model-card export card.json -f json -o card.json   # Export to JSON
smart-model-card export card.json -f md -o card.md       # Export to Markdown

smart-model-card hash --card card.json                   # SHA-256 checksum
smart-model-card diff old.json new.json                  # Field-by-field comparison
smart-model-card annotate card.json --author "Dr. Smith" --note "Approved"
```

## Model Card Structure

| Section | What Goes Here |
|---------|---------------|
| **1. Model Details** | Name, version, developer, release date, what it does, algorithms used, license, contact |
| **2. Intended Use** | Who uses it, for what clinical purpose, target patients, where it runs, when not to use it |
| **3. Data & Factors** | Training datasets, how data was collected, demographics, data governance |
| **4. Features & Outputs** | Input variables and types, output format, uncertainty, how to interpret outputs |
| **5. Performance** | Validation datasets, metrics (AUC, sensitivity, etc.), calibration, subgroup performance |
| **6. Methodology** | How the model was built, training process, preprocessing, explainability approach |
| **7. Additional Info** | Benefits vs risks, monitoring plan, ethical considerations, limitations, safe use guidance |

The model card also stores: timestamped notes (annotations), lifecycle status, and creation timestamp.

Some optional text fields exist for documenting things like device identifiers or classification labels if relevant to your context.

## Testing

```bash
pytest tests/ -v
```

| Test File | Tests | What It Covers |
|-----------|-------|----------------|
| `test_model_card.py` | 7 | Card creation, validation, export |
| `test_provenance.py` | 3 | File hashing, card diffing |
| `test_cac.py` | 1 | Keyword-based code lookup |
| `test_from_dict.py` | 45 | Save/load round-trip for all sections |
| `test_templates.py` | 35 | Templates and quick_card |

**91 tests total**

## Development

```bash
git clone https://github.com/ankurlohachab/smart-model-card.git
cd smart-model-card
python -m venv venv
source venv/bin/activate
pip install -e .[dev]
pytest tests/ -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT - see [LICENSE](LICENSE).

## Citation

```bibtex
@software{smart_model_card,
  title={SMART Model Card: Structured Model Documentation for Healthcare AI},
  author={Lohachab, Ankur},
  organization={Department of Advanced Computing Sciences, Maastricht University},
  year={2025},
  url={https://github.com/ankurlohachab/smart-model-card}
}
```

## Author

Ankur Lohachab, Department of Advanced Computing Sciences, Maastricht University

- **Issues**: [GitHub Issues](https://github.com/ankurlohachab/smart-model-card/issues)
- **Examples**: See `examples/` directory
- **Email**: ankur.lohachab@maastrichtuniversity.nl
