"""
Interactive CLI for guided model card creation

Author: Ankur Lohachab
Department of Advanced Computing Sciences, Maastricht University
"""

import sys
import re
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from smart_model_card import ModelCard, ModelDetails, IntendedUse
from smart_model_card.sections import (
    DataFactors, FeaturesOutputs, PerformanceValidation,
    Methodology, AdditionalInfo, SourceDataset, InputFeature,
    OutputFeature, ValidationDataset, PerformanceMetric
)
from smart_model_card.exporters import HTMLExporter, JSONExporter
from smart_model_card.templates import quick_card, TEMPLATES, REGULATORY_PRESETS


def validate_date(date_str: str) -> bool:
    """Validate date in YYYY-MM-DD format"""
    if not date_str:
        return True

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return True

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_numeric_range(value: float, min_val: Optional[float] = None, max_val: Optional[float] = None) -> bool:
    """Validate numeric value is within range"""
    if min_val is not None and value < min_val:
        return False
    if max_val is not None and value > max_val:
        return False
    return True


def prompt_input(prompt: str, required: bool = True, default: Optional[str] = None, validator=None, validator_msg: str = "Invalid input format") -> str:
    """Prompt user for input with optional default and validation"""
    if default:
        prompt = f"{prompt} [{default}]"

    while True:
        value = input(f"  {prompt}: ").strip()

        if not value and default:
            return default

        if not value and not required:
            return ""

        if not value and required:
            print("  ⚠ This field is required. Please provide a value.")
            continue

        if validator and not validator(value):
            print(f"  ⚠ {validator_msg}")
            continue

        return value


def prompt_choice(prompt: str, choices: List[str]) -> str:
    """Prompt user to select from choices with retry limit"""
    print(f"\n  {prompt}")
    for i, choice in enumerate(choices, 1):
        print(f"    {i}. {choice}")

    max_retries = 5
    retries = 0

    while retries < max_retries:
        selection = input("  Select number: ").strip()
        try:
            idx = int(selection) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
            else:
                print(f"  ⚠ Please enter a number between 1 and {len(choices)}.")
        except ValueError:
            print(f"  ⚠ Please enter a valid number (1-{len(choices)}).")

        retries += 1
        if retries < max_retries:
            print(f"  (Attempt {retries + 1}/{max_retries})")

    print(f"  ⚠ Too many invalid attempts. Using default: {choices[0]}")
    return choices[0]


def prompt_yes_no(prompt: str, default: bool = False) -> bool:
    """Prompt yes/no question"""
    default_str = "Y/n" if default else "y/N"
    response = input(f"  {prompt} [{default_str}]: ").strip().lower()

    if not response:
        return default

    return response in ['y', 'yes']


def prompt_float(prompt: str, required: bool = True, min_val: Optional[float] = None, max_val: Optional[float] = None) -> Optional[float]:
    """Prompt for float value with optional range validation"""
    while True:
        value = input(f"  {prompt}: ").strip()

        if not value and not required:
            return None

        if not value and required:
            print("  ⚠ This field is required.")
            continue

        try:
            num = float(value)
            if not validate_numeric_range(num, min_val, max_val):
                range_msg = ""
                if min_val is not None and max_val is not None:
                    range_msg = f"between {min_val} and {max_val}"
                elif min_val is not None:
                    range_msg = f"greater than or equal to {min_val}"
                elif max_val is not None:
                    range_msg = f"less than or equal to {max_val}"
                print(f"  ⚠ Value must be {range_msg}.")
                continue
            return num
        except ValueError:
            print("  ⚠ Please enter a valid number.")


def prompt_int(prompt: str, required: bool = True, min_val: Optional[int] = None, max_val: Optional[int] = None) -> Optional[int]:
    """Prompt for integer value with optional range validation"""
    while True:
        value = input(f"  {prompt}: ").strip()

        if not value and not required:
            return None

        if not value and required:
            print("  ⚠ This field is required.")
            continue

        try:
            num = int(value)
            if not validate_numeric_range(num, min_val, max_val):
                range_msg = ""
                if min_val is not None and max_val is not None:
                    range_msg = f"between {min_val} and {max_val}"
                elif min_val is not None:
                    range_msg = f"greater than or equal to {min_val}"
                elif max_val is not None:
                    range_msg = f"less than or equal to {max_val}"
                print(f"  ⚠ Value must be {range_msg}.")
                continue
            return num
        except ValueError:
            print("  ⚠ Please enter a valid integer.")


