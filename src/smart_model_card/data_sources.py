"""
Flexible Data Source Adapters

Support for various data sources including OMOP, synthetic data packages,
and custom data sources.

Author: Ankur Lohachab
Department of Advanced Computing Sciences, Maastricht University
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from smart_model_card.sections import SourceDataset, ConceptSet, CohortCriteria


class DataSourceAdapter(ABC):
    """Base adapter for data sources"""

    @abstractmethod
    def get_dataset_info(self) -> SourceDataset:
        """Get dataset metadata as SourceDataset"""
        pass

    @abstractmethod
    def get_concept_sets(self) -> List[ConceptSet]:
        """Get concept sets if applicable"""
        pass

    @abstractmethod
    def get_cohort_criteria(self) -> Optional[CohortCriteria]:
        """Get cohort criteria if applicable"""
        pass


class OMOPAdapter(DataSourceAdapter):
    """Adapter for OMOP CDM data sources"""

    def __init__(
        self,
        cohort_definition: Dict[str, Any],
        cohort_results: Optional[Dict[str, Any]] = None,
        source_name: str = "OMOP CDM Database",
        source_origin: str = "Electronic Health Records",
        client: Any = None
    ):
        self.cohort_definition = cohort_definition
        self.cohort_results = cohort_results
        self.source_name = source_name
        self.source_origin = source_origin
        self.client = client

    def get_dataset_info(self) -> SourceDataset:
        """Extract dataset info from OMOP cohort with detailed demographics"""
        person_count = 0
        if self.cohort_results:
            person_count = self.cohort_results.get('personCount', 0)

        cohort_name = self.cohort_definition.get('name', 'OMOP Cohort')

        collection_period = self._extract_collection_period()

        demographics = self._extract_detailed_demographics()

        return SourceDataset(
            name=f"{cohort_name}",
            origin=f"{self.source_name} - {self.source_origin}",
            size=person_count,
            collection_period=collection_period,
            population_characteristics=self._extract_population_characteristics(),
            demographics=demographics
        )

    def get_concept_sets(self) -> List[ConceptSet]:
        """Extract concept sets from OMOP cohort definition with concept names"""
        import json
        concept_sets = []

        if "expression" in self.cohort_definition:
            expr = self.cohort_definition["expression"]

            if isinstance(expr, str):
                try:
                    expr = json.loads(expr)
                except:
                    return concept_sets

            if "ConceptSets" in expr:
                cohort_name = self.cohort_definition.get('name', 'Cohort')

                for idx, cs in enumerate(expr["ConceptSets"]):
                    concept_ids = []
                    concept_names = []

                    if "expression" in cs and "items" in cs["expression"]:
                        for item in cs["expression"]["items"]:
                            if "concept" in item:
                                concept = item["concept"]
                                if "CONCEPT_ID" in concept:
                                    concept_ids.append(concept["CONCEPT_ID"])
                                if "CONCEPT_NAME" in concept:
                                    concept_names.append(concept["CONCEPT_NAME"])

                    cs_name = cs.get("name", "")
                    if not cs_name or cs_name == "Unnamed Concept Set":
                        cs_name = f"{cohort_name} - Concept Set {idx+1}" if len(expr["ConceptSets"]) > 1 else cohort_name

                    desc_parts = []
                    if concept_ids:
                        desc_parts.append(f"{len(concept_ids)} concept{'s' if len(concept_ids) > 1 else ''}")
                        if len(concept_ids) <= 5:
                            desc_parts.append(f"IDs: {', '.join(map(str, concept_ids))}")
                        else:
                            desc_parts.append(f"IDs: {', '.join(map(str, concept_ids[:5]))}... (+{len(concept_ids)-5} more)")

                    valid_names = [n for n in concept_names if n]
                    if valid_names:
                        desc_parts.append(f"Names: {', '.join(valid_names[:2])}")

                    concept_sets.append(ConceptSet(
                        name=cs_name,
                        vocabulary="OMOP",
                        concept_ids=concept_ids,
                        description=" | ".join(desc_parts) if desc_parts else "OMOP concept set"
                    ))

        return concept_sets

    def get_cohort_criteria(self) -> Optional[CohortCriteria]:
        """Extract cohort criteria from OMOP definition with enhanced details"""
        import json

        if "expression" not in self.cohort_definition:
            return None

        expr = self.cohort_definition["expression"]

        if isinstance(expr, str):
            try:
                expr = json.loads(expr)
            except:
                return None

        inclusion_rules = []
        exclusion_rules = []
        observation_window = None

        if "PrimaryCriteria" in expr:
            pc = expr["PrimaryCriteria"]

            criteria_list = pc.get("CriteriaList", [])
            if criteria_list:
                for idx, criterion in enumerate(criteria_list):
                    if isinstance(criterion, dict):
                        for key in criterion.keys():
                            if key != "CorrelatedCriteria":
                                criterion_type = key.replace('Occurrence', ' Occurrence')
                                inclusion_rules.append(f"Patients with {criterion_type}")

                                criterion_data = criterion.get(key, {})
                                if isinstance(criterion_data, dict) and "CodesetId" in criterion_data:
                                    codeset_id = criterion_data["CodesetId"]
                                    if "ConceptSets" in expr:
                                        for cs in expr["ConceptSets"]:
                                            if cs.get("id") == codeset_id:
                                                cs_name = cs.get("name", f"Concept Set {codeset_id}")
                                                inclusion_rules[-1] += f" (using concept set: {cs_name})"
                                                break

        if "InclusionRules" in expr:
            for idx, rule in enumerate(expr["InclusionRules"]):
                name = rule.get('name', f'Inclusion Rule {idx+1}')
                desc = rule.get('description', '')

                if not name or 'demo' in name.lower() and not desc:
                    continue

                if desc and desc.strip():
                    inclusion_rules.append(f"{name}: {desc}")
                elif name and name.strip():
                    inclusion_rules.append(name)

        if "PrimaryCriteria" in expr and "ObservationWindow" in expr["PrimaryCriteria"]:
            obs = expr["PrimaryCriteria"]["ObservationWindow"]
            prior = obs.get("PriorDays", 0)
            post = obs.get("PostDays", 0)
            observation_window = f"Continuous observation required: {prior} days before and {post} days after index date"

        if "CensoringCriteria" in expr and expr["CensoringCriteria"]:
            censoring = expr["CensoringCriteria"]
            if isinstance(censoring, list):
                for censor in censoring:
                    if isinstance(censor, dict):
                        for key in censor.keys():
                            criterion_type = key.replace('Occurrence', ' Occurrence')
                            exclusion_rules.append(f"Exclude patients with {criterion_type}")

        if not inclusion_rules:
            inclusion_rules = ["Patients meeting OMOP concept set criteria (see Concept Sets section)"]

        if not exclusion_rules:
            exclusion_rules = ["No additional exclusion criteria beyond primary cohort definition"]

        return CohortCriteria(
            inclusion_rules=inclusion_rules,
            exclusion_rules=exclusion_rules,
            observation_window=observation_window
        )

    def _extract_collection_period(self) -> str:
        """Extract collection period from cohort definition or results"""
        if self.cohort_definition.get('createdDate'):
            created = self.cohort_definition['createdDate']
            if isinstance(created, (int, float)) and created > 1000000000000:
                from datetime import datetime
                created_dt = datetime.fromtimestamp(created / 1000)
                return f"Cohort defined on {created_dt.strftime('%Y-%m-%d')}"
            elif 'T' in str(created):
                created = str(created).split('T')[0]
                return f"Cohort defined on {created}"

        return "See cohort definition for temporal constraints"

    def _extract_population_characteristics(self) -> str:
        """Extract detailed population characteristics from cohort results and definition"""
        if not self.cohort_results:
            return "OMOP CDM standardized cohort. Demographics and clinical characteristics defined by inclusion criteria."

        parts = []

        if "personCount" in self.cohort_results:
            count = self.cohort_results['personCount']
            parts.append(f"Total patients: {count:,}")

        if "summary" in self.cohort_results:
            summary = self.cohort_results["summary"]

            if "age" in summary:
                age_info = summary["age"]
                if isinstance(age_info, dict):
                    if "mean" in age_info and "std" in age_info:
                        parts.append(f"Age: {age_info['mean']:.1f}±{age_info['std']:.1f} years")
                    elif "min" in age_info and "max" in age_info:
                        parts.append(f"Age range: {age_info['min']}-{age_info['max']} years")
                else:
                    parts.append(f"Age: {age_info}")

            if "gender" in summary:
                gender_info = summary["gender"]
                if isinstance(gender_info, dict):
                    gender_parts = []
                    for gender, count in gender_info.items():
                        pct = (count / self.cohort_results['personCount'] * 100) if self.cohort_results['personCount'] > 0 else 0
                        gender_parts.append(f"{gender}: {pct:.1f}%")
                    if gender_parts:
                        parts.append(f"Gender - {', '.join(gender_parts)}")

        if not parts or len(parts) <= 1:
            parts.append("OMOP CDM standardized vocabulary applied")

            concept_sets = self.get_concept_sets()
            if concept_sets:
                cs_count = len(concept_sets)
                parts.append(f"{cs_count} clinical concept set{'s' if cs_count > 1 else ''} defining phenotypes")

        return ". ".join(parts) if parts else "OMOP CDM cohort"

    def _extract_detailed_demographics(self) -> Optional[Dict[str, str]]:
        """Extract detailed demographics from cohort results for tabular display"""
        if not self.cohort_results:
            return None

        demographics = {}

        if "summary" in self.cohort_results:
            summary = self.cohort_results["summary"]

            if "age" in summary:
                age_info = summary["age"]
                if isinstance(age_info, dict):
                    if "mean" in age_info and "std" in age_info:
                        demographics["Age"] = f"Mean: {age_info['mean']:.1f} years (SD: {age_info['std']:.1f})"
                        if "min" in age_info and "max" in age_info:
                            demographics["Age"] += f", Range: {age_info['min']}-{age_info['max']} years"
                    elif "min" in age_info and "max" in age_info:
                        demographics["Age"] = f"Range: {age_info['min']}-{age_info['max']} years"
                else:
                    demographics["Age"] = str(age_info)

            if "gender" in summary:
                gender_info = summary["gender"]
                if isinstance(gender_info, dict):
                    total = sum(gender_info.values())
                    gender_parts = []
                    for gender, count in gender_info.items():
                        pct = (count / total * 100) if total > 0 else 0
                        gender_parts.append(f"{gender}: {count} ({pct:.1f}%)")
                    demographics["Gender"] = ", ".join(gender_parts)
                else:
                    demographics["Gender"] = str(gender_info)

            if "race" in summary:
                race_info = summary["race"]
                if isinstance(race_info, dict):
                    total = sum(race_info.values())
                    race_parts = []
                    for race, count in race_info.items():
                        pct = (count / total * 100) if total > 0 else 0
                        race_parts.append(f"{race}: {count} ({pct:.1f}%)")
                    demographics["Race/Ethnicity"] = ", ".join(race_parts)
                else:
                    demographics["Race/Ethnicity"] = str(race_info)

        return demographics if demographics else None

    def get_data_distribution_summary(self):
        """
        Generate comprehensive data distribution summary from OMOP cohort.
        Returns dict if detailed stats available, otherwise string.
        """
        if self.cohort_results and "summary" in self.cohort_results:
            summary = self.cohort_results["summary"]
            distribution = {}

            if "personCount" in self.cohort_results:
                distribution["Total Cohort Size"] = f"{self.cohort_results['personCount']:,} patients extracted from OMOP CDM using standardized vocabularies (SNOMED CT, ICD-10, LOINC, RxNorm)"

            if "age" in summary:
                age_info = summary["age"]
                if isinstance(age_info, dict):
                    age_parts = []
                    if "mean" in age_info and "std" in age_info:
                        age_parts.append(f"Mean: {age_info['mean']:.1f} years (SD: {age_info['std']:.1f})")
                    if "min" in age_info and "max" in age_info:
                        age_parts.append(f"Range: {age_info['min']}-{age_info['max']} years")
                    if "median" in age_info:
                        age_parts.append(f"Median: {age_info['median']:.1f} years")
                    distribution["Age Distribution"] = ", ".join(age_parts) if age_parts else str(age_info)
                else:
                    distribution["Age Distribution"] = str(age_info)

            if "gender" in summary:
                gender_info = summary["gender"]
                if isinstance(gender_info, dict):
                    total = sum(gender_info.values())
                    gender_parts = []
                    for gender, count in gender_info.items():
                        pct = (count / total * 100) if total > 0 else 0
                        gender_parts.append(f"{gender}: {count} ({pct:.1f}%)")
                    distribution["Gender Distribution"] = ", ".join(gender_parts)
                else:
                    distribution["Gender Distribution"] = str(gender_info)

            if "race" in summary:
                race_info = summary["race"]
                if isinstance(race_info, dict):
                    total = sum(race_info.values())
                    race_parts = []
                    for race, count in race_info.items():
                        pct = (count / total * 100) if total > 0 else 0
                        race_parts.append(f"{race}: {count} ({pct:.1f}%)")
                    distribution["Race/Ethnicity Distribution"] = ", ".join(race_parts)
                else:
                    distribution["Race/Ethnicity Distribution"] = str(race_info)

            concept_sets = self.get_concept_sets()
            if concept_sets:
                total_concepts = sum(len(cs.concept_ids) for cs in concept_sets)
                distribution["Clinical Phenotypes"] = f"{len(concept_sets)} concept set{'s' if len(concept_sets) > 1 else ''} defining clinical phenotypes ({total_concepts} OMOP standard concept IDs)"

            return distribution if distribution else self._get_default_distribution_text()

        return self._get_default_distribution_text()

    def _get_default_distribution_text(self) -> str:
        """Generate default text-based distribution summary"""
        distribution = {}

        if self.cohort_results and "personCount" in self.cohort_results:
            count = self.cohort_results['personCount']
            distribution["Cohort Size"] = f"{count:,} patients extracted from OMOP CDM using ATLAS cohort definition. Data standardized using OMOP vocabularies (SNOMED CT, ICD-10, LOINC, RxNorm)."

        concept_sets = self.get_concept_sets()
        if concept_sets:
            total_concepts = sum(len(cs.concept_ids) for cs in concept_sets)
            cs_details = []
            for cs in concept_sets:
                cs_details.append(f"{cs.name} ({len(cs.concept_ids)} concept{'s' if len(cs.concept_ids) != 1 else ''})")
            distribution["Clinical Phenotypes"] = f"{len(concept_sets)} concept set{'s' if len(concept_sets) > 1 else ''} used: {'; '.join(cs_details)}. Total {total_concepts} OMOP standard concept IDs."

        cohort_name = self.cohort_definition.get('name', '')
        if cohort_name:
            characteristics = []
            if 'male' in cohort_name.lower() or 'female' in cohort_name.lower():
                gender = 'Male' if 'male' in cohort_name.lower() and 'female' not in cohort_name.lower() else 'Female' if 'female' in cohort_name.lower() and 'male' not in cohort_name.lower() else 'Mixed gender'
                characteristics.append(f"Gender: {gender}")

            import re
            age_match = re.search(r'(\d+)\s*(?:plus|and|to|-)\s*(\d+)?', cohort_name.lower())
            if age_match:
                age_lower = age_match.group(1)
                age_upper = age_match.group(2)
                if age_upper:
                    characteristics.append(f"Age range: {age_lower}-{age_upper} years")
                else:
                    characteristics.append(f"Age: {age_lower}+ years")

            if characteristics:
                distribution["Cohort Characteristics"] = "; ".join(characteristics) + " (based on cohort definition)"

        distribution["Demographics Note"] = "Detailed demographic statistics (age distribution, gender breakdown, race/ethnicity) should be obtained using OHDSI Heracles characterization analyses. Run Heracles on this cohort to generate comprehensive demographic summaries including mean/median age, gender percentages, and race/ethnicity distribution."

        return distribution if len(distribution) > 1 else "OMOP CDM standardized cohort. Detailed demographics available via Heracles characterization."


class SyntheticDataAdapter(DataSourceAdapter):
    """Generic adapter for synthetic data packages (MedSynth, Synthea, custom)"""

    def __init__(
        self,
        package_name: str,
        package_version: str,
        num_subjects: int,
        generation_method: str,
        privacy_method: Optional[str] = None,
        population_characteristics: Optional[str] = None
    ):
        self.package_name = package_name
        self.package_version = package_version
        self.num_subjects = num_subjects
        self.generation_method = generation_method
        self.privacy_method = privacy_method
        self.population_characteristics = population_characteristics or "Synthetic population"

    def get_dataset_info(self) -> SourceDataset:
        """Get synthetic dataset info"""
        privacy_note = f" with {self.privacy_method}" if self.privacy_method else ""

        return SourceDataset(
            name=f"{self.package_name} Synthetic Dataset (v{self.package_version})",
            origin=f"Synthetic data generated using {self.package_name}{privacy_note}",
            size=self.num_subjects,
            collection_period="Synthetic (not applicable)",
            population_characteristics=self.population_characteristics
        )

    def get_concept_sets(self) -> List[ConceptSet]:
        """Synthetic data typically doesn't define concept sets"""
        return []

    def get_cohort_criteria(self) -> Optional[CohortCriteria]:
        """Synthetic data typically doesn't have cohort criteria"""
        return None


