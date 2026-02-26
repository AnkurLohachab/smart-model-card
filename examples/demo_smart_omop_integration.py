"""
Demo: Real smart-omop Integration

Demonstrates creating a model card using real OMOP data from smart-omop package.
This example uses the actual AWS OMOP instance to fetch cohort data.

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
    create_omop_adapter
)
from smart_model_card.sections import (
    InputFeature,
    OutputFeature,
    ValidationDataset,
    PerformanceMetric
)

# Import smart-omop
try:
    from smart_omop import OMOPClient
    SMART_OMOP_AVAILABLE = True
except ImportError:
    SMART_OMOP_AVAILABLE = False
    print("Warning: smart-omop not installed. Install with: pip install smart-omop")


BASE_URL = "http://ec2-13-49-5-87.eu-north-1.compute.amazonaws.com:8080/WebAPI"


def fetch_omop_cohort_data():
    """Fetch real COPD cohort data from smart-omop"""
    if not SMART_OMOP_AVAILABLE:
        return None, None

    print("Fetching COPD cohort data from OMOP WebAPI...")

    try:
        with OMOPClient(BASE_URL) as client:
            # Fetch existing COPD cohort (ID 145)
            cohort_definition = client.get_cohort(cohort_id=145)
            print(f"✓ Fetched cohort: {cohort_definition.get('name', 'Unknown')}")

            # Get cohort results
            try:
                cohort_results = client.get_cohort_results(
                    cohort_id=145,
                    source_key="KAGGLECOPD"
                )
                print(f"✓ Person count: {cohort_results.get('personCount', 'N/A')}")
            except Exception as e:
                print(f"  Note: Could not fetch results: {e}")
                cohort_results = None

            return cohort_definition, cohort_results

    except Exception as e:
        print(f"Error fetching OMOP data: {e}")
        return None, None


def create_model_card_with_omop_data(cohort_definition, cohort_results):
    """Create model card using real OMOP cohort data"""

    print("\nCreating model card with OMOP data...")

    # Create OMOP data adapter
    omop_adapter = create_omop_adapter(
        cohort_definition=cohort_definition,
        cohort_results=cohort_results,
        source_name="KAGGLECOPD - OMOP CDM Database",
        source_origin="Electronic Health Records (Kaggle COPD Dataset)"
    )

    # Extract data from adapter
    source_dataset = omop_adapter.get_dataset_info()
    concept_sets = omop_adapter.get_concept_sets()
    cohort_criteria = omop_adapter.get_cohort_criteria()

    print(f"✓ Extracted {len(concept_sets)} concept sets from OMOP cohort")
    print(f"✓ Extracted cohort criteria with {len(cohort_criteria.inclusion_rules)} rules")

    # Build model card
    card = ModelCard()

    # Section 1: Model Details
    card.set_model_details(ModelDetails(
        model_name="COPD-Exacerbation-Risk-Model",
        version="1.0.0",
        developer_organization="Department of Advanced Computing Sciences, Maastricht University",
        release_date="2025-01-15",
        description="Machine learning model for predicting COPD exacerbation risk using OMOP CDM data. Trained on real-world EHR data with standardized OMOP vocabulary.",
        clinical_function="decision_support",
        algorithms_used="Random Forest Classifier with SHAP explainability",
        gmdn_code="62948",
        licensing="MIT License",
        support_contact="ankur.lohachab@maastrichtuniversity.nl",
        literature_references=[
            "OMOP Common Data Model specification v5.4",
            "OHDSI Methods Library for observational research"
        ]
    ))

    # Section 2: Intended Use
    card.set_intended_use(IntendedUse(
        primary_intended_users="Pulmonologists, respiratory care specialists, primary care physicians",
        clinical_indications="Risk stratification for patients with confirmed COPD diagnosis",
        patient_target_group="Adults with COPD diagnosis (OMOP concept ID: 255573 and descendants)",
        contraindications="Not validated for acute exacerbations or pediatric populations",
        intended_use_environment="hospital_outpatient",
        out_of_scope_applications="Diagnosis of COPD, emergency triage, asthma management",
        warnings="Model trained on specific population; validate performance on local data before deployment"
    ))

    # Section 3: Data & Factors
    # Use real OMOP concept sets and cohort criteria with enhanced descriptions

    # Generate comprehensive data distribution summary
    data_distribution = omop_adapter.get_data_distribution_summary()

    # Generate data representativeness assessment based on actual cohort
    source_name = cohort_definition.get('name', 'COPD cohort')
    person_count = cohort_results.get('personCount', 0) if cohort_results else 0

    # Build data-driven representativeness statement
    representativeness_parts = []

    # Database source
    representativeness_parts.append(
        f"**Data Source:** KAGGLECOPD database accessed via OMOP CDM v5.x through OHDSI WebAPI. "
        f"The '{source_name}' cohort (n={person_count}) represents patients meeting standardized inclusion criteria defined using OMOP concept sets."
    )

    # Geographic representativeness
    representativeness_parts.append(
        f"**Geographic Scope:** Single healthcare database. Generalizability to other geographic regions and healthcare systems requires external validation. "
        f"Recommend validation across: (1) diverse healthcare settings (academic medical centers, community hospitals, outpatient clinics), "
        f"(2) different geographic regions with varying population demographics and care practices, "
        f"(3) international databases to assess cross-border applicability."
    )

    # Demographic representativeness
    representativeness_parts.append(
        f"**Demographic Coverage:** Assess representativeness by comparing cohort demographics against target deployment population. "
        f"Key considerations: (1) Age distribution - ensure adequate representation across age strata relevant for COPD (typically 40+ years), "
        f"(2) Gender balance - verify sufficient representation of both genders given sex differences in COPD presentation, "
        f"(3) Race/ethnicity - validate performance across racial/ethnic subgroups, particularly underrepresented minorities, "
        f"(4) Socioeconomic factors - consider healthcare access disparities and social determinants of health."
    )

    # Temporal representativeness
    representativeness_parts.append(
        f"**Temporal Validity:** Verify that cohort observation period aligns with current clinical practice. "
        f"Consider: (1) Changes in diagnostic criteria for COPD since cohort creation, "
        f"(2) Evolution of treatment guidelines and medication formularies, "
        f"(3) Impact of policy changes (e.g., smoking regulations) on COPD epidemiology, "
        f"(4) Healthcare delivery changes (e.g., telemedicine adoption). "
        f"Recommend periodic model retraining on contemporary data."
    )

    # Clinical representativeness
    representativeness_parts.append(
        f"**Clinical Spectrum:** Cohort phenotype defined by specific OMOP concept sets. "
        f"Ensure target population matches inclusion/exclusion criteria. "
        f"Model performance may vary for: (1) COPD severity not well-represented in training data, "
        f"(2) Comorbidity profiles differing from cohort, "
        f"(3) Medication regimens not captured during training period."
    )

    data_representativeness = "\n\n".join(representativeness_parts)

    # Generate comprehensive data governance statement
    data_governance = (
        f"Data access: OMOP CDM database accessed via OHDSI WebAPI with institutional data use agreements. "
        f"Ethics approval: Cohort extraction performed under institutional IRB protocol for observational research using de-identified EHR data. "
        f"De-identification: OMOP CDM de-identification standards applied conforming to HIPAA Safe Harbor method (removal of 18 PHI identifiers including dates, geographic subdivisions, patient identifiers). "
        f"Consent: Waiver of informed consent granted for secondary use of de-identified observational data. "
        f"Data security: Access controlled through authenticated OHDSI WebAPI endpoints; data transferred via encrypted connections. "
        f"Audit trail: Cohort definition versioned in ATLAS; generation logs maintained for reproducibility."
    )

    card.set_data_factors(DataFactors(
        concept_sets=concept_sets,
        primary_cohort_criteria=cohort_criteria,
        source_datasets=[source_dataset],
        data_distribution_summary=data_distribution,
        data_representativeness=data_representativeness,
        data_governance=data_governance
    ))

    # Section 4: Features & Outputs
    card.set_features_outputs(FeaturesOutputs(
        input_features=[
            InputFeature(
                name="age_at_index",
                data_type="numeric",
                required=True,
                clinical_domain="Demographics",
                value_range="40-90",
                units="years"
            ),
            InputFeature(
                name="gender_concept_id",
                data_type="categorical",
                required=True,
                clinical_domain="Demographics",
                value_range="OMOP gender concepts (8507, 8532)"
            ),
            InputFeature(
                name="copd_severity_indicator",
                data_type="categorical",
                required=True,
                clinical_domain="Clinical History",
                value_range="Mild, Moderate, Severe (derived from OMOP concepts)"
            ),
            InputFeature(
                name="prior_exacerbation_count",
                data_type="numeric",
                required=True,
                clinical_domain="Clinical History",
                value_range="0-10",
                units="count"
            ),
            InputFeature(
                name="medication_adherence_score",
                data_type="numeric",
                required=False,
                clinical_domain="Medication History",
                value_range="0.0-1.0",
                units="proportion"
            )
        ],
        output_features=[
            OutputFeature(
                name="exacerbation_risk_12mo",
                type="probability",
                units="probability",
                value_range="0.0-1.0"
            ),
            OutputFeature(
                name="risk_tier",
                type="classification",
                classes=["Low", "Medium", "High"]
            )
        ],
        feature_type_distribution="5 input features: 3 numeric, 2 categorical. All derived from OMOP CDM standard tables (person, condition_occurrence, drug_exposure).",
        uncertainty_quantification="Prediction intervals via quantile regression. Calibrated probability scores with Platt scaling.",
        output_interpretability="SHAP values provided for each prediction. Risk tier based on validated thresholds aligned with clinical guidelines."
    ))

    # Section 5: Performance & Validation
    card.set_performance_validation(PerformanceValidation(
        validation_datasets=[
            ValidationDataset(
                name="KAGGLECOPD Holdout Set",
                source_institution="Same as training (temporal split)",
                population_characteristics=f"n={int(source_dataset.size * 0.2)}, 2023 data",
                validation_type="Internal temporal holdout"
            )
        ],
        claimed_metrics=[
            PerformanceMetric("AUC-ROC", 0.82, "Claimed (Internal)"),
            PerformanceMetric("Sensitivity", 0.75, "Claimed (Internal)"),
            PerformanceMetric("Specificity", 0.79, "Claimed (Internal)")
        ],
        validated_metrics=[
            PerformanceMetric("AUC-ROC", 0.80, "Internally Validated", "Overall"),
            PerformanceMetric("Calibration Slope", 0.96, "Internally Validated", "Overall")
        ],
        calibration_analysis="Calibration slope 0.96 on holdout set. Hosmer-Lemeshow test p=0.38 indicates good calibration. Calibration plot shows agreement across deciles.",
        fairness_assessment="Performance evaluated across gender subgroups. No significant disparity detected (AUC difference <0.03). Additional external validation recommended for diverse populations.",
        metric_validation_status="All metrics validated on temporal holdout set. External validation in progress at partner institutions."
    ))

    # Section 6: Methodology
    card.set_methodology(Methodology(
        model_development_workflow="OMOP CDM data extraction → Feature engineering from OMOP tables → Cohort definition using ATLAS → Train/validation split → Model training → Calibration → SHAP analysis",
        training_procedure="Random Forest with 300 trees, max depth 8, class balancing. Training on OMOP-derived features. Hyperparameters tuned via 5-fold cross-validation. Training time: 8 minutes on 16-core CPU.",
        data_preprocessing="OMOP concept standardization applied. Missing values imputed using median (numeric) and mode (categorical). Temporal train-test split to prevent leakage. Feature scaling with standard normalization.",
        synthetic_data_usage="No synthetic data used in training. Model reproducibility validated using MedSynth synthetic OMOP data (n=500) for testing pipeline.",
        explainable_ai_method="SHAP (SHapley Additive exPlanations) for feature importance. TreeExplainer used for Random Forest. Individual prediction explanations with force plots.",
        global_vs_local_interpretability="Global: SHAP summary plots, feature importance ranking. Local: Per-patient SHAP values showing contribution of each OMOP-derived feature to risk prediction."
    ))

    # Section 7: Additional Information
    card.set_additional_info(AdditionalInfo(
        benefit_risk_summary="Benefits: Early risk stratification enables proactive intervention. Risks: Over-reliance may miss atypical cases. Net benefit analysis positive for risk thresholds 15-70%.",
        post_market_surveillance_plan="Quarterly monitoring of prediction performance. Alert if AUC drops >0.05 or calibration slope <0.90. Annual retraining on updated OMOP data. Feedback mechanism for clinical users.",
        ethical_considerations="Model trained using OMOP CDM ensuring standardized data representation. No direct use of protected attributes. Fairness across demographics validated. Transparent documentation for regulatory review.",
        caveats_limitations="Trained on single database (KAGGLECOPD). Performance on other OMOP instances requires validation. Limited to COPD patients with sufficient observation history. Not validated for post-transplant or end-stage disease.",
        recommendations_for_safe_use="1) Verify OMOP vocabulary mappings in local database. 2) Validate calibration on local population. 3) Use as decision support, not replacement for clinical judgment. 4) Monitor for concept drift. 5) Ensure OMOP CDM version compatibility (v5.x).",
        explainability_recommendations="Display SHAP feature contributions alongside risk score. Highlight OMOP concept IDs and names for transparency. Provide link to cohort definition in ATLAS for reproducibility.",
        supporting_documents=[
            "OMOP Cohort Definition (ATLAS JSON)",
            "OHDSI Methods Validation Report",
            "Model Technical Specification",
            "SHAP Analysis Results",
            "Fairness Assessment Report"
        ]
    ))

    return card


def main():
    """Run demo: Create model card with real OMOP data"""

    print("=" * 70)
    print("DEMO: Creating Model Card with Real smart-omop Data")
    print("=" * 70)

    # Fetch real OMOP cohort data
    cohort_definition, cohort_results = fetch_omop_cohort_data()

    if cohort_definition is None:
        print("\nFailed to fetch OMOP data. Cannot create model card.")
        print("Please ensure:")
        print("1. smart-omop is installed: pip install smart-omop")
        print("2. Network connectivity to OMOP WebAPI")
        return

    # Create model card using OMOP data
    card = create_model_card_with_omop_data(cohort_definition, cohort_results)

    # Export to multiple formats
    print("\nExporting model card...")

    json_path = JSONExporter.export(card, "./output/omop_demo_model_card.json")
    print(f"✓ JSON exported: {json_path}")

    html_path = HTMLExporter.export(card, "./output/omop_demo_model_card.html")
    print(f"✓ HTML exported: {html_path}")

    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print(f"\nModel card created using real OMOP cohort:")
    print(f"  Cohort: {cohort_definition.get('name', 'Unknown')}")
    if cohort_results:
        print(f"  Persons: {cohort_results.get('personCount', 'N/A')}")
    print(f"\nOpen HTML file to view: {html_path}")
    print("\nKey Features Demonstrated:")
    print("  ✓ Real OMOP cohort definition integration")
    print("  ✓ Automatic concept set extraction")
    print("  ✓ Cohort criteria from OMOP expression")
    print("  ✓ Standardized vocabulary documentation")
    print("  ✓ Reproducible model card generation")


if __name__ == "__main__":
    main()
