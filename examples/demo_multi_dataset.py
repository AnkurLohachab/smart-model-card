"""
Demo: Multi-Dataset Model Card with Dropdown

Shows the multi-dataset dropdown selector functionality
"""

from smart_model_card import (
    ModelCard,
    ModelDetails,
    IntendedUse,
    DataFactors,
    FeaturesOutputs,
    PerformanceValidation,
    Methodology,
    AdditionalInfo,
    HTMLExporter,
    JSONExporter
)
from smart_model_card.sections import (
    SourceDataset,
    ConceptSet,
    CohortCriteria,
    InputFeature,
    OutputFeature,
    ValidationDataset,
    PerformanceMetric
)

# Create model card with multiple datasets
card = ModelCard()

# Section 1: Model Details
card.set_model_details(ModelDetails(
    model_name="Multi-Site-COPD-Model",
    version="2.0.0",
    developer_organization="Department of Advanced Computing Sciences, Maastricht University",
    release_date="2025-01-15",
    description="Multi-site COPD risk model trained on three different hospital databases",
    clinical_function="decision_support",
    algorithms_used="XGBoost Ensemble",
    licensing="MIT License",
    support_contact="support@example.com"
))

# Section 2: Intended Use
card.set_intended_use(IntendedUse(
    primary_intended_users="Pulmonologists",
    clinical_indications="COPD risk stratification",
    patient_target_group="Adults with COPD",
    intended_use_environment="hospital_outpatient"
))

# Section 3: Data & Factors with MULTIPLE datasets
card.set_data_factors(DataFactors(
    source_datasets=[
        SourceDataset(
            name="Hospital A - Academic Medical Center",
            origin="Academic medical center EHR system, urban setting",
            size=1250,
            collection_period="2020-01-01 to 2023-12-31",
            population_characteristics="Urban population, diverse demographics, 65% male, mean age 68",
            demographics={
                "age": "Mean: 68, Range: 45-92",
                "gender": "Male: 65%, Female: 35%",
                "race": "White: 45%, Black: 30%, Hispanic: 15%, Asian: 8%, Other: 2%"
            }
        ),
        SourceDataset(
            name="Hospital B - Community Hospital",
            origin="Community hospital EHR system, suburban setting",
            size=890,
            collection_period="2020-06-01 to 2023-12-31",
            population_characteristics="Suburban population, predominantly white, 58% male, mean age 71",
            demographics={
                "age": "Mean: 71, Range: 50-88",
                "gender": "Male: 58%, Female: 42%",
                "race": "White: 78%, Black: 12%, Hispanic: 7%, Asian: 2%, Other: 1%"
            }
        ),
        SourceDataset(
            name="Hospital C - Rural Health Center",
            origin="Rural health center, integrated care network",
            size=445,
            collection_period="2021-01-01 to 2023-12-31",
            population_characteristics="Rural population, older demographic, 52% male, mean age 73",
            demographics={
                "age": "Mean: 73, Range: 55-90",
                "gender": "Male: 52%, Female: 48%",
                "race": "White: 92%, Black: 3%, Hispanic: 3%, Asian: 1%, Other: 1%"
            }
        )
    ],
    concept_sets=[
        ConceptSet(
            name="COPD Diagnosis",
            vocabulary="SNOMED",
            concept_ids=[255573],
            description="Primary COPD diagnosis codes"
        )
    ],
    primary_cohort_criteria=CohortCriteria(
        inclusion_rules=[
            "Patients with COPD diagnosis",
            "Age >= 40 years"
        ],
        exclusion_rules=["Active cancer treatment"],
        observation_window="Minimum 12 months prior history"
    ),
    data_distribution_summary={
        "Total Patients": "2,585 across 3 sites",
        "Age Range": "45-92 years",
        "Gender": "Male: 60%, Female: 40%",
        "Follow-up": "Mean 24 months"
    },
    data_representativeness="Multi-site study covering urban, suburban, and rural populations",
    data_governance="IRB approved at all sites, HIPAA compliant de-identification"
))

# Section 4: Features & Outputs
card.set_features_outputs(FeaturesOutputs(
    input_features=[
        InputFeature(name="age", data_type="numeric", required=True,
                    clinical_domain="Demographics", value_range="40-90", units="years"),
        InputFeature(name="gender", data_type="categorical", required=True,
                    clinical_domain="Demographics", value_range="M/F")
    ],
    output_features=[
        OutputFeature(name="risk_score", type="probability",
                     value_range="0.0-1.0", units="probability")
    ],
    feature_type_distribution="Demographics and clinical features",
    uncertainty_quantification="Calibrated probabilities",
    output_interpretability="SHAP values"
))

# Section 5: Performance
card.set_performance_validation(PerformanceValidation(
    validation_datasets=[
        ValidationDataset(
            name="Combined Test Set",
            source_institution="All 3 hospitals",
            population_characteristics="n=517 (20% holdout)",
            validation_type="Multi-site holdout"
        )
    ],
    claimed_metrics=[
        PerformanceMetric("AUC-ROC", 0.84, "Claimed"),
        PerformanceMetric("Sensitivity", 0.78, "Claimed")
    ],
    validated_metrics=[
        PerformanceMetric("AUC-ROC", 0.82, "Validated", "Overall"),
        PerformanceMetric("AUC-ROC", 0.83, "Validated", "Hospital A"),
        PerformanceMetric("AUC-ROC", 0.81, "Validated", "Hospital B"),
        PerformanceMetric("AUC-ROC", 0.80, "Validated", "Hospital C")
    ],
    calibration_analysis="Calibration slope 0.94 across all sites",
    fairness_assessment="Performance consistent across demographic subgroups",
    metric_validation_status="Externally validated on independent test set"
))

# Section 6: Methodology
card.set_methodology(Methodology(
    model_development_workflow="Multi-site data aggregation → Feature engineering → Ensemble training",
    training_procedure="XGBoost with site-specific calibration",
    data_preprocessing="OMOP standardization, site stratification"
))

# Section 7: Additional Info
card.set_additional_info(AdditionalInfo(
    benefit_risk_summary="Multi-site validation improves generalizability",
    ethical_considerations="Fairness validated across sites and demographics",
    caveats_limitations="Requires validation on additional external sites",
    recommendations_for_safe_use="Monitor performance when deploying to new sites"
))

# Export
print("=" * 70)
print("Creating Multi-Dataset Model Card")
print("=" * 70)

json_path = JSONExporter.export(card, "./output/multi_dataset_card.json")
print(f"✓ JSON exported: {json_path}")

html_path = HTMLExporter.export(card, "./output/multi_dataset_card.html")
print(f"✓ HTML exported: {html_path}")

print("\n" + "=" * 70)
print("✓ Multi-Dataset Model Card Created!")
print("=" * 70)
print(f"\nOpen HTML to see the dataset dropdown: {html_path}")
print("\nThe dropdown will show:")
print("  - Hospital A - Academic Medical Center")
print("  - Hospital B - Community Hospital")
print("  - Hospital C - Rural Health Center")