class CustomDataAdapter(DataSourceAdapter):
    """Adapter for custom data sources"""

    def __init__(
        self,
        name: str,
        origin: str,
        size: int,
        collection_period: str,
        population_characteristics: str,
        concept_sets: Optional[List[ConceptSet]] = None,
        cohort_criteria: Optional[CohortCriteria] = None
    ):
        self._name = name
        self._origin = origin
        self._size = size
        self._collection_period = collection_period
        self._population_characteristics = population_characteristics
        self._concept_sets = concept_sets or []
        self._cohort_criteria = cohort_criteria

    def get_dataset_info(self) -> SourceDataset:
        """Get custom dataset info"""
        return SourceDataset(
            name=self._name,
            origin=self._origin,
            size=self._size,
            collection_period=self._collection_period,
            population_characteristics=self._population_characteristics
        )

    def get_concept_sets(self) -> List[ConceptSet]:
        """Get concept sets if provided"""
        return self._concept_sets

    def get_cohort_criteria(self) -> Optional[CohortCriteria]:
        """Get cohort criteria if provided"""
        return self._cohort_criteria


def create_omop_adapter(
    cohort_definition: Dict[str, Any],
    cohort_results: Optional[Dict[str, Any]] = None,
    source_name: str = "OMOP CDM Database",
    source_origin: str = "Electronic Health Records",
    client: Any = None
) -> OMOPAdapter:
    """
    Create adapter for OMOP CDM data source.

    Args:
        cohort_definition: OMOP cohort definition from smart-omop
        cohort_results: Optional cohort generation results
        source_name: Name of the data source
        source_origin: Origin description

    Returns:
        OMOPAdapter instance
    """
    return OMOPAdapter(cohort_definition, cohort_results, source_name, source_origin, client)


