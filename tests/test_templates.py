"""
Tests for templates, quick_card(), and regulatory presets.

Author: Ankur Lohachab
Department of Advanced Computing Sciences, Maastricht University
"""

import pytest

from smart_model_card import (
    ModelCard,
    quick_card,
    TEMPLATES,
    REGULATORY_PRESETS,
)


class TestQuickCard:
    """Tests for the quick_card() factory function."""

    def test_minimal_args_produces_valid_card(self):
        card = quick_card(
            model_name="Test Model",
            description="A test model",
            developer="Test Org",
            contact="test@example.com",
        )
        assert isinstance(card, ModelCard)
        card.validate()

    def test_default_template_is_screening(self):
        card = quick_card("M", "D", "O", "a@b.com")
        assert card.model_details.clinical_function == "screening"

    def test_model_details_injected(self):
        card = quick_card(
            model_name="My COPD Model",
            description="Predicts COPD risk",
            developer="My Hospital",
            contact="team@hospital.org",
        )
        assert card.model_details.model_name == "My COPD Model"
        assert card.model_details.description == "Predicts COPD risk"
        assert card.model_details.developer_organization == "My Hospital"
        assert card.model_details.support_contact == "team@hospital.org"

    def test_version_and_date_auto_set(self):
        card = quick_card("M", "D", "O", "a@b.com")
        assert card.model_details.version == "1.0.0"
        assert len(card.model_details.release_date) == 10

    def test_unknown_template_raises(self):
        with pytest.raises(ValueError, match="Unknown template"):
            quick_card("M", "D", "O", "a@b.com", template="nonexistent")

    def test_override_flat_kwargs(self):
        card = quick_card(
            "M", "D", "O", "a@b.com",
            algorithms_used="Custom Neural Network",
            version="2.5.0",
            licensing="Apache-2.0",
        )
        assert card.model_details.algorithms_used == "Custom Neural Network"
        assert card.model_details.version == "2.5.0"
        assert card.model_details.licensing == "Apache-2.0"

    def test_override_section_kwargs(self):
        card = quick_card(
            "M", "D", "O", "a@b.com",
            intended_use__contraindications="Not for pediatric use",
        )
        assert card.intended_use.contraindications == "Not for pediatric use"

    def test_override_methodology(self):
        card = quick_card(
            "M", "D", "O", "a@b.com",
            methodology__training_procedure="10-fold CV with early stopping",
        )
        assert card.methodology.training_procedure == "10-fold CV with early stopping"


class TestAllTemplates:
    """Tests that every template produces a valid card."""

    @pytest.mark.parametrize("template_id", list(TEMPLATES.keys()))
    def test_template_produces_valid_card(self, template_id):
        card = quick_card(
            model_name=f"Test-{template_id}",
            description=f"Testing {template_id} template",
            developer="Test Org",
            contact="test@example.com",
            template=template_id,
        )
        card.validate()

    @pytest.mark.parametrize("template_id", list(TEMPLATES.keys()))
    def test_template_has_correct_clinical_function(self, template_id):
        expected = TEMPLATES[template_id]["sections"]["model_details"]["clinical_function"]
        card = quick_card("M", "D", "O", "a@b.com", template=template_id)
        assert card.model_details.clinical_function == expected

    def test_five_templates_exist(self):
        assert len(TEMPLATES) == 5
        assert set(TEMPLATES.keys()) == {
            "copd_risk_predictor",
            "screening_tool",
            "diagnostic_classifier",
            "triage_model",
            "monitoring_model",
        }

    def test_each_template_has_name_and_description(self):
        for tid, tmpl in TEMPLATES.items():
            assert "name" in tmpl, f"Template {tid} missing 'name'"
            assert "description" in tmpl, f"Template {tid} missing 'description'"


class TestJurisdiction:
    """Tests for regulatory jurisdiction presets."""

    def test_eu_adds_classifications(self):
        card = quick_card("M", "D", "O", "a@b.com", jurisdiction="eu")
        rc = card.model_details.regulatory_classifications
        assert any(c["framework"] == "EU MDR" for c in rc)
        assert any(c["framework"] == "EU AI Act" for c in rc)

    def test_us_adds_fda(self):
        card = quick_card("M", "D", "O", "a@b.com", jurisdiction="us")
        rc = card.model_details.regulatory_classifications
        assert any(c["framework"] == "FDA" for c in rc)
        assert len(rc) == 1

    def test_both_adds_all(self):
        card = quick_card("M", "D", "O", "a@b.com", jurisdiction="both")
        rc = card.model_details.regulatory_classifications
        frameworks = {c["framework"] for c in rc}
        assert "EU MDR" in frameworks
        assert "FDA" in frameworks
        assert "EU AI Act" in frameworks

    def test_no_jurisdiction_no_classifications(self):
        card = quick_card("M", "D", "O", "a@b.com")
        rc = card.model_details.regulatory_classifications
        assert rc is None

    def test_unknown_jurisdiction_raises(self):
        with pytest.raises(ValueError, match="Unknown jurisdiction"):
            quick_card("M", "D", "O", "a@b.com", jurisdiction="japan")

    def test_jurisdiction_case_insensitive(self):
        card = quick_card("M", "D", "O", "a@b.com", jurisdiction="EU")
        rc = card.model_details.regulatory_classifications
        assert any(c["framework"] == "EU MDR" for c in rc)

    def test_regulatory_presets_structure(self):
        for key in ["eu", "us", "both"]:
            preset = REGULATORY_PRESETS[key]
            assert "classifications" in preset
            assert "documentation_requirements" in preset
            assert len(preset["classifications"]) > 0
            assert len(preset["documentation_requirements"]) > 0


class TestQuickCardRoundTrip:
    """Tests that quick_card output survives round-trip."""

    @pytest.mark.parametrize("template_id", list(TEMPLATES.keys()))
    def test_round_trip(self, template_id):
        card = quick_card(
            model_name=f"RT-{template_id}",
            description="Round trip test",
            developer="Test",
            contact="t@t.com",
            template=template_id,
            jurisdiction="eu",
        )
        d1 = card.to_dict()
        card2 = ModelCard.from_dict(d1)
        d2 = card2.to_dict()
        assert d1 == d2

    def test_round_trip_with_overrides(self):
        card = quick_card(
            "My Model", "Test", "Org", "a@b.com",
            template="copd_risk_predictor",
            jurisdiction="both",
            algorithms_used="Custom XGBoost",
            intended_use__warnings="Use with caution",
        )
        d1 = card.to_dict()
        card2 = ModelCard.from_dict(d1)
        d2 = card2.to_dict()
        assert d1 == d2
        assert d2["1. Model Details"]["Algorithm(s) Used"] == "Custom XGBoost"


class TestQuickCardExports:
    """Tests that quick_card output exports correctly."""

    def test_to_dict_has_all_sections(self):
        card = quick_card("M", "D", "O", "a@b.com")
        d = card.to_dict()
        assert "1. Model Details" in d
        assert "2. Intended Use and Clinical Context" in d
        assert "3. Data & Factors" in d
        assert "4. Features & Outputs" in d
        assert "5. Performance & Validation" in d
        assert "6. Methodology & Explainability" in d
        assert "7. Additional Information" in d

    def test_regulatory_in_export(self):
        card = quick_card("M", "D", "O", "a@b.com", jurisdiction="eu")
        d = card.to_dict()
        rc = d["1. Model Details"]["Regulatory Classifications"]
        assert len(rc) == 2