def prompt_omop_integration() -> Optional[Dict[str, Any]]:
    """Prompt for OMOP data integration with improved workflow"""
    print("\n" + "-"*60)
    print("OMOP CDM Integration (Optional)")
    print("-"*60)
    print("You can integrate OMOP Common Data Model cohort data.")
    print("This requires smart-omop package and OHDSI WebAPI access.")

    if not prompt_yes_no("Would you like to add OMOP data?", default=False):
        return None

    try:
        from smart_model_card.integrations import OMOPIntegration
        from smart_omop import CohortBuilder

        print("\n  Choose integration method:")
        print("    1. Fetch existing cohort from OHDSI WebAPI")
        print("    2. Create new cohort from scratch")
        print("    3. Use locally saved cohort data")

        max_retries = 5
        retries = 0
        choice_idx = -1

        while retries < max_retries:
            selection = input("  Select number: ").strip()
            try:
                choice_idx = int(selection) - 1
                if 0 <= choice_idx < 3:
                    break
                print(f"  Please enter a number between 1 and 3")
                retries += 1
            except ValueError:
                print(f"  Please enter a valid number")
                retries += 1

        if retries >= max_retries or choice_idx == -1:
            print("  Too many invalid attempts. Skipping OMOP integration.")
            return None

        if choice_idx == 0:
            return _fetch_existing_cohort()

        elif choice_idx == 1:
            return _create_new_cohort()

        else:
            print("\n  For local OMOP data, you can manually add it after creation.")
            print("  Skipping OMOP integration for now.")
            return None

    except ImportError:
        print("\n  ⚠ OMOP integration requires 'smart-omop' package.")
        print("  Install it with: pip install smart-omop")
        print("  Skipping OMOP integration.")
        return None
    except Exception as e:
        print(f"\n  ⚠ Unexpected error: {e}")
        print("  Skipping OMOP integration.")
        return None


def _fetch_existing_cohort() -> Optional[Dict[str, Any]]:
    """Fetch existing cohort from WebAPI"""
    from smart_model_card.integrations import OMOPIntegration
    from smart_omop import OMOPClient

    max_url_retries = 3
    sources = None
    selected_source = None
    cohort_id = None
    include_heracles = True
    webapi_url = None

    for url_attempt in range(max_url_retries):
        webapi_url = prompt_input("\n  OHDSI WebAPI URL (e.g., https://your-atlas.org/WebAPI)", required=True)

        print("\n  Connecting to OHDSI WebAPI...")

        try:
            with OMOPClient(webapi_url) as client:
                print("  Fetching available CDM sources...")
                sources = client.get_sources()

                if not sources:
                    print("  ⚠ No CDM sources found on this WebAPI.")
                    print("  Please check your WebAPI URL or contact your administrator.")

                    if url_attempt < max_url_retries - 1:
                        if prompt_yes_no("\n  Retry with different URL?", default=True):
                            continue
                        else:
                            return None
                    else:
                        return None

                print(f"\n  Available CDM sources ({len(sources)}):")
                for i, source in enumerate(sources, 1):
                    source_key = source.get('sourceKey', 'Unknown')
                    source_name = source.get('sourceName', 'Unknown')
                    print(f"    {i}. {source_key} - {source_name}")

                max_retries = 5
                retries = 0
                selected_source = None

                while retries < max_retries:
                    selection = input(f"\n  Select source number (1-{len(sources)}): ").strip()
                    try:
                        source_idx = int(selection) - 1
                        if 0 <= source_idx < len(sources):
                            selected_source = sources[source_idx]
                            break
                        print(f"  Please enter a number between 1 and {len(sources)}")
                        retries += 1
                    except ValueError:
                        print(f"  Please enter a valid number")
                        retries += 1

                if retries >= max_retries or not selected_source:
                    print("  Too many invalid attempts. Skipping OMOP integration.")
                    return None

                source_key = selected_source['sourceKey']
                print(f"\n  Selected source: {source_key}")

                cohort_id = prompt_int("\n  Cohort ID", required=True, min_val=1)

                include_heracles = prompt_yes_no("\n  Include Heracles characterization reports?", default=True)

                break

        except Exception as e:
            print(f"\n  ⚠ Error connecting to WebAPI: {e}")
            print("  Please check your WebAPI URL and network connection.")

            if url_attempt < max_url_retries - 1:
                if prompt_yes_no("\n  Retry with different URL?", default=True):
                    continue
                else:
                    return None
            else:
                print("  Maximum connection attempts reached.")
                return None

    if not sources or not selected_source or cohort_id is None or webapi_url is None:
        return None

    try:
        print("\n  Fetching cohort data...")

        with OMOPIntegration(webapi_url=webapi_url, source_key=source_key) as integration:
            cohort_data = integration.get_cohort_with_reports(
                cohort_id=cohort_id,
                include_heracles=include_heracles
            )

        print(f"\n  ✓ Successfully fetched cohort: {cohort_data.get('name', 'Unknown')}")
        return cohort_data

    except Exception as e:
        print(f"\n  ⚠ Error fetching cohort: {e}")

        if "does not exist" in str(e).lower():
            print(f"\n  Cohort ID {cohort_id} was not found.")
            print(f"  Suggestions:")
            print(f"    - Check the cohort ID in ATLAS web interface")
            print(f"    - Use smart-omop CLI to list available cohorts")
        elif "heracles" in str(e).lower():
            print(f"\n  Heracles reports may not be available for this cohort.")
            print(f"  You can:")
            print(f"    - Run Heracles analysis first using smart-omop CLI")
            print(f"    - Retry without Heracles reports")

        return None


