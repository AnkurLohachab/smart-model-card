"""
Domain Templates, Regulatory Presets, and quick_card() Factory

Provides pre-built templates for common medical AI use cases,
regulatory classification presets by jurisdiction, and a factory
function to create valid model cards in ~5 lines.

Author: Ankur Lohachab
Department of Advanced Computing Sciences, Maastricht University
"""

from __future__ import annotations

import copy
from datetime import date
from typing import Any, Dict, List, Optional

from smart_model_card.model_card import ModelCard
from smart_model_card.sections import (
    ModelDetails,
    IntendedUse,
    DataFactors,
    FeaturesOutputs,
    PerformanceValidation,
    Methodology,
    AdditionalInfo,
    SourceDataset,
    InputFeature,
    OutputFeature,
    ValidationDataset,
    PerformanceMetric,
)


REGULATORY_PRESETS: Dict[str, Dict[str, Any]] = {
    "eu": {
        "classifications": [
            {"framework": "EU MDR", "class": "IIa", "rule": "Rule 11"},
            {"framework": "EU AI Act", "class": "high-risk"},
        ],
        "documentation_requirements": [
            "Technical documentation per Annex II MDR",
            "Clinical evaluation report (MEDDEV 2.7/1 Rev 4)",
            "Post-market surveillance plan",
            "Conformity assessment by Notified Body",
            "AI Act conformity assessment (high-risk)",
        ],
    },
    "us": {
        "classifications": [
            {"framework": "FDA", "class": "II", "pathway": "510(k)"},
        ],
        "documentation_requirements": [
            "510(k) premarket notification or De Novo request",
            "Software documentation per FDA guidance",
            "Clinical validation study",
            "Predetermined change control plan (if applicable)",
        ],
    },
    "both": {
        "classifications": [
            {"framework": "EU MDR", "class": "IIa", "rule": "Rule 11"},
            {"framework": "EU AI Act", "class": "high-risk"},
            {"framework": "FDA", "class": "II", "pathway": "510(k)"},
        ],
        "documentation_requirements": [
            "Technical documentation per Annex II MDR",
            "Clinical evaluation report (MEDDEV 2.7/1 Rev 4)",
            "Post-market surveillance plan",
            "Conformity assessment by Notified Body",
            "AI Act conformity assessment (high-risk)",
            "510(k) premarket notification or De Novo request",
            "Software documentation per FDA guidance",
            "Clinical validation study",
        ],
    },
}


