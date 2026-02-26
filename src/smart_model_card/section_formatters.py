"""
Section Formatters for Professional HTML Model Cards

Author: Ankur Lohachab
Department of Advanced Computing Sciences, Maastricht University
"""

from typing import Dict, Any, List, Union


FIELD_TOOLTIPS = {
    "Model Name": "Unique identifier and name of the AI/ML model",
    "Version": "Version number of the model (e.g., 1.0.0, 2.1.3)",
    "Developer / Organization": "Organization or team that developed the model",
    "Release Date": "Date when the model was released or deployed (YYYY-MM-DD format)",
    "Description": "Brief description of what the model does and its purpose",
    "Clinical Function": "Clinical function category of the model (e.g., diagnosis, screening, decision_support)",
    "Intended Purpose": "Free-text regulatory intended purpose statement as defined in MDR Article 2(12) / FDA intended use",
    "Information Significance": "IMDRF N12 Section 5.1: significance of the information provided by the model to the healthcare decision (inform, drive, treat_or_diagnose)",
    "Basic UDI-DI": "Basic UDI-DI as defined in MDR Article 27 and Annex VI Part C, identifying the device model/product line",
    "UDI-DI": "UDI-DI identifying the specific device configuration",
    "Regulatory Classifications": "Multi-jurisdictional device classifications (e.g., EU MDR, FDA, EU AI Act)",
    "Algorithm(s) Used": "Machine learning algorithms and techniques used (e.g., Random Forest, XGBoost, Neural Network)",
    "GMDN Code": "Global Medical Device Nomenclature code if applicable for medical devices",
    "Licensing": "Software license under which the model is distributed",
    "Support Contact": "Contact information for technical support and inquiries",
    "Literature References": "Published papers or documentation related to the model",

    "Primary Intended Users": "Target audience who will use the model (e.g., clinicians, radiologists, researchers)",
    "Clinical Indications": "Specific clinical scenarios or conditions where the model should be used",
    "Patient target group": "Demographic and clinical characteristics of the patient population the model is designed for",
    "Contraindications": "Situations or conditions where the model should not be used",
    "Intended Use Environment": "Clinical or operational setting where the model is designed to operate",
    "Out of Scope Applications": "Uses or applications that are explicitly not supported or recommended",
    "Warnings": "Important safety warnings and precautions for model use",

    "Source Datasets": "Description of datasets used for training and development",
    "Data Distribution Summary": "Statistical summary of data distribution including demographics and clinical variables",
    "Data Representativeness": "How well the training data represents the target population",
    "Data Governance": "Policies and procedures for data access, privacy, and compliance (e.g., HIPAA, GDPR)",

    "Input Features": "Variables and features required as input to the model",
    "Output Features": "Predictions or outputs produced by the model",
    "Feature Type Distribution": "Distribution of feature types (numeric, categorical, text, etc.)",
    "Uncertainty Quantification": "How the model quantifies and reports prediction uncertainty",
    "Output Interpretability": "Methods used to explain and interpret model predictions",

    "Validation Dataset(s)": "Datasets used to validate model performance",
    "Claimed Metrics": "Performance metrics reported by the model developers",
    "Validated Metrics": "Performance metrics independently validated",
    "Calibration Analysis": "Analysis of how well predicted probabilities match actual outcomes",
    "Fairness Assessment": "Evaluation of model fairness across different demographic groups",
    "Metric Validation Status": "Overall status of metric validation and verification",

    "Model Development Workflow": "Step-by-step process used to develop the model",
    "Training Procedure": "Specific training methodology, hyperparameters, and optimization approach",
    "Data Preprocessing": "Data cleaning, normalization, and transformation steps applied",
    "Synthetic Data Usage": "Description of any synthetic or augmented data used",
    "Explainable AI Method": "Techniques used to make the model interpretable (e.g., SHAP, LIME, attention maps)",
    "Global vs. Local Interpretability": "Explanation of global model behavior vs. individual prediction explanations",

    "Benefit–Risk Summary": "Summary of potential benefits and risks of using the model",
    "Post-Market Surveillance Plan": "Plan for monitoring model performance after deployment",
    "Ethical Considerations": "Ethical implications and considerations for model use",
    "Caveats & Limitations": "Known limitations, edge cases, and constraints of the model",
    "Recommendations for Safe Use": "Guidelines and best practices for safe and effective model use",
    "Explainability Recommendations": "Recommendations for interpreting and explaining model outputs to end users",
    "Supporting Documents": "Links to additional documentation, validation reports, or supplementary materials",

    "Validation Datasets": "Datasets used to evaluate model performance independent of training data",
    "Performance Metrics": "Quantitative measures of model accuracy, precision, recall, and other performance indicators",
    "OMOP Concept Sets": "Standardized medical concepts from OMOP Common Data Model used to define clinical variables",
    "Primary Cohort Criteria": "Inclusion and exclusion rules defining the patient population cohort",
    "Source Datasets": "Datasets used for training and development of the model",
}