def _create_new_cohort() -> Optional[Dict[str, Any]]:
    """Create new cohort from scratch"""
    from smart_model_card.integrations import OMOPIntegration
    from smart_omop import OMOPClient, CohortBuilder

    print("\n  Creating new cohort from scratch")

    max_url_retries = 3
    sources = None
    selected_source = None
    webapi_url = None

    for url_attempt in range(max_url_retries):
        webapi_url = prompt_input("\n  OHDSI WebAPI URL (e.g., https://your-atlas.org/WebAPI)", required=True)

        print("\n  Connecting to OHDSI WebAPI...")

        try:
            with OMOPClient(webapi_url) as client:
                print("  Fetching available CDM sources...")
                sources = client.get_sources()

                if not sources:
                    print("  ⚠ No CDM sources found on this WebAPI.")

                    if url_attempt < max_url_retries - 1:
                        if prompt_yes_no("\n  Retry with different URL?", default=True):
                            continue
                        else:
                            return None
                    else:
                        return None

                print(f"\n  Available CDM sources ({len(sources)}):")
                for i, source in enumerate(sources, 1):
                    source_key = source.get('sourceKey', 'Unknown')
                    source_name = source.get('sourceName', 'Unknown')
                    print(f"    {i}. {source_key} - {source_name}")

                max_retries = 5
                retries = 0
                selected_source = None

                while retries < max_retries:
                    selection = input(f"\n  Select source number (1-{len(sources)}): ").strip()
                    try:
                        source_idx = int(selection) - 1
                        if 0 <= source_idx < len(sources):
                            selected_source = sources[source_idx]
                            break
                        print(f"  Please enter a number between 1 and {len(sources)}")
                        retries += 1
                    except ValueError:
                        print(f"  Please enter a valid number")
                        retries += 1

                if retries >= max_retries or not selected_source:
                    print("  Too many invalid attempts. Skipping OMOP integration.")
                    return None

                source_key = selected_source['sourceKey']
                print(f"\n  Selected source: {source_key}")

                break

        except Exception as e:
            print(f"\n  ⚠ Error connecting to WebAPI: {e}")
            print("  Please check your WebAPI URL and network connection.")

            if url_attempt < max_url_retries - 1:
                if prompt_yes_no("\n  Retry with different URL?", default=True):
                    continue
                else:
                    return None
            else:
                print("  Maximum connection attempts reached.")
                return None

    if not sources or not selected_source or webapi_url is None:
        return None

    print("\n  Define your cohort:")
    cohort_name = prompt_input("  Cohort name", required=True)
    cohort_description = prompt_input("  Description", required=False)

    print("\n  Inclusion criteria:")
    concept_ids_str = prompt_input("  Concept IDs (comma-separated, e.g., 255573)", required=True)
    concept_ids = [int(x.strip()) for x in concept_ids_str.split(",") if x.strip().isdigit()]

    if not concept_ids:
        print("  ⚠ No valid concept IDs provided. Cannot create cohort.")
        return None

    min_age = prompt_input("  Minimum age (leave empty for no limit)", required=False)
    max_age = prompt_input("  Maximum age (leave empty for no limit)", required=False)

    gender = prompt_input("  Gender filter (M/F/leave empty for all)", required=False)

    print("\n  Creating cohort definition...")

    try:
        from smart_omop import Gender

        with OMOPClient(webapi_url) as client:
            builder = CohortBuilder(cohort_name)

            if cohort_description:
                builder.description = cohort_description

            builder.with_condition("Conditions", concept_ids)

            min_age_int = int(min_age) if min_age and min_age.isdigit() else None
            max_age_int = int(max_age) if max_age and max_age.isdigit() else None

            if min_age_int is not None or max_age_int is not None:
                builder.with_age_range(min_age=min_age_int, max_age=max_age_int)

            if gender and gender.upper() in ['M', 'F']:
                gender_enum = Gender.MALE if gender.upper() == 'M' else Gender.FEMALE
                builder.with_gender(gender_enum)

            cohort_def = builder.build()
            created_cohort = client.create_cohort(cohort_def.to_dict())
            cohort_id = created_cohort.get('id')

            print(f"  ✓ Cohort created with ID: {cohort_id}")

            if prompt_yes_no("\n  Generate cohort on database now?", default=True):
                print("  Generating cohort...")
                client.generate_cohort(cohort_id, source_key)
                print("  ✓ Cohort generation started (may take a few minutes)")

                import time
                time.sleep(5)

                try:
                    include_heracles = prompt_yes_no("\n  Include Heracles characterization reports?", default=False)

                    if include_heracles:
                        print("  Note: Heracles reports may not be available immediately.")
                        print("  You may need to run Heracles analysis separately.")

                    with OMOPIntegration(webapi_url=webapi_url, source_key=source_key) as integration:
                        cohort_data = integration.get_cohort_with_reports(
                            cohort_id=cohort_id,
                            include_heracles=include_heracles
                        )

                    print(f"\n  ✓ Successfully fetched cohort: {cohort_data.get('name', 'Unknown')}")
                    return cohort_data

                except Exception as e:
                    print(f"\n  ⚠ Cohort created but couldn't fetch results yet: {e}")
                    print(f"  The cohort may still be generating.")
                    print(f"  You can retry later with cohort ID: {cohort_id}")
                    return None

            else:
                print(f"\n  Cohort created but not generated.")
                print(f"  To generate later, use:")
                print(f"    smart-omop --base-url {webapi_url} generate --cohort-id {cohort_id} --source-key {source_key}")
                return None

    except Exception as e:
        print(f"\n  ⚠ Error creating cohort: {e}")
        import traceback
        traceback.print_exc()
        return None


