"""
Tests for from_dict() / from_json() round-trip deserialization.

Verifies that card.to_dict() -> ModelCard.from_dict() -> .to_dict()
produces an identical dictionary, and that from_json() works from file.

Author: Ankur Lohachab
Department of Advanced Computing Sciences, Maastricht University
"""

import json
import os
import tempfile

import pytest

from smart_model_card import ModelCard, ModelDetails, IntendedUse
from smart_model_card.sections import (
    DataFactors,
    FeaturesOutputs,
    PerformanceValidation,
    Methodology,
    AdditionalInfo,
    Annotation,
    SourceDataset,
    InputFeature,
    OutputFeature,
    ValidationDataset,
    PerformanceMetric,
    ConceptSet,
    CohortCriteria,
)


def _build_minimal_card() -> ModelCard:
    """Build a minimal valid card."""
    card = ModelCard()
    card.set_model_details(ModelDetails(
        model_name="Test",
        version="1.0.0",
        developer_organization="Test Org",
        release_date="2025-01-01",
        description="A test model",
        clinical_function="decision_support",
        algorithms_used="Logistic Regression",
        licensing="MIT",
        support_contact="test@example.com",
    ))
    card.set_intended_use(IntendedUse(
        primary_intended_users="Clinicians",
        clinical_indications="COPD risk",
        patient_target_group="Adults 40+",
        intended_use_environment="hospital_outpatient",
    ))
    card.set_data_factors(DataFactors(
        source_datasets=[SourceDataset("DS1", "Hospital A", 1000, "2020-2024", "Adults")],
        data_distribution_summary="Balanced",
        data_representativeness="Representative",
        data_governance="IRB approved",
    ))
    card.set_features_outputs(FeaturesOutputs(
        input_features=[InputFeature("age", "numeric", True, "Demographics")],
        output_features=[OutputFeature("risk_score", "probability")],
        feature_type_distribution="80% numeric, 20% categorical",
        uncertainty_quantification="Confidence intervals",
        output_interpretability="SHAP values",
    ))
    card.set_performance_validation(PerformanceValidation(
        validation_datasets=[ValidationDataset("Val1", "Hospital B", "Adults", "internal")],
        claimed_metrics=[PerformanceMetric("AUC", 0.85, "Claimed")],
        validated_metrics=[PerformanceMetric("AUC", 0.83, "Validated")],
    ))
    card.set_methodology(Methodology(
        model_development_workflow="Standard ML pipeline",
        training_procedure="5-fold cross-validation",
        data_preprocessing="Standardization and imputation",
    ))
    card.set_additional_info(AdditionalInfo(
        benefit_risk_summary="Benefits outweigh risks for intended population",
        ethical_considerations="No known ethical concerns",
        caveats_limitations="Limited to adult COPD patients",
        recommendations_for_safe_use="Use as decision support only",
    ))
    return card


