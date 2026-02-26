"""
Visualization Generation for OMOP Reports

Generates charts and visualizations from OMOP Heracles reports for model cards.

Author: Ankur Lohachab
Department of Advanced Computing Sciences, Maastricht University
"""

from typing import Dict, List, Optional
import base64
from io import BytesIO


def generate_age_distribution_chart(age_data: List[Dict], title: str = "Age Distribution") -> Optional[str]:
    """
    Generate age distribution bar chart

    Args:
        age_data: List of dicts with Age, Count keys
        title: Chart title

    Returns:
        Base64 encoded PNG image string or None
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        ages = [item['Age'] for item in age_data]
        counts = [item['Count'] for item in age_data]

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(ages, counts, color='#3498db', alpha=0.7, edgecolor='black')
        ax.set_xlabel('Age (years)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Patient Count', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()

        return f"data:image/png;base64,{image_base64}"

    except ImportError:
        print("Warning: matplotlib not available for visualization generation")
        return None
    except Exception as e:
        print(f"Error generating age chart: {e}")
        return None


def generate_gender_pie_chart(gender_data: List[Dict], title: str = "Gender Distribution") -> Optional[str]:
    """
    Generate gender distribution pie chart

    Args:
        gender_data: List of dicts with Gender, Count keys
        title: Chart title

    Returns:
        Base64 encoded PNG image string or None
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        genders = [item['Gender'] for item in gender_data]
        counts = [item['Count'] for item in gender_data]

        colors = ['#e74c3c', '#3498db', '#95a5a6']

        fig, ax = plt.subplots(figsize=(8, 8))
        wedges, texts, autotexts = ax.pie(
            counts,
            labels=genders,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors[:len(genders)]
        )

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(12)

        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()

        return f"data:image/png;base64,{image_base64}"

    except ImportError:
        return None
    except Exception as e:
        print(f"Error generating gender chart: {e}")
        return None


