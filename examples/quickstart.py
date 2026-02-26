"""
Quickstart Example - Basic Model Card

This example demonstrates creating a basic model card and exporting to HTML/JSON.
"""

from smart_model_card import ModelCard, ModelDetails, IntendedUse, DataFactors
from smart_model_card.exporters import HTMLExporter, JSONExporter
from smart_model_card.sections import PerformanceMetrics, ValidationDataset
from datetime import datetime

# Initialize model card
card = ModelCard(
    model_details=ModelDetails(
        model_name="COPD-Risk-Predictor",
        version="1.0.0",
        developer="Department of Advanced Computing Sciences, Maastricht University",
        release_date="2025-01-15",
        description="Predicts 12-month COPD exacerbation risk using clinical features",
        clinical_function="decision_support",
        algorithm="Random Forest Classifier"
    ),
    intended_use=IntendedUse(
        primary_users="Pulmonologists, respiratory care specialists",
        clinical_indications="Risk stratification for patients with confirmed COPD",
        patient_target_group="Adults aged 40+ with COPD diagnosis",
        use_environment="hospital_outpatient"
    )
)

# Add data information
card.data_factors = DataFactors(
    data_distribution_summary={
        "Total Patients": "500",
        "Age Range": "45-88 years",
        "Gender": "Male: 62%, Female: 38%"
    }
)

# Add performance metrics
card.performance.add_metric(
    PerformanceMetrics(
        metric_name="AUC-ROC",
        value=0.82,
        validation_status="Internally Validated",
        subgroup="Overall"
    )
)

card.performance.add_metric(
    PerformanceMetrics(
        metric_name="Sensitivity",
        value=0.75,
        validation_status="Internally Validated"
    )
)

# Export
print("Exporting model card...")
HTMLExporter.export(card, "output/quickstart_card.html")
JSONExporter.export(card, "output/quickstart_card.json")
print("✓ HTML exported: output/quickstart_card.html")
print("✓ JSON exported: output/quickstart_card.json")
