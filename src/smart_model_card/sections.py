"""
Model Card Section Definitions

Implements the 7 standard sections for medical AI model cards with all fields
from the standardized template.

Author: Ankur Lohachab
Department of Advanced Computing Sciences, Maastricht University
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
import math
import re


def _validate_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _validate_date_iso(value: str, field_name: str) -> None:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except Exception as exc:
        raise ValueError(f"{field_name} must be in ISO format YYYY-MM-DD") from exc


def _normalize_enum(
    value: str,
    field_name: str,
    allowed: List[str],
    aliases: Optional[Dict[str, str]] = None
) -> str:
    if value is None:
        raise ValueError(f"{field_name} must be provided")

    aliases = aliases or {}

    def normalize_token(token: str) -> str:
        canonical = re.sub(r"[\s\-]+", "_", token.strip().lower())
        if not canonical:
            raise ValueError(f"{field_name} must not contain empty choices")
        if canonical in allowed:
            return canonical
        if canonical in aliases:
            return aliases[canonical]
        raise ValueError(f"{field_name} must be one of {allowed}")

    tokens = re.split(r"[;,]+", value) if re.search(r"[;,]", value) else [value]
    normalized_tokens = [normalize_token(tok) for tok in tokens if tok.strip()]
    return ", ".join(normalized_tokens)


def _validate_email_or_url(value: str, field_name: str) -> None:
    if value is None:
        raise ValueError(f"{field_name} must be provided")
    if "@" in value or value.startswith("http"):
        return
    raise ValueError(f"{field_name} must be an email or URL")


def _capture(errors: Optional[List[str]], section: str, field: str, func) -> None:
    """
    Run validation function and either raise or append errors.

    If errors list is provided, append formatted message instead of raising.
    """
    try:
        func()
    except ValueError as exc:
        if errors is None:
            raise
        errors.append(f"{section} -> {field}: {exc}")


PHI_KEYWORDS = [
    "patient name",
    "mrn",
    "medical record number",
    "ssn",
    "social security",
    "address",
    "phone",
    "email",
    "date of birth",
    "dob",
    "street",
    "zip",
    "postal",
    "contact",
    "guardian",
    "relative",
    "employer"
]


def _check_phi_leak(value, field_name: str, errors: Optional[List[str]]) -> None:
    """Check for PHI keywords in string or dict values"""
    if isinstance(value, dict):
        for k, v in value.items():
            if isinstance(v, str):
                _check_phi_leak(v, f"{field_name}.{k}", errors)
        return

    if not isinstance(value, str):
        return

    lower = value.lower()
    for kw in PHI_KEYWORDS:
        if kw in lower:
            _capture(errors, "PHI Guard", field_name, lambda: (_ for _ in ()).throw(ValueError(f"Potential PHI keyword detected: {kw}")))


@dataclass
class Annotation:
    """Free-form notes/comments for interoperability and review."""
    author: str
    note: str
    created_at: str = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "author": self.author,
            "note": self.note,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> Annotation:
        return cls(
            author=d.get("author", ""),
            note=d.get("note", ""),
            created_at=d.get("created_at", datetime.utcnow().isoformat()),
        )


@dataclass
class ModelDetails:
    """Section 1: Model Details"""
    model_name: str
    version: str
    developer_organization: str
    release_date: str
    description: str
    clinical_function: str
    algorithms_used: str
    licensing: str
    support_contact: str

    gmdn_code: Optional[str] = None
    literature_references: Optional[List[str]] = None
    clinical_study_references: Optional[List[str]] = None
    logo_image: Optional[str] = None
    intended_purpose: Optional[str] = None
    information_significance: Optional[str] = None
    basic_udi_di: Optional[str] = None
    udi_di: Optional[str] = None
    regulatory_classifications: Optional[List[Dict[str, str]]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Model Name": self.model_name,
            "Version": self.version,
            "Developer / Organization": self.developer_organization,
            "Release Date": self.release_date,
            "Description": self.description,
            "Clinical Function": self.clinical_function,
            "Intended Purpose": self.intended_purpose,
            "Information Significance": self.information_significance,
            "Algorithm(s) Used": self.algorithms_used,
            "GMDN Code": self.gmdn_code,
            "Basic UDI-DI": self.basic_udi_di,
            "UDI-DI": self.udi_di,
            "Regulatory Classifications": self.regulatory_classifications if self.regulatory_classifications else [],
            "Licensing": self.licensing,
            "Support Contact": self.support_contact,
            "Literature References": self.literature_references or [],
            "Clinical Study References": self.clinical_study_references or [],
            "Logo / Image (optional)": self.logo_image
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ModelDetails:
        return cls(
            model_name=d.get("Model Name", ""),
            version=d.get("Version", ""),
            developer_organization=d.get("Developer / Organization", ""),
            release_date=d.get("Release Date", ""),
            description=d.get("Description", ""),
            clinical_function=d.get("Clinical Function", ""),
            algorithms_used=d.get("Algorithm(s) Used", ""),
            licensing=d.get("Licensing", ""),
            support_contact=d.get("Support Contact", ""),
            gmdn_code=d.get("GMDN Code"),
            literature_references=d.get("Literature References") or None,
            clinical_study_references=d.get("Clinical Study References") or None,
            logo_image=d.get("Logo / Image (optional)"),
            intended_purpose=d.get("Intended Purpose"),
            information_significance=d.get("Information Significance"),
            basic_udi_di=d.get("Basic UDI-DI"),
            udi_di=d.get("UDI-DI"),
            regulatory_classifications=d.get("Regulatory Classifications") or None,
        )

    def validate(self, errors: Optional[List[str]] = None) -> None:
        section = "Model Details"
        _capture(errors, section, "Model Name", lambda: _validate_non_empty(self.model_name, "Model Name"))
        _capture(errors, section, "Version", lambda: _validate_non_empty(self.version, "Version"))
        _capture(errors, section, "Developer / Organization", lambda: _validate_non_empty(self.developer_organization, "Developer / Organization"))
        _capture(errors, section, "Release Date", lambda: _validate_date_iso(self.release_date, "Release Date"))
        _capture(errors, section, "Description", lambda: _validate_non_empty(self.description, "Description"))
        allowed_purposes = [
            "diagnosis",
            "screening",
            "triage",
            "monitoring",
            "decision_support",
            "workflow_support",
            "other"
        ]
        purpose_aliases = {
            "clinical_decision_support": "decision_support",
            "cds": "decision_support",
            "workflow": "workflow_support"
        }
        _capture(
            errors,
            section,
            "Clinical Function",
            lambda: setattr(
                self,
                "clinical_function",
                _normalize_enum(self.clinical_function, "Clinical Function", allowed_purposes, purpose_aliases)
            )
        )
        if self.information_significance is not None:
            allowed_significance = ["inform", "drive", "treat_or_diagnose"]
            _capture(
                errors,
                section,
                "Information Significance",
                lambda: setattr(
                    self,
                    "information_significance",
                    _normalize_enum(self.information_significance, "Information Significance", allowed_significance)
                )
            )
        if self.regulatory_classifications is not None:
            allowed_rc_keys = {"framework", "class", "rule", "pathway"}
            for i, entry in enumerate(self.regulatory_classifications):
                def _validate_rc_entry(idx=i, e=entry):
                    if not isinstance(e, dict):
                        raise ValueError(f"Regulatory Classifications[{idx}]: must be a dict")
                    if not e.get("framework"):
                        raise ValueError(f"Regulatory Classifications[{idx}]: 'framework' is required")
                    if not e.get("class"):
                        raise ValueError(f"Regulatory Classifications[{idx}]: 'class' is required")
                    extra = set(e.keys()) - allowed_rc_keys
                    if extra:
                        raise ValueError(f"Regulatory Classifications[{idx}]: unknown fields {extra}")
                _capture(errors, section, f"Regulatory Classifications[{i}]", _validate_rc_entry)
        _capture(errors, section, "Algorithm(s) Used", lambda: _validate_non_empty(self.algorithms_used, "Algorithm(s) Used"))
        _capture(errors, section, "Licensing", lambda: _validate_non_empty(self.licensing, "Licensing"))
        _capture(errors, section, "Support Contact", lambda: _validate_email_or_url(self.support_contact, "Support Contact"))


@dataclass
class IntendedUse:
    """Section 2: Intended Use and Clinical Context"""
    primary_intended_users: str
    clinical_indications: str
    patient_target_group: str
    intended_use_environment: str

    contraindications: Optional[str] = None
    out_of_scope_applications: Optional[str] = None
    warnings: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Primary Intended Users": self.primary_intended_users,
            "Clinical Indications": self.clinical_indications,
            "Patient target group": self.patient_target_group,
            "Contraindications": self.contraindications,
            "Intended Use Environment": self.intended_use_environment,
            "Out of Scope Applications": self.out_of_scope_applications,
            "Warnings": self.warnings
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> IntendedUse:
        return cls(
            primary_intended_users=d.get("Primary Intended Users", ""),
            clinical_indications=d.get("Clinical Indications", ""),
            patient_target_group=d.get("Patient target group", ""),
            intended_use_environment=d.get("Intended Use Environment", ""),
            contraindications=d.get("Contraindications"),
            out_of_scope_applications=d.get("Out of Scope Applications"),
            warnings=d.get("Warnings"),
        )

    def validate(self, errors: Optional[List[str]] = None) -> None:
        section = "Intended Use and Clinical Context"
        _capture(errors, section, "Primary Intended Users", lambda: _validate_non_empty(self.primary_intended_users, "Primary Intended Users"))
        _capture(errors, section, "Clinical Indications", lambda: _validate_non_empty(self.clinical_indications, "Clinical Indications"))
        _capture(errors, section, "Patient target group", lambda: _validate_non_empty(self.patient_target_group, "Patient target group"))
        _check_phi_leak(self.primary_intended_users, "Primary Intended Users", errors)
        _check_phi_leak(self.clinical_indications, "Clinical Indications", errors)
        _check_phi_leak(self.patient_target_group, "Patient target group", errors)
        if self.contraindications:
            _check_phi_leak(self.contraindications, "Contraindications", errors)
        if self.out_of_scope_applications:
            _check_phi_leak(self.out_of_scope_applications, "Out of Scope Applications", errors)
        if self.warnings:
            _check_phi_leak(self.warnings, "Warnings", errors)
        env_allowed = [
            "hospital_inpatient",
            "hospital_outpatient",
            "emergency",
            "telemedicine",
            "research",
            "home",
            "other"
        ]
        env_aliases = {
            "inpatient": "hospital_inpatient",
            "outpatient": "hospital_outpatient",
            "outpatient_clinic": "hospital_outpatient",
            "outpatient_clinics": "hospital_outpatient",
            "hospital_departments": "hospital_inpatient",
            "ed": "emergency",
            "telehealth": "telemedicine",
            "home_care": "home",
            "primary_care": "hospital_outpatient"
        }
        _capture(
            errors,
            section,
            "Intended Use Environment",
            lambda: setattr(
                self,
                "intended_use_environment",
                _normalize_enum(self.intended_use_environment, "Intended Use Environment", env_allowed, env_aliases)
            )
        )


@dataclass
class ConceptSet:
    """OMOP/SNOMED/LOINC concept set definition"""
    name: str
    vocabulary: str
    concept_ids: List[int]
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ConceptSet:
        return cls(
            name=d.get("name", ""),
            vocabulary=d.get("vocabulary", ""),
            concept_ids=d.get("concept_ids", []),
            description=d.get("description"),
        )


@dataclass
class CohortCriteria:
    """Primary cohort inclusion/exclusion criteria"""
    inclusion_rules: List[str]
    exclusion_rules: List[str]
    observation_window: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> CohortCriteria:
        return cls(
            inclusion_rules=d.get("inclusion_rules", []),
            exclusion_rules=d.get("exclusion_rules", []),
            observation_window=d.get("observation_window"),
        )


@dataclass
class SourceDataset:
    """Source dataset metadata"""
    name: str
    origin: str
    size: int
    collection_period: str
    population_characteristics: str
    demographics: Optional[Dict[str, str]] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> SourceDataset:
        return cls(
            name=d.get("name", ""),
            origin=d.get("origin", ""),
            size=d.get("size", 0),
            collection_period=d.get("collection_period", ""),
            population_characteristics=d.get("population_characteristics", ""),
            demographics=d.get("demographics"),
        )


@dataclass
class DataFactors:
    """Section 3: Data & Factors"""
    source_datasets: List[SourceDataset]
    data_distribution_summary: Union[str, Dict[str, str]]
    data_representativeness: str
    data_governance: str
    deid_method: Optional[str] = None
    date_handling: Optional[str] = None
    cell_suppression: Optional[str] = None
    deid_report_uri: Optional[str] = None
    deid_report_hash: Optional[str] = None

    concept_sets: Optional[List[ConceptSet]] = None
    primary_cohort_criteria: Optional[CohortCriteria] = None
    omop_detailed_reports: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Concept Sets": [
                {
                    "name": cs.name,
                    "vocabulary": cs.vocabulary,
                    "concept_ids": cs.concept_ids,
                    "description": cs.description
                } for cs in (self.concept_sets or [])
            ],
            "Primary Cohort Criteria": {
                "inclusion_rules": self.primary_cohort_criteria.inclusion_rules if self.primary_cohort_criteria else [],
                "exclusion_rules": self.primary_cohort_criteria.exclusion_rules if self.primary_cohort_criteria else [],
                "observation_window": self.primary_cohort_criteria.observation_window if self.primary_cohort_criteria else None
            } if self.primary_cohort_criteria else None,
            "Source Datasets": [
                {
                    "name": ds.name,
                    "origin": ds.origin,
                    "size": ds.size,
                    "collection_period": ds.collection_period,
                    "population_characteristics": ds.population_characteristics,
                    "demographics": ds.demographics if ds.demographics else None
                } for ds in self.source_datasets
            ],
            "Data Distribution Summary": self.data_distribution_summary,
            "Data Representativeness": self.data_representativeness,
            "Data Governance": self.data_governance,
            "De-identification Method": self.deid_method,
            "Date Handling": self.date_handling,
            "Cell-size Suppression": self.cell_suppression,
            "De-id Report URI": self.deid_report_uri,
            "De-id Report Hash": self.deid_report_hash,
            "OMOP Detailed Reports": self.omop_detailed_reports
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> DataFactors:
        concept_sets = None
        raw_cs = d.get("Concept Sets")
        if raw_cs:
            concept_sets = [ConceptSet.from_dict(cs) for cs in raw_cs]

        cohort_criteria = None
        raw_cc = d.get("Primary Cohort Criteria")
        if raw_cc:
            cohort_criteria = CohortCriteria.from_dict(raw_cc)

        source_datasets = [
            SourceDataset.from_dict(ds)
            for ds in d.get("Source Datasets", [])
        ]

        return cls(
            source_datasets=source_datasets,
            data_distribution_summary=d.get("Data Distribution Summary", ""),
            data_representativeness=d.get("Data Representativeness", ""),
            data_governance=d.get("Data Governance", ""),
            deid_method=d.get("De-identification Method"),
            date_handling=d.get("Date Handling"),
            cell_suppression=d.get("Cell-size Suppression"),
            deid_report_uri=d.get("De-id Report URI"),
            deid_report_hash=d.get("De-id Report Hash"),
            concept_sets=concept_sets,
            primary_cohort_criteria=cohort_criteria,
            omop_detailed_reports=d.get("OMOP Detailed Reports"),
        )

    def validate(self, errors: Optional[List[str]] = None) -> None:
        section = "Data & Factors"
        _capture(
            errors,
            section,
            "Source Datasets",
            lambda: None if self.source_datasets else _validate_non_empty("", "Source Datasets")
        )
        for ds in self.source_datasets or []:
            _capture(
                errors,
                section,
                "Source Dataset size",
                lambda: None if (ds.size is not None and ds.size >= 0) else _validate_non_empty("", "Source Dataset size >= 0")
            )
        if isinstance(self.data_distribution_summary, dict):
            _capture(errors, section, "Data Distribution Summary", lambda: None if self.data_distribution_summary else _validate_non_empty("", "Data Distribution Summary"))
        else:
            _capture(errors, section, "Data Distribution Summary", lambda: _validate_non_empty(self.data_distribution_summary, "Data Distribution Summary"))

        _capture(errors, section, "Data Representativeness", lambda: _validate_non_empty(self.data_representativeness, "Data Representativeness"))
        _capture(errors, section, "Data Governance", lambda: _validate_non_empty(self.data_governance, "Data Governance"))

        if self.data_distribution_summary:
            _check_phi_leak(self.data_distribution_summary, "Data Distribution Summary", errors)
        if self.data_governance:
            _check_phi_leak(self.data_governance, "Data Governance", errors)
        if self.deid_method:
            _check_phi_leak(self.deid_method, "De-identification Method", errors)


@dataclass
class InputFeature:
    """Model input feature specification"""
    name: str
    data_type: str
    required: bool
    clinical_domain: str
    value_range: Optional[str] = None
    units: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> InputFeature:
        return cls(
            name=d.get("name", ""),
            data_type=d.get("data_type", ""),
            required=d.get("required", True),
            clinical_domain=d.get("clinical_domain", ""),
            value_range=d.get("value_range"),
            units=d.get("units"),
        )


@dataclass
class OutputFeature:
    """Model output specification"""
    name: str
    type: str
    units: Optional[str] = None
    value_range: Optional[str] = None
    classes: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> OutputFeature:
        return cls(
            name=d.get("name", ""),
            type=d.get("type", ""),
            units=d.get("units"),
            value_range=d.get("value_range"),
            classes=d.get("classes"),
        )


@dataclass
class FeaturesOutputs:
    """Section 4: Features & Outputs"""
    input_features: List[InputFeature]
    output_features: List[OutputFeature]
    feature_type_distribution: str
    uncertainty_quantification: str
    output_interpretability: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Input Features": [
                {
                    "name": f.name,
                    "data_type": f.data_type,
                    "required": f.required,
                    "clinical_domain": f.clinical_domain,
                    "value_range": f.value_range,
                    "units": f.units
                } for f in self.input_features
            ],
            "Output Features": [
                {
                    "name": f.name,
                    "type": f.type,
                    "units": f.units,
                    "value_range": f.value_range,
                    "classes": f.classes
                } for f in self.output_features
            ],
            "Feature Type Distribution": self.feature_type_distribution,
            "Uncertainty Quantification": self.uncertainty_quantification,
            "Output Interpretability": self.output_interpretability
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> FeaturesOutputs:
        return cls(
            input_features=[
                InputFeature.from_dict(f) for f in d.get("Input Features", [])
            ],
            output_features=[
                OutputFeature.from_dict(f) for f in d.get("Output Features", [])
            ],
            feature_type_distribution=d.get("Feature Type Distribution", ""),
            uncertainty_quantification=d.get("Uncertainty Quantification", ""),
            output_interpretability=d.get("Output Interpretability", ""),
        )

    def validate(self, errors: Optional[List[str]] = None) -> None:
        section = "Features & Outputs"
        _capture(
            errors,
            section,
            "Input Features",
            lambda: None if self.input_features else _validate_non_empty("", "Input Features")
        )
        allowed_input_types = ["numeric", "categorical", "text", "image", "signal", "other"]
        input_aliases = {"numerical": "numeric"}
        for f in self.input_features or []:
            _capture(errors, section, "Input Feature name", lambda: _validate_non_empty(f.name, "Input Feature name"))
            _capture(
                errors,
                section,
                "Input Feature data_type",
                lambda: setattr(
                    f,
                    "data_type",
                    _normalize_enum(f.data_type, "Input Feature data_type", allowed_input_types, input_aliases)
                )
            )
        _capture(
            errors,
            section,
            "Output Features",
            lambda: None if self.output_features else _validate_non_empty("", "Output Features")
        )
        allowed_output_types = ["classification", "regression", "probability", "score", "segmentation", "text", "other"]
        output_aliases = {"class": "classification"}
        for f in self.output_features or []:
            _capture(errors, section, "Output Feature name", lambda: _validate_non_empty(f.name, "Output Feature name"))
            _capture(
                errors,
                section,
                "Output Feature type",
                lambda: setattr(
                    f,
                    "type",
                    _normalize_enum(f.type, "Output Feature type", allowed_output_types, output_aliases)
                )
            )
        _capture(errors, section, "Feature Type Distribution", lambda: _validate_non_empty(self.feature_type_distribution, "Feature Type Distribution"))
        _capture(errors, section, "Uncertainty Quantification", lambda: _validate_non_empty(self.uncertainty_quantification, "Uncertainty Quantification"))
        _capture(errors, section, "Output Interpretability", lambda: _validate_non_empty(self.output_interpretability, "Output Interpretability"))


@dataclass
class ValidationDataset:
    """Validation dataset specification"""
    name: str
    source_institution: str
    population_characteristics: str
    validation_type: str

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ValidationDataset:
        return cls(
            name=d.get("name", ""),
            source_institution=d.get("source_institution", ""),
            population_characteristics=d.get("population_characteristics", ""),
            validation_type=d.get("validation_type", ""),
        )


@dataclass
class PerformanceMetric:
    """Performance metric with validation status"""
    metric_name: str
    value: float
    validation_status: str
    subgroup: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> PerformanceMetric:
        return cls(
            metric_name=d.get("metric_name", ""),
            value=d.get("value", 0.0),
            validation_status=d.get("validation_status", ""),
            subgroup=d.get("subgroup"),
        )


@dataclass
class PerformanceValidation:
    """Section 5: Performance & Validation"""
    validation_datasets: List[ValidationDataset]
    claimed_metrics: List[PerformanceMetric]
    validated_metrics: List[PerformanceMetric]

    calibration_analysis: Optional[str] = None
    fairness_assessment: Optional[str] = None
    metric_validation_status: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Validation Dataset(s)": [
                {
                    "name": vd.name,
                    "source_institution": vd.source_institution,
                    "population_characteristics": vd.population_characteristics,
                    "validation_type": vd.validation_type
                } for vd in self.validation_datasets
            ],
            "Claimed Metrics": [
                {
                    "metric_name": m.metric_name,
                    "value": m.value,
                    "validation_status": m.validation_status,
                    "subgroup": m.subgroup
                } for m in self.claimed_metrics
            ],
            "Validated Metrics": [
                {
                    "metric_name": m.metric_name,
                    "value": m.value,
                    "validation_status": m.validation_status,
                    "subgroup": m.subgroup
                } for m in self.validated_metrics
            ],
            "Calibration Analysis": self.calibration_analysis,
            "Fairness Assessment": self.fairness_assessment,
            "Metric Validation Status": self.metric_validation_status
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> PerformanceValidation:
        return cls(
            validation_datasets=[
                ValidationDataset.from_dict(vd)
                for vd in d.get("Validation Dataset(s)", [])
            ],
            claimed_metrics=[
                PerformanceMetric.from_dict(m)
                for m in d.get("Claimed Metrics", [])
            ],
            validated_metrics=[
                PerformanceMetric.from_dict(m)
                for m in d.get("Validated Metrics", [])
            ],
            calibration_analysis=d.get("Calibration Analysis"),
            fairness_assessment=d.get("Fairness Assessment"),
            metric_validation_status=d.get("Metric Validation Status"),
        )

    def validate(self, errors: Optional[List[str]] = None) -> None:
        section = "Performance & Validation"
        _capture(
            errors,
            section,
            "Validation Dataset(s)",
            lambda: None if self.validation_datasets else _validate_non_empty("", "Validation Dataset(s)")
        )
        allowed_statuses = ["claimed", "internal", "external", "validated"]

        def _validate_metric_status(status: str, field_name: str) -> None:
            if status is None:
                raise ValueError(f"{field_name} validation_status must be provided")
            normalized = status.lower()
            if not any(normalized.startswith(s) for s in allowed_statuses):
                raise ValueError(f"{field_name} validation_status must start with one of {allowed_statuses}")

        prob_metric_tokens = [
            "auc",
            "roc",
            "pr",
            "precision",
            "recall",
            "specificity",
            "sensitivity",
            "f1",
            "dice",
            "iou",
            "brier",
            "accuracy"
        ]

        def _validate_metric_value(metric: PerformanceMetric) -> None:
            if metric.value is None or not math.isfinite(metric.value):
                raise ValueError("PerformanceMetric value must be a finite number")
            name_norm = (metric.metric_name or "").lower()
            if any(tok in name_norm for tok in prob_metric_tokens):
                if metric.value < 0.0 or metric.value > 1.0:
                    raise ValueError(f"PerformanceMetric '{metric.metric_name}' must be within [0, 1]")

        for m in self.claimed_metrics + self.validated_metrics:
            _capture(errors, section, "PerformanceMetric validation_status", lambda: _validate_metric_status(m.validation_status, "PerformanceMetric"))
            _capture(errors, section, f"PerformanceMetric {m.metric_name} value", lambda: _validate_metric_value(m))
        _capture(errors, section, "Metric Validation Status", lambda: _validate_non_empty(self.metric_validation_status or "Validated", "Metric Validation Status"))


@dataclass
class Methodology:
    """Section 6: Methodology & Explainability"""
    model_development_workflow: str
    training_procedure: str
    data_preprocessing: str

    synthetic_data_usage: Optional[str] = None
    explainable_ai_method: Optional[str] = None
    global_vs_local_interpretability: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Model Development Workflow": self.model_development_workflow,
            "Training Procedure": self.training_procedure,
            "Data Preprocessing": self.data_preprocessing,
            "Synthetic Data Usage": self.synthetic_data_usage,
            "Explainable AI Method": self.explainable_ai_method,
            "Global vs. Local Interpretability": self.global_vs_local_interpretability
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> Methodology:
        return cls(
            model_development_workflow=d.get("Model Development Workflow", ""),
            training_procedure=d.get("Training Procedure", ""),
            data_preprocessing=d.get("Data Preprocessing", ""),
            synthetic_data_usage=d.get("Synthetic Data Usage"),
            explainable_ai_method=d.get("Explainable AI Method"),
            global_vs_local_interpretability=d.get("Global vs. Local Interpretability"),
        )

    def validate(self, errors: Optional[List[str]] = None) -> None:
        section = "Methodology & Explainability"
        _capture(errors, section, "Model Development Workflow", lambda: _validate_non_empty(self.model_development_workflow, "Model Development Workflow"))
        _capture(errors, section, "Training Procedure", lambda: _validate_non_empty(self.training_procedure, "Training Procedure"))
        _capture(errors, section, "Data Preprocessing", lambda: _validate_non_empty(self.data_preprocessing, "Data Preprocessing"))


@dataclass
class AdditionalInfo:
    """Section 7: Additional Information"""
    benefit_risk_summary: str
    ethical_considerations: str
    caveats_limitations: str
    recommendations_for_safe_use: str

    post_market_surveillance_plan: Optional[str] = None
    explainability_recommendations: Optional[str] = None
    supporting_documents: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Benefit–Risk Summary": self.benefit_risk_summary,
            "Post-Market Surveillance Plan": self.post_market_surveillance_plan,
            "Ethical Considerations": self.ethical_considerations,
            "Caveats & Limitations": self.caveats_limitations,
            "Recommendations for Safe Use": self.recommendations_for_safe_use,
            "Explainability Recommendations": self.explainability_recommendations,
            "Supporting Documents": self.supporting_documents or []
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> AdditionalInfo:
        docs = d.get("Supporting Documents") or None
        return cls(
            benefit_risk_summary=d.get("Benefit\u2013Risk Summary", ""),
            ethical_considerations=d.get("Ethical Considerations", ""),
            caveats_limitations=d.get("Caveats & Limitations", ""),
            recommendations_for_safe_use=d.get("Recommendations for Safe Use", ""),
            post_market_surveillance_plan=d.get("Post-Market Surveillance Plan"),
            explainability_recommendations=d.get("Explainability Recommendations"),
            supporting_documents=docs if docs else None,
        )

    def validate(self, errors: Optional[List[str]] = None) -> None:
        section = "Additional Information"
        _capture(errors, section, "Benefit–Risk Summary", lambda: _validate_non_empty(self.benefit_risk_summary, "Benefit–Risk Summary"))
        _capture(errors, section, "Ethical Considerations", lambda: _validate_non_empty(self.ethical_considerations, "Ethical Considerations"))
        _capture(errors, section, "Caveats & Limitations", lambda: _validate_non_empty(self.caveats_limitations, "Caveats & Limitations"))
        _capture(errors, section, "Recommendations for Safe Use", lambda: _validate_non_empty(self.recommendations_for_safe_use, "Recommendations for Safe Use"))
        _check_phi_leak(self.benefit_risk_summary, "Benefit–Risk Summary", errors)
        _check_phi_leak(self.ethical_considerations, "Ethical Considerations", errors)
        _check_phi_leak(self.caveats_limitations, "Caveats & Limitations", errors)
        _check_phi_leak(self.recommendations_for_safe_use, "Recommendations for Safe Use", errors)