def generate_race_distribution_chart(race_data: List[Dict], title: str = "Race Distribution") -> Optional[str]:
    """
    Generate race distribution horizontal bar chart

    Args:
        race_data: List of dicts with Race, Count keys
        title: Chart title

    Returns:
        Base64 encoded PNG image string or None
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        filtered = [item for item in race_data if item['Race'] != "No matching concept"]

        if not filtered:
            return None

        races = [item['Race'] for item in filtered]
        counts = [item['Count'] for item in filtered]

        fig, ax = plt.subplots(figsize=(10, max(6, len(races) * 0.5)))
        y_pos = range(len(races))
        ax.barh(y_pos, counts, color='#2ecc71', alpha=0.7, edgecolor='black')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(races, fontsize=10)
        ax.set_xlabel('Patient Count', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

        for i, count in enumerate(counts):
            ax.text(count, i, f' {count}', va='center', fontweight='bold')

        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()

        return f"data:image/png;base64,{image_base64}"

    except ImportError:
        return None
    except Exception as e:
        print(f"Error generating race chart: {e}")
        return None


def generate_concept_relationship_graph(concept_id: int, concept_name: str, related_concepts: List[Dict]) -> Optional[str]:
    """
    Generate network graph showing concept relationships

    Args:
        concept_id: Primary concept ID
        concept_name: Primary concept name
        related_concepts: List of related concepts from Athena API

    Returns:
        Base64 encoded PNG image string or None
    """
    if not related_concepts:
        return None

    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches

        fig, ax = plt.subplots(figsize=(14, 10))

        center_x, center_y = 0, 0

        main_circle = plt.Circle((center_x, center_y), 0.15, color='#e74c3c', alpha=0.8, zorder=10)
        ax.add_patch(main_circle)
        ax.text(center_x, center_y, f"{concept_id}\n{concept_name[:30]}...",
                ha='center', va='center', fontsize=9, fontweight='bold',
                color='white', zorder=11, wrap=True)

        import math
        num_related = min(len(related_concepts), 15)
        angle_step = 2 * math.pi / num_related

        for i, related in enumerate(related_concepts[:num_related]):
            angle = i * angle_step
            x = center_x + 1.2 * math.cos(angle)
            y = center_y + 1.2 * math.sin(angle)

            ax.plot([center_x, x], [center_y, y], 'gray', alpha=0.3, linewidth=1, zorder=1)

            circle = plt.Circle((x, y), 0.12, color='#3498db', alpha=0.7, zorder=5)
            ax.add_patch(circle)

            rel_name = related.get('concept_name', '')[:20]
            rel_id = related.get('concept_id', '')
            relationship = related.get('relationship', '')[:15]

            ax.text(x, y, f"{rel_id}\n{rel_name}...",
                    ha='center', va='center', fontsize=7, color='white', zorder=6)

            mid_x = (center_x + x) / 2
            mid_y = (center_y + y) / 2
            ax.text(mid_x, mid_y, relationship, ha='center', va='center',
                    fontsize=6, color='#7f8c8d', style='italic', zorder=7)

        ax.set_xlim(-1.8, 1.8)
        ax.set_ylim(-1.8, 1.8)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f'Concept Relationships for {concept_name} ({concept_id})',
                     fontsize=14, fontweight='bold', pad=20)

        main_patch = mpatches.Patch(color='#e74c3c', label='Primary Concept')
        related_patch = mpatches.Patch(color='#3498db', label='Related Concepts')
        ax.legend(handles=[main_patch, related_patch], loc='upper right', fontsize=10)

        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()

        return f"data:image/png;base64,{image_base64}"

    except ImportError:
        return None
    except Exception as e:
        print(f"Error generating concept relationship graph: {e}")
        return None


def generate_all_visualizations(detailed_reports: Dict) -> Dict[str, Optional[str]]:
    """
    Generate all available visualizations from detailed reports

    Args:
        detailed_reports: Dict from OMOPReportParser.get_all_detailed_reports()

    Returns:
        Dict mapping chart_name -> base64 image data URI
    """
    visualizations = {}

    if 'person' in detailed_reports:
        person = detailed_reports['person']

        if person.get('age_distribution'):
            visualizations['age_distribution'] = generate_age_distribution_chart(
                person['age_distribution'],
                "Patient Age Distribution"
            )

        if person.get('gender_distribution'):
            visualizations['gender_distribution'] = generate_gender_pie_chart(
                person['gender_distribution'],
                "Gender Distribution"
            )

        if person.get('race_distribution'):
            visualizations['race_distribution'] = generate_race_distribution_chart(
                person['race_distribution'],
                "Race/Ethnicity Distribution"
            )

    return {k: v for k, v in visualizations.items() if v is not None}


def generate_performance_metrics_bar_chart(metrics_data: List[Dict], title: str = "Performance Metrics") -> Optional[str]:
    """
    Generate bar chart for performance metrics comparison

    Args:
        metrics_data: List of dicts with metric_name, value, subgroup keys
        title: Chart title

    Returns:
        Base64 encoded PNG image string or None
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np

        if not metrics_data:
            return None

        metric_groups = {}
        for m in metrics_data:
            name = m.get('metric_name', 'Unknown')
            value = m.get('value')
            subgroup = m.get('subgroup') or 'Overall'

            if name not in metric_groups:
                metric_groups[name] = {}
            metric_groups[name][subgroup] = value

        fig, ax = plt.subplots(figsize=(10, 6))

        metric_names = list(metric_groups.keys())
        x = np.arange(len(metric_names))
        width = 0.15

        all_subgroups = set()
        for name in metric_names:
            all_subgroups.update(metric_groups[name].keys())
        all_subgroups = sorted(list(all_subgroups))

        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']

        for i, subgroup in enumerate(all_subgroups):
            values = [metric_groups[name].get(subgroup, 0) for name in metric_names]
            offset = width * (i - len(all_subgroups)/2 + 0.5)
            ax.bar(x + offset, values, width, label=subgroup,
                   color=colors[i % len(colors)], alpha=0.8, edgecolor='black')

        ax.set_xlabel('Metrics', fontsize=12, fontweight='bold')
        ax.set_ylabel('Value', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(metric_names, rotation=0)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(0, 1.0)

        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()

        return f"data:image/png;base64,{image_base64}"

    except ImportError:
        return None
    except Exception as e:
        print(f"Error generating performance bar chart: {e}")
        return None


def generate_performance_metrics_line_chart(metrics_data: List[Dict], title: str = "Performance Across Subgroups") -> Optional[str]:
    """
    Generate line chart showing metric performance across subgroups

    Args:
        metrics_data: List of dicts with metric_name, value, subgroup keys
        title: Chart title

    Returns:
        Base64 encoded PNG image string or None
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        if not metrics_data:
            return None

        metric_groups = {}
        for m in metrics_data:
            name = m.get('metric_name', 'Unknown')
            value = m.get('value')
            subgroup = m.get('subgroup') or 'Overall'

            if name not in metric_groups:
                metric_groups[name] = []
            metric_groups[name].append((subgroup, value))

        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']

        for i, (metric_name, data_points) in enumerate(metric_groups.items()):
            data_points.sort()
            subgroups = [d[0] for d in data_points]
            values = [d[1] for d in data_points]

            ax.plot(subgroups, values, marker='o', linewidth=2,
                   label=metric_name, color=colors[i % len(colors)],
                   markersize=8)

        ax.set_xlabel('Subgroups', fontsize=12, fontweight='bold')
        ax.set_ylabel('Metric Value', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1.0)
        plt.xticks(rotation=45, ha='right')

        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()

        return f"data:image/png;base64,{image_base64}"

    except ImportError:
        return None
    except Exception as e:
        print(f"Error generating performance line chart: {e}")
        return None