def _build_full_card() -> ModelCard:
    """Build a fully populated card with all optional fields and v3 fields."""
    card = _build_minimal_card()

    card.set_model_details(ModelDetails(
        model_name="COPD-Risk-Predictor",
        version="2.0.0",
        developer_organization="Maastricht University",
        release_date="2025-06-15",
        description="XGBoost model for COPD exacerbation risk",
        clinical_function="decision_support",
        algorithms_used="XGBoost",
        licensing="Apache-2.0",
        support_contact="research@maastricht.nl",
        gmdn_code="GMDN-12345",
        literature_references=["Smith et al. 2024", "Jones et al. 2023"],
        clinical_study_references=["NCT123456", "NCT789012"],
        logo_image="logo.png",
        intended_purpose="Software intended to estimate 5-year COPD exacerbation risk",
        information_significance="inform",
        basic_udi_di="R8546SMART10",
        udi_di="R8546SMART10V200",
        regulatory_classifications=[
            {"framework": "EU MDR", "class": "IIa", "rule": "Rule 11"},
            {"framework": "FDA", "class": "II", "pathway": "510(k)"},
        ],
    ))

    card.set_intended_use(IntendedUse(
        primary_intended_users="Pulmonologists",
        clinical_indications="COPD exacerbation risk assessment",
        patient_target_group="Adults 40+ with confirmed COPD",
        intended_use_environment="hospital_outpatient",
        contraindications="Not for use in pediatric patients",
        out_of_scope_applications="Not for asthma patients",
        warnings="Must be used with clinical judgment",
    ))

    card.set_data_factors(DataFactors(
        source_datasets=[
            SourceDataset("COPD-EHR", "Hospital A", 5000, "2018-2024", "COPD patients",
                          demographics={"age_range": "40-90", "gender": "60% male"}),
            SourceDataset("External-Val", "Hospital B", 1000, "2020-2023", "External cohort"),
        ],
        data_distribution_summary={"age": "mean 65, std 12", "gender": "60% male"},
        data_representativeness="Multi-center European cohort",
        data_governance="Ethics committee approved, GDPR compliant",
        deid_method="k-anonymity with k=5",
        date_handling="Date shifting +/- 30 days",
        cell_suppression="Cells < 5 suppressed",
        deid_report_uri="https://example.com/deid-report",
        deid_report_hash="sha256:abc123",
        concept_sets=[
            ConceptSet("COPD Diagnosis", "SNOMED", [255573, 4063381], "COPD concepts"),
            ConceptSet("Spirometry", "LOINC", [19926, 20150], "Lung function tests"),
        ],
        primary_cohort_criteria=CohortCriteria(
            inclusion_rules=["Age >= 40", "COPD diagnosis (SNOMED 255573)"],
            exclusion_rules=["Active malignancy", "Lung transplant"],
            observation_window="365 days prior to index date",
        ),
        omop_detailed_reports={"cohort_id": 145, "person_count": 30},
    ))

    card.set_features_outputs(FeaturesOutputs(
        input_features=[
            InputFeature("age", "numeric", True, "Demographics", "18-100", "years"),
            InputFeature("fev1", "numeric", True, "Pulmonology", "0-6", "liters"),
            InputFeature("smoking_status", "categorical", True, "Lifestyle"),
        ],
        output_features=[
            OutputFeature("risk_score", "probability", None, "0-1"),
            OutputFeature("risk_category", "classification", None, None, ["low", "medium", "high"]),
        ],
        feature_type_distribution="67% numeric, 33% categorical",
        uncertainty_quantification="Bootstrap confidence intervals",
        output_interpretability="SHAP values with local explanations",
    ))

    card.set_performance_validation(PerformanceValidation(
        validation_datasets=[
            ValidationDataset("Internal-Val", "Hospital A", "Random 20% holdout", "internal"),
            ValidationDataset("External-Val", "Hospital B", "External cohort", "external"),
        ],
        claimed_metrics=[
            PerformanceMetric("AUC", 0.89, "Claimed"),
            PerformanceMetric("Sensitivity", 0.82, "Claimed"),
        ],
        validated_metrics=[
            PerformanceMetric("AUC", 0.86, "Validated"),
            PerformanceMetric("Sensitivity", 0.79, "Validated"),
            PerformanceMetric("AUC", 0.84, "Validated", subgroup="Female"),
        ],
        calibration_analysis="Hosmer-Lemeshow p=0.42",
        fairness_assessment="No significant disparity across gender/age groups",
        metric_validation_status="Externally validated",
    ))

    card.set_methodology(Methodology(
        model_development_workflow="CRISP-DM with clinical validation",
        training_procedure="5-fold stratified CV with early stopping",
        data_preprocessing="Missing value imputation, outlier removal, normalization",
        synthetic_data_usage="None",
        explainable_ai_method="SHAP (TreeExplainer)",
        global_vs_local_interpretability="Both global feature importance and local explanations",
    ))

    card.set_additional_info(AdditionalInfo(
        benefit_risk_summary="Early risk identification enables preventive interventions",
        ethical_considerations="Potential bias in underrepresented populations monitored",
        caveats_limitations="Limited to European COPD populations",
        recommendations_for_safe_use="Use as decision support only, clinical judgment required",
        post_market_surveillance_plan="Quarterly performance monitoring with drift detection",
        explainability_recommendations="Review SHAP explanations for clinical plausibility",
        supporting_documents=["clinical_study_report.pdf", "validation_protocol.docx"],
    ))

    card.annotations = [
        Annotation(author="Dr. Smith", note="Reviewed and approved for clinical use"),
        Annotation(author="Regulatory", note="Submitted for EU MDR conformity assessment"),
    ]

    card.retention_until = "2030-12-31T23:59:59"
    card.lifecycle_status = "active"

    return card