def section_model_details() -> ModelDetails:
    """Guided input for Section 1: Model Details"""
    print("\n" + "="*60)
    print("[Section 1/7] Model Details")
    print("="*60)

    clinical_function = prompt_choice(
        "Clinical Function",
        ["decision_support", "screening", "diagnosis", "triage", "monitoring", "workflow_support", "other"]
    )
    intended_purpose = prompt_input(
        "Intended Purpose - free-text regulatory statement (optional)",
        required=False
    ) or None
    info_sig_input = prompt_input(
        "Information Significance (inform / drive / treat_or_diagnose) (optional)",
        required=False
    )
    information_significance = info_sig_input if info_sig_input in ("inform", "drive", "treat_or_diagnose") else None
    basic_udi_di = prompt_input("Basic UDI-DI (optional)", required=False) or None
    udi_di = prompt_input("UDI-DI (optional)", required=False) or None

    regulatory_classifications = []
    if prompt_yes_no("Add regulatory classifications?"):
        while True:
            framework = prompt_input("  Framework (e.g., EU MDR, FDA, EU AI Act)", required=True)
            reg_class = prompt_input("  Class (e.g., IIa, II, high-risk)", required=True)
            rule = prompt_input("  Rule (optional)", required=False) or None
            pathway = prompt_input("  Pathway (optional)", required=False) or None
            entry = {"framework": framework, "class": reg_class}
            if rule:
                entry["rule"] = rule
            if pathway:
                entry["pathway"] = pathway
            regulatory_classifications.append(entry)
            if not prompt_yes_no("Add another classification?"):
                break

    return ModelDetails(
        model_name=prompt_input("Model Name (e.g., COPD-Risk-Predictor-v2)", required=True),
        version=prompt_input("Version", default="1.0.0"),
        developer_organization=prompt_input("Developer/Organization (e.g., University Hospital Research Lab)", required=True),
        release_date=prompt_input(
            "Release Date (YYYY-MM-DD)",
            required=False,
            validator=validate_date,
            validator_msg="Please enter a valid date in YYYY-MM-DD format (e.g., 2025-01-15)"
        ),
        description=prompt_input("Description (e.g., Predicts 5-year diabetes risk using EHR data)", required=True),
        clinical_function=clinical_function,
        intended_purpose=intended_purpose,
        information_significance=information_significance,
        algorithms_used=prompt_input("Algorithm(s) Used (e.g., XGBoost Classifier, Random Forest)", required=True),
        licensing=prompt_input("License", default="MIT"),
        support_contact=prompt_input(
            "Support Contact (email)",
            required=True,
            validator=validate_email,
            validator_msg="Please enter a valid email address (e.g., user@example.com)"
        ),
        basic_udi_di=basic_udi_di,
        udi_di=udi_di,
        regulatory_classifications=regulatory_classifications if regulatory_classifications else None
    )


def section_intended_use() -> IntendedUse:
    """Guided input for Section 2: Intended Use"""
    print("\n" + "="*60)
    print("[Section 2/7] Intended Use and Clinical Context")
    print("="*60)

    return IntendedUse(
        primary_intended_users=prompt_input("Primary Intended Users (e.g., Cardiologists, Primary care physicians)", required=True),
        clinical_indications=prompt_input("Clinical Indications (e.g., Risk stratification for heart failure patients)", required=True),
        patient_target_group=prompt_input("Patient Target Group (e.g., Adults aged 40-75 with hypertension)", required=True),
        intended_use_environment=prompt_choice(
            "Intended Use Environment",
            ["hospital_inpatient", "hospital_outpatient", "emergency", "telemedicine", "research", "home", "other"]
        ),
        contraindications=prompt_input("Contraindications", required=False),
        out_of_scope_applications=prompt_input("Out of Scope Applications", required=False),
        warnings=prompt_input("Warnings", required=False)
    )


