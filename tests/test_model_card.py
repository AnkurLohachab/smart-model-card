"""
Tests for ModelCard class

Author: Ankur Lohachab
Department of Advanced Computing Sciences, Maastricht University
"""

import pytest
from smart_model_card import (
    ModelCard,
    ModelDetails,
    IntendedUse,
    get_model_card_json_schema,
    performance_from_dict
)
from smart_model_card.sections import (
    DataFactors,
    FeaturesOutputs,
    PerformanceValidation,
    Methodology,
    AdditionalInfo,
    SourceDataset,
    InputFeature,
    OutputFeature,
    ValidationDataset,
    PerformanceMetric
)


def test_model_card_creation():
    """Test creating a ModelCard instance"""
    card = ModelCard()
    assert card.model_details is None
    assert card.created_at is not None


def test_model_card_validation_fails_when_incomplete():
    """Test that validation fails when sections are missing"""
    card = ModelCard()

    with pytest.raises(RuntimeError, match="Missing sections"):
        card.validate()


def test_model_card_validation_succeeds_when_complete():
    """Test that validation succeeds when all sections are present"""
    card = ModelCard()

    card.set_model_details(ModelDetails(
        model_name="Test",
        version="1.0.0",
        developer_organization="Test Org",
        release_date="2025-01-01",
        description="Test",
        clinical_function="decision_support",
        algorithms_used="Test",
        licensing="MIT",
        support_contact="test@example.com"
    ))

    card.set_intended_use(IntendedUse(
        primary_intended_users="Test",
        clinical_indications="Test",
        patient_target_group="Test",
        intended_use_environment="hospital_outpatient"
    ))

    card.set_data_factors(DataFactors(
        source_datasets=[SourceDataset("Test", "Test", 100, "2025", "Test")],
        data_distribution_summary="Test",
        data_representativeness="Test",
        data_governance="Test"
    ))

    card.set_features_outputs(FeaturesOutputs(
        input_features=[InputFeature("test", "numeric", True, "Test")],
        output_features=[OutputFeature("test", "probability")],
        feature_type_distribution="Test",
        uncertainty_quantification="Test",
        output_interpretability="Test"
    ))

    card.set_performance_validation(PerformanceValidation(
        validation_datasets=[ValidationDataset("Test", "Test", "Test", "Test")],
        claimed_metrics=[PerformanceMetric("AUC", 0.85, "Claimed")],
        validated_metrics=[PerformanceMetric("AUC", 0.83, "Validated")]
    ))

    card.set_methodology(Methodology(
        model_development_workflow="Test",
        training_procedure="Test",
        data_preprocessing="Test"
    ))

    card.set_additional_info(AdditionalInfo(
        benefit_risk_summary="Test",
        ethical_considerations="Test",
        caveats_limitations="Test",
        recommendations_for_safe_use="Test"
    ))

    card.validate()


def test_model_card_to_dict():
    """Test exporting model card to dictionary"""
    card = ModelCard()

    card.set_model_details(ModelDetails(
        model_name="Test Model",
        version="1.0.0",
        developer_organization="Test Org",
        release_date="2025-01-01",
        description="Test Description",
        clinical_function="decision_support",
        algorithms_used="Test Algorithm",
        licensing="MIT",
        support_contact="test@example.com"
    ))

    card.set_intended_use(IntendedUse(
        primary_intended_users="Testers",
        clinical_indications="Testing",
        patient_target_group="Test Patients",
        intended_use_environment="hospital_outpatient"
    ))

    card.set_data_factors(DataFactors(
        source_datasets=[SourceDataset("Test Dataset", "Test Origin", 1000, "2025", "Test Pop")],
        data_distribution_summary="Test",
        data_representativeness="Test",
        data_governance="Test"
    ))

    card.set_features_outputs(FeaturesOutputs(
        input_features=[InputFeature("age", "numeric", True, "Demographics")],
        output_features=[OutputFeature("risk", "probability")],
        feature_type_distribution="1 numeric",
        uncertainty_quantification="CI",
        output_interpretability="Test"
    ))

    card.set_performance_validation(PerformanceValidation(
        validation_datasets=[ValidationDataset("Test", "Test", "Test", "Internal")],
        claimed_metrics=[PerformanceMetric("AUC", 0.85, "Claimed")],
        validated_metrics=[PerformanceMetric("AUC", 0.83, "Validated")]
    ))

    card.set_methodology(Methodology(
        model_development_workflow="Test workflow",
        training_procedure="Test training",
        data_preprocessing="Test preprocessing"
    ))

    card.set_additional_info(AdditionalInfo(
        benefit_risk_summary="Test",
        ethical_considerations="Test",
        caveats_limitations="Test",
        recommendations_for_safe_use="Test"
    ))

    data = card.to_dict()

    assert "1. Model Details" in data
    assert "2. Intended Use and Clinical Context" in data
    assert data["1. Model Details"]["Model Name"] == "Test Model"
    assert data["created_at"] is not None


def test_fluent_interface():
    """Test fluent interface for building model card"""
    card = (
        ModelCard()
        .set_model_details(ModelDetails(
            model_name="Test",
            version="1.0.0",
            developer_organization="Test",
        release_date="2025-01-01",
        description="Test",
        clinical_function="decision_support",
        algorithms_used="Test",
        licensing="MIT",
        support_contact="test@example.com"
        ))
        .set_intended_use(IntendedUse(
            primary_intended_users="Test",
            clinical_indications="Test",
            patient_target_group="Test",
            intended_use_environment="Test"
        ))
    )

    assert card.model_details is not None
    assert card.intended_use is not None


def test_json_schema_exports_required_sections():
    schema = get_model_card_json_schema()
    required = schema["required"]
    assert "1. Model Details" in required
    assert "7. Additional Information" in required


def test_performance_from_dict_builds_validation():
    perf = performance_from_dict({
        "claimed": [{"metric": "AUC", "value": 0.9, "status": "claimed"}],
        "validated": [{"metric": "AUC", "value": 0.85, "status": "external", "subgroup": "overall"}],
        "calibration": "Brier=0.1",
        "fairness": "no disparity",
        "metric_validation_status": "External validated",
        "validation_datasets": [{"name": "Ext", "source_institution": "Site", "population_characteristics": "n=100", "validation_type": "external"}]
    })
    assert len(perf.claimed_metrics) == 1
    assert len(perf.validated_metrics) == 1
    assert perf.validated_metrics[0].subgroup == "overall"
