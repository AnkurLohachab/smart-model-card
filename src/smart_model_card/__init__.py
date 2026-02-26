"""
smart-model-card: Structured Model Cards for Medical AI

A Python package for creating standardized documentation for medical AI models.
Provides a 7-section template, domain-specific presets, OMOP CDM data integration,
and multi-format export (JSON, HTML, Markdown).

Author: Ankur Lohachab
Affiliation: Department of Advanced Computing Sciences, Maastricht University
License: MIT
"""

__version__ = "3.0.0"
__author__ = "Ankur Lohachab"
__affiliation__ = "Department of Advanced Computing Sciences, Maastricht University"

from smart_model_card.model_card import ModelCard
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
from smart_model_card.exporters import (
    HTMLExporter,
    JSONExporter,
    MarkdownExporter
)
from smart_model_card.schema import get_model_card_json_schema
from smart_model_card.data_sources import (
    create_omop_adapter,
    create_synthetic_adapter,
    create_custom_adapter,
    OMOPAdapter,
    SyntheticDataAdapter,
    CustomDataAdapter
)
from smart_model_card.integrations import (
    OMOPIntegration,
    create_concept_set_from_omop,
    create_cohort_criteria_from_omop,
    summarize_omop_cohort,
    build_data_factors_from_smart_omop,
    refresh_data_factors_from_omop,
    performance_from_dict,
    performance_from_file,
    log_model_card_to_mlflow,
    log_model_card_to_wandb
)
from smart_model_card.sections import (
    SourceDataset,
    InputFeature,
    OutputFeature,
    ValidationDataset,
    PerformanceMetric,
    ConceptSet,
    CohortCriteria,
)
from smart_model_card.cac import ComputerAssistedCoder, CodeSuggestion
from smart_model_card.omop_reports import OMOPReportParser, load_reports_from_directory
from smart_model_card.templates import quick_card, TEMPLATES, REGULATORY_PRESETS

__all__ = [
    "ModelCard",
    "ModelDetails",
    "IntendedUse",
    "DataFactors",
    "FeaturesOutputs",
    "PerformanceValidation",
    "Methodology",
    "AdditionalInfo",
    "Annotation",
    "SourceDataset",
    "InputFeature",
    "OutputFeature",
    "ValidationDataset",
    "PerformanceMetric",
    "ConceptSet",
    "CohortCriteria",
    "HTMLExporter",
    "JSONExporter",
    "MarkdownExporter",
    "get_model_card_json_schema",
    "create_omop_adapter",
    "create_synthetic_adapter",
    "create_custom_adapter",
    "OMOPAdapter",
    "SyntheticDataAdapter",
    "CustomDataAdapter",
    "OMOPIntegration",
    "create_concept_set_from_omop",
    "create_cohort_criteria_from_omop",
    "summarize_omop_cohort",
    "build_data_factors_from_smart_omop",
    "refresh_data_factors_from_omop",
    "performance_from_dict",
    "performance_from_file",
    "log_model_card_to_mlflow",
    "log_model_card_to_wandb",
    "ComputerAssistedCoder",
    "CodeSuggestion",
    "OMOPReportParser",
    "load_reports_from_directory",
    "quick_card",
    "TEMPLATES",
    "REGULATORY_PRESETS",
]