def section_data_factors() -> DataFactors:
    """Guided input for Section 3: Data & Factors"""
    print("\n" + "="*60)
    print("[Section 3/7] Data & Factors")
    print("="*60)

    omop_data = prompt_omop_integration()

    if omop_data and 'data_factors' in omop_data:
        print("\n  ✓ Using OMOP-generated DataFactors")
        print(f"  ✓ Source Dataset: {omop_data['name']}")
        print(f"  ✓ Detailed Reports: {'Included' if omop_data.get('reports') else 'Not available'}")

        if prompt_yes_no("\n  Add additional non-OMOP datasets?", default=False):
            print("\n  Adding supplementary datasets...")
            omop_df = omop_data['data_factors']

            while True:
                print(f"\n  Dataset {len(omop_df.source_datasets) + 1}:")
                name = prompt_input("  Dataset Name (e.g., Hospital A - EHR Database)", required=True)
                origin = prompt_input("  Origin/Source (e.g., Academic medical center, 2020-2024)", required=True)
                size = prompt_int("  Size (number of records)", required=True, min_val=1)
                period = prompt_input("  Collection Period (e.g., 2020-01-01 to 2024-12-31)", required=True)
                pop_char = prompt_input("  Population Characteristics (e.g., Urban population, 65% male, mean age 62)", required=True)

                omop_df.source_datasets.append(SourceDataset(name, origin, size, period, pop_char))

                if not prompt_yes_no("\n  Add another dataset?", default=False):
                    break

        return omop_data['data_factors']

    print("\n  Manual data entry (no OMOP integration)")

    datasets = []
    print("\nAdd source datasets:")

    while True:
        print(f"\n  Dataset {len(datasets) + 1}:")
        name = prompt_input("  Dataset Name (e.g., Hospital A - EHR Database)", required=True)
        origin = prompt_input("  Origin/Source (e.g., Academic medical center, 2020-2024)", required=True)
        size = prompt_int("  Size (number of records)", required=True, min_val=1)
        period = prompt_input("  Collection Period (e.g., 2020-01-01 to 2024-12-31)", required=True)
        pop_char = prompt_input("  Population Characteristics (e.g., Urban population, 65% male, mean age 62)", required=True)

        datasets.append(SourceDataset(name, origin, size, period, pop_char))

        if not prompt_yes_no("\nAdd another dataset?", default=False):
            break

    return DataFactors(
        source_datasets=datasets,
        data_distribution_summary=prompt_input("Data Distribution Summary (e.g., 10000 patients, balanced age/gender, 30% positive cases)", required=True),
        data_representativeness=prompt_input("Data Representativeness (e.g., Representative of urban academic hospital population)", required=True),
        data_governance=prompt_input("Data Governance (e.g., IRB-approved, HIPAA-compliant, de-identified per Safe Harbor)", required=True),
        omop_detailed_reports=None
    )


def section_features_outputs() -> FeaturesOutputs:
    """Guided input for Section 4: Features & Outputs"""
    print("\n" + "="*60)
    print("[Section 4/7] Features & Outputs")
    print("="*60)

    input_features = []
    print("\nAdd input features:")

    while True:
        print(f"\n  Feature {len(input_features) + 1}:")
        name = prompt_input("  Feature Name (e.g., age, fev1_percent, smoking_status)", required=True)
        data_type = prompt_choice("  Data Type", ["numeric", "categorical", "text", "image", "signal", "other"])
        required = prompt_yes_no("  Required?", default=True)
        domain = prompt_input("  Clinical Domain (e.g., Demographics, Labs, Vitals, Medications)", required=True)

        input_features.append(InputFeature(name, data_type, required, domain))

        if not prompt_yes_no("\nAdd another input feature?", default=True):
            break

    output_features = []
    print("\nAdd output features:")

    while True:
        print(f"\n  Output {len(output_features) + 1}:")
        name = prompt_input("  Output Name (e.g., risk_score, diagnosis, alert_level)", required=True)
        output_type = prompt_choice("  Type", ["probability", "classification", "regression", "ranking"])

        output_features.append(OutputFeature(name, output_type))

        if not prompt_yes_no("\nAdd another output?", default=False):
            break

    return FeaturesOutputs(
        input_features=input_features,
        output_features=output_features,
        feature_type_distribution=prompt_input("Feature Type Distribution", required=False),
        uncertainty_quantification=prompt_input("Uncertainty Quantification", required=False),
        output_interpretability=prompt_input("Output Interpretability", required=False)
    )


def section_performance() -> PerformanceValidation:
    """Guided input for Section 5: Performance & Validation"""
    print("\n" + "="*60)
    print("[Section 5/7] Performance & Validation")
    print("="*60)

    val_datasets = []
    print("\nAdd validation datasets:")

    while True:
        print(f"\n  Dataset {len(val_datasets) + 1}:")
        name = prompt_input("  Dataset Name (e.g., Hospital A - EHR Database)", required=True)
        institution = prompt_input("  Source Institution (e.g., Same hospital, External validation site)", required=True)
        pop = prompt_input("  Population Characteristics (e.g., Urban population, 65% male, mean age 62)", required=True)
        val_type = prompt_choice("  Validation Type", ["internal", "external", "cross_validation"])

        val_datasets.append(ValidationDataset(name, institution, pop, val_type))

        if not prompt_yes_no("\nAdd another validation dataset?", default=False):
            break

    metrics = []
    print("\nAdd performance metrics:")

    while True:
        print(f"\n  Metric {len(metrics) + 1}:")
        metric_name = prompt_input("  Metric Name (e.g., AUC-ROC, Sensitivity)", required=True)
        value = prompt_float("  Value (typically 0.0-1.0)", required=True, min_val=0.0, max_val=1.0)
        status = prompt_choice("  Validation Status", ["Claimed", "Validated", "External"])
        subgroup = prompt_input("  Subgroup (optional)", required=False)

        metrics.append(PerformanceMetric(metric_name, value, status, subgroup if subgroup else None))

        if not prompt_yes_no("\nAdd another metric?", default=True):
            break

    return PerformanceValidation(
        validation_datasets=val_datasets,
        claimed_metrics=[m for m in metrics if m.validation_status == "Claimed"],
        validated_metrics=[m for m in metrics if m.validation_status != "Claimed"],
        calibration_analysis=prompt_input("Calibration Analysis", required=False),
        fairness_assessment=prompt_input("Fairness Assessment", required=False),
        metric_validation_status=prompt_input("Overall Validation Status", required=False)
    )


