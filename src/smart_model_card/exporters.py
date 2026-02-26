"""
Model Card Exporters

Export model cards to various formats (JSON, HTML, Markdown).

Author: Ankur Lohachab
Department of Advanced Computing Sciences, Maastricht University
"""

import json
from pathlib import Path
from typing import Any, Dict
from smart_model_card.model_card import ModelCard
from smart_model_card.html_template import get_html_template
from smart_model_card.section_formatters import (
    format_section_1,
    format_section_2,
    format_section_4,
    format_section_5,
    format_section_6,
    format_section_7
)


class JSONExporter:
    """Export model card to JSON format"""

    @staticmethod
    def export(model_card: ModelCard, output_path: str, public: bool = False) -> str:
        """
        Export model card to JSON file.

        Args:
            model_card: ModelCard instance
            output_path: Path to output JSON file
            public: If True, strips internal-only fields (e.g., de-id report URIs)

        Returns:
            Path to created file
        """
        data = model_card.to_dict(public=public)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        return str(output_file)

    @staticmethod
    def export_from_dict(data: Dict[str, Any], output_path: str) -> str:
        """
        Export already constructed model card dictionary to JSON file.

        Args:
            data: Model card dictionary following schema
            output_path: Path to output JSON file

        Returns:
            Path to created file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        return str(output_file)


class MarkdownExporter:
    """Export model card to Markdown format"""

    @staticmethod
    def export(model_card: ModelCard, output_path: str, public: bool = False) -> str:
        """
        Export model card to Markdown file.

        Args:
            model_card: ModelCard instance
            output_path: Path to output Markdown file

        Returns:
            Path to created file
        """
        data = model_card.to_dict(public=public)
        md_content = MarkdownExporter._dict_to_markdown(data)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            f.write(md_content)

        return str(output_file)

    @staticmethod
    def _dict_to_markdown(data: Dict[str, Any], level: int = 1) -> str:
        """Convert dictionary to Markdown format"""
        lines = []

        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{'#' * level} {key}\n")
                lines.append(MarkdownExporter._dict_to_markdown(value, level + 1))
            elif isinstance(value, list):
                lines.append(f"{'#' * level} {key}\n")
                for item in value:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            lines.append(f"- **{k}**: {v}\n")
                    else:
                        lines.append(f"- {item}\n")
            else:
                if value is not None:
                    lines.append(f"**{key}**: {value}\n\n")

        return "".join(lines)


class HTMLExporter:
    """Export model card to HTML format"""

    @staticmethod
    def export(model_card: ModelCard, output_path: str) -> str:
        """
        Export model card to HTML file.

        Args:
            model_card: ModelCard instance
            output_path: Path to output HTML file

        Returns:
            Path to created file
        """
        data = model_card.to_dict()
        html_content = HTMLExporter._generate_html(data, model_card.model_details.model_name)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            f.write(html_content)

        return str(output_file)

    @staticmethod
    def _generate_html(data: Dict[str, Any], model_name: str) -> str:
        """Generate complete HTML document with professional styling"""
        sections_html = []

        for section_key, section_data in data.items():
            if section_key == "created_at":
                continue

            if section_key == "1. Model Details":
                sections_html.append(format_section_1(section_data))
            elif section_key == "2. Intended Use and Clinical Context":
                sections_html.append(format_section_2(section_data))
            elif section_key == "3. Data & Factors":
                sections_html.append(HTMLExporter._format_section_3_professional(section_data))
            elif section_key == "4. Features & Outputs":
                sections_html.append(format_section_4(section_data))
            elif section_key == "5. Performance & Validation":
                sections_html.append(format_section_5(section_data))
            elif section_key == "6. Methodology & Explainability":
                sections_html.append(format_section_6(section_data))
            elif section_key == "7. Additional Information":
                sections_html.append(format_section_7(section_data))

        created_at = data.get("created_at", "")
        return get_html_template(model_name, "\n".join(sections_html), created_at)

    @staticmethod
    def _format_section_3_professional(section_data: Dict[str, Any]) -> str:
        """Professional formatting for Section 3: Data & Factors"""
        from smart_model_card.section_formatters import format_section_header, format_kv, add_tooltip

        html = format_section_header("sec3", "3. Data & Factors")

        concept_sets = section_data.get("Concept Sets", [])
        if concept_sets:
            html += '<div style="display:flex;justify-content:space-between;align-items:center">'
            html += f'<h3>{add_tooltip("OMOP Concept Sets")}</h3>'
            import json
            concept_sets_json = json.dumps(concept_sets).replace("'", "\\'")
            html += f'<button onclick="downloadAsJSON({concept_sets_json}, \'concept_sets.json\')" '
            html += 'style="padding:0.5rem 1rem;cursor:pointer;border:1px solid var(--rule);border-radius:4px;background:white">'
            html += '📥 Download JSON</button></div>'
            for cs in concept_sets:
                if isinstance(cs, dict):
                    name = cs.get('name', 'Concept Set')
                    vocab = cs.get('vocabulary', 'OMOP')
                    desc = cs.get('description', '')
                    concept_ids = cs.get('concept_ids', [])

                    html += '<div class="concept-card">'
                    html += f'<strong>{name}</strong> ({vocab})<br>'
                    if desc:
                        html += f'<p style="color:var(--muted);font-size:.9rem;margin-top:.5rem">{desc}</p>'

                    if concept_ids:
                        html += '<div style="margin-top:.75rem">'
                        try:
                            from smart_model_card.athena_api import AthenaAPI
                            from smart_model_card.visualizations import generate_concept_relationship_graph

                            enriched_concepts = AthenaAPI.get_concepts_batch(concept_ids[:5])

                            for concept_id in concept_ids[:5]:
                                if concept_id in enriched_concepts:
                                    info = enriched_concepts[concept_id]
                                    concept_name = info.get('concept_name', f'Concept {concept_id}')
                                    domain = info.get('domain_id', 'Unknown')
                                    vocabulary = info.get('vocabulary_id', 'Unknown')

                                    html += f'<div style="margin:0.5rem 0">'
                                    html += f'<span class="concept-id">{concept_id}</span> '
                                    html += f'<strong>{concept_name}</strong> '
                                    html += f'<span style="color:var(--muted);font-size:0.85rem">[{domain}, {vocabulary}]</span>'

                                    related = AthenaAPI.get_related_concepts(concept_id)
                                    if related:
                                        html += f'<div style="margin-top:4px;font-size:0.85em;color:var(--muted)">'
                                        html += f'🔗 {len(related)} related concepts'
                                        html += '</div>'

                                        concept_graph = generate_concept_relationship_graph(concept_id, concept_name, related)
                                        if concept_graph:
                                            html += f'<div style="margin-top:8px">'
                                            html += f'<img src="{concept_graph}" alt="Concept Relationships" class="zoomable-img" style="max-width:100%;height:auto;border-radius:8px" />'
                                            html += '</div>'

                                    html += '</div>'
                                else:
                                    html += f'<span class="concept-id">{concept_id}</span> '

                            if len(concept_ids) > 5:
                                html += f'<div style="color:var(--muted);font-style:italic;margin-top:0.5rem">...and {len(concept_ids) - 5} more concepts</div>'
                        except Exception as e:
                            ids_html = ", ".join(f'<span class="concept-id">{cid}</span>' for cid in concept_ids)
                            html += f"<div>{ids_html}</div>"

                        html += '</div>'

                    html += '</div>'

        cohort_criteria = section_data.get("Primary Cohort Criteria")
        if cohort_criteria and isinstance(cohort_criteria, dict):
            html += '<div style="display:flex;justify-content:space-between;align-items:center">'
            html += f'<h3>{add_tooltip("Primary Cohort Criteria")}</h3>'

            criteria_json = json.dumps(cohort_criteria).replace("'", "\\'")
            html += f'<button onclick="downloadAsJSON({criteria_json}, \'cohort_criteria.json\')" '
            html += 'style="padding:0.5rem 1rem;cursor:pointer;border:1px solid var(--rule);border-radius:4px;background:white">'
            html += '📥 Download JSON</button></div>'

            html += '<div class="concept-card">'

            inclusion_rules = cohort_criteria.get('inclusion_rules', [])
            if inclusion_rules:
                html += '<strong>Inclusion Rules:</strong><ul>'
                for rule in inclusion_rules:
                    if rule and rule.strip():
                        html += f'<li>{rule}</li>'
                html += '</ul>'

            exclusion_rules = cohort_criteria.get('exclusion_rules', [])
            if exclusion_rules:
                html += '<strong>Exclusion Rules:</strong><ul>'
                for rule in exclusion_rules:
                    if rule and 'No explicit exclusion' not in rule:
                        html += f'<li>{rule}</li>'
                html += '</ul>'

            obs_window = cohort_criteria.get('observation_window')
            if obs_window:
                html += f'<strong>Observation Window:</strong><br>{obs_window}'

            html += '</div>'

        source_datasets = section_data.get("Source Datasets", [])
        if source_datasets:
            html += '<div style="display:flex;justify-content:space-between;align-items:center">'
            html += f'<h3>{add_tooltip("Source Datasets")}</h3>'

            import json
            datasets_json = json.dumps([{
                'name': ds.get('name'),
                'origin': ds.get('origin'),
                'size': ds.get('size'),
                'collection_period': ds.get('collection_period'),
                'population_characteristics': ds.get('population_characteristics')
            } for ds in source_datasets if isinstance(ds, dict)]).replace("'", "\\'")

            html += f'<button onclick="downloadAsJSON({datasets_json}, \'source_datasets.json\')" '
            html += 'style="padding:0.5rem 1rem;cursor:pointer;border:1px solid var(--rule);border-radius:4px;background:white">'
            html += '📥 Download JSON</button></div>'

            if len(source_datasets) > 1:
                html += '<div style="margin:1rem 0;padding:0.75rem;background:var(--chip);border-radius:6px">'
                html += '<label for="dataset-select" style="font-weight:600;margin-right:8px">Select Dataset:</label>'
                html += '<select id="dataset-select" onchange="switchDataset(this.value)" style="padding:6px 12px;border:1px solid var(--rule);border-radius:4px;background:white;cursor:pointer">'
                for idx, ds in enumerate(source_datasets):
                    if isinstance(ds, dict):
                        ds_name = ds.get("name", f"Dataset {idx+1}")
                        selected = "selected" if idx == 0 else ""
                        html += f'<option value="{idx}" {selected}>{ds_name}</option>'
                html += '</select></div>'

            for idx, ds in enumerate(source_datasets):
                if isinstance(ds, dict):
                    display_style = "display:block" if idx == 0 else "display:none"
                    html += f'<div class="concept-card dataset-details" id="dataset-{idx}" style="{display_style}">'
                    html += f'<strong>{ds.get("name", "Dataset")}</strong><br>'
                    html += f'<div style="font-size:0.9rem;color:var(--muted);margin-top:0.5rem">'
                    html += f'Origin: {ds.get("origin", "N/A")}<br>'
                    if isinstance(ds.get("size"), int):
                        html += f'Size: <strong>{ds["size"]:,}</strong> records<br>'
                    else:
                        html += f'Size: {ds.get("size", "N/A")}<br>'
                    html += f'Period: {ds.get("collection_period", "N/A")}<br>'
                    html += f'Population: {ds.get("population_characteristics", "N/A")}'
                    html += f'</div></div>'

        data_dist_summary = section_data.get("Data Distribution Summary")
        if source_datasets and len(source_datasets) > 1:
            html += '<div style="display:flex;justify-content:space-between;align-items:center">'
            html += f'<h3>{add_tooltip("Data Distribution Summary")}</h3>'

            all_demographics = []
            for ds in source_datasets:
                if isinstance(ds, dict):
                    demographics = ds.get('demographics', {})
                    if demographics:
                        all_demographics.append({
                            'dataset': ds.get('name', 'Unknown'),
                            'demographics': demographics
                        })

            if all_demographics:
                demographics_json = json.dumps(all_demographics).replace("'", "\\'")
                html += f'<button onclick="downloadAsJSON({demographics_json}, \'data_distribution.json\')" '
                html += 'style="padding:0.5rem 1rem;cursor:pointer;border:1px solid var(--rule);border-radius:4px;background:white">'
                html += '📥 Download JSON</button>'

            html += '</div>'

            for idx, ds in enumerate(source_datasets):
                if isinstance(ds, dict):
                    display_style = "display:block" if idx == 0 else "display:none"
                    html += f'<div class="dataset-summary" id="summary-{idx}" style="{display_style}">'

                    demographics = ds.get('demographics', {})
                    if demographics:
                        html += '<div class="concept-card">'
                        for key, value in demographics.items():
                            html += f'<div class="kv" style="grid-template-columns: 200px 1fr"><div class="kv-label">{key.title()}:</div><div class="kv-value">{value}</div></div>'
                        html += '</div>'
                    else:
                        html += '<div class="concept-card">No detailed demographics available</div>'

                    html += '</div>'
        else:
            html += format_kv("Data Distribution Summary", data_dist_summary)

        data_repr = section_data.get("Data Representativeness")
        if source_datasets and len(source_datasets) > 1:
            html += f'<h3>{add_tooltip("Data Representativeness")}</h3>'
            for idx, ds in enumerate(source_datasets):
                if isinstance(ds, dict):
                    display_style = "display:block" if idx == 0 else "display:none"
                    html += f'<div class="dataset-representativeness" id="repr-{idx}" style="{display_style}">'

                    ds_name = ds.get('name', 'Dataset')
                    origin = ds.get('origin', '')
                    pop_chars = ds.get('population_characteristics', '')

                    html += '<div class="concept-card">'
                    html += f'<strong>Dataset:</strong> {ds_name}<br>'
                    if origin:
                        html += f'<strong>Setting:</strong> {origin}<br><br>'
                    if pop_chars:
                        html += f'<strong>Population:</strong> {pop_chars}<br><br>'

                    if data_repr:
                        html += f'<div style="margin-top:0.5rem;color:var(--muted)">{data_repr}</div>'
                    html += '</div>'

                    html += '</div>'
        else:
            html += format_kv("Data Representativeness", data_repr)

        html += format_kv("Data Governance", section_data.get("Data Governance"))

        omop_reports = section_data.get("OMOP Detailed Reports")
        html += HTMLExporter._format_detailed_omop_reports_professional(omop_reports)

        html += "</div>"

        html += '''<script>
function switchDataset(idx) {
    // Switch dataset details
    document.querySelectorAll('.dataset-details').forEach(el => el.style.display = 'none');
    const selectedDataset = document.getElementById('dataset-' + idx);
    if (selectedDataset) selectedDataset.style.display = 'block';

    // Switch data distribution summary
    document.querySelectorAll('.dataset-summary').forEach(el => el.style.display = 'none');
    const selectedSummary = document.getElementById('summary-' + idx);
    if (selectedSummary) selectedSummary.style.display = 'block';

    // Switch data representativeness
    document.querySelectorAll('.dataset-representativeness').forEach(el => el.style.display = 'none');
    const selectedRepr = document.getElementById('repr-' + idx);
    if (selectedRepr) selectedRepr.style.display = 'block';
}
</script>'''

        return html

    @staticmethod
    def _format_detailed_omop_reports_professional(omop_reports: Dict[str, Any]) -> str:
        """
        Format detailed OMOP reports with professional styling and intelligent N/A display.

        IMPORTANT: This section ALWAYS appears with consistent structure for standardization.
        If no data exists, subsections show "N/A" instead of being hidden.
        """
        person_reports = omop_reports.get("person", {}) if isinstance(omop_reports, dict) else {}

        html = '<div style="margin-top:2rem;padding-top:2rem;border-top:2px solid var(--rule)">'
        html += '<div style="display:flex;justify-content:space-between;align-items:center">'
        html += '<h3>📊 Detailed Reports</h3>'

        if isinstance(omop_reports, dict) and omop_reports:
            import json
            reports_json = json.dumps(omop_reports).replace("'", "\\'")
            html += f'<button onclick="downloadAsJSON({reports_json}, \'omop_detailed_reports.json\')" '
            html += 'style="padding:0.5rem 1rem;cursor:pointer;border:1px solid var(--rule);border-radius:4px;background:white">'
            html += '📥 Download All Reports</button>'

        html += '</div>'

        age_dist = person_reports.get('age_distribution')
        gender_dist = person_reports.get('gender_distribution')
        race_dist = person_reports.get('race_distribution')

        has_age = age_dist and isinstance(age_dist, list) and len(age_dist) > 0
        has_gender = gender_dist and isinstance(gender_dist, list) and len(gender_dist) > 0
        has_race = race_dist and isinstance(race_dist, list) and len(race_dist) > 0

        html += '<h4>Demographics</h4>'

        if has_age or has_gender or has_race:
            try:
                from smart_model_card.visualizations import generate_all_visualizations

                viz_input = {'person': person_reports}
                visualizations = generate_all_visualizations(viz_input)

                if visualizations:
                    html += '<div class="chart-grid">'

                    if 'age_distribution' in visualizations and visualizations['age_distribution']:
                        html += '<div class="chart-card">'
                        html += '<h4>Age Distribution</h4>'
                        html += f'<img src="{visualizations["age_distribution"]}" alt="Age Distribution" class="zoomable-img" style="max-width:100%;height:auto" />'
                        html += '</div>'

                    if 'gender_distribution' in visualizations and visualizations['gender_distribution']:
                        html += '<div class="chart-card">'
                        html += '<h4>Gender Distribution</h4>'
                        html += f'<img src="{visualizations["gender_distribution"]}" alt="Gender Distribution" class="zoomable-img" style="max-width:100%;height:auto" />'
                        html += '</div>'

                    if 'race_distribution' in visualizations and visualizations['race_distribution']:
                        html += '<div class="chart-card">'
                        html += '<h4>Race/Ethnicity Distribution</h4>'
                        html += f'<img src="{visualizations["race_distribution"]}" alt="Race Distribution" class="zoomable-img" style="max-width:100%;height:auto" />'
                        html += '</div>'

                    html += '</div>'
            except Exception as e:
                html += '<p style="color:var(--muted);font-style:italic">N/A - Visualization generation failed</p>'
        else:
            html += '<p style="color:var(--muted);font-style:italic">N/A - No visualization data available</p>'

        html += '<h4 style="margin-top:2rem">Detailed Tables</h4>'

        tables_to_paginate = []

        html += '<h5 style="margin-top:1rem">Age Distribution</h5>'
        if has_age:
            html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">'
            html += '<div></div>'
            html += '<button onclick="downloadTableAsCSV(\'ageTable\', \'age_distribution.csv\')" '
            html += 'style="padding:0.5rem 1rem;cursor:pointer;border:1px solid var(--rule);border-radius:4px;background:white">'
            html += '📥 Download CSV</button></div>'
            html += '<input type="text" class="search-box" placeholder="Search..." onkeyup="filterTable(this, \'ageTable\')">'
            html += '<div class="table-wrap"><table id="ageTable">'
            html += '<thead><tr><th>Year of Birth</th><th>Age</th><th>Count</th><th>Percentage</th></tr></thead><tbody>'
            for row in age_dist:
                if isinstance(row, dict):
                    html += f'<tr><td>{row.get("Year of Birth", "N/A")}</td><td>{row.get("Age", "N/A")}</td><td>{row.get("Count", "N/A")}</td><td>{row.get("Percentage", "N/A")}</td></tr>'
            html += '</tbody></table></div>'
            html += '<div id="pagination-ageTable"></div>'
            if len(age_dist) > 10:
                tables_to_paginate.append("ageTable")
        else:
            html += '<p style="color:var(--muted);font-style:italic">N/A - No age distribution data available</p>'

        html += '<h5 style="margin-top:2rem">Gender Distribution</h5>'
        if has_gender:
            html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">'
            html += '<div></div>'
            html += '<button onclick="downloadTableAsCSV(\'genderTable\', \'gender_distribution.csv\')" '
            html += 'style="padding:0.5rem 1rem;cursor:pointer;border:1px solid var(--rule);border-radius:4px;background:white">'
            html += '📥 Download CSV</button></div>'
            html += '<div class="table-wrap"><table id="genderTable">'
            html += '<thead><tr><th>Gender</th><th>Concept ID</th><th>Count</th><th>Percentage</th></tr></thead><tbody>'
            for row in gender_dist:
                if isinstance(row, dict):
                    html += f'<tr><td>{row.get("Gender", "N/A")}</td><td><span class="concept-id">{row.get("Concept ID", "N/A")}</span></td><td>{row.get("Count", "N/A")}</td><td>{row.get("Percentage", "N/A")}</td></tr>'
            html += '</tbody></table></div>'
            html += '<div id="pagination-genderTable"></div>'
            if len(gender_dist) > 10:
                tables_to_paginate.append("genderTable")
        else:
            html += '<p style="color:var(--muted);font-style:italic">N/A - No gender distribution data available</p>'

        html += '<h5 style="margin-top:2rem">Race/Ethnicity Distribution</h5>'
        if has_race:
            html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">'
            html += '<div></div>'
            html += '<button onclick="downloadTableAsCSV(\'raceTable\', \'race_distribution.csv\')" '
            html += 'style="padding:0.5rem 1rem;cursor:pointer;border:1px solid var(--rule);border-radius:4px;background:white">'
            html += '📥 Download CSV</button></div>'
            html += '<div class="table-wrap"><table id="raceTable">'
            html += '<thead><tr><th>Race/Ethnicity</th><th>Concept ID</th><th>Count</th><th>Percentage</th></tr></thead><tbody>'
            for row in race_dist:
                if isinstance(row, dict):
                    html += f'<tr><td>{row.get("Race", row.get("Ethnicity", "N/A"))}</td><td><span class="concept-id">{row.get("Concept ID", "N/A")}</span></td><td>{row.get("Count", "N/A")}</td><td>{row.get("Percentage", "N/A")}</td></tr>'
            html += '</tbody></table></div>'
            html += '<div id="pagination-raceTable"></div>'
            if len(race_dist) > 10:
                tables_to_paginate.append("raceTable")
        else:
            html += '<p style="color:var(--muted);font-style:italic">N/A - No race/ethnicity distribution data available</p>'

        if tables_to_paginate:
            html += '<script>'
            html += 'window.addEventListener("DOMContentLoaded", function() {'
            for table_id in tables_to_paginate:
                html += f'initPagination("{table_id}", 10);'
            html += '});'
            html += '</script>'

        html += '</div>'

        return html