TEMPLATES: Dict[str, Dict[str, Any]] = {
    "copd_risk_predictor": {
        "name": "COPD Risk Predictor",
        "description": "Pre-built template for COPD exacerbation risk prediction models using EHR data.",
        "sections": {
            "model_details": {
                "clinical_function": "decision_support",
                "algorithms_used": "XGBoost / Gradient Boosting",
            },
            "intended_use": {
                "primary_intended_users": "Pulmonologists, respiratory therapists, primary care physicians",
                "clinical_indications": "COPD exacerbation risk assessment in stable COPD patients",
                "patient_target_group": "Adults aged 40 and older with confirmed COPD diagnosis",
                "intended_use_environment": "hospital_outpatient",
                "contraindications": "Not for use in acute exacerbation or ICU settings",
                "out_of_scope_applications": "Not validated for asthma, interstitial lung disease, or pediatric populations",
            },
            "data_factors": {
                "source_datasets": [{"name": "EHR Dataset", "origin": "Hospital EHR system", "size": 0,
                                     "collection_period": "To be specified", "population_characteristics": "COPD patients"}],
                "data_distribution_summary": "EHR-derived cohort with demographics, spirometry, medications, and comorbidities",
                "data_representativeness": "To be assessed against target population",
                "data_governance": "IRB/Ethics committee approved, GDPR/HIPAA compliant",
            },
            "features_outputs": {
                "input_features": [
                    {"name": "age", "data_type": "numeric", "required": True, "clinical_domain": "Demographics", "units": "years"},
                    {"name": "fev1_percent_predicted", "data_type": "numeric", "required": True, "clinical_domain": "Pulmonology", "units": "%"},
                    {"name": "exacerbation_history", "data_type": "numeric", "required": True, "clinical_domain": "Pulmonology"},
                    {"name": "smoking_status", "data_type": "categorical", "required": True, "clinical_domain": "Lifestyle"},
                    {"name": "comorbidity_count", "data_type": "numeric", "required": False, "clinical_domain": "General"},
                ],
                "output_features": [
                    {"name": "exacerbation_risk_score", "type": "probability", "value_range": "0-1"},
                    {"name": "risk_category", "type": "classification", "classes": ["low", "moderate", "high"]},
                ],
                "feature_type_distribution": "Majority numeric (spirometry, demographics) with categorical lifestyle factors",
                "uncertainty_quantification": "Bootstrap confidence intervals on risk score",
                "output_interpretability": "SHAP values for feature attribution",
            },
            "performance": {
                "validation_datasets": [{"name": "Holdout Set", "source_institution": "To be specified",
                                         "population_characteristics": "Random 20% holdout", "validation_type": "internal"}],
                "claimed_metrics": [{"metric_name": "AUC", "value": 0.80, "validation_status": "Claimed"}],
                "validated_metrics": [{"metric_name": "AUC", "value": 0.80, "validation_status": "Claimed"}],
            },
            "methodology": {
                "model_development_workflow": "CRISP-DM methodology with clinical expert involvement",
                "training_procedure": "Stratified k-fold cross-validation with hyperparameter tuning",
                "data_preprocessing": "Missing value imputation, feature normalization, outlier detection",
            },
            "additional_info": {
                "benefit_risk_summary": "Early identification of high-risk patients enables preventive interventions and care planning",
                "ethical_considerations": "Potential bias in populations underrepresented in training data",
                "caveats_limitations": "Performance may vary in populations not represented in training data",
                "recommendations_for_safe_use": "Use as clinical decision support only; does not replace clinical judgment",
            },
        },
    },

    "screening_tool": {
        "name": "Screening Tool",
        "description": "Generic template for population screening models using lab results and demographics.",
        "sections": {
            "model_details": {
                "clinical_function": "screening",
                "algorithms_used": "Logistic Regression / Random Forest",
            },
            "intended_use": {
                "primary_intended_users": "Primary care physicians, screening program coordinators",
                "clinical_indications": "Population-level screening for early disease detection",
                "patient_target_group": "Target population as defined by screening guidelines",
                "intended_use_environment": "hospital_outpatient",
                "out_of_scope_applications": "Not for diagnostic confirmation or treatment selection",
            },
            "data_factors": {
                "source_datasets": [{"name": "Screening Dataset", "origin": "To be specified", "size": 0,
                                     "collection_period": "To be specified", "population_characteristics": "Screening population"}],
                "data_distribution_summary": "Demographics and laboratory results from screening population",
                "data_representativeness": "To be assessed against target screening population",
                "data_governance": "Approved by institutional ethics committee",
            },
            "features_outputs": {
                "input_features": [
                    {"name": "age", "data_type": "numeric", "required": True, "clinical_domain": "Demographics", "units": "years"},
                    {"name": "sex", "data_type": "categorical", "required": True, "clinical_domain": "Demographics"},
                    {"name": "lab_value", "data_type": "numeric", "required": True, "clinical_domain": "Laboratory"},
                ],
                "output_features": [
                    {"name": "screening_result", "type": "classification", "classes": ["negative", "positive"]},
                    {"name": "confidence_score", "type": "probability", "value_range": "0-1"},
                ],
                "feature_type_distribution": "Mix of numeric (labs, vitals) and categorical (demographics)",
                "uncertainty_quantification": "Prediction confidence intervals",
                "output_interpretability": "Feature importance ranking",
            },
            "performance": {
                "validation_datasets": [{"name": "Validation Set", "source_institution": "To be specified",
                                         "population_characteristics": "Holdout", "validation_type": "internal"}],
                "claimed_metrics": [
                    {"metric_name": "Sensitivity", "value": 0.90, "validation_status": "Claimed"},
                    {"metric_name": "Specificity", "value": 0.80, "validation_status": "Claimed"},
                ],
                "validated_metrics": [
                    {"metric_name": "Sensitivity", "value": 0.90, "validation_status": "Claimed"},
                    {"metric_name": "Specificity", "value": 0.80, "validation_status": "Claimed"},
                ],
            },
            "methodology": {
                "model_development_workflow": "Standard ML pipeline with clinical validation",
                "training_procedure": "Cross-validation with stratified sampling",
                "data_preprocessing": "Data cleaning, normalization, and balancing for screening prevalence",
            },
            "additional_info": {
                "benefit_risk_summary": "Early detection enables timely intervention; false positives may cause unnecessary follow-up",
                "ethical_considerations": "Equitable screening across demographic groups must be ensured",
                "caveats_limitations": "Screening performance depends on disease prevalence in target population",
                "recommendations_for_safe_use": "Positive screening results must be confirmed with diagnostic testing",
            },
        },
    },

    "diagnostic_classifier": {
        "name": "Diagnostic Classifier",
        "description": "Template for diagnostic classification models (imaging, pathology, multi-class).",
        "sections": {
            "model_details": {
                "clinical_function": "diagnosis",
                "algorithms_used": "Deep Learning / CNN",
            },
            "intended_use": {
                "primary_intended_users": "Radiologists, pathologists, specialist clinicians",
                "clinical_indications": "Automated diagnostic classification support",
                "patient_target_group": "Patients referred for diagnostic evaluation",
                "intended_use_environment": "hospital_inpatient",
                "out_of_scope_applications": "Not for screening or risk prediction; requires clinical confirmation",
            },
            "data_factors": {
                "source_datasets": [{"name": "Diagnostic Dataset", "origin": "To be specified", "size": 0,
                                     "collection_period": "To be specified", "population_characteristics": "Diagnostic cohort"}],
                "data_distribution_summary": "Annotated diagnostic data with expert-verified labels",
                "data_representativeness": "To be assessed for demographic and clinical diversity",
                "data_governance": "Multi-reader annotation protocol, ethics approved",
            },
            "features_outputs": {
                "input_features": [
                    {"name": "clinical_data", "data_type": "image", "required": True, "clinical_domain": "Radiology/Pathology"},
                ],
                "output_features": [
                    {"name": "diagnosis", "type": "classification", "classes": ["normal", "abnormal"]},
                    {"name": "confidence", "type": "probability", "value_range": "0-1"},
                ],
                "feature_type_distribution": "Primarily image data with optional clinical metadata",
                "uncertainty_quantification": "Softmax confidence with calibration",
                "output_interpretability": "Grad-CAM attention maps highlighting diagnostic regions",
            },
            "performance": {
                "validation_datasets": [{"name": "Expert-annotated Test Set", "source_institution": "To be specified",
                                         "population_characteristics": "Multi-reader annotated", "validation_type": "internal"}],
                "claimed_metrics": [
                    {"metric_name": "AUC", "value": 0.90, "validation_status": "Claimed"},
                    {"metric_name": "Sensitivity", "value": 0.85, "validation_status": "Claimed"},
                    {"metric_name": "Specificity", "value": 0.90, "validation_status": "Claimed"},
                ],
                "validated_metrics": [
                    {"metric_name": "AUC", "value": 0.90, "validation_status": "Claimed"},
                ],
            },
            "methodology": {
                "model_development_workflow": "Transfer learning with domain-specific fine-tuning",
                "training_procedure": "Pre-trained backbone with task-specific classification head",
                "data_preprocessing": "Image normalization, augmentation, and quality filtering",
            },
            "additional_info": {
                "benefit_risk_summary": "Assists clinicians in diagnostic accuracy; not a standalone diagnostic tool",
                "ethical_considerations": "Diagnostic performance must be validated across diverse populations",
                "caveats_limitations": "Performance may degrade on image quality or acquisition protocols different from training data",
                "recommendations_for_safe_use": "All AI-generated diagnoses must be reviewed and confirmed by qualified clinicians",
            },
        },
    },

    "triage_model": {
        "name": "Triage Model",
        "description": "Template for emergency triage models using vitals, chief complaint, and clinical data.",
        "sections": {
            "model_details": {
                "clinical_function": "triage",
                "algorithms_used": "Gradient Boosting / Neural Network",
            },
            "intended_use": {
                "primary_intended_users": "Emergency physicians, triage nurses, emergency department staff",
                "clinical_indications": "Automated priority assignment in emergency department triage",
                "patient_target_group": "Patients presenting to the emergency department",
                "intended_use_environment": "emergency",
                "contraindications": "Not for use in mass casualty events or disaster triage",
                "out_of_scope_applications": "Not for outpatient or elective care prioritization",
            },
            "data_factors": {
                "source_datasets": [{"name": "ED Triage Dataset", "origin": "To be specified", "size": 0,
                                     "collection_period": "To be specified", "population_characteristics": "ED patients"}],
                "data_distribution_summary": "Emergency department visit data with vitals, chief complaints, and outcomes",
                "data_representativeness": "To be assessed for case-mix and acuity distribution",
                "data_governance": "Retrospective data with ethics approval",
            },
            "features_outputs": {
                "input_features": [
                    {"name": "heart_rate", "data_type": "numeric", "required": True, "clinical_domain": "Vitals", "units": "bpm"},
                    {"name": "blood_pressure_systolic", "data_type": "numeric", "required": True, "clinical_domain": "Vitals", "units": "mmHg"},
                    {"name": "respiratory_rate", "data_type": "numeric", "required": True, "clinical_domain": "Vitals", "units": "breaths/min"},
                    {"name": "temperature", "data_type": "numeric", "required": True, "clinical_domain": "Vitals", "units": "celsius"},
                    {"name": "chief_complaint", "data_type": "text", "required": True, "clinical_domain": "Presentation"},
                    {"name": "age", "data_type": "numeric", "required": True, "clinical_domain": "Demographics", "units": "years"},
                ],
                "output_features": [
                    {"name": "triage_level", "type": "classification", "classes": ["1-resuscitation", "2-emergent", "3-urgent", "4-less_urgent", "5-non_urgent"]},
                    {"name": "acuity_score", "type": "score", "value_range": "1-5"},
                ],
                "feature_type_distribution": "Primarily numeric vitals with text chief complaint",
                "uncertainty_quantification": "Prediction uncertainty for borderline cases",
                "output_interpretability": "Feature contribution to triage level assignment",
            },
            "performance": {
                "validation_datasets": [{"name": "ED Holdout Set", "source_institution": "To be specified",
                                         "population_characteristics": "Temporal holdout", "validation_type": "internal"}],
                "claimed_metrics": [{"metric_name": "Accuracy", "value": 0.80, "validation_status": "Claimed"}],
                "validated_metrics": [{"metric_name": "Accuracy", "value": 0.80, "validation_status": "Claimed"}],
            },
            "methodology": {
                "model_development_workflow": "Retrospective development with prospective validation planned",
                "training_procedure": "Temporal split training with class-weighted loss",
                "data_preprocessing": "Vital sign normalization, text encoding, missing value handling",
            },
            "additional_info": {
                "benefit_risk_summary": "Supports consistent triage decisions; under-triage risk must be monitored",
                "ethical_considerations": "Triage equity across demographic groups must be continuously monitored",
                "caveats_limitations": "Text-based features may be affected by language and documentation style variations",
                "recommendations_for_safe_use": "Clinical staff must review and can override all triage recommendations",
            },
        },
    },

    "monitoring_model": {
        "name": "Monitoring Model",
        "description": "Template for continuous patient monitoring with time-series physiological data.",
        "sections": {
            "model_details": {
                "clinical_function": "monitoring",
                "algorithms_used": "LSTM / Temporal CNN",
            },
            "intended_use": {
                "primary_intended_users": "Intensivists, ICU nurses, clinical monitoring teams",
                "clinical_indications": "Continuous monitoring and early warning for clinical deterioration",
                "patient_target_group": "Hospitalized patients requiring continuous monitoring",
                "intended_use_environment": "hospital_inpatient",
                "contraindications": "Not for ambulatory or home monitoring without clinical oversight",
                "out_of_scope_applications": "Not for diagnostic purposes or treatment selection",
            },
            "data_factors": {
                "source_datasets": [{"name": "ICU Monitoring Dataset", "origin": "To be specified", "size": 0,
                                     "collection_period": "To be specified", "population_characteristics": "ICU patients"}],
                "data_distribution_summary": "Continuous time-series physiological data from bedside monitors",
                "data_representativeness": "To be assessed for patient case-mix and monitoring device types",
                "data_governance": "Prospective data collection with informed consent where applicable",
            },
            "features_outputs": {
                "input_features": [
                    {"name": "ecg_signal", "data_type": "signal", "required": True, "clinical_domain": "Cardiology"},
                    {"name": "spo2", "data_type": "numeric", "required": True, "clinical_domain": "Pulmonology", "units": "%"},
                    {"name": "blood_pressure_continuous", "data_type": "signal", "required": False, "clinical_domain": "Hemodynamics"},
                ],
                "output_features": [
                    {"name": "deterioration_risk", "type": "probability", "value_range": "0-1"},
                    {"name": "alert_level", "type": "classification", "classes": ["normal", "warning", "critical"]},
                ],
                "feature_type_distribution": "Primarily time-series signal data with numeric vitals",
                "uncertainty_quantification": "Rolling prediction confidence with alert threshold calibration",
                "output_interpretability": "Temporal attention highlighting contributing signal segments",
            },
            "performance": {
                "validation_datasets": [{"name": "ICU Holdout", "source_institution": "To be specified",
                                         "population_characteristics": "Temporal holdout", "validation_type": "internal"}],
                "claimed_metrics": [
                    {"metric_name": "AUC", "value": 0.85, "validation_status": "Claimed"},
                    {"metric_name": "Sensitivity", "value": 0.90, "validation_status": "Claimed"},
                ],
                "validated_metrics": [
                    {"metric_name": "AUC", "value": 0.85, "validation_status": "Claimed"},
                ],
            },
            "methodology": {
                "model_development_workflow": "Time-series model development with temporal validation",
                "training_procedure": "Sequence-to-sequence training with sliding window approach",
                "data_preprocessing": "Signal filtering, resampling, artifact removal, and normalization",
            },
            "additional_info": {
                "benefit_risk_summary": "Early warning enables timely intervention; alert fatigue risk must be managed",
                "ethical_considerations": "Monitoring equity and alert threshold fairness across patient groups",
                "caveats_limitations": "Signal quality and monitoring device compatibility may affect performance",
                "recommendations_for_safe_use": "All alerts require clinical assessment; alarm thresholds should be site-calibrated",
            },
        },
    },
}