def add_tooltip(label: str) -> str:
    """
    Add tooltip icon to a label if tooltip text is available.

    Args:
        label: The label text

    Returns:
        HTML string with label and optional tooltip icon
    """
    if label in FIELD_TOOLTIPS:
        tooltip_text = FIELD_TOOLTIPS[label].replace('"', '&quot;')
        return f'{label} <span class="info-icon" data-tooltip="{tooltip_text}">?</span>'
    return label


def safe_display(value: Any, default: str = "N/A") -> str:
    """
    Display value if exists, otherwise show N/A.

    Args:
        value: The value to display
        default: Default value to show if no data (default: "N/A")

    Returns:
        String representation of value or default
    """
    if value is None or value == "":
        return default
    if isinstance(value, (list, dict)) and not value:
        return default
    return str(value)


def format_section_header(section_id: str, section_title: str) -> str:
    """Generate collapsible section header"""
    return f'''<div class="section" id="{section_id}">
  <h2>
    <button class="section-toggle" type="button" aria-expanded="true">
      <span class="caret"></span>
      <span>{section_title}</span>
    </button>
  </h2>'''


def format_kv(label: str, value: Any, show_na: bool = True) -> str:
    """
    Format key-value pair with intelligent N/A display and tooltip.

    Args:
        label: The label text
        value: The value to display
        show_na: If True, show "N/A" for empty values; if False, hide the entire row

    Returns:
        HTML string for key-value pair
    """
    is_empty = (value is None or value == "" or
                (isinstance(value, (list, dict)) and not value))

    if is_empty:
        if not show_na:
            return ""
        value_html = '<span style="color:var(--muted);font-style:italic">N/A</span>'
    elif isinstance(value, list):
        items = "".join(f"<li>{item}</li>" for item in value if item)
        if not items:
            if not show_na:
                return ""
            value_html = '<span style="color:var(--muted);font-style:italic">N/A</span>'
        else:
            value_html = f"<ul>{items}</ul>"
    else:
        value_html = str(value)

    label_html = label
    if label in FIELD_TOOLTIPS:
        tooltip_text = FIELD_TOOLTIPS[label].replace('"', '&quot;')
        label_html = f'{label}<span class="info-icon" data-tooltip="{tooltip_text}">?</span>'

    return f'<div class="kv"><div class="kv-label">{label_html}:</div><div class="kv-value">{value_html}</div></div>'


def format_section_1(data: Dict[str, Any]) -> str:
    """Format Section 1: Model Details"""
    html = format_section_header("sec1", "1. Model Details")

    fields = [
        ("Model Name", data.get("Model Name")),
        ("Version", data.get("Version")),
        ("Developer / Organization", data.get("Developer / Organization")),
        ("Release Date", data.get("Release Date")),
        ("Description", data.get("Description")),
        ("Clinical Function", data.get("Clinical Function")),
        ("Intended Purpose", data.get("Intended Purpose")),
        ("Information Significance", data.get("Information Significance")),
        ("Algorithm(s) Used", data.get("Algorithm(s) Used")),
        ("GMDN Code", data.get("GMDN Code")),
        ("Basic UDI-DI", data.get("Basic UDI-DI")),
        ("UDI-DI", data.get("UDI-DI")),
        ("Licensing", data.get("Licensing")),
        ("Support Contact", data.get("Support Contact")),
        ("Literature References", data.get("Literature References")),
    ]

    for label, value in fields:
        html += format_kv(label, value)

    reg_class = data.get("Regulatory Classifications", [])
    label_html = add_tooltip("Regulatory Classifications")
    if reg_class:
        html += f'<div class="kv-row"><span class="kv-label">{label_html}</span>'
        html += '<span class="kv-value"><table><thead><tr><th>Framework</th><th>Class</th><th>Rule</th><th>Pathway</th></tr></thead><tbody>'
        for entry in reg_class:
            fw = entry.get("framework", "")
            cl = entry.get("class", "")
            rl = entry.get("rule", "")
            pw = entry.get("pathway", "")
            html += f'<tr><td>{fw}</td><td>{cl}</td><td>{rl or "—"}</td><td>{pw or "—"}</td></tr>'
        html += '</tbody></table></span></div>'
    else:
        html += format_kv("Regulatory Classifications", None)

    html += "</div>"
    return html


