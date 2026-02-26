"""
Model Card Core Class

Main class for building comprehensive medical AI model cards.

Author: Ankur Lohachab
Department of Advanced Computing Sciences, Maastricht University
"""

from __future__ import annotations
from typing import Optional, Dict, Any
from datetime import datetime

from smart_model_card.sections import (
    ModelDetails,
    IntendedUse,
    DataFactors,
    FeaturesOutputs,
    PerformanceValidation,
    Methodology,
    AdditionalInfo,
    Annotation
)
from typing import List
import json


class ModelCardValidationError(RuntimeError):
    """Aggregated validation error capturing multiple issues."""

    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


class ModelCard:
    """
    Comprehensive medical AI model card builder.

    Implements standardized template with 7 sections covering all aspects
    of medical AI model documentation for regulatory compliance and transparency.
    """

    def __init__(self):
        self.model_details: Optional[ModelDetails] = None
        self.intended_use: Optional[IntendedUse] = None
        self.data_factors: Optional[DataFactors] = None
        self.features_outputs: Optional[FeaturesOutputs] = None
        self.performance_validation: Optional[PerformanceValidation] = None
        self.methodology: Optional[Methodology] = None
        self.additional_info: Optional[AdditionalInfo] = None
        self.annotations: List[Annotation] = []
        self.created_at: str = datetime.now().isoformat()
        self.retention_until: Optional[str] = None
        self.lifecycle_status: Optional[str] = None

    def set_model_details(self, details: ModelDetails) -> ModelCard:
        """Set Section 1: Model Details"""
        self.model_details = details
        return self

    def set_intended_use(self, intended_use: IntendedUse) -> ModelCard:
        """Set Section 2: Intended Use and Clinical Context"""
        self.intended_use = intended_use
        return self

    def set_data_factors(self, data_factors: DataFactors) -> ModelCard:
        """Set Section 3: Data & Factors"""
        self.data_factors = data_factors
        return self

    def set_features_outputs(self, features_outputs: FeaturesOutputs) -> ModelCard:
        """Set Section 4: Features & Outputs"""
        self.features_outputs = features_outputs
        return self

    def set_performance_validation(self, performance: PerformanceValidation) -> ModelCard:
        """Set Section 5: Performance & Validation"""
        self.performance_validation = performance
        return self

    def set_methodology(self, methodology: Methodology) -> ModelCard:
        """Set Section 6: Methodology & Explainability"""
        self.methodology = methodology
        return self

    def set_additional_info(self, additional_info: AdditionalInfo) -> ModelCard:
        """Set Section 7: Additional Information"""
        self.additional_info = additional_info
        return self

    def collect_validation_errors(self) -> List[str]:
        """
        Collect validation errors across sections without raising immediately.

        Returns:
            List of error strings (empty if valid)
        """
        errors: List[str] = []

        missing = []

        if self.model_details is None:
            missing.append("Model Details")
        if self.intended_use is None:
            missing.append("Intended Use")
        if self.data_factors is None:
            missing.append("Data & Factors")
        if self.features_outputs is None:
            missing.append("Features & Outputs")
        if self.performance_validation is None:
            missing.append("Performance & Validation")
        if self.methodology is None:
            missing.append("Methodology")
        if self.additional_info is None:
            missing.append("Additional Information")

        if missing:
            errors.append(f"Missing sections: {', '.join(missing)}")

        if self.model_details:
            self.model_details.validate(errors)
        if self.intended_use:
            self.intended_use.validate(errors)
        if self.data_factors:
            self.data_factors.validate(errors)
        if self.features_outputs:
            self.features_outputs.validate(errors)
        if self.performance_validation:
            self.performance_validation.validate(errors)
        if self.methodology:
            self.methodology.validate(errors)
        if self.additional_info:
            self.additional_info.validate(errors)
        if self.retention_until:
            try:
                datetime.fromisoformat(self.retention_until)
            except Exception:
                errors.append("Lifecycle -> Retention Until: must be ISO datetime")
        return errors

    def validate(self) -> None:
        """
        Validate that all required sections are present and fields meet constraints.

        Raises:
            ModelCardValidationError: If any section or field fails validation.
        """
        errors = self.collect_validation_errors()
        if errors:
            raise ModelCardValidationError(errors)

    def to_dict(self, public: bool = False) -> Dict[str, Any]:
        """
        Export model card to dictionary format.

        Returns:
            Complete model card as nested dictionary
        """
        self.validate()

        data = {
            "created_at": self.created_at,
            "1. Model Details": self.model_details.to_dict(),
            "2. Intended Use and Clinical Context": self.intended_use.to_dict(),
            "3. Data & Factors": self.data_factors.to_dict(),
            "4. Features & Outputs": self.features_outputs.to_dict(),
            "5. Performance & Validation": self.performance_validation.to_dict(),
            "6. Methodology & Explainability": self.methodology.to_dict(),
            "7. Additional Information": self.additional_info.to_dict(),
            "Notes": [a.to_dict() for a in self.annotations] if self.annotations else []
        }

        if self.retention_until or self.lifecycle_status:
            data["Lifecycle"] = {
                "retention_until": self.retention_until,
                "lifecycle_status": self.lifecycle_status
            }

        if public:
            df = data.get("3. Data & Factors", {})
            for k in ["De-id Report URI", "De-id Report Hash"]:
                df.pop(k, None)
            data["3. Data & Factors"] = df
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ModelCard:
        """
        Load model card from dictionary (reverse of to_dict).

        Args:
            data: Dictionary containing model card data

        Returns:
            Fully reconstructed ModelCard instance
        """
        card = cls()

        if "created_at" in data:
            card.created_at = data["created_at"]

        s1 = data.get("1. Model Details")
        if s1:
            card.model_details = ModelDetails.from_dict(s1)

        s2 = data.get("2. Intended Use and Clinical Context")
        if s2:
            card.intended_use = IntendedUse.from_dict(s2)

        s3 = data.get("3. Data & Factors")
        if s3:
            card.data_factors = DataFactors.from_dict(s3)

        s4 = data.get("4. Features & Outputs")
        if s4:
            card.features_outputs = FeaturesOutputs.from_dict(s4)

        s5 = data.get("5. Performance & Validation")
        if s5:
            card.performance_validation = PerformanceValidation.from_dict(s5)

        s6 = data.get("6. Methodology & Explainability")
        if s6:
            card.methodology = Methodology.from_dict(s6)

        s7 = data.get("7. Additional Information")
        if s7:
            card.additional_info = AdditionalInfo.from_dict(s7)

        notes = data.get("Notes")
        if notes:
            card.annotations = [Annotation.from_dict(n) for n in notes]

        lifecycle = data.get("Lifecycle")
        if lifecycle:
            card.retention_until = lifecycle.get("retention_until")
            card.lifecycle_status = lifecycle.get("lifecycle_status")

        return card

    @classmethod
    def from_json(cls, path: str) -> ModelCard:
        """
        Load model card from a JSON file.

        Args:
            path: Path to the JSON file

        Returns:
            Fully reconstructed ModelCard instance
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
