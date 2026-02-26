"""
JSON Schema export for smart-model-card.

Provides a fixed structure aligned with the regulated sections and fields.
"""

from __future__ import annotations

from typing import Dict, Any


def get_model_card_json_schema() -> Dict[str, Any]:
    """Return a JSON Schema describing the model card payload."""
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Smart Model Card",
        "type": "object",
        "required": [
            "created_at",
            "1. Model Details",
            "2. Intended Use and Clinical Context",
            "3. Data & Factors",
            "4. Features & Outputs",
            "5. Performance & Validation",
            "6. Methodology & Explainability",
            "7. Additional Information",
        ],
        "properties": {
            "created_at": {"type": "string", "format": "date-time"},
            "1. Model Details": {
                "type": "object",
                "required": [
                    "Model Name",
                    "Version",
                    "Developer / Organization",
                    "Release Date",
                    "Description",
                    "Clinical Function",
                    "Algorithm(s) Used",
                    "Licensing",
                    "Support Contact",
                ],
                "properties": {
                    "Model Name": {"type": "string"},
                    "Version": {"type": "string"},
                    "Developer / Organization": {"type": "string"},
                    "Release Date": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
                    "Description": {"type": "string"},
                    "Clinical Function": {
                        "type": "string",
                        "enum": [
                            "diagnosis",
                            "screening",
                            "triage",
                            "monitoring",
                            "decision_support",
                            "workflow_support",
                            "other",
                        ],
                    },
                    "Intended Purpose": {"type": ["string", "null"]},
                    "Information Significance": {
                        "type": ["string", "null"],
                        "enum": ["inform", "drive", "treat_or_diagnose", None],
                    },
                    "Algorithm(s) Used": {"type": "string"},
                    "GMDN Code": {"type": ["string", "null"]},
                    "Basic UDI-DI": {"type": ["string", "null"]},
                    "UDI-DI": {"type": ["string", "null"]},
                    "Regulatory Classifications": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["framework", "class"],
                            "properties": {
                                "framework": {"type": "string"},
                                "class": {"type": "string"},
                                "rule": {"type": "string"},
                                "pathway": {"type": "string"},
                            },
                            "additionalProperties": False,
                        },
                        "default": [],
                    },
                    "Licensing": {"type": "string"},
                    "Support Contact": {"type": "string"},
                    "Literature References": {"type": "array", "items": {"type": "string"}},
                    "Clinical Study References": {"type": "array", "items": {"type": "string"}},
                    "Logo / Image (optional)": {"type": ["string", "null"]},
                },
            },
            "2. Intended Use and Clinical Context": {
                "type": "object",
                "required": [
                    "Primary Intended Users",
                    "Clinical Indications",
                    "Patient target group",
                    "Intended Use Environment",
                ],
                "properties": {
                    "Primary Intended Users": {"type": "string"},
                    "Clinical Indications": {"type": "string"},
                    "Patient target group": {"type": "string"},
                    "Contraindications": {"type": ["string", "null"]},
                    "Intended Use Environment": {"type": "string"},
                    "Out of Scope Applications": {"type": ["string", "null"]},
                    "Warnings": {"type": ["string", "null"]},
                },
            },
            "3. Data & Factors": {
                "type": "object",
                "required": [
                    "Source Datasets",
                    "Data Distribution Summary",
                    "Data Representativeness",
                    "Data Governance",
                ],
                "properties": {
                    "Concept Sets": {"type": "array", "items": {"type": "object"}},
                    "Primary Cohort Criteria": {"type": ["object", "null"]},
                    "Source Datasets": {"type": "array", "items": {"type": "object"}, "minItems": 1},
                    "Data Distribution Summary": {"type": "string"},
                    "Data Representativeness": {"type": "string"},
                    "Data Governance": {"type": "string"},
                },
            },
            "4. Features & Outputs": {
                "type": "object",
                "required": [
                    "Input Features",
                    "Output Features",
                    "Feature Type Distribution",
                    "Uncertainty Quantification",
                    "Output Interpretability",
                ],
                "properties": {
                    "Input Features": {"type": "array", "items": {"type": "object"}, "minItems": 1},
                    "Output Features": {"type": "array", "items": {"type": "object"}, "minItems": 1},
                    "Feature Type Distribution": {"type": "string"},
                    "Uncertainty Quantification": {"type": "string"},
                    "Output Interpretability": {"type": "string"},
                },
            },
            "5. Performance & Validation": {
                "type": "object",
                "required": [
                    "Validation Dataset(s)",
                    "Claimed Metrics",
                    "Validated Metrics",
                    "Metric Validation Status",
                ],
                "properties": {
                    "Validation Dataset(s)": {"type": "array", "items": {"type": "object"}, "minItems": 1},
                    "Claimed Metrics": {"type": "array", "items": {"type": "object"}},
                    "Validated Metrics": {"type": "array", "items": {"type": "object"}},
                    "Calibration Analysis": {"type": ["string", "null"]},
                    "Fairness Assessment": {"type": ["string", "null"]},
                    "Metric Validation Status": {"type": "string"},
                },
            },
            "6. Methodology & Explainability": {
                "type": "object",
                "required": [
                    "Model Development Workflow",
                    "Training Procedure",
                    "Data Preprocessing",
                ],
                "properties": {
                    "Model Development Workflow": {"type": "string"},
                    "Training Procedure": {"type": "string"},
                    "Data Preprocessing": {"type": "string"},
                    "Synthetic Data Usage": {"type": ["string", "null"]},
                    "Explainable AI Method": {"type": ["string", "null"]},
                    "Global vs. Local Interpretability": {"type": ["string", "null"]},
                },
            },
            "7. Additional Information": {
                "type": "object",
                "required": [
                    "Benefit–Risk Summary",
                    "Ethical Considerations",
                    "Caveats & Limitations",
                    "Recommendations for Safe Use",
                ],
                "properties": {
                    "Benefit–Risk Summary": {"type": "string"},
                    "Post-Market Surveillance Plan": {"type": ["string", "null"]},
                    "Ethical Considerations": {"type": "string"},
                    "Caveats & Limitations": {"type": "string"},
                    "Recommendations for Safe Use": {"type": "string"},
                    "Explainability Recommendations": {"type": ["string", "null"]},
                    "Supporting Documents": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
    }