class TestFullRoundTrip:
    """Tests that to_dict() -> from_dict() -> to_dict() is identity."""

    def test_minimal_card_round_trip(self):
        card = _build_minimal_card()
        d1 = card.to_dict()
        card2 = ModelCard.from_dict(d1)
        d2 = card2.to_dict()
        assert d1 == d2

    def test_full_card_round_trip(self):
        card = _build_full_card()
        d1 = card.to_dict()
        card2 = ModelCard.from_dict(d1)
        d2 = card2.to_dict()
        assert d1 == d2

    def test_round_trip_preserves_created_at(self):
        card = _build_minimal_card()
        card.created_at = "2025-06-15T10:30:00"
        d1 = card.to_dict()
        card2 = ModelCard.from_dict(d1)
        assert card2.created_at == "2025-06-15T10:30:00"

    def test_round_trip_preserves_annotations(self):
        card = _build_full_card()
        d1 = card.to_dict()
        card2 = ModelCard.from_dict(d1)
        assert len(card2.annotations) == 2
        assert card2.annotations[0].author == "Dr. Smith"
        assert card2.annotations[1].note == "Submitted for EU MDR conformity assessment"

    def test_round_trip_preserves_lifecycle(self):
        card = _build_full_card()
        d1 = card.to_dict()
        card2 = ModelCard.from_dict(d1)
        assert card2.retention_until == "2030-12-31T23:59:59"
        assert card2.lifecycle_status == "active"


class TestFromJson:
    """Tests for ModelCard.from_json() convenience method."""

    def test_from_json_round_trip(self, tmp_path):
        card = _build_full_card()
        d1 = card.to_dict()
        path = str(tmp_path / "card.json")
        with open(path, "w") as f:
            json.dump(d1, f)
        card2 = ModelCard.from_json(path)
        d2 = card2.to_dict()
        assert d1 == d2

    def test_from_json_minimal(self, tmp_path):
        card = _build_minimal_card()
        d1 = card.to_dict()
        path = str(tmp_path / "minimal.json")
        with open(path, "w") as f:
            json.dump(d1, f)
        card2 = ModelCard.from_json(path)
        d2 = card2.to_dict()
        assert d1 == d2

    def test_from_json_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            ModelCard.from_json("/nonexistent/path.json")


class TestV3FieldsRoundTrip:
    """Tests that v3 schema fields survive the round-trip."""

    def test_clinical_function_survives(self):
        card = _build_minimal_card()
        d = card.to_dict()
        card2 = ModelCard.from_dict(d)
        assert card2.model_details.clinical_function == "decision_support"

    def test_intended_purpose_survives(self):
        card = _build_full_card()
        d = card.to_dict()
        card2 = ModelCard.from_dict(d)
        assert "5-year COPD" in card2.model_details.intended_purpose

    def test_information_significance_survives(self):
        card = _build_full_card()
        d = card.to_dict()
        card2 = ModelCard.from_dict(d)
        assert card2.model_details.information_significance == "inform"

    def test_udi_fields_survive(self):
        card = _build_full_card()
        d = card.to_dict()
        card2 = ModelCard.from_dict(d)
        assert card2.model_details.basic_udi_di == "R8546SMART10"
        assert card2.model_details.udi_di == "R8546SMART10V200"

    def test_regulatory_classifications_survive(self):
        card = _build_full_card()
        d = card.to_dict()
        card2 = ModelCard.from_dict(d)
        assert len(card2.model_details.regulatory_classifications) == 2
        assert card2.model_details.regulatory_classifications[0]["framework"] == "EU MDR"
        assert card2.model_details.regulatory_classifications[1]["pathway"] == "510(k)"

    def test_null_v3_fields_survive(self):
        card = _build_minimal_card()
        d = card.to_dict()
        card2 = ModelCard.from_dict(d)
        assert card2.model_details.intended_purpose is None
        assert card2.model_details.information_significance is None
        assert card2.model_details.basic_udi_di is None
        assert card2.model_details.udi_di is None


