"""
Complete Model Card Example

Demonstrates creating a comprehensive medical AI model card with all sections
and integration with smart-omop for cohort definitions.

This example creates a model card for a hypothetical COPD risk prediction model.

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
    MarkdownExporter
)
from smart_model_card.sections import (
    ConceptSet,
    CohortCriteria,
    SourceDataset,
    InputFeature,
    OutputFeature,
    ValidationDataset,
    PerformanceMetric
)


def create_copd_risk_model_card():
    """Create complete model card for COPD risk prediction model"""

    # Section 1: Model Details
    model_details = ModelDetails(
        model_name="COPD-Risk-Predictor",
        version="2.1.0",
        developer_organization="Department of Advanced Computing Sciences, Maastricht University",
        release_date="2025-01-15",
        description="AI model for predicting 5-year risk of COPD exacerbation in patients with existing COPD diagnosis. Uses clinical history, demographics, and lab results to generate risk scores.",
        clinical_function="decision_support",
        algorithms_used="Gradient Boosting (XGBoost) with SHAP explainability",
        gmdn_code="62948",
        licensing="MIT License",
        support_contact="ankur.lohachab@maastrichtuniversity.nl",
        literature_references=[
            "Smith J et al. (2024) Machine Learning for COPD Risk Prediction. J Med AI. 15(3):245-260",
            "Johnson A et al. (2023) Validation of AI Models in Respiratory Medicine. Thorax. 78:890-901"
        ],
        clinical_study_references=[
            "Internal Validation Study Report v2.0 (2024-12-15)",
            "External Validation at University Hospital Network (2024-11-20)"
        ]
    )

    # Section 2: Intended Use and Clinical Context
    intended_use = IntendedUse(
        primary_intended_users="Pulmonologists, respiratory therapists, primary care physicians with training in COPD management",
        clinical_indications="Patients aged 40-80 with confirmed COPD diagnosis (GOLD criteria) for risk stratification and care planning",
        patient_target_group="Adults with diagnosed COPD (ICD-10: J44.x), minimum 6 months follow-up data",
        contraindications="Not validated for acute exacerbations, pediatric patients, or patients without confirmed COPD diagnosis",
        intended_use_environment="hospital_outpatient, hospital_inpatient",
        out_of_scope_applications="Emergency triage, diagnosis of COPD (prediction only), asthma-COPD overlap syndrome",
        warnings="Model outputs are estimates and should not replace clinical judgment. Requires periodic recalibration for local populations."
    )

    # Section 3: Data & Factors
    concept_sets = [
        ConceptSet(
            name="COPD Diagnosis",
            vocabulary="OMOP/SNOMED",
            concept_ids=[255573, 40481087, 4063381],
            description="Chronic obstructive lung disease and related conditions"
        ),
        ConceptSet(
            name="Smoking History",
            vocabulary="OMOP/SNOMED",
            concept_ids=[4209585, 4276526],
            description="Current and former smoking status"
        ),
        ConceptSet(
            name="Pulmonary Function Tests",
            vocabulary="LOINC",
            concept_ids=[19868, 19870, 20150],
            description="FEV1, FVC, FEV1/FVC ratio measurements"
        )
    ]

    cohort_criteria = CohortCriteria(
        inclusion_rules=[
            "Age >= 40 and <= 80 years",
            "Confirmed COPD diagnosis (concept set 0)",
            "At least one pulmonary function test in prior 12 months",
            "Minimum 6 months observation period"
        ],
        exclusion_rules=[
            "Active lung cancer diagnosis",
            "Lung transplant recipients",
            "Missing critical baseline variables (>20% missingness)"
        ],
        observation_window="Prior: 365 days, Post: 1825 days (5 years)"
    )

    source_datasets = [
        SourceDataset(
            name="University Hospital CDW",
            origin="Electronic Health Records (2015-2023)",
            size=8542,
            collection_period="2015-01-01 to 2023-12-31",
            population_characteristics="Urban academic medical center, 62% male, mean age 65.3±9.8 years, 45% current smokers"
        ),
        SourceDataset(
            name="Regional Health Network",
            origin="Multi-site OMOP CDM database",
            size=3821,
            collection_period="2017-06-01 to 2023-12-31",
            population_characteristics="Community hospitals, 58% male, mean age 67.1±10.2 years, ethnically diverse"
        )
    ]

    data_factors = DataFactors(
        concept_sets=concept_sets,
        primary_cohort_criteria=cohort_criteria,
        source_datasets=source_datasets,
        data_distribution_summary="Training cohort (n=8,542): 62% male, mean age 65.3 years, 45% current smokers, 38% GOLD stage III-IV. Racial distribution: 72% White, 15% Black, 8% Hispanic, 5% Other.",
        data_representativeness="Training data represents urban academic center population. External validation shows performance degradation in rural populations (AUC 0.78 vs 0.85) and underrepresented ethnic groups.",
        data_governance="IRB approval obtained (protocol #2023-HS-456). Data de-identified per HIPAA Safe Harbor. Patient consent waived for retrospective analysis. Data access restricted to authorized researchers."
    )

    # Section 4: Features & Outputs
    input_features = [
        InputFeature(
            name="age",
            data_type="numeric",
            required=True,
            clinical_domain="Demographics",
            value_range="40-80",
            units="years"
        ),
        InputFeature(
            name="gender",
            data_type="categorical",
            required=True,
            clinical_domain="Demographics",
            value_range="Male, Female"
        ),
        InputFeature(
            name="smoking_status",
            data_type="categorical",
            required=True,
            clinical_domain="Social History",
            value_range="Never, Former, Current"
        ),
        InputFeature(
            name="fev1_percent_predicted",
            data_type="numeric",
            required=True,
            clinical_domain="Pulmonary Function",
            value_range="15-100",
            units="%"
        ),
        InputFeature(
            name="exacerbation_count_12mo",
            data_type="numeric",
            required=True,
            clinical_domain="Clinical History",
            value_range="0-10",
            units="count"
        ),
        InputFeature(
            name="comorbidity_count",
            data_type="numeric",
            required=False,
            clinical_domain="Comorbidities",
            value_range="0-15",
            units="count"
        )
    ]

    output_features = [
        OutputFeature(
            name="exacerbation_risk_5yr",
            type="probability",
            units="probability",
            value_range="0.0-1.0",
            classes=None
        ),
        OutputFeature(
            name="risk_category",
            type="classification",
            units=None,
            value_range=None,
            classes=["Low (<20%)", "Moderate (20-50%)", "High (>50%)"]
        )
    ]

    features_outputs = FeaturesOutputs(
        input_features=input_features,
        output_features=output_features,
        feature_type_distribution="6 input features: 3 numeric, 3 categorical. All features derived from structured EHR data.",
        uncertainty_quantification="Prediction intervals calculated via quantile regression (90% CI). Calibrated probabilities output with Platt scaling.",
        output_interpretability="Risk score with calibrated probability. SHAP values provided for top 5 contributing features per prediction."
    )

    # Section 5: Performance & Validation
    validation_datasets = [
        ValidationDataset(
            name="Internal Holdout Set",
            source_institution="University Hospital CDW",
            population_characteristics="n=2,136, similar to training set demographics",
            validation_type="Internal temporal holdout (2023 data)"
        ),
        ValidationDataset(
            name="External Validation Cohort",
            source_institution="Regional Health Network (3 sites)",
            population_characteristics="n=3,821, community hospitals, broader demographic distribution",
            validation_type="External multi-site prospective"
        )
    ]

    claimed_metrics = [
        PerformanceMetric("AUC-ROC", 0.85, "Claimed (Internal)", None),
        PerformanceMetric("Sensitivity", 0.78, "Claimed (Internal)", None),
        PerformanceMetric("Specificity", 0.82, "Claimed (Internal)", None),
        PerformanceMetric("Calibration (Brier Score)", 0.15, "Claimed (Internal)", None)
    ]

    validated_metrics = [
        PerformanceMetric("AUC-ROC", 0.83, "Externally Validated", "Overall"),
        PerformanceMetric("AUC-ROC", 0.85, "Externally Validated", "Male"),
        PerformanceMetric("AUC-ROC", 0.80, "Externally Validated", "Female"),
        PerformanceMetric("AUC-ROC", 0.84, "Externally Validated", "Age 40-60"),
        PerformanceMetric("AUC-ROC", 0.82, "Externally Validated", "Age 60-80"),
        PerformanceMetric("Calibration Slope", 0.98, "Externally Validated", "Overall")
    ]

    performance_validation = PerformanceValidation(
        validation_datasets=validation_datasets,
        claimed_metrics=claimed_metrics,
        validated_metrics=validated_metrics,
        calibration_analysis="Calibration slope 0.98 (95% CI: 0.92-1.04) on external validation. Calibration plot shows good agreement across risk deciles. Hosmer-Lemeshow test p=0.42.",
        fairness_assessment="Performance evaluated across gender, age, and race subgroups. AUC差异 <0.05 across all subgroups except Hispanic (n=308, AUC=0.76, requires further validation). No significant calibration differences by subgroup.",
        metric_validation_status="All reported metrics validated on external multi-site cohort. Fairness assessment conducted per FDA guidance on AI bias."
    )

    # Section 6: Methodology & Explainability
    methodology = Methodology(
        model_development_workflow="Data extraction from OMOP CDM → Feature engineering → Train/validation/test split (60/20/20) → Hyperparameter tuning (5-fold CV) → Model training → Calibration → External validation → SHAP analysis",
        training_procedure="XGBoost classifier with 500 trees, max depth 6, learning rate 0.05. Trained on 5,126 samples with class balancing (SMOTE). Training time: 12 minutes on 16-core CPU. Early stopping with 50-round patience.",
        data_preprocessing="Missing value imputation (median for numeric, mode for categorical). Outlier capping at 1st/99th percentiles. Feature scaling (standard normalization). Temporal train-test split to prevent leakage.",
        synthetic_data_usage="No synthetic data used for training. MedSynth synthetic data (n=500) used for algorithm testing and user training only.",
        explainable_ai_method="SHAP (SHapley Additive exPlanations) TreeExplainer for feature importance. Top 5 contributing features displayed per prediction with directional impact.",
        global_vs_local_interpretability="Global: SHAP feature importance ranking, partial dependence plots. Local: Per-prediction SHAP values with force plots for individual risk assessment."
    )

    # Section 7: Additional Information
    additional_info = AdditionalInfo(
        benefit_risk_summary="Benefits: Early identification of high-risk patients enabling proactive intervention, reduced emergency visits (estimated 15-20% in pilot study). Risks: Potential over-treatment of false positives, reliance on model may miss atypical presentations. Net benefit analysis shows clinical utility for risk thresholds 20-60%.",
        post_market_surveillance_plan="Quarterly performance monitoring on live deployment data. Alert triggers: AUC drop >0.05, calibration slope <0.90 or >1.10, subgroup performance disparity >0.10. Annual model retraining with updated data. Incident reporting system for adverse events.",
        ethical_considerations="Model trained on predominantly White population; generalizability to other ethnicities requires validation. No protected attributes (race, ethnicity) used as input features. Fairness audit conducted pre-deployment. Transparent communication of model limitations to end users.",
        caveats_limitations="Limited performance in Hispanic subgroup (requires additional validation). Not validated for COPD-asthma overlap, acute exacerbations, or post-lung-transplant patients. Performance degrades with >20% missing features. Calibration requires periodic updates.",
        recommendations_for_safe_use="1) Use only for patients meeting inclusion criteria. 2) Interpret outputs alongside clinical judgment. 3) Review SHAP explanations for biological plausibility. 4) Monitor for concept drift in local population. 5) Annual recalibration recommended. 6) Do not use for emergency decision-making.",
        explainability_recommendations="Display risk category and probability with confidence interval. Show top 5 SHAP features with directional impact. Include calibration plot for clinician reference. Provide link to full model card and technical documentation.",
        supporting_documents=[
            "Technical Validation Report v2.0 (internal)",
            "External Validation Study Protocol",
            "Instructions for Use (IFU) Document",
            "Fairness Audit Report",
            "Model Risk Assessment (MRA)",
            "Software Bill of Materials (SBOM)"
        ]
    )

    # Build complete model card
    card = ModelCard()
    card.set_model_details(model_details)
    card.set_intended_use(intended_use)
    card.set_data_factors(data_factors)
    card.set_features_outputs(features_outputs)
    card.set_performance_validation(performance_validation)
    card.set_methodology(methodology)
    card.set_additional_info(additional_info)

    return card


def main():
    """Create and export model card to multiple formats"""
    print("Creating COPD Risk Prediction Model Card...")

    # Create model card
    card = create_copd_risk_model_card()

    # Export to JSON
    json_path = JSONExporter.export(card, "./output/copd_risk_model_card.json")
    print(f"✓ JSON exported: {json_path}")

    # Export to HTML
    html_path = HTMLExporter.export(card, "./output/copd_risk_model_card.html")
    print(f"✓ HTML exported: {html_path}")

    # Export to Markdown
    md_path = MarkdownExporter.export(card, "./output/copd_risk_model_card.md")
    print(f"✓ Markdown exported: {md_path}")

    print("\nModel card creation complete!")
    print("Open HTML file in browser to view formatted card.")


if __name__ == "__main__":
    main()