def format_section_2(data: Dict[str, Any]) -> str:
    """Format Section 2: Intended Use"""
    html = format_section_header("sec2", "2. Intended Use and Clinical Context")

    fields = [
        ("Primary Intended Users", data.get("Primary Intended Users")),
        ("Clinical Indications", data.get("Clinical Indications")),
        ("Patient target group", data.get("Patient target group")),
        ("Contraindications", data.get("Contraindications")),
        ("Intended Use Environment", data.get("Intended Use Environment")),
        ("Out of Scope Applications", data.get("Out of Scope Applications")),
        ("Warnings", data.get("Warnings")),
    ]

    for label, value in fields:
        html += format_kv(label, value)

    html += "</div>"
    return html


def format_section_4(data: Dict[str, Any]) -> str:
    """Format Section 4: Features & Outputs"""
    html = format_section_header("sec4", "4. Features & Outputs")

    input_features = data.get("Input Features", [])
    if input_features:
        html += f'<h3>{add_tooltip("Input Features")}</h3>'
        html += '<input type="text" class="search-box" placeholder="Search features..." onkeyup="filterTable(this, \'inputFeaturesTable\')">'
        html += '<div class="table-wrap"><table id="inputFeaturesTable">'
        html += '<thead><tr><th>Name</th><th>Type</th><th>Required</th><th>Domain</th><th>Range</th><th>Units</th></tr></thead>'
        html += '<tbody>'

        for feat in input_features:
            if isinstance(feat, dict):
                name = feat.get('name', '')
                data_type = feat.get('data_type', '')
                required = '✓' if feat.get('required') else ''
                domain = feat.get('clinical_domain', '')
                value_range = feat.get('value_range', '—')
                units = feat.get('units', '—')

                html += f'<tr>'
                html += f'<td><span class="code">{name}</span></td>'
                html += f'<td>{data_type}</td>'
                html += f'<td>{required}</td>'
                html += f'<td>{domain}</td>'
                html += f'<td>{value_range}</td>'
                html += f'<td>{units}</td>'
                html += f'</tr>'

        html += '</tbody></table></div>'

    output_features = data.get("Output Features", [])
    if output_features:
        html += f'<h3>{add_tooltip("Output Features")}</h3>'
        html += '<div class="table-wrap"><table>'
        html += '<thead><tr><th>Name</th><th>Type</th><th>Range/Classes</th><th>Units</th></tr></thead>'
        html += '<tbody>'

        for feat in output_features:
            if isinstance(feat, dict):
                name = feat.get('name', '')
                feat_type = feat.get('type', '')

                range_val = feat.get('value_range', '')
                classes = feat.get('classes', [])
                if classes:
                    range_val = ', '.join(str(c) for c in classes)

                units = feat.get('units', '—')

                html += f'<tr>'
                html += f'<td><span class="code">{name}</span></td>'
                html += f'<td>{feat_type}</td>'
                html += f'<td>{range_val}</td>'
                html += f'<td>{units}</td>'
                html += f'</tr>'

        html += '</tbody></table></div>'

    html += format_kv("Feature Type Distribution", data.get("Feature Type Distribution"))
    html += format_kv("Uncertainty Quantification", data.get("Uncertainty Quantification"))
    html += format_kv("Output Interpretability", data.get("Output Interpretability"))

    html += "</div>"
    return html