def section_methodology() -> Methodology:
    """Guided input for Section 6: Methodology & Explainability"""
    print("\n" + "="*60)
    print("[Section 6/7] Methodology & Explainability")
    print("="*60)

    return Methodology(
        model_development_workflow=prompt_input("Development Workflow (e.g., Data extraction → Feature engineering → Model training → Validation)", required=True),
        training_procedure=prompt_input("Training Procedure (e.g., 5-fold cross-validation, hyperparameter tuning with grid search)", required=True),
        data_preprocessing=prompt_input("Data Preprocessing (e.g., Missing value imputation, normalization, outlier removal)", required=True),
        synthetic_data_usage=prompt_input("Synthetic Data Usage (if any)", required=False),
        explainable_ai_method=prompt_input("Explainability Method (if any)", required=False),
        global_vs_local_interpretability=prompt_input("Global vs Local Interpretability", required=False)
    )


def section_additional_info() -> AdditionalInfo:
    """Guided input for Section 7: Additional Information"""
    print("\n" + "="*60)
    print("[Section 7/7] Additional Information")
    print("="*60)

    return AdditionalInfo(
        benefit_risk_summary=prompt_input("Benefit-Risk Summary (e.g., Improves early detection with minimal false positives)", required=True),
        ethical_considerations=prompt_input("Ethical Considerations (e.g., Monitored for demographic bias, transparent decision-making)", required=True),
        caveats_limitations=prompt_input("Caveats & Limitations (e.g., Not validated in pediatric populations, limited to specific conditions)", required=True),
        recommendations_for_safe_use=prompt_input("Recommendations for Safe Use (e.g., Use as screening tool, not for diagnosis; require clinical validation)", required=True),
        post_market_surveillance_plan=prompt_input("Post-Market Surveillance Plan", required=False),
        explainability_recommendations=prompt_input("Explainability Recommendations", required=False)
    )