class TestModelDetailsFromDict:
    """Tests for ModelDetails.from_dict()."""

    def test_required_fields(self):
        d = {
            "Model Name": "Test",
            "Version": "1.0",
            "Developer / Organization": "Org",
            "Release Date": "2025-01-01",
            "Description": "A model",
            "Clinical Function": "screening",
            "Algorithm(s) Used": "RF",
            "Licensing": "MIT",
            "Support Contact": "a@b.com",
        }
        md = ModelDetails.from_dict(d)
        assert md.model_name == "Test"
        assert md.clinical_function == "screening"

    def test_optional_fields_default_none(self):
        d = {"Model Name": "X", "Version": "1", "Developer / Organization": "O",
             "Release Date": "2025-01-01", "Description": "D",
             "Clinical Function": "other", "Algorithm(s) Used": "A",
             "Licensing": "MIT", "Support Contact": "a@b.com"}
        md = ModelDetails.from_dict(d)
        assert md.gmdn_code is None
        assert md.intended_purpose is None
        assert md.information_significance is None
        assert md.basic_udi_di is None
        assert md.udi_di is None

    def test_regulatory_classifications_empty_list(self):
        d = {"Model Name": "X", "Version": "1", "Developer / Organization": "O",
             "Release Date": "2025-01-01", "Description": "D",
             "Clinical Function": "other", "Algorithm(s) Used": "A",
             "Licensing": "MIT", "Support Contact": "a@b.com",
             "Regulatory Classifications": []}
        md = ModelDetails.from_dict(d)
        assert md.regulatory_classifications is None


class TestIntendedUseFromDict:
    def test_round_trip(self):
        iu = IntendedUse(
            primary_intended_users="Doctors",
            clinical_indications="Diagnosis",
            patient_target_group="Adults",
            intended_use_environment="hospital_outpatient",
            contraindications="None known",
            warnings="Use with care",
        )
        d = iu.to_dict()
        iu2 = IntendedUse.from_dict(d)
        assert iu2.to_dict() == d


class TestDataFactorsFromDict:
    def test_round_trip_with_omop(self):
        df = DataFactors(
            source_datasets=[SourceDataset("DS", "Origin", 100, "2024", "Adults")],
            data_distribution_summary="Balanced",
            data_representativeness="Good",
            data_governance="Approved",
            concept_sets=[ConceptSet("CS1", "SNOMED", [123, 456], "Test")],
            primary_cohort_criteria=CohortCriteria(
                ["Age > 40"], ["Cancer"], "365 days"
            ),
            omop_detailed_reports={"cohort_id": 1},
        )
        d = df.to_dict()
        df2 = DataFactors.from_dict(d)
        assert df2.to_dict() == d

    def test_round_trip_without_omop(self):
        df = DataFactors(
            source_datasets=[SourceDataset("DS", "Origin", 100, "2024", "Adults")],
            data_distribution_summary="Balanced",
            data_representativeness="Good",
            data_governance="Approved",
        )
        d = df.to_dict()
        df2 = DataFactors.from_dict(d)
        assert df2.to_dict() == d

    def test_demographics_preserved(self):
        df = DataFactors(
            source_datasets=[SourceDataset("DS", "O", 50, "2024", "All",
                                            demographics={"age": "50+", "sex": "M/F"})],
            data_distribution_summary="Test",
            data_representativeness="Test",
            data_governance="Test",
        )
        d = df.to_dict()
        df2 = DataFactors.from_dict(d)
        assert df2.source_datasets[0].demographics == {"age": "50+", "sex": "M/F"}


