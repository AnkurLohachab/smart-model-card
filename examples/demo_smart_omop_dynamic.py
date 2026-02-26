"""
Demo: Dynamic smart-omop Integration with Full Report Support

Demonstrates creating a model card using OMOP data with dynamic report parsing.
Uses person, dashboard, condition, and other reports from smart-omop CLI.

Usage:
    1. Create cohort: smart-omop --base-url <url> create-cohort --name "COPD Patients" --concept-ids 255573 --age-gte 40
    2. Generate: smart-omop --base-url <url> generate --cohort-id <id> --source-key KAGGLECOPD
    3. Run Heracles: smart-omop --base-url <url> heracles --cohort-id <id> --source-key KAGGLECOPD
    4. Export reports: smart-omop --base-url <url> export-reports --cohort-id <id> --source-key KAGGLECOPD --output-dir ./reports
    5. Run this script

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
from smart_model_card.omop_reports import OMOPReportParser, load_reports_from_directory

# Import smart-omop
try:
    from smart_omop import OMOPClient
    SMART_OMOP_AVAILABLE = True
except ImportError:
    SMART_OMOP_AVAILABLE = False
    print("Warning: smart-omop not installed. Install with: pip install smart-omop")


BASE_URL = "http://ec2-13-49-5-87.eu-north-1.compute.amazonaws.com:8080/WebAPI"


def fetch_omop_data_with_reports(cohort_id: int, reports_dir: str = "./output"):
    """Fetch OMOP cohort data and load Heracles reports"""
    if not SMART_OMOP_AVAILABLE:
        return None, None, None

    print(f"Fetching OMOP cohort {cohort_id} with reports...")

    try:
        with OMOPClient(BASE_URL) as client:
            # Fetch cohort definition
            cohort_definition = client.get_cohort(cohort_id=cohort_id)
            print(f"✓ Fetched cohort: {cohort_definition.get('name', 'Unknown')}")

            # Get cohort results
            try:
                cohort_results = client.get_cohort_results(
                    cohort_id=cohort_id,
                    source_key="KAGGLECOPD"
                )
                print(f"✓ Person count: {cohort_results.get('personCount', 'N/A')}")
            except Exception as e:
                print(f"  Note: Could not fetch results: {e}")
                cohort_results = None

            # Load Heracles reports from directory
            print(f"\nLoading Heracles reports from {reports_dir}...")
            report_parser = load_reports_from_directory(reports_dir)

            if report_parser.person_report:
                print("✓ Loaded person demographics report")
            if report_parser.dashboard_report:
                print("✓ Loaded dashboard report")
            if report_parser.condition_report:
                print("✓ Loaded condition report")
            if report_parser.drug_report:
                print("✓ Loaded drug report")

            return cohort_definition, cohort_results, report_parser

    except Exception as e:
        print(f"Error fetching OMOP data: {e}")
        return None, None, None


def create_model_card_with_dynamic_reports(cohort_definition, cohort_results, report_parser):
    """Create model card using dynamic report parsing"""

    print("\nCreating model card with dynamic OMOP reports...")

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
        version="2.0.0",
        developer_organization="Department of Advanced Computing Sciences, Maastricht University",
        release_date="2025-01-15",
        description="Machine learning model for predicting COPD exacerbation risk using OMOP CDM data with comprehensive Heracles characterization. Trained on real-world EHR data with standardized OMOP vocabulary.",
        clinical_function="decision_support",
        algorithms_used="Random Forest Classifier with SHAP explainability",
        gmdn_code="62948",
        licensing="MIT License",
        support_contact="ankur.lohachab@maastrichtuniversity.nl",
        literature_references=[
            "OMOP Common Data Model specification v5.4",
            "OHDSI Methods Library for observational research",
            "OHDSI Heracles: Characterization of observational datasets"
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

    # Section 3: Data & Factors with Dynamic Reports
    # Generate comprehensive data distribution using reports
    person_count = cohort_results.get('personCount', 0) if cohort_results else 0

    # Build concept sets description
    concept_sets_info = ""
    if concept_sets:
        total_concepts = sum(len(cs.concept_ids) for cs in concept_sets)
        cs_details = []
        for cs in concept_sets:
            cs_details.append(f"{cs.name} ({len(cs.concept_ids)} concept{'s' if len(cs.concept_ids) != 1 else ''})")
        concept_sets_info = f"{len(concept_sets)} concept set{'s' if len(concept_sets) > 1 else ''} used: {'; '.join(cs_details)}. Total {total_concepts} OMOP standard concept IDs."

    # Use report parser to generate dynamic data distribution
    data_distribution = report_parser.generate_data_distribution_summary(
        cohort_size=person_count,
        concept_sets_info=concept_sets_info
    )

    print(f"✓ Generated dynamic data distribution with {len(data_distribution)} metrics")

    # Data representativeness
    source_name = cohort_definition.get('name', 'COPD cohort')
    representativeness_parts = []

    representativeness_parts.append(
        f"**Data Source:** KAGGLECOPD database accessed via OMOP CDM v5.x through OHDSI WebAPI. "
        f"The '{source_name}' cohort (n={person_count}) represents patients meeting standardized inclusion criteria defined using OMOP concept sets. "
        f"Demographics characterized using OHDSI Heracles analyses."
    )

    representativeness_parts.append(
        f"**Geographic Scope:** Single healthcare database. Generalizability to other geographic regions and healthcare systems requires external validation. "
        f"Recommend validation across: (1) diverse healthcare settings (academic medical centers, community hospitals, outpatient clinics), "
        f"(2) different geographic regions with varying population demographics and care practices, "
        f"(3) international databases to assess cross-border applicability."
    )

    representativeness_parts.append(
        f"**Demographic Coverage:** Demographics extracted from Heracles characterization provide detailed population statistics. "
        f"Key validation steps: (1) Compare age distribution against target deployment population, "
        f"(2) Verify gender representation matches clinical setting, "
        f"(3) Assess race/ethnicity distribution for potential biases, "
        f"(4) Consider socioeconomic factors and healthcare access disparities."
    )

    representativeness_parts.append(
        f"**Temporal Validity:** Verify that cohort observation period aligns with current clinical practice. "
        f"Monitor for: (1) Changes in diagnostic criteria, "
        f"(2) Evolution of treatment guidelines, "
        f"(3) Healthcare delivery changes. "
        f"Periodic retraining recommended."
    )

    data_representativeness = "\n\n".join(representativeness_parts)

    # Data governance
    data_governance = (
        f"**Data Access:** OMOP CDM database accessed via OHDSI WebAPI with institutional data use agreements. "
        f"**Ethics:** Cohort extraction performed under institutional IRB protocol for observational research using de-identified EHR data. "
        f"**De-identification:** OMOP CDM de-identification standards applied conforming to HIPAA Safe Harbor method. "
        f"**Consent:** Waiver granted for secondary use of de-identified data. "
        f"**Security:** Access controlled through authenticated OHDSI WebAPI endpoints; encrypted data transfer. "
        f"**Audit:** Cohort definition versioned in ATLAS; Heracles characterization results archived for reproducibility."
    )

    # Get all detailed reports for interactive display
    detailed_reports = report_parser.get_all_detailed_reports()
    print(f"✓ Prepared detailed reports for {len(detailed_reports)} report types")

    card.set_data_factors(DataFactors(
        concept_sets=concept_sets,
        primary_cohort_criteria=cohort_criteria,
        source_datasets=[source_dataset],
        data_distribution_summary=data_distribution,  # Summary for quick view
        data_representativeness=data_representativeness,
        data_governance=data_governance,
        omop_detailed_reports=detailed_reports  # Detailed reports for interactive tabs
    ))

    # Sections 4-7 (abbreviated for brevity)
    card.set_features_outputs(FeaturesOutputs(
        input_features=[
            InputFeature(name="age_at_index", data_type="numeric", required=True,
                        clinical_domain="Demographics", value_range="40-90", units="years"),
            InputFeature(name="gender_concept_id", data_type="categorical", required=True,
                        clinical_domain="Demographics", value_range="OMOP gender concepts"),
            InputFeature(name="copd_severity", data_type="categorical", required=True,
                        clinical_domain="Clinical History", value_range="Mild/Moderate/Severe")
        ],
        output_features=[
            OutputFeature(name="exacerbation_risk_12mo", type="probability",
                         units="probability", value_range="0.0-1.0"),
            OutputFeature(name="risk_tier", type="classification",
                         classes=["Low", "Medium", "High"])
        ],
        feature_type_distribution="3 input features derived from OMOP CDM tables (person, condition_occurrence)",
        uncertainty_quantification="Calibrated probability scores with Platt scaling",
        output_interpretability="SHAP values for each prediction"
    ))

    card.set_performance_validation(PerformanceValidation(
        validation_datasets=[
            ValidationDataset(
                name="KAGGLECOPD Holdout Set",
                source_institution="Same as training (temporal split)",
                population_characteristics=f"n={int(person_count * 0.2)}, 2023 data",
                validation_type="Internal temporal holdout"
            )
        ],
        claimed_metrics=[
            PerformanceMetric("AUC-ROC", 0.82, "Claimed (Internal)"),
            PerformanceMetric("Sensitivity", 0.75, "Claimed (Internal)")
        ],
        validated_metrics=[
            PerformanceMetric("AUC-ROC", 0.80, "Internally Validated", "Overall")
        ],
        calibration_analysis="Calibration slope 0.96 on holdout set",
        fairness_assessment="Performance evaluated across gender subgroups from Heracles data",
        metric_validation_status="All metrics validated on temporal holdout set"
    ))

    card.set_methodology(Methodology(
        model_development_workflow="OMOP CDM extraction → Heracles characterization → Feature engineering → Training",
        training_procedure="Random Forest with 300 trees, hyperparameter tuning via 5-fold CV",
        data_preprocessing="OMOP concept standardization, missing value imputation, temporal train-test split",
        synthetic_data_usage="No synthetic data",
        explainable_ai_method="SHAP (SHapley Additive exPlanations)",
        global_vs_local_interpretability="Global: SHAP summary plots. Local: Per-patient SHAP values"
    ))

    card.set_additional_info(AdditionalInfo(
        benefit_risk_summary="Benefits: Early risk stratification. Risks: Over-reliance may miss atypical cases",
        post_market_surveillance_plan="Quarterly performance monitoring with alerts",
        ethical_considerations="OMOP CDM standardization, fairness validated across demographics",
        caveats_limitations="Single database (KAGGLECOPD), requires validation on other OMOP instances",
        recommendations_for_safe_use="1) Verify OMOP mappings 2) Validate local calibration 3) Use as decision support",
        explainability_recommendations="Display SHAP values with predictions",
        supporting_documents=[
            "OMOP Cohort Definition (ATLAS JSON)",
            "Heracles Characterization Results",
            "OHDSI Methods Validation Report"
        ]
    ))

    return card


def main():
    """Run demo with dynamic reports"""

    print("=" * 70)
    print("DEMO: smart-omop Dynamic Reports Integration")
    print("=" * 70)

    # Use cohort 168 that we just created
    cohort_id = 168

    # Fetch OMOP data and load reports
    cohort_definition, cohort_results, report_parser = fetch_omop_data_with_reports(
        cohort_id=cohort_id,
        reports_dir="./output"
    )

    if not cohort_definition:
        print("\nFailed to fetch OMOP data.")
        return

    if not report_parser.person_report:
        print("\n⚠ Warning: No person report found!")
        print("   Run: smart-omop --base-url <url> get-report --cohort-id 168 --source-key KAGGLECOPD --type person --output ./output/person_report.json")
        print("   Continuing with basic data...")

    # Create model card
    card = create_model_card_with_dynamic_reports(cohort_definition, cohort_results, report_parser)

    # Export
    print("\nExporting model card...")
    json_path = JSONExporter.export(card, "./output/dynamic_model_card.json")
    print(f"✓ JSON exported: {json_path}")

    html_path = HTMLExporter.export(card, "./output/dynamic_model_card.html")
    print(f"✓ HTML exported: {html_path}")

    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print(f"\nModel card created with dynamic report parsing")
    print(f"  Cohort: {cohort_definition.get('name')}")
    if cohort_results:
        print(f"  Persons: {cohort_results.get('personCount')}")
    print(f"\nOpen HTML: {html_path}")


if __name__ == "__main__":
    main()