def quick_card(
    model_name: str,
    description: str,
    developer: str,
    contact: str,
    template: str = "screening_tool",
    jurisdiction: Optional[str] = None,
    **overrides: Any,
) -> ModelCard:
    """
    Create a valid ModelCard in ~5 lines.

    Args:
        model_name: Name of the model
        description: Short description of the model
        developer: Developer or organization name
        contact: Support contact email or URL
        template: Template ID (default: "screening_tool").
                  Options: copd_risk_predictor, screening_tool,
                  diagnostic_classifier, triage_model, monitoring_model
        jurisdiction: Optional regulatory jurisdiction ("eu", "us", "both")
        **overrides: Override any template defaults.
                     Flat keys go to model_details (e.g., algorithms_used="RF").
                     Use section__field syntax for other sections
                     (e.g., intended_use__contraindications="None known").

    Returns:
        A validated ModelCard ready for export.

    Example:
        >>> card = quick_card(
        ...     model_name="My Model",
        ...     description="A screening model",
        ...     developer="My Org",
        ...     contact="team@myorg.com",
        ...     template="screening_tool",
        ...     jurisdiction="eu",
        ... )
        >>> card.to_dict()  # ready to export
    """
    if template not in TEMPLATES:
        available = ", ".join(sorted(TEMPLATES.keys()))
        raise ValueError(f"Unknown template '{template}'. Available: {available}")

    tmpl = copy.deepcopy(TEMPLATES[template])
    sections = tmpl["sections"]

    md_kwargs = dict(sections["model_details"])
    md_kwargs["model_name"] = model_name
    md_kwargs["description"] = description
    md_kwargs["developer_organization"] = developer
    md_kwargs["support_contact"] = contact
    md_kwargs["version"] = "1.0.0"
    md_kwargs["release_date"] = date.today().isoformat()
    md_kwargs["licensing"] = "To be specified"

    if jurisdiction:
        jurisdiction = jurisdiction.lower()
        if jurisdiction not in REGULATORY_PRESETS:
            raise ValueError(f"Unknown jurisdiction '{jurisdiction}'. Available: eu, us, both")
        preset = REGULATORY_PRESETS[jurisdiction]
        md_kwargs["regulatory_classifications"] = copy.deepcopy(preset["classifications"])

    section_overrides: Dict[str, Dict[str, Any]] = {}
    for key, value in overrides.items():
        if "__" in key:
            section_name, field_name = key.split("__", 1)
            section_overrides.setdefault(section_name, {})[field_name] = value
        else:
            md_kwargs[key] = value

    model_details = ModelDetails(**md_kwargs)

    iu_kwargs = dict(sections["intended_use"])
    iu_kwargs.update(section_overrides.get("intended_use", {}))
    intended_use = IntendedUse(**iu_kwargs)

    df_kwargs = dict(sections["data_factors"])
    df_kwargs.update(section_overrides.get("data_factors", {}))
    raw_datasets = df_kwargs.pop("source_datasets", [])
    df_kwargs["source_datasets"] = [
        SourceDataset(**ds) if isinstance(ds, dict) else ds
        for ds in raw_datasets
    ]
    data_factors = DataFactors(**df_kwargs)

    fo_kwargs = dict(sections["features_outputs"])
    fo_kwargs.update(section_overrides.get("features_outputs", {}))
    raw_inputs = fo_kwargs.pop("input_features", [])
    raw_outputs = fo_kwargs.pop("output_features", [])
    fo_kwargs["input_features"] = [
        InputFeature(**f) if isinstance(f, dict) else f
        for f in raw_inputs
    ]
    fo_kwargs["output_features"] = [
        OutputFeature(**f) if isinstance(f, dict) else f
        for f in raw_outputs
    ]
    features_outputs = FeaturesOutputs(**fo_kwargs)

    pv_kwargs = dict(sections["performance"])
    pv_kwargs.update(section_overrides.get("performance", {}))
    raw_vds = pv_kwargs.pop("validation_datasets", [])
    raw_claimed = pv_kwargs.pop("claimed_metrics", [])
    raw_validated = pv_kwargs.pop("validated_metrics", [])
    pv_kwargs["validation_datasets"] = [
        ValidationDataset(**vd) if isinstance(vd, dict) else vd
        for vd in raw_vds
    ]
    pv_kwargs["claimed_metrics"] = [
        PerformanceMetric(**m) if isinstance(m, dict) else m
        for m in raw_claimed
    ]
    pv_kwargs["validated_metrics"] = [
        PerformanceMetric(**m) if isinstance(m, dict) else m
        for m in raw_validated
    ]
    performance = PerformanceValidation(**pv_kwargs)

    meth_kwargs = dict(sections["methodology"])
    meth_kwargs.update(section_overrides.get("methodology", {}))
    methodology = Methodology(**meth_kwargs)

    ai_kwargs = dict(sections["additional_info"])
    ai_kwargs.update(section_overrides.get("additional_info", {}))
    additional_info = AdditionalInfo(**ai_kwargs)

    card = ModelCard()
    card.set_model_details(model_details)
    card.set_intended_use(intended_use)
    card.set_data_factors(data_factors)
    card.set_features_outputs(features_outputs)
    card.set_performance_validation(performance)
    card.set_methodology(methodology)
    card.set_additional_info(additional_info)

    card.validate()
    return card
