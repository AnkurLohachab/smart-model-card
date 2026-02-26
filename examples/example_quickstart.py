"""
Quick Start Example

Minimal example showing how to create a simple model card.

Author: Ankur Lohachab
Department of Advanced Computing Sciences, Maastricht University
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
    HTMLExporter
)
from smart_model_card.sections import (
    SourceDataset,
    InputFeature,
    OutputFeature,
    ValidationDataset,
    PerformanceMetric
)


def main():
    """Create a minimal model card"""

    # Create model card
    card = ModelCard()

    # Section 1: Model Details
    card.set_model_details(ModelDetails(
        model_name="Simple Risk Model",
        version="1.0.0",
        developer_organization="Your Organization",
        release_date="2025-01-15",
        description="Simple risk prediction model",
        clinical_function="decision_support",
        algorithms_used="Logistic Regression",
        licensing="MIT License",
        support_contact="support@example.com"
    ))

    # Section 2: Intended Use
    card.set_intended_use(IntendedUse(
        primary_intended_users="Clinicians",
        clinical_indications="Risk assessment",
        patient_target_group="Adults aged 18+",
        intended_use_environment="hospital_outpatient"
    ))

    # Section 3: Data & Factors
    card.set_data_factors(DataFactors(
        source_datasets=[
            SourceDataset(
                name="Training Dataset",
                origin="EHR System",
                size=10000,
                collection_period="2020-2024",
                population_characteristics="Adults aged 18+"
            )
        ],
        data_distribution_summary="Balanced dataset with representative demographics",
        data_representativeness="Representative of target population",
        data_governance="IRB approved, de-identified per HIPAA"
    ))

    # Section 4: Features & Outputs
    card.set_features_outputs(FeaturesOutputs(
        input_features=[
            InputFeature("age", "numeric", True, "Demographics", "18-100", "years"),
            InputFeature("gender", "categorical", True, "Demographics", "M/F")
        ],
        output_features=[
            OutputFeature("risk_score", "probability", "probability", "0.0-1.0")
        ],
        feature_type_distribution="2 features: 1 numeric, 1 categorical",
        uncertainty_quantification="Prediction intervals (90% CI)",
        output_interpretability="Calibrated risk probability"
    ))

    # Section 5: Performance & Validation
    card.set_performance_validation(PerformanceValidation(
        validation_datasets=[
            ValidationDataset(
                name="Test Set",
                source_institution="Same as training",
                population_characteristics="n=2000",
                validation_type="Internal holdout"
            )
        ],
        claimed_metrics=[
            PerformanceMetric("AUC-ROC", 0.80, "Claimed")
        ],
        validated_metrics=[
            PerformanceMetric("AUC-ROC", 0.78, "Validated")
        ]
    ))

    # Section 6: Methodology
    card.set_methodology(Methodology(
        model_development_workflow="Data extraction -> Feature engineering -> Training -> Validation",
        training_procedure="Logistic regression with L2 regularization",
        data_preprocessing="Standard scaling, missing value imputation"
    ))

    # Section 7: Additional Information
    card.set_additional_info(AdditionalInfo(
        benefit_risk_summary="Benefits outweigh risks for intended use",
        ethical_considerations="Fairness evaluated across demographic groups",
        caveats_limitations="Limited to training population characteristics",
        recommendations_for_safe_use="Use alongside clinical judgment"
    ))

    # Export to HTML
    html_path = HTMLExporter.export(card, "./output/quickstart_model_card.html")
    print(f"Model card created: {html_path}")
    print("Open HTML file in browser to view.")


if __name__ == "__main__":
    main()