def create_synthetic_adapter(
    package_name: str = "MedSynth",
    package_version: str = "1.0.0",
    num_subjects: int = 100,
    generation_method: str = "Statistical synthesis",
    privacy_method: Optional[str] = None,
    population_characteristics: Optional[str] = None
) -> SyntheticDataAdapter:
    """
    Create adapter for synthetic data packages (MedSynth, Synthea, custom).

    Args:
        package_name: Name of synthetic data package
        package_version: Version of the package
        num_subjects: Number of synthetic subjects
        generation_method: Description of generation method
        privacy_method: Privacy protection method if applicable
        population_characteristics: Description of synthetic population

    Returns:
        SyntheticDataAdapter instance
    """
    return SyntheticDataAdapter(
        package_name,
        package_version,
        num_subjects,
        generation_method,
        privacy_method,
        population_characteristics
    )


def create_custom_adapter(
    name: str,
    origin: str,
    size: int,
    collection_period: str,
    population_characteristics: str,
    concept_sets: Optional[List[ConceptSet]] = None,
    cohort_criteria: Optional[CohortCriteria] = None
) -> CustomDataAdapter:
    """
    Create adapter for custom data sources.

    Args:
        name: Dataset name
        origin: Dataset origin/source
        size: Number of records/subjects
        collection_period: Data collection period
        population_characteristics: Population description
        concept_sets: Optional concept sets
        cohort_criteria: Optional cohort criteria

    Returns:
        CustomDataAdapter instance
    """
    return CustomDataAdapter(
        name,
        origin,
        size,
        collection_period,
        population_characteristics,
        concept_sets,
        cohort_criteria
    )