class TestFeaturesOutputsFromDict:
    def test_round_trip(self):
        fo = FeaturesOutputs(
            input_features=[
                InputFeature("age", "numeric", True, "Demo", "0-120", "years"),
                InputFeature("gender", "categorical", True, "Demo"),
            ],
            output_features=[
                OutputFeature("prob", "probability", None, "0-1"),
                OutputFeature("class", "classification", None, None, ["A", "B"]),
            ],
            feature_type_distribution="50/50",
            uncertainty_quantification="CI",
            output_interpretability="SHAP",
        )
        d = fo.to_dict()
        fo2 = FeaturesOutputs.from_dict(d)
        assert fo2.to_dict() == d


class TestPerformanceValidationFromDict:
    def test_round_trip(self):
        pv = PerformanceValidation(
            validation_datasets=[
                ValidationDataset("V1", "HospA", "Adults", "internal"),
                ValidationDataset("V2", "HospB", "External", "external"),
            ],
            claimed_metrics=[PerformanceMetric("AUC", 0.9, "Claimed")],
            validated_metrics=[
                PerformanceMetric("AUC", 0.88, "Validated"),
                PerformanceMetric("AUC", 0.85, "Validated", subgroup="Female"),
            ],
            calibration_analysis="Good",
            fairness_assessment="Fair",
            metric_validation_status="Validated",
        )
        d = pv.to_dict()
        pv2 = PerformanceValidation.from_dict(d)
        assert pv2.to_dict() == d

    def test_subgroups_preserved(self):
        pv = PerformanceValidation(
            validation_datasets=[ValidationDataset("V", "H", "P", "internal")],
            claimed_metrics=[PerformanceMetric("AUC", 0.9, "Claimed")],
            validated_metrics=[PerformanceMetric("AUC", 0.85, "Validated", "Over 65")],
        )
        d = pv.to_dict()
        pv2 = PerformanceValidation.from_dict(d)
        assert pv2.validated_metrics[0].subgroup == "Over 65"


class TestMethodologyFromDict:
    def test_round_trip(self):
        m = Methodology(
            model_development_workflow="CRISP-DM",
            training_procedure="CV",
            data_preprocessing="Standardization",
            synthetic_data_usage="None",
            explainable_ai_method="SHAP",
            global_vs_local_interpretability="Both",
        )
        d = m.to_dict()
        m2 = Methodology.from_dict(d)
        assert m2.to_dict() == d


class TestAdditionalInfoFromDict:
    def test_round_trip(self):
        ai = AdditionalInfo(
            benefit_risk_summary="Good",
            ethical_considerations="None",
            caveats_limitations="Limited data",
            recommendations_for_safe_use="Clinical oversight",
            post_market_surveillance_plan="Quarterly review",
            explainability_recommendations="Use SHAP",
            supporting_documents=["doc1.pdf", "doc2.pdf"],
        )
        d = ai.to_dict()
        ai2 = AdditionalInfo.from_dict(d)
        assert ai2.to_dict() == d

    def test_en_dash_key(self):
        """Verify the en-dash in 'Benefit\u2013Risk Summary' is handled."""
        d = {
            "Benefit\u2013Risk Summary": "Test",
            "Ethical Considerations": "Test",
            "Caveats & Limitations": "Test",
            "Recommendations for Safe Use": "Test",
        }
        ai = AdditionalInfo.from_dict(d)
        assert ai.benefit_risk_summary == "Test"