def format_section_5(data: Dict[str, Any]) -> str:
    """Format Section 5: Performance & Validation"""
    html = format_section_header("sec5", "5. Performance & Validation")

    val_datasets = data.get("Validation Dataset(s)", [])
    if val_datasets:
        html += f'<h3>{add_tooltip("Validation Datasets")}</h3>'
        for ds in val_datasets:
            if isinstance(ds, dict):
                html += '<div class="concept-card">'
                html += f'<strong>{ds.get("name", "Dataset")}</strong><br>'
                html += f'<div style="margin-top:0.5rem;color:var(--muted);font-size:0.9rem">'
                html += f'Source: {safe_display(ds.get("source_institution"))}<br>'
                html += f'Population: {safe_display(ds.get("population_characteristics"))}<br>'
                html += f'Validation Type: {safe_display(ds.get("validation_type"))}'
                html += f'</div></div>'
    else:
        html += f'<h3>{add_tooltip("Validation Datasets")}</h3>'
        html += '<p style="color:var(--muted);font-style:italic">N/A</p>'

    claimed_metrics = data.get("Claimed Metrics", [])
    validated_metrics = data.get("Validated Metrics", [])

    all_metrics = claimed_metrics + validated_metrics

    if all_metrics:
        html += f'<h3>{add_tooltip("Performance Metrics")}</h3>'

        try:
            from smart_model_card.visualizations import (
                generate_performance_metrics_bar_chart,
                generate_performance_metrics_line_chart
            )

            bar_chart = generate_performance_metrics_bar_chart(all_metrics, "Performance Metrics Comparison")
            has_subgroups = any(m.get('subgroup') and m.get('subgroup') != 'Overall' for m in all_metrics if isinstance(m, dict))
            line_chart = generate_performance_metrics_line_chart(all_metrics, "Metrics Across Subgroups") if has_subgroups else None

            if bar_chart or line_chart:
                html += '<div class="chart-grid">'
                if bar_chart:
                    html += '<div class="chart-card">'
                    html += '<h4>Metrics Comparison</h4>'
                    html += f'<img src="{bar_chart}" alt="Performance Metrics Bar Chart" class="zoomable-img" style="max-width:100%;height:auto" />'
                    html += '</div>'
                if line_chart:
                    html += '<div class="chart-card">'
                    html += '<h4>Performance Trends</h4>'
                    html += f'<img src="{line_chart}" alt="Performance Metrics Line Chart" class="zoomable-img" style="max-width:100%;height:auto" />'
                    html += '</div>'
                html += '</div>'
        except Exception as e:
            pass

        html += '<div class="metrics-grid">'

        for metric in all_metrics:
            if isinstance(metric, dict):
                html += '<div class="metric-card">'
                html += f'<div class="metric-value">{safe_display(metric.get("value"))}</div>'
                html += f'<div class="metric-label">{safe_display(metric.get("metric_name", "Metric"))}</div>'

                subgroup = metric.get("subgroup")
                if subgroup and subgroup != "Overall":
                    html += f'<div style="font-size:0.85rem;color:var(--muted);margin-top:0.25rem">{subgroup}</div>'

                html += f'<div class="badge badge-warning">Claimed</div>'
                html += '</div>'

        html += '</div>'
    else:
        html += f'<h3>{add_tooltip("Performance Metrics")}</h3>'
        html += '<p style="color:var(--muted);font-style:italic">N/A</p>'

    html += format_kv("Calibration Analysis", data.get("Calibration Analysis"))
    html += format_kv("Fairness Assessment", data.get("Fairness Assessment"))
    html += format_kv("Metric Validation Status", data.get("Metric Validation Status"))

    html += "</div>"
    return html


def format_section_6(data: Dict[str, Any]) -> str:
    """Format Section 6: Methodology"""
    html = format_section_header("sec6", "6. Methodology & Explainability")

    fields = [
        ("Model Development Workflow", data.get("Model Development Workflow")),
        ("Training Procedure", data.get("Training Procedure")),
        ("Data Preprocessing", data.get("Data Preprocessing")),
        ("Synthetic Data Usage", data.get("Synthetic Data Usage")),
        ("Explainable AI Method", data.get("Explainable AI Method")),
        ("Global vs. Local Interpretability", data.get("Global vs. Local Interpretability")),
    ]

    for label, value in fields:
        html += format_kv(label, value)

    html += "</div>"
    return html


def format_section_7(data: Dict[str, Any]) -> str:
    """Format Section 7: Additional Info"""
    html = format_section_header("sec7", "7. Additional Information")

    fields = [
        ("Benefit–Risk Summary", data.get("Benefit–Risk Summary")),
        ("Post-Market Surveillance Plan", data.get("Post-Market Surveillance Plan")),
        ("Ethical Considerations", data.get("Ethical Considerations")),
        ("Caveats & Limitations", data.get("Caveats & Limitations")),
        ("Recommendations for Safe Use", data.get("Recommendations for Safe Use")),
        ("Explainability Recommendations", data.get("Explainability Recommendations")),
        ("Supporting Documents", data.get("Supporting Documents")),
    ]

    for label, value in fields:
        html += format_kv(label, value)

    html += "</div>"
    return html
