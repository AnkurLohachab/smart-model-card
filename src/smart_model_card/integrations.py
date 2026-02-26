"""
Integration Utilities

Helper functions for integrating with smart-omop and medsynth packages.

Author: Ankur Lohachab
Department of Advanced Computing Sciences, Maastricht University
"""

from typing import List, Optional, Dict, Any
from smart_model_card.sections import (
    ConceptSet,
    CohortCriteria,
    SourceDataset,
    DataFactors,
    PerformanceValidation,
    PerformanceMetric,
    ValidationDataset
)
from smart_model_card.data_sources import create_omop_adapter
from smart_model_card.exporters import JSONExporter
import json
import csv
import tempfile
from pathlib import Path

try:
    from smart_omop import OMOPClient
    SMART_OMOP_AVAILABLE = True
except ImportError:
    SMART_OMOP_AVAILABLE = False


class OMOPIntegration:
    """
    Wrapper class for integrating with smart-omop package.

    Provides methods to fetch cohort data, characterizations, and concept information
    from OHDSI WebAPI, and automatically populate DataFactors section.
    """

    def __init__(self, webapi_url: str, source_key: str):
        """
        Initialize OMOP integration.

        Args:
            webapi_url: Base URL for OHDSI WebAPI (e.g., https://atlas.example.org/WebAPI)
            source_key: CDM source key identifier
        """
        if not SMART_OMOP_AVAILABLE:
            raise ImportError(
                "smart-omop package is required for OMOP integration. "
                "Install it with: pip install smart-omop"
            )

        self.webapi_url = webapi_url
        self.source_key = source_key
        self._client = None

    def __enter__(self):
        """Context manager entry"""
        self._client = OMOPClient(self.webapi_url).__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self._client:
            return self._client.__exit__(exc_type, exc_val, exc_tb)

    def get_cohort_with_reports(
        self,
        cohort_id: int,
        include_heracles: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch cohort definition and optionally Heracles characterization reports.

        Args:
            cohort_id: Cohort ID in OHDSI ATLAS
            include_heracles: Whether to include Heracles characterization reports

        Returns:
            Dictionary containing:
                - cohort_id: The cohort ID
                - name: Cohort name
                - description: Cohort description
                - definition: Full cohort definition
                - results: Cohort results (person_count, etc.)
                - reports: Dictionary of Heracles reports if include_heracles=True
                    - person: Demographics (age, gender, race)
                    - condition: Condition occurrences
                    - drug: Drug exposures
                    - procedure: Procedures
                    - dashboard: Summary statistics
                - data_factors: Pre-built DataFactors object ready to use
        """
        if self._client is None:
            raise RuntimeError("OMOPIntegration must be used as a context manager")

        print(f"  Fetching cohort definition for ID {cohort_id}...")

        cohort_def = self._client.get_cohort(cohort_id)

        result = {
            'cohort_id': cohort_id,
            'name': cohort_def.get('name', 'Unknown Cohort'),
            'description': cohort_def.get('description', ''),
            'definition': cohort_def
        }

        try:
            print(f"  Fetching cohort results...")
            cohort_results = self._client.get_cohort_results(cohort_id, self.source_key)
            result['results'] = cohort_results
            person_count = cohort_results.get('personCount', 0)
            status = cohort_results.get('status', 'UNKNOWN')
            print(f"  ✓ Cohort has {person_count} persons (status: {status})")
        except Exception as e:
            print(f"  ⚠ Could not fetch cohort results: {e}")
            result['results'] = None
            person_count = 0

        if include_heracles:
            print(f"  Fetching Heracles characterization reports...")
            reports = {}

            try:
                print(f"    - Fetching person demographics...")
                reports['person'] = self._client.get_heracles_person_report(
                    cohort_id, self.source_key
                )
                print(f"    ✓ Person report fetched")
            except Exception as e:
                print(f"    ⚠ Person report not available: {e}")
                reports['person'] = None

            try:
                print(f"    - Fetching dashboard summary...")
                reports['dashboard'] = self._client.get_heracles_dashboard_report(
                    cohort_id, self.source_key
                )
                print(f"    ✓ Dashboard report fetched")
            except Exception as e:
                print(f"    ⚠ Dashboard report not available: {e}")
                reports['dashboard'] = None

            try:
                print(f"    - Fetching condition occurrences...")
                reports['condition'] = self._client.get_heracles_condition_report(
                    cohort_id, self.source_key
                )
                print(f"    ✓ Condition report fetched")
            except Exception as e:
                print(f"    ⚠ Condition report not available: {e}")
                reports['condition'] = None

            try:
                print(f"    - Fetching drug exposures...")
                reports['drug'] = self._client.get_heracles_drug_report(
                    cohort_id, self.source_key
                )
                print(f"    ✓ Drug report fetched")
            except Exception as e:
                print(f"    ⚠ Drug report not available: {e}")
                reports['drug'] = None

            try:
                print(f"    - Fetching procedure occurrences...")
                reports['procedure'] = self._client.get_heracles_procedure_report(
                    cohort_id, self.source_key
                )
                print(f"    ✓ Procedure report fetched")
            except Exception as e:
                print(f"    ⚠ Procedure report not available: {e}")
                reports['procedure'] = None

            result['reports'] = reports
        else:
            reports = {}
            result['reports'] = None

        print(f"  Building DataFactors from OMOP data...")
        result['data_factors'] = self._build_data_factors_from_reports(
            cohort_def, cohort_results, reports
        )
        print(f"  ✓ DataFactors section ready")

        return result

    def _build_data_factors_from_reports(
        self,
        cohort_def: Dict[str, Any],
        cohort_results: Optional[Dict[str, Any]],
        reports: Dict[str, Any]
    ) -> DataFactors:
        """
        Build DataFactors section from OMOP cohort data and Heracles reports.

        Args:
            cohort_def: Cohort definition
            cohort_results: Cohort results (person count, etc.)
            reports: Dictionary of Heracles reports

        Returns:
            DataFactors object populated with OMOP data
        """
        demographics = {}
        person_count = 0

        if cohort_results:
            person_count = cohort_results.get('personCount', 0)

        if reports.get('person'):
            person_report = reports['person']
            if 'AGE' in person_report or 'age' in person_report:
                age_data = person_report.get('AGE') or person_report.get('age', {})
                if age_data:
                    demographics['age'] = f"Distribution: {age_data}"

            if 'GENDER' in person_report or 'gender' in person_report:
                gender_data = person_report.get('GENDER') or person_report.get('gender', {})
                if gender_data:
                    demographics['gender'] = f"Distribution: {gender_data}"

            if 'RACE' in person_report or 'race' in person_report:
                race_data = person_report.get('RACE') or person_report.get('race', {})
                if race_data:
                    demographics['race'] = f"Distribution: {race_data}"

        source_dataset = SourceDataset(
            name=f"{cohort_def.get('name', 'OMOP Cohort')} (ID: {cohort_def.get('id')})",
            origin=f"OHDSI WebAPI ({self.webapi_url}), Source: {self.source_key}",
            size=person_count,
            collection_period="From OMOP CDM database (see cohort definition for observation windows)",
            population_characteristics=f"OMOP CDM standardized cohort. {cohort_def.get('description', '')}",
            demographics=demographics if demographics else None
        )

        distribution_parts = [f"Total persons: {person_count}"]
        if demographics:
            distribution_parts.append(f"Demographics available: {', '.join(demographics.keys())}")
        if reports.get('condition'):
            distribution_parts.append("Condition occurrences captured")
        if reports.get('drug'):
            distribution_parts.append("Drug exposures captured")
        if reports.get('procedure'):
            distribution_parts.append("Procedures captured")

        data_distribution = ". ".join(distribution_parts)

        return DataFactors(
            source_datasets=[source_dataset],
            data_distribution_summary=data_distribution,
            data_representativeness=(
                f"Data from OMOP CDM database (source: {self.source_key}). "
                "Standardized using OMOP Common Data Model vocabularies. "
                "Representativeness should be validated for target deployment population."
            ),
            data_governance=(
                f"OMOP CDM standardized data. Accessed via OHDSI WebAPI. "
                f"Cohort definition ID: {cohort_def.get('id')}. "
                "Refer to source database data governance policies."
            ),
            omop_detailed_reports=reports
        )


def create_concept_set_from_omop(
    name: str,
    concept_ids: List[int],
    vocabulary: str = "OMOP",
    description: Optional[str] = None
) -> ConceptSet:
    """
    Create ConceptSet from OMOP concept IDs.

    Args:
        name: Concept set name
        concept_ids: List of OMOP concept IDs
        vocabulary: Vocabulary system (default: OMOP)
        description: Optional description

    Returns:
        ConceptSet instance
    """
    return ConceptSet(
        name=name,
        vocabulary=vocabulary,
        concept_ids=concept_ids,
        description=description
    )


def create_cohort_criteria_from_omop(
    cohort_definition: Dict[str, Any]
) -> CohortCriteria:
    """
    Create CohortCriteria from OMOP cohort definition.

    Args:
        cohort_definition: OMOP cohort definition dictionary

    Returns:
        CohortCriteria instance
    """
    inclusion_rules = []
    exclusion_rules = []

    if "expression" in cohort_definition:
        expr = cohort_definition["expression"]

        if "InclusionRules" in expr:
            for rule in expr["InclusionRules"]:
                rule_desc = f"{rule.get('name', 'Unnamed')}: {rule.get('description', '')}"
                inclusion_rules.append(rule_desc)

        if "PrimaryCriteria" in expr:
            pc = expr["PrimaryCriteria"]
            if "ObservationWindow" in pc:
                obs_window = pc["ObservationWindow"]
                prior = obs_window.get("PriorDays", 0)
                post = obs_window.get("PostDays", 0)
                observation_window = f"Prior: {prior} days, Post: {post} days"
            else:
                observation_window = None
        else:
            observation_window = None
    else:
        observation_window = None

    return CohortCriteria(
        inclusion_rules=inclusion_rules or ["No explicit inclusion rules"],
        exclusion_rules=exclusion_rules or ["No explicit exclusion rules"],
        observation_window=observation_window
    )


def create_dataset_from_medsynth(
    medsynth_config: Dict[str, Any]
) -> SourceDataset:
    """
    Create SourceDataset from MedSynth configuration.

    Args:
        medsynth_config: MedSynth configuration dictionary

    Returns:
        SourceDataset instance
    """
    return SourceDataset(
        name=f"MedSynth Synthetic Dataset (v{medsynth_config.get('version', 'unknown')})",
        origin="Privacy-preserving synthetic data generated using MedSynth",
        size=medsynth_config.get("num_subjects", 0),
        collection_period="Synthetic (not applicable)",
        population_characteristics=medsynth_config.get(
            "population_characteristics",
            "Synthetic OMOP CDM data with privacy protection"
        )
    )


def summarize_omop_cohort(
    cohort_definition: Dict[str, Any],
    cohort_results: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create summary text from OMOP cohort definition and results.

    Args:
        cohort_definition: OMOP cohort definition
        cohort_results: Optional cohort generation results

    Returns:
        Summary string
    """
    summary_parts = []

    summary_parts.append(f"Cohort: {cohort_definition.get('name', 'Unnamed')}")

    if cohort_results:
        person_count = cohort_results.get('personCount', 'N/A')
        summary_parts.append(f"Person Count: {person_count}")

    if "expression" in cohort_definition and "ConceptSets" in cohort_definition["expression"]:
        concept_sets = cohort_definition["expression"]["ConceptSets"]
        summary_parts.append(f"Concept Sets: {len(concept_sets)}")

    return "; ".join(summary_parts)


def build_data_factors_from_smart_omop(
    client: Any,
    cohort_id: int,
    source_key: str
) -> Dict[str, Any]:
    """
    Convenience helper: pull OMOP cohort definition/results via smart-omop
    and return concept sets, cohort criteria, and source dataset payloads.

    Args:
        client: smart_omop.OMOPClient instance
        cohort_id: Cohort id to fetch
        source_key: Source key for generation/results

    Returns:
        Dict with concept_sets, primary_cohort_criteria, source_datasets
    """
    try:
        from smart_omop import OMOPClient  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise ImportError("smart-omop is required for OMOP integration. Install with smart-model-card[omop].") from exc

    if not isinstance(client, OMOPClient):  # pragma: no cover - sanity guard
        raise TypeError("client must be a smart_omop.OMOPClient instance")

    cohort_def = client.get_cohort(cohort_id)
    cohort_results = client.get_cohort_results(cohort_id, source_key)

    adapter = create_omop_adapter(
        cohort_definition=cohort_def,
        cohort_results=cohort_results,
        source_name=cohort_def.get("name", f"Cohort {cohort_id}"),
        source_origin="OMOP CDM via smart-omop"
    )

    return {
        "concept_sets": adapter.get_concept_sets(),
        "primary_cohort_criteria": adapter.get_cohort_criteria(),
        "source_datasets": [adapter.get_dataset_info()]
    }


def refresh_data_factors_from_omop(
    card: Any,
    client: Any,
    cohort_id: int,
    source_key: str
) -> Any:
    """
    Update a ModelCard's DataFactors using smart-omop cohort definition/results.

    Args:
        card: ModelCard instance (mutated in place)
        client: smart_omop.OMOPClient instance
        cohort_id: Cohort id
        source_key: Source key for generation/results

    Returns:
        The updated card (for chaining)
    """
    payload = build_data_factors_from_smart_omop(client, cohort_id, source_key)
    card.set_data_factors(DataFactors(
        concept_sets=payload["concept_sets"],
        primary_cohort_criteria=payload["primary_cohort_criteria"],
        source_datasets=payload["source_datasets"],
        data_distribution_summary="Describe demographics/clinical distribution",
        data_representativeness="Compare against deployment setting",
        data_governance="IRB/consent/de-ID details"
    ))
    return card


def performance_from_dict(data: Dict[str, Any]) -> PerformanceValidation:
    """
    Build PerformanceValidation from a dict payload.

    Expected keys:
        claimed: list of {metric, value, status?, subgroup?}
        validated: list of {metric, value, status?, subgroup?}
        calibration: str
        fairness: str
        metric_validation_status: str
        validation_datasets: list of {name, source_institution, population_characteristics, validation_type}
    """
    def _metrics(items: List[Dict[str, Any]], default_status: str) -> List[PerformanceMetric]:
        out: List[PerformanceMetric] = []
        for m in items:
            out.append(PerformanceMetric(
                metric_name=m.get("metric") or m.get("metric_name"),
                value=float(m.get("value", 0.0)),
                validation_status=m.get("status") or m.get("validation_status") or default_status,
                subgroup=m.get("subgroup")
            ))
        return out

    claimed_raw = data.get("claimed") or []
    validated_raw = data.get("validated") or []
    datasets_raw = data.get("validation_datasets") or []

    datasets = [
        ValidationDataset(
            name=d.get("name", "Validation dataset"),
            source_institution=d.get("source_institution", "Unknown"),
            population_characteristics=d.get("population_characteristics", ""),
            validation_type=d.get("validation_type", "internal")
        ) for d in datasets_raw
    ] or [ValidationDataset("Validation dataset", "Unknown", "", "internal")]

    return PerformanceValidation(
        validation_datasets=datasets,
        claimed_metrics=_metrics(claimed_raw, "claimed"),
        validated_metrics=_metrics(validated_raw, "validated"),
        calibration_analysis=data.get("calibration"),
        fairness_assessment=data.get("fairness"),
        metric_validation_status=data.get("metric_validation_status", "claimed/internal/external status")
    )


def performance_from_file(path: str) -> PerformanceValidation:
    """
    Build PerformanceValidation from a JSON or CSV file.

    JSON schema: see performance_from_dict docstring.
    CSV columns: metric_name, value, validation_status (claimed|internal|external),
                 subgroup (optional), kind (claimed|validated), plus optional
                 calibration, fairness in a separate JSON if desired.
    """
    file_path = Path(path)
    if file_path.suffix.lower() == ".json":
        with file_path.open() as f:
            payload = json.load(f)
        return performance_from_dict(payload)

    if file_path.suffix.lower() == ".csv":
        claimed: List[Dict[str, Any]] = []
        validated: List[Dict[str, Any]] = []
        with file_path.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                item = {
                    "metric": row.get("metric_name") or row.get("metric"),
                    "value": float(row.get("value", 0.0)),
                    "status": row.get("validation_status"),
                    "subgroup": row.get("subgroup")
                }
                kind = (row.get("kind") or "").lower()
                if kind == "claimed":
                    claimed.append(item)
                else:
                    validated.append(item)
        return performance_from_dict({
            "claimed": claimed,
            "validated": validated
        })

    raise ValueError("Unsupported metrics file type; use .json or .csv")


def log_model_card_to_mlflow(card: Any, artifact_path: str = "model_card.json") -> str:
    """
    Export model card to JSON and log as MLflow artifact (if mlflow installed).
    """
    try:
        import mlflow  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise ImportError("mlflow is required for MLflow logging. Install mlflow or use pip install mlflow.") from exc

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "model_card.json"
        JSONExporter.export(card, str(out_path))
        mlflow.log_artifact(str(out_path), artifact_path=str(Path(artifact_path).parent) if "/" in artifact_path else None)
    return artifact_path


def log_model_card_to_wandb(card: Any, artifact_path: str = "model_card.json") -> str:
    """
    Export model card to JSON and log as a W&B file (if wandb installed).
    """
    try:
        import wandb  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise ImportError("wandb is required for Weights & Biases logging. Install wandb or use pip install wandb.") from exc

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "model_card.json"
        JSONExporter.export(card, str(out_path))
        wandb.save(str(out_path), base_path=tmpdir)
    return artifact_path