class TestSubTypeFromDict:
    """Tests for from_dict() on sub-type dataclasses."""

    def test_source_dataset(self):
        d = {"name": "DS", "origin": "O", "size": 100,
             "collection_period": "2024", "population_characteristics": "All",
             "demographics": {"age": "50+"}}
        sd = SourceDataset.from_dict(d)
        assert sd.name == "DS"
        assert sd.demographics == {"age": "50+"}

    def test_concept_set(self):
        d = {"name": "CS", "vocabulary": "SNOMED", "concept_ids": [1, 2],
             "description": "Test"}
        cs = ConceptSet.from_dict(d)
        assert cs.concept_ids == [1, 2]

    def test_cohort_criteria(self):
        d = {"inclusion_rules": ["R1"], "exclusion_rules": ["R2"],
             "observation_window": "365d"}
        cc = CohortCriteria.from_dict(d)
        assert cc.inclusion_rules == ["R1"]
        assert cc.observation_window == "365d"

    def test_input_feature(self):
        d = {"name": "age", "data_type": "numeric", "required": True,
             "clinical_domain": "Demo", "value_range": "0-120", "units": "years"}
        f = InputFeature.from_dict(d)
        assert f.units == "years"

    def test_output_feature(self):
        d = {"name": "risk", "type": "probability", "classes": ["low", "high"]}
        f = OutputFeature.from_dict(d)
        assert f.classes == ["low", "high"]

    def test_validation_dataset(self):
        d = {"name": "V1", "source_institution": "H",
             "population_characteristics": "P", "validation_type": "external"}
        vd = ValidationDataset.from_dict(d)
        assert vd.validation_type == "external"

    def test_performance_metric(self):
        d = {"metric_name": "AUC", "value": 0.85,
             "validation_status": "Validated", "subgroup": "Male"}
        pm = PerformanceMetric.from_dict(d)
        assert pm.subgroup == "Male"

    def test_annotation(self):
        d = {"author": "Dr. X", "note": "Approved", "created_at": "2025-01-01"}
        a = Annotation.from_dict(d)
        assert a.author == "Dr. X"
        assert a.created_at == "2025-01-01"


class TestOMOPReportsRoundTrip:
    """Tests that OMOP detailed reports survive the round-trip."""

    def test_omop_reports_preserved(self):
        card = _build_full_card()
        d = card.to_dict()
        card2 = ModelCard.from_dict(d)
        assert card2.data_factors.omop_detailed_reports == {"cohort_id": 145, "person_count": 30}

    def test_concept_sets_preserved(self):
        card = _build_full_card()
        d = card.to_dict()
        card2 = ModelCard.from_dict(d)
        assert len(card2.data_factors.concept_sets) == 2
        assert card2.data_factors.concept_sets[0].name == "COPD Diagnosis"
        assert card2.data_factors.concept_sets[1].vocabulary == "LOINC"

    def test_cohort_criteria_preserved(self):
        card = _build_full_card()
        d = card.to_dict()
        card2 = ModelCard.from_dict(d)
        cc = card2.data_factors.primary_cohort_criteria
        assert "Age >= 40" in cc.inclusion_rules
        assert "Active malignancy" in cc.exclusion_rules
        assert cc.observation_window == "365 days prior to index date"


class TestEdgeCases:
    """Edge-case tests for from_dict robustness."""

    def test_empty_annotations(self):
        card = _build_minimal_card()
        d = card.to_dict()
        assert d["Notes"] == []
        card2 = ModelCard.from_dict(d)
        assert card2.annotations == []

    def test_no_lifecycle(self):
        card = _build_minimal_card()
        d = card.to_dict()
        assert "Lifecycle" not in d
        card2 = ModelCard.from_dict(d)
        assert card2.retention_until is None
        assert card2.lifecycle_status is None

    def test_dict_data_distribution(self):
        """Test that dict-type data_distribution_summary survives round-trip."""
        card = _build_full_card()
        d = card.to_dict()
        card2 = ModelCard.from_dict(d)
        dist = card2.data_factors.data_distribution_summary
        assert isinstance(dist, dict)
        assert dist["age"] == "mean 65, std 12"

    def test_multiple_source_datasets(self):
        card = _build_full_card()
        d = card.to_dict()
        card2 = ModelCard.from_dict(d)
        assert len(card2.data_factors.source_datasets) == 2

    def test_empty_literature_refs_normalize(self):
        """Empty list refs from to_dict() should normalize to None."""
        card = _build_minimal_card()
        d = card.to_dict()
        assert d["1. Model Details"]["Literature References"] == []
        card2 = ModelCard.from_dict(d)
        assert card2.model_details.literature_references is None

    def test_populated_literature_refs(self):
        card = _build_full_card()
        d = card.to_dict()
        card2 = ModelCard.from_dict(d)
        assert card2.model_details.literature_references == ["Smith et al. 2024", "Jones et al. 2023"]

    def test_from_dict_validates_after_reconstruction(self):
        """Reconstructed card should pass validation."""
        card = _build_full_card()
        d = card.to_dict()
        card2 = ModelCard.from_dict(d)
        card2.validate()
