"""
OMOP Report Parser for Dynamic Section 3 Generation

Parses smart-omop report JSON files (person, dashboard, condition, drug, etc.)
and generates structured data for model card Section 3.

Author: Ankur Lohachab
Department of Advanced Computing Sciences, Maastricht University
"""

from typing import Dict, Any, List, Optional, Union
import json
from pathlib import Path


class OMOPReportParser:
    """Parser for OMOP Heracles characterization reports with detailed data preservation"""

    def __init__(self, person_report: Optional[Dict] = None,
                 dashboard_report: Optional[Dict] = None,
                 condition_report: Optional[Dict] = None,
                 drug_report: Optional[Dict] = None):
        """
        Initialize with report data dictionaries

        Args:
            person_report: Person demographics report
            dashboard_report: Dashboard summary report
            condition_report: Condition occurrence report
            drug_report: Drug exposure report
        """
        self.person_report = person_report or {}
        self.dashboard_report = dashboard_report or {}
        self.condition_report = condition_report or {}
        self.drug_report = drug_report or {}

        self.has_person = bool(self.person_report)
        self.has_dashboard = bool(self.dashboard_report)
        self.has_condition = bool(self.condition_report)
        self.has_drug = bool(self.drug_report)

    @classmethod
    def from_files(cls, person_path: Optional[str] = None,
                   dashboard_path: Optional[str] = None,
                   condition_path: Optional[str] = None,
                   drug_path: Optional[str] = None):
        """Load reports from JSON files"""
        def load_json(path):
            if path and Path(path).exists():
                with open(path, 'r') as f:
                    return json.load(f)
            return {}

        return cls(
            person_report=load_json(person_path),
            dashboard_report=load_json(dashboard_path),
            condition_report=load_json(condition_path),
            drug_report=load_json(drug_path)
        )

    def get_demographics_summary(self) -> Dict[str, str]:
        """
        Extract demographics summary from person/dashboard reports

        Returns:
            Dict with demographic categories and formatted strings
        """
        demographics = {}

        gender_data = self.person_report.get('gender') or self.dashboard_report.get('gender')
        if gender_data:
            total = sum(item['countValue'] for item in gender_data)
            gender_parts = []
            for item in gender_data:
                name = item['conceptName']
                count = item['countValue']
                pct = (count / total * 100) if total > 0 else 0
                gender_parts.append(f"{name.title()}: {count} ({pct:.1f}%)")
            demographics["Gender Distribution"] = ", ".join(gender_parts)

        if 'yearOfBirthStats' in self.person_report and self.person_report['yearOfBirthStats']:
            yob_stats = self.person_report['yearOfBirthStats'][0]
            min_yob = yob_stats.get('minValue')
            max_yob = yob_stats.get('maxValue')

            if min_yob and max_yob:
                from datetime import datetime
                current_year = datetime.now().year
                max_age = current_year - min_yob
                min_age = current_year - max_yob

                demographics["Age Range"] = f"{min_age}-{max_age} years (birth years {min_yob}-{max_yob})"

                yob_dist = self.person_report.get('yearOfBirth', [])
                if yob_dist:
                    total_count = sum(item['countValue'] for item in yob_dist)
                    weighted_age_sum = 0
                    for item in yob_dist:
                        yob = min_yob + item['intervalIndex'] * yob_stats.get('intervalSize', 1)
                        age = current_year - yob
                        weighted_age_sum += age * item['countValue']

                    mean_age = weighted_age_sum / total_count if total_count > 0 else 0
                    demographics["Mean Age"] = f"{mean_age:.1f} years"

        race_data = self.person_report.get('race')
        if race_data:
            race_parts = []
            total = sum(item['countValue'] for item in race_data if item['conceptName'] != "No matching concept")

            for item in race_data:
                name = item['conceptName']
                if name == "No matching concept":
                    continue
                count = item['countValue']
                pct = (count / total * 100) if total > 0 else 0
                race_parts.append(f"{name}: {count} ({pct:.1f}%)")

            if race_parts:
                demographics["Race Distribution"] = ", ".join(race_parts)
            else:
                demographics["Race"] = "Not recorded in source data"

        ethnicity_data = self.person_report.get('ethnicity')
        if ethnicity_data:
            ethnicity_parts = []
            total = sum(item['countValue'] for item in ethnicity_data if item['conceptName'] != "No matching concept")

            for item in ethnicity_data:
                name = item['conceptName']
                if name == "No matching concept":
                    continue
                count = item['countValue']
                pct = (count / total * 100) if total > 0 else 0
                ethnicity_parts.append(f"{name}: {count} ({pct:.1f}%)")

            if ethnicity_parts:
                demographics["Ethnicity Distribution"] = ", ".join(ethnicity_parts)
            else:
                demographics["Ethnicity"] = "Not recorded in source data"

        return demographics

    def get_detailed_age_distribution(self) -> Optional[List[Dict]]:
        """
        Get detailed age distribution for interactive tables

        Returns:
            List of dicts with year of birth bins and counts
        """
        if 'yearOfBirth' not in self.person_report or 'yearOfBirthStats' not in self.person_report:
            return None

        yob_dist = self.person_report['yearOfBirth']
        yob_stats = self.person_report['yearOfBirthStats'][0] if self.person_report['yearOfBirthStats'] else {}

        min_yob = yob_stats.get('minValue')
        interval_size = yob_stats.get('intervalSize', 1)

        from datetime import datetime
        current_year = datetime.now().year

        detailed = []
        for item in yob_dist:
            yob = min_yob + item['intervalIndex'] * interval_size if min_yob else item['intervalIndex']
            age = current_year - yob
            detailed.append({
                'Year of Birth': yob,
                'Age': age,
                'Count': item['countValue'],
                'Percentage': f"{item['percentValue'] * 100:.2f}%"
            })

        detailed.sort(key=lambda x: x['Age'], reverse=True)
        return detailed

    def get_detailed_gender_distribution(self) -> Optional[List[Dict]]:
        """Get gender distribution for interactive tables"""
        gender_data = self.person_report.get('gender') or self.dashboard_report.get('gender')
        if not gender_data:
            return None

        total = sum(item['countValue'] for item in gender_data)
        result = []
        for item in gender_data:
            result.append({
                'Gender': item['conceptName'],
                'Concept ID': item['conceptId'],
                'Count': item['countValue'],
                'Percentage': f"{(item['countValue'] / total * 100):.2f}%" if total > 0 else "0%"
            })

        return result

    def get_detailed_race_distribution(self) -> Optional[List[Dict]]:
        """Get race distribution for interactive tables"""
        race_data = self.person_report.get('race')
        if not race_data:
            return None

        result = []
        total = sum(item['countValue'] for item in race_data if item['conceptName'] != "No matching concept")

        for item in race_data:
            result.append({
                'Race': item['conceptName'],
                'Concept ID': item['conceptId'],
                'Count': item['countValue'],
                'Percentage': f"{(item['countValue'] / total * 100):.2f}%" if total > 0 and item['conceptName'] != "No matching concept" else "N/A"
            })

        return result

    def get_detailed_ethnicity_distribution(self) -> Optional[List[Dict]]:
        """Get ethnicity distribution for interactive tables"""
        ethnicity_data = self.person_report.get('ethnicity')
        if not ethnicity_data:
            return None

        result = []
        total = sum(item['countValue'] for item in ethnicity_data if item['conceptName'] != "No matching concept")

        for item in ethnicity_data:
            result.append({
                'Ethnicity': item['conceptName'],
                'Concept ID': item['conceptId'],
                'Count': item['countValue'],
                'Percentage': f"{(item['countValue'] / total * 100):.2f}%" if total > 0 and item['conceptName'] != "No matching concept" else "N/A"
            })

        return result

    def get_all_detailed_reports(self) -> Dict[str, Any]:
        """
        Get all detailed reports in structured format for interactive display

        Returns:
            Dict with report_type -> detailed data
        """
        reports = {}

        if self.has_person:
            reports['person'] = {
                'age_distribution': self.get_detailed_age_distribution(),
                'gender_distribution': self.get_detailed_gender_distribution(),
                'race_distribution': self.get_detailed_race_distribution(),
                'ethnicity_distribution': self.get_detailed_ethnicity_distribution()
            }

        if self.has_dashboard:
            reports['dashboard'] = {
                'gender': self.get_detailed_gender_distribution()
            }

        if self.has_condition:
            reports['condition'] = self.condition_report

        if self.has_drug:
            reports['drug'] = self.drug_report

        return reports

    def get_condition_summary(self) -> Optional[str]:
        """Extract top conditions from condition report"""
        if not self.condition_report:
            return None

        return "Condition data available in report"

    def get_drug_summary(self) -> Optional[str]:
        """Extract top drugs from drug report"""
        if not self.drug_report:
            return None

        return "Drug exposure data available in report"

    def generate_data_distribution_summary(self, cohort_size: int,
                                          concept_sets_info: str) -> Dict[str, str]:
        """
        Generate complete data distribution summary for Section 3

        Args:
            cohort_size: Total number of patients
            concept_sets_info: Description of concept sets used

        Returns:
            Dictionary with distribution summary sections
        """
        distribution = {}

        distribution["Cohort Size"] = (
            f"{cohort_size:,} patients extracted from OMOP CDM. "
            f"Data characterized using OHDSI Heracles analyses with standardized "
            f"clinical vocabularies (SNOMED CT, ICD-10, LOINC, RxNorm)."
        )

        if concept_sets_info:
            distribution["Clinical Phenotypes"] = concept_sets_info

        demographics = self.get_demographics_summary()
        distribution.update(demographics)

        if demographics:
            distribution["Data Quality"] = (
                "Demographics extracted from Heracles characterization. "
                "All counts and percentages based on OMOP CDM standardized data."
            )

        return distribution


def load_reports_from_directory(reports_dir: Union[str, Path]) -> OMOPReportParser:
    """
    Load all available reports from a directory

    Args:
        reports_dir: Path to directory containing report JSON files

    Returns:
        OMOPReportParser with loaded reports
    """
    reports_dir = Path(reports_dir)

    def find_report(base_name):
        for variant in [f"{base_name}.json", f"{base_name}_report.json"]:
            path = reports_dir / variant
            if path.exists():
                return str(path)
        return None

    return OMOPReportParser.from_files(
        person_path=find_report("person"),
        dashboard_path=find_report("dashboard"),
        condition_path=find_report("condition"),
        drug_path=find_report("drug")
    )