def _quick_start_mode() -> ModelCard:
    """Quick Start: pick a template, answer ~8 questions, get a card."""
    print("\n" + "="*60)
    print("Quick Start Mode")
    print("="*60)

    print("\n  Available templates:")
    template_ids = list(TEMPLATES.keys())
    for i, tid in enumerate(template_ids, 1):
        tmpl = TEMPLATES[tid]
        print(f"    {i}. {tmpl['name']}")
        print(f"       {tmpl['description']}")

    max_retries = 5
    retries = 0
    template_id = template_ids[0]

    while retries < max_retries:
        selection = input(f"\n  Select template (1-{len(template_ids)}): ").strip()
        try:
            idx = int(selection) - 1
            if 0 <= idx < len(template_ids):
                template_id = template_ids[idx]
                break
            print(f"  Please enter 1-{len(template_ids)}")
        except ValueError:
            print("  Please enter a valid number")
        retries += 1

    print(f"\n  Selected: {TEMPLATES[template_id]['name']}")

    print("\n  Regulatory jurisdiction (auto-fills classifications):")
    jurisdiction = prompt_choice(
        "Select jurisdiction",
        ["EU (MDR + AI Act)", "US (FDA)", "Both (EU + US)", "Skip (none)"]
    )
    jurisdiction_map = {
        "EU (MDR + AI Act)": "eu",
        "US (FDA)": "us",
        "Both (EU + US)": "both",
        "Skip (none)": None,
    }
    jurisdiction_key = jurisdiction_map.get(jurisdiction)

    if jurisdiction_key:
        preset = REGULATORY_PRESETS[jurisdiction_key]
        print(f"\n  Auto-filled regulatory classifications:")
        for c in preset["classifications"]:
            parts = [f"{c['framework']} Class {c['class']}"]
            if c.get("rule"):
                parts.append(f"({c['rule']})")
            if c.get("pathway"):
                parts.append(f"({c['pathway']})")
            print(f"    - {' '.join(parts)}")
        print(f"\n  Documentation requirements:")
        for req in preset["documentation_requirements"][:3]:
            print(f"    - {req}")
        if len(preset["documentation_requirements"]) > 3:
            print(f"    ... and {len(preset['documentation_requirements']) - 3} more")

    print("\n" + "-"*60)
    print("  Answer a few essential questions:")
    print("-"*60)

    model_name = prompt_input("Model Name", required=True)
    description = prompt_input("Description", required=True)
    developer = prompt_input("Developer / Organization", required=True)
    contact = prompt_input(
        "Support Contact (email)",
        required=True,
        validator=validate_email,
        validator_msg="Please enter a valid email address"
    )
    algorithms = prompt_input("Algorithm(s) Used", required=True)

    overrides = {"algorithms_used": algorithms}

    card = quick_card(
        model_name=model_name,
        description=description,
        developer=developer,
        contact=contact,
        template=template_id,
        jurisdiction=jurisdiction_key,
        **overrides,
    )

    print("\n" + "="*60)
    print("  Auto-filled sections summary:")
    print("="*60)
    d = card.to_dict()
    print(f"  1. Model Details:      {card.model_details.model_name} v{card.model_details.version}")
    print(f"     Clinical Function:  {card.model_details.clinical_function}")
    rc = card.model_details.regulatory_classifications
    print(f"     Regulatory:         {len(rc) if rc else 0} classification(s)")
    print(f"  2. Intended Use:       {card.intended_use.primary_intended_users[:50]}...")
    print(f"  3. Data & Factors:     {len(card.data_factors.source_datasets)} dataset(s)")
    print(f"  4. Features & Outputs: {len(card.features_outputs.input_features)} input, {len(card.features_outputs.output_features)} output")
    print(f"  5. Performance:        {len(card.performance_validation.claimed_metrics)} metric(s)")
    print(f"  6. Methodology:        Pre-filled")
    print(f"  7. Additional Info:    Pre-filled")

    if prompt_yes_no("\n  Would you like to customize any section?", default=False):
        section_funcs = {
            "1": ("Model Details", section_model_details, card.set_model_details),
            "2": ("Intended Use", section_intended_use, card.set_intended_use),
            "3": ("Data & Factors", section_data_factors, card.set_data_factors),
            "4": ("Features & Outputs", section_features_outputs, card.set_features_outputs),
            "5": ("Performance", section_performance, card.set_performance_validation),
            "6": ("Methodology", section_methodology, card.set_methodology),
            "7": ("Additional Info", section_additional_info, card.set_additional_info),
        }
        while True:
            print("\n  Which section to customize?")
            for num, (name, _, _) in section_funcs.items():
                print(f"    {num}. {name}")
            print(f"    0. Done")

            choice = input("  Select: ").strip()
            if choice == "0" or not choice:
                break
            if choice in section_funcs:
                name, func, setter = section_funcs[choice]
                setter(func())
            else:
                print("  Invalid selection")

    print("\n" + "="*60)
    print("Quick Start - Card Complete!")
    print("="*60)
    return card


def _load_and_edit_mode(load_path: Optional[str] = None) -> ModelCard:
    """Load & Edit: load existing JSON, modify specific sections, re-export."""
    print("\n" + "="*60)
    print("Load & Edit Mode")
    print("="*60)

    if not load_path:
        load_path = prompt_input("Path to existing model card JSON file", required=True)

    if not os.path.exists(load_path):
        print(f"  File not found: {load_path}")
        raise FileNotFoundError(f"File not found: {load_path}")

    print(f"\n  Loading: {load_path}")
    card = ModelCard.from_json(load_path)
    print(f"  Loaded: {card.model_details.model_name} v{card.model_details.version}")

    print("\n" + "-"*60)
    print("  Current card sections:")
    print("-"*60)
    if card.model_details:
        print(f"  1. Model Details:      {card.model_details.model_name}")
    if card.intended_use:
        print(f"  2. Intended Use:       {card.intended_use.primary_intended_users[:50]}")
    if card.data_factors:
        print(f"  3. Data & Factors:     {len(card.data_factors.source_datasets)} dataset(s)")
    if card.features_outputs:
        print(f"  4. Features & Outputs: {len(card.features_outputs.input_features)} input features")
    if card.performance_validation:
        print(f"  5. Performance:        {len(card.performance_validation.claimed_metrics)} claimed metric(s)")
    if card.methodology:
        print(f"  6. Methodology:        Filled")
    if card.additional_info:
        print(f"  7. Additional Info:    Filled")

    section_funcs = {
        "1": ("Model Details", section_model_details, card.set_model_details),
        "2": ("Intended Use", section_intended_use, card.set_intended_use),
        "3": ("Data & Factors", section_data_factors, card.set_data_factors),
        "4": ("Features & Outputs", section_features_outputs, card.set_features_outputs),
        "5": ("Performance", section_performance, card.set_performance_validation),
        "6": ("Methodology", section_methodology, card.set_methodology),
        "7": ("Additional Info", section_additional_info, card.set_additional_info),
    }

    while True:
        print("\n  Which section to edit?")
        for num, (name, _, _) in section_funcs.items():
            print(f"    {num}. {name}")
        print(f"    0. Done - validate and export")

        choice = input("  Select: ").strip()
        if choice == "0" or not choice:
            break
        if choice in section_funcs:
            name, func, setter = section_funcs[choice]
            setter(func())
            print(f"\n  Section {choice} updated.")
        else:
            print("  Invalid selection")

    card.validate()
    print("\n" + "="*60)
    print("Load & Edit - Card Updated!")
    print("="*60)
    return card


