"""
Complete Workflow Demo - smart-model-card

Demonstrates the complete workflow of creating a medical AI model card:
1. Using smart-omop for OMOP data integration
2. Creating model card with all sections
3. Exporting to multiple formats
4. Using CLI commands

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
    HTMLExporter,
    JSONExporter,
    MarkdownExporter,
    build_data_factors_from_smart_omop
)
from smart_model_card.sections import (
    InputFeature,
    OutputFeature,
    ValidationDataset,
    PerformanceMetric
)

# Check if smart-omop is available
try:
    from smart_omop import OMOPClient
    SMART_OMOP_AVAILABLE = True
except ImportError:
    SMART_OMOP_AVAILABLE = False
    print("⚠ smart-omop not installed. Skipping OMOP integration demo.")
    print("  Install with: pip install smart-omop")


def create_model_card_with_omop():
    """Create a model card using real OMOP data from AWS WebAPI"""

    if not SMART_OMOP_AVAILABLE:
        print("\nSkipping OMOP integration demo (smart-omop not installed)")
        return create_model_card_without_omop()

    print("\n" + "="*70)
    print("CREATING MODEL CARD WITH REAL OMOP DATA")
    print("="*70)

    # OMOP WebAPI URL (using the provided AWS instance)
    WEBAPI_URL = "http://ec2-13-49-5-87.eu-north-1.compute.amazonaws.com:8080/WebAPI"

    try:
        # Fetch OMOP cohort data
        print("\n1. Fetching COPD cohort from OMOP WebAPI...")
        with OMOPClient(WEBAPI_URL) as client:
            # Build DataFactors section using smart-omop
            omop_data = build_data_factors_from_smart_omop(
                client=client,
                cohort_id=145,  # COPD cohort
                source_key="KAGGLECOPD"
            )
            print("   ✓ Fetched OMOP cohort data")
            print(f"   ✓ Extracted {len(omop_data['concept_sets'])} concept sets")

    except Exception as e:
        print(f"   ✗ Failed to fetch OMOP data: {e}")
        print("   Falling back to example without OMOP data...")
        return create_model_card_without_omop()

    # Create model card
    print("\n2. Building model card with 7 sections...")
    card = ModelCard()

    # Section 1: Model Details
    card.set_model_details(ModelDetails(
        model_name="COPD-Risk-Predictor-v2",
        version="2.0.0",
        developer_organization="Maastricht University - Dept. of Advanced Computing Sciences",
        release_date="2025-01-15",
        description="AI model for predicting COPD exacerbation risk using OMOP CDM standardized data",
        clinical_function="decision_support",
        algorithms_used="Gradient Boosting (XGBoost) with SHAP explainability",
        gmdn_code="62948",
        licensing="MIT License",
        support_contact="ankur.lohachab@maastrichtuniversity.nl",
        literature_references=[
            "OMOP Common Data Model v5.4 specification",
            "OHDSI Methods Library for observational studies"
        ]
    ))
    print("   ✓ Section 1: Model Details")

    # Section 2: Intended Use
    card.set_intended_use(IntendedUse(
        primary_intended_users="Pulmonologists, respiratory therapists, primary care physicians",
        clinical_indications="Risk stratification for patients with confirmed COPD diagnosis",
        patient_target_group="Adults aged 40-80 with diagnosed COPD (OMOP concept: 255573)",
        contraindications="Not validated for acute exacerbations or pediatric populations",
        intended_use_environment="hospital_outpatient",
        out_of_scope_applications="COPD diagnosis, emergency triage, asthma management",
        warnings="Validate performance on local population before deployment"
    ))
    print("   ✓ Section 2: Intended Use")

    # Section 3: Data & Factors (using OMOP data)
    card.set_data_factors(DataFactors(
        concept_sets=omop_data["concept_sets"],
        primary_cohort_criteria=omop_data["primary_cohort_criteria"],
        source_datasets=omop_data["source_datasets"],
        data_distribution_summary="OMOP CDM standardized cohort. Demographic distribution: Age 40-90, Gender balanced. Clinical features include diagnosis codes, medication history, lab results.",
        data_representativeness="Data from KAGGLECOPD database. Representative of COPD patient population in observational studies. Geographic and demographic representativeness should be validated for target deployment.",
        data_governance="OMOP CDM de-identification standards applied. IRB approved. HIPAA Safe Harbor method. Accessed via OHDSI WebAPI.",
        deid_method="OMOP CDM Safe Harbor de-identification",
        date_handling="Dates shifted uniformly per patient"
    ))
    print("   ✓ Section 3: Data & Factors (with real OMOP concept sets)")

    # Section 4: Features & Outputs
    card.set_features_outputs(FeaturesOutputs(
        input_features=[
            InputFeature("age_at_index", "numeric", True, "Demographics", "40-90", "years"),
            InputFeature("gender_concept_id", "categorical", True, "Demographics", "OMOP: 8507, 8532"),
            InputFeature("fev1_percent_predicted", "numeric", True, "Pulmonary Function", "15-100", "%"),
            InputFeature("copd_severity", "categorical", True, "Clinical History", "Mild, Moderate, Severe"),
            InputFeature("prior_exacerbations_12mo", "numeric", True, "Clinical History", "0-10", "count"),
            InputFeature("medication_adherence", "numeric", False, "Medication", "0.0-1.0", "proportion")
        ],
        output_features=[
            OutputFeature("exacerbation_risk_12mo", "probability", "probability", "0.0-1.0"),
            OutputFeature("risk_tier", "classification", classes=["Low", "Medium", "High"])
        ],
        feature_type_distribution="6 input features: 4 numeric, 2 categorical. All derived from OMOP CDM tables.",
        uncertainty_quantification="Prediction intervals via quantile regression. Calibrated probabilities with Platt scaling.",
        output_interpretability="SHAP values for each prediction. Risk tiers based on clinical guidelines."
    ))
    print("   ✓ Section 4: Features & Outputs")

    # Section 5: Performance & Validation
    card.set_performance_validation(PerformanceValidation(
        validation_datasets=[
            ValidationDataset(
                "Internal Holdout (Temporal)",
                "KAGGLECOPD",
                "n=6, 2023 data, temporal split",
                "Internal temporal holdout"
            ),
            ValidationDataset(
                "External Validation Cohort",
                "Partner Hospital Network",
                "n=1,500, prospective validation",
                "External prospective"
            )
        ],
        claimed_metrics=[
            PerformanceMetric("AUC-ROC", 0.84, "Claimed (Internal)"),
            PerformanceMetric("Sensitivity", 0.77, "Claimed (Internal)"),
            PerformanceMetric("Specificity", 0.81, "Claimed (Internal)")
        ],
        validated_metrics=[
            PerformanceMetric("AUC-ROC", 0.82, "Internally Validated", "Overall"),
            PerformanceMetric("AUC-ROC", 0.83, "Internally Validated", "Male"),
            PerformanceMetric("AUC-ROC", 0.80, "Internally Validated", "Female"),
            PerformanceMetric("AUC-ROC", 0.79, "Externally Validated", "Overall")
        ],
        calibration_analysis="Calibration slope 0.94 on holdout. Hosmer-Lemeshow p=0.42. Good calibration across deciles.",
        fairness_assessment="Performance evaluated across gender and age subgroups. AUC difference <0.03. No significant disparities detected.",
        metric_validation_status="Internal validation complete. External validation at 2 partner sites (ongoing)."
    ))
    print("   ✓ Section 5: Performance & Validation")

    # Section 6: Methodology
    card.set_methodology(Methodology(
        model_development_workflow="OMOP data extraction → Feature engineering → ATLAS cohort definition → Train/validation split → Model training → Calibration → SHAP analysis → Clinical validation",
        training_procedure="XGBoost with 500 trees, max depth 6, learning rate 0.05. 5-fold cross-validation for hyperparameter tuning. Class balancing via scale_pos_weight. Training time: 12 minutes on 16-core CPU.",
        data_preprocessing="OMOP concept standardization. Missing values: median (numeric), mode (categorical). Temporal split for validation. Feature scaling with robust normalization. Leakage prevention via strict temporal cutoff.",
        synthetic_data_usage="No synthetic data in training. Pipeline validated on MedSynth synthetic OMOP data (n=500) for reproducibility testing.",
        explainable_ai_method="SHAP (SHapley Additive exPlanations) with TreeExplainer. Feature importance ranking. Individual prediction explanations with force plots.",
        global_vs_local_interpretability="Global: SHAP summary plots showing overall feature importance. Local: Per-patient SHAP values for each prediction showing contribution of OMOP-derived features."
    ))
    print("   ✓ Section 6: Methodology & Explainability")

    # Section 7: Additional Information
    card.set_additional_info(AdditionalInfo(
        benefit_risk_summary="Benefits: Early risk stratification enables proactive intervention, reducing hospitalizations. Risks: Over-reliance may miss atypical presentations. Net benefit analysis positive for risk thresholds 15-70%.",
        post_market_surveillance_plan="Quarterly performance monitoring. Alert if AUC drops >0.05 or calibration slope <0.90. Annual model retraining on updated OMOP data. User feedback mechanism for clinical utility.",
        ethical_considerations="OMOP CDM ensures standardized data representation. No direct use of protected attributes. Fairness validated across demographics. Transparent documentation for regulatory review.",
        caveats_limitations="Trained on single OMOP database. Performance on other OMOP instances requires validation. Limited to patients with sufficient observation history. Not validated for post-transplant or end-stage disease.",
        recommendations_for_safe_use="1) Verify OMOP vocabulary mappings in local database. 2) Validate calibration on local population. 3) Use as decision support, not replacement for judgment. 4) Monitor for concept drift. 5) Ensure OMOP CDM v5.x compatibility.",
        explainability_recommendations="Display SHAP contributions with risk score. Show OMOP concept IDs/names for transparency. Provide link to ATLAS cohort definition for reproducibility.",
        supporting_documents=[
            "OMOP Cohort Definition (ATLAS JSON)",
            "SHAP Analysis Report",
            "Calibration Plots",
            "Fairness Assessment Report",
            "Clinical Validation Protocol"
        ]
    ))
    print("   ✓ Section 7: Additional Information")

    return card


def create_model_card_without_omop():
    """Create a basic model card without OMOP integration"""

    print("\n" + "="*70)
    print("CREATING BASIC MODEL CARD (WITHOUT OMOP)")
    print("="*70)

    card = ModelCard()

    # Import necessary classes for non-OMOP version
    from smart_model_card.sections import SourceDataset

    # Simplified sections
    card.set_model_details(ModelDetails(
        model_name="Simple-Risk-Model",
        version="1.0.0",
        developer_organization="Your Organization",
        release_date="2025-01-15",
        description="Simple risk prediction model",
        clinical_function="decision_support",
        algorithms_used="Logistic Regression",
        licensing="MIT License",
        support_contact="support@example.com"
    ))

    card.set_intended_use(IntendedUse(
        primary_intended_users="Clinicians",
        clinical_indications="General risk assessment",
        patient_target_group="Adults aged 18+",
        intended_use_environment="hospital_outpatient"
    ))

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
        data_distribution_summary="Balanced demographics",
        data_representativeness="Representative of target population",
        data_governance="IRB approved, HIPAA compliant"
    ))

    card.set_features_outputs(FeaturesOutputs(
        input_features=[
            InputFeature("age", "numeric", True, "Demographics", "18-100", "years")
        ],
        output_features=[
            OutputFeature("risk_score", "probability", "probability", "0.0-1.0")
        ],
        feature_type_distribution="1 numeric feature",
        uncertainty_quantification="Prediction intervals (90% CI)",
        output_interpretability="Calibrated probability"
    ))

    card.set_performance_validation(PerformanceValidation(
        validation_datasets=[
            ValidationDataset("Test Set", "Same institution", "n=2000", "Internal holdout")
        ],
        claimed_metrics=[PerformanceMetric("AUC-ROC", 0.80, "Claimed")],
        validated_metrics=[PerformanceMetric("AUC-ROC", 0.78, "Validated")]
    ))

    card.set_methodology(Methodology(
        model_development_workflow="Standard ML workflow",
        training_procedure="Logistic regression with L2 regularization",
        data_preprocessing="Standard scaling, imputation"
    ))

    card.set_additional_info(AdditionalInfo(
        benefit_risk_summary="Benefits outweigh risks",
        ethical_considerations="Fairness evaluated",
        caveats_limitations="Limited to training population",
        recommendations_for_safe_use="Use with clinical judgment"
    ))

    return card


def export_model_card(card: ModelCard, prefix: str = "demo"):
    """Export model card to multiple formats"""

    print(f"\n3. Exporting model card to multiple formats...")

    # JSON
    json_path = JSONExporter.export(card, f"./output/{prefix}_model_card.json")
    print(f"   ✓ JSON: {json_path}")

    # HTML
    html_path = HTMLExporter.export(card, f"./output/{prefix}_model_card.html")
    print(f"   ✓ HTML: {html_path}")

    # Markdown
    md_path = MarkdownExporter.export(card, f"./output/{prefix}_model_card.md")
    print(f"   ✓ Markdown: {md_path}")

    return json_path, html_path, md_path


def main():
    """Run complete workflow demo"""

    print("\n" + "="*70)
    print("SMART-MODEL-CARD - COMPLETE WORKFLOW DEMO")
    print("="*70)
    print("\nDemonstrating the complete model card creation workflow:")
    print("1. Integration with real OMOP data (smart-omop)")
    print("2. Creating comprehensive 7-section model card")
    print("3. Exporting to JSON, HTML, and Markdown")
    print("4. CLI command examples")

    # Create model card (with or without OMOP based on availability)
    card = create_model_card_with_omop()

    # Export to multiple formats
    json_path, html_path, md_path = export_model_card(card, prefix="complete_demo")

    # CLI examples
    print("\n4. CLI Command Examples:")
    print("   You can now use these CLI commands:")
    print(f"   • Validate: smart-model-card validate {json_path}")
    print(f"   • Export:   smart-model-card export {json_path} --format html --output output/exported.html")
    print(f"   • Hash:     smart-model-card hash --card {json_path}")
    print(f"   • Create:   smart-model-card create --model-name 'My Model' --output output/new_card.json")

    print("\n" + "="*70)
    print("DEMO COMPLETE!")
    print("="*70)
    print(f"\nModel card created successfully!")
    print(f"• Open HTML file to view: {html_path}")
    print(f"• JSON file for programmatic use: {json_path}")
    print(f"• Markdown file for documentation: {md_path}")

    if SMART_OMOP_AVAILABLE:
        print("\nKey Features Demonstrated:")
        print("  ✓ Real OMOP cohort data integration via smart-omop")
        print("  ✓ Automatic concept set extraction from OMOP")
        print("  ✓ Cohort criteria from OMOP cohort definition")
        print("  ✓ Complete 7-section medical AI model card")
        print("  ✓ Multi-format export (JSON, HTML, Markdown)")
        print("  ✓ Regulatory-compliant documentation")
        print("  ✓ OHDSI/OMOP CDM alignment")
    else:
        print("\nNote: Install smart-omop to unlock OMOP integration features:")
        print("  pip install smart-omop")

    print("\n" + "="*70)


if __name__ == "__main__":
    main()