def _full_wizard_mode() -> ModelCard:
    """Full Wizard: guided through all 7 sections (~40 questions)."""
    print("\n" + "="*60)
    print("Full Wizard Mode")
    print("="*60)
    print("\nThis will guide you through all 7 sections.")
    print("You can skip optional fields by pressing Enter.\n")

    card = ModelCard()
    card.set_model_details(section_model_details())
    card.set_intended_use(section_intended_use())
    card.set_data_factors(section_data_factors())
    card.set_features_outputs(section_features_outputs())
    card.set_performance_validation(section_performance())
    card.set_methodology(section_methodology())
    card.set_additional_info(section_additional_info())

    print("\n" + "="*60)
    print("Full Wizard - Card Complete!")
    print("="*60)
    return card


def interactive_create_model_card(
    template: Optional[str] = None,
    load_path: Optional[str] = None,
    jurisdiction: Optional[str] = None,
) -> ModelCard:
    """
    Interactive workflow to create a model card.

    Supports 3 modes:
      1. Quick Start - pick a template, answer ~8 questions
      2. Full Wizard - guided through all 7 sections
      3. Load & Edit - load existing JSON, modify, re-export

    Args:
        template: Pre-select Quick Start mode with this template ID
        load_path: Pre-select Load & Edit mode with this JSON path
        jurisdiction: Pre-select jurisdiction for Quick Start mode
    """
    print("\n" + "*"*60)
    print("SMART Model Card - Interactive Creation")
    print("*"*60)

    if load_path:
        return _load_and_edit_mode(load_path)
    if template:
        print(f"\n  Using template: {template}")
        model_name = prompt_input("Model Name", required=True)
        description = prompt_input("Description", required=True)
        developer = prompt_input("Developer / Organization", required=True)
        contact = prompt_input("Support Contact (email)", required=True,
                               validator=validate_email,
                               validator_msg="Please enter a valid email")
        algorithms = prompt_input("Algorithm(s) Used", required=True)
        card = quick_card(model_name, description, developer, contact,
                          template=template, jurisdiction=jurisdiction,
                          algorithms_used=algorithms)
        return card

    print("\n  Choose creation mode:")
    mode = prompt_choice(
        "How would you like to create your model card?",
        [
            "Quick Start (pick a template, ~8 questions)",
            "Full Wizard (all 7 sections, ~40 questions)",
            "Load & Edit (modify existing JSON card)",
        ]
    )

    if mode.startswith("Quick Start"):
        return _quick_start_mode()
    elif mode.startswith("Load & Edit"):
        return _load_and_edit_mode()
    else:
        return _full_wizard_mode()


def _export_card(card: ModelCard) -> List[tuple]:
    """Export a model card to files. Returns list of (format, path) tuples."""
    print("\n" + "="*60)
    print("Exporting Model Card")
    print("="*60)

    output_dir = prompt_input("Output directory", default="output")
    output_base = prompt_input("Output filename (without extension)", default="model_card")

    os.makedirs(output_dir, exist_ok=True)

    formats = []
    if prompt_yes_no("Export HTML?", default=True):
        formats.append("html")
    if prompt_yes_no("Export JSON?", default=True):
        formats.append("json")

    exported_files = []
    for fmt in formats:
        output_path = os.path.join(output_dir, f"{output_base}.{fmt}")
        if fmt == "html":
            HTMLExporter.export(card, output_path)
        elif fmt == "json":
            JSONExporter.export(card, output_path)

        abs_path = os.path.abspath(output_path)
        exported_files.append((fmt, abs_path))
        print(f"  Exported {fmt.upper()}: {abs_path}")

    return exported_files


def run_interactive_wizard(
    template: Optional[str] = None,
    load_path: Optional[str] = None,
    jurisdiction: Optional[str] = None,
):
    """Run the full interactive wizard with export - for use by CLI"""
    card = interactive_create_model_card(
        template=template,
        load_path=load_path,
        jurisdiction=jurisdiction,
    )

    exported_files = _export_card(card)

    print("\n" + "="*60)
    print("Model Card Complete!")
    print("="*60)

    print("\nYour model card has been saved to:")
    for fmt, path in exported_files:
        print(f"  {fmt.upper()}: {path}")

    html_files = [path for fmt, path in exported_files if fmt == "html"]
    if html_files:
        print("\n" + "-"*60)
        print("To view your model card:")
        print("-"*60)
        for html_path in html_files:
            print(f"\n  Open in browser:")
            print(f"    open {html_path}")
            print(f"\n  Or use this command:")
            print(f"    python -m webbrowser {html_path}")

    json_files = [path for fmt, path in exported_files if fmt == "json"]
    if json_files:
        print("\n  View JSON:")
        for json_path in json_files:
            print(f"    cat {json_path}")
