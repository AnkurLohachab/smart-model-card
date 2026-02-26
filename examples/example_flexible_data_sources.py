"""
Flexible Data Sources Example

Demonstrates using various data sources: OMOP, MedSynth, Synthea, custom packages.
Shows how the package adapts to any data source while maintaining standardization.

Author: Ankur Lohachab
Department of Advanced Computing Sciences, Maastricht University
"""

from smart_model_card import (
    ModelCard,
    ModelDetails,
    IntendedUse,
    DataFactors,
    FeaturesOutputs,
    PerformanceValidation,
    Methodology,
    AdditionalInfo,
    HTMLExporter,
    create_synthetic_adapter,
    create_custom_adapter
)
from smart_model_card.sections import (
    InputFeature,
    OutputFeature,
    ValidationDataset,
    PerformanceMetric
)


def example_medsynth_integration():
    """Example using MedSynth synthetic data"""
    print("\n" + "=" * 60)
    print("Example 1: MedSynth Synthetic Data")
    print("=" * 60)

    # Create MedSynth adapter
    medsynth_adapter = create_synthetic_adapter(
        package_name="MedSynth",
        package_version="1.0.0",
        num_subjects=500,
        generation_method="Multi-Scale Statistical Texture Synthesis (MS-STS)",
        privacy_method="Privacy-preserving synthesis (MI < 1.8 bits)",
        population_characteristics="Synthetic COPD patients with privacy protection"
    )

    dataset = medsynth_adapter.get_dataset_info()
    print(f"✓ Dataset: {dataset.name}")
    print(f"  Subjects: {dataset.size}")
    print(f"  Method: {dataset.origin}")


def example_synthea_integration():
    """Example using Synthea synthetic data"""
    print("\n" + "=" * 60)
    print("Example 2: Synthea Synthetic Data")
    print("=" * 60)

    # Create Synthea adapter
    synthea_adapter = create_synthetic_adapter(
        package_name="Synthea",
        package_version="3.2.0",
        num_subjects=1000,
        generation_method="Agent-based patient simulation",
        privacy_method=None,  # Synthea is inherently synthetic
        population_characteristics="Synthetic US population with realistic demographics and disease progression"
    )

    dataset = synthea_adapter.get_dataset_info()
    print(f"✓ Dataset: {dataset.name}")
    print(f"  Subjects: {dataset.size}")
    print(f"  Method: {dataset.origin}")


def example_custom_synthetic_package():
    """Example using custom synthetic data package"""
    print("\n" + "=" * 60)
    print("Example 3: Custom Synthetic Package")
    print("=" * 60)

    # Create adapter for any custom synthetic package
    custom_synth_adapter = create_synthetic_adapter(
        package_name="MyCustomSynth",
        package_version="2.0.1",
        num_subjects=250,
        generation_method="GAN-based synthetic EHR generation",
        privacy_method="Differential privacy (epsilon=1.0)",
        population_characteristics="Synthetic cardiovascular patients"
    )

    dataset = custom_synth_adapter.get_dataset_info()
    print(f"✓ Dataset: {dataset.name}")
    print(f"  Subjects: {dataset.size}")
    print(f"  Privacy: Differential privacy")


def example_proprietary_database():
    """Example using proprietary clinical database"""
    print("\n" + "=" * 60)
    print("Example 4: Proprietary Clinical Database")
    print("=" * 60)

    # Create custom adapter for proprietary data
    proprietary_adapter = create_custom_adapter(
        name="Institution XYZ Clinical Data Warehouse",
        origin="Multi-center EHR system (Epic, Cerner)",
        size=50000,
        collection_period="2015-2024",
        population_characteristics="Urban academic medical centers, 55% female, mean age 62 years, ethnically diverse"
    )

    dataset = proprietary_adapter.get_dataset_info()
    print(f"✓ Dataset: {dataset.name}")
    print(f"  Size: {dataset.size} patients")
    print(f"  Period: {dataset.collection_period}")


def example_publicly_available_dataset():
    """Example using publicly available dataset (e.g., MIMIC, eICU)"""
    print("\n" + "=" * 60)
    print("Example 5: Publicly Available Dataset (MIMIC-IV)")
    print("=" * 60)

    # Create custom adapter for public dataset
    mimic_adapter = create_custom_adapter(
        name="MIMIC-IV Database",
        origin="ICU data from Beth Israel Deaconess Medical Center",
        size=73181,  # Actual MIMIC-IV patient count
        collection_period="2008-2019",
        population_characteristics="ICU patients, de-identified per HIPAA, freely available for research"
    )

    dataset = mimic_adapter.get_dataset_info()
    print(f"✓ Dataset: {dataset.name}")
    print(f"  Size: {dataset.size} patients")
    print(f"  Public: Yes (PhysioNet)")


def create_model_card_mixed_sources():
    """Create model card using multiple data sources"""
    print("\n" + "=" * 60)
    print("Example 6: Model Card with Multiple Data Sources")
    print("=" * 60)

    card = ModelCard()

    # Model details
    card.set_model_details(ModelDetails(
        model_name="Multi-Source-Training-Model",
        version="1.5.0",
        developer_organization="Research Institution",
        release_date="2025-01-20",
        description="Model trained on multiple data sources for robustness",
        clinical_function="other",
        algorithms_used="Ensemble of models trained on different sources",
        licensing="Apache 2.0",
        support_contact="research@institution.edu"
    ))

    card.set_intended_use(IntendedUse(
        primary_intended_users="Researchers, data scientists",
        clinical_indications="Multi-source validation",
        patient_target_group="Various",
        intended_use_environment="research"
    ))

    # Use multiple data sources
    medsynth = create_synthetic_adapter(
        "MedSynth", "1.0.0", 500,
        "Privacy-preserving synthesis", "MS-STS"
    )

    synthea = create_synthetic_adapter(
        "Synthea", "3.2.0", 1000,
        "Agent-based simulation"
    )

    real_data = create_custom_adapter(
        "Clinical Database",
        "Real EHR data",
        10000,
        "2020-2024",
        "Mixed population"
    )

    # Combine all sources
    all_datasets = [
        real_data.get_dataset_info(),
        medsynth.get_dataset_info(),
        synthea.get_dataset_info()
    ]

    card.set_data_factors(DataFactors(
        source_datasets=all_datasets,
        data_distribution_summary="Mixed training approach: Real EHR (10k), MedSynth synthetic (500), Synthea synthetic (1k)",
        data_representativeness="Multiple sources improve generalizability. Synthetic data used for augmentation and testing only.",
        data_governance="Real data: IRB approved, de-identified. Synthetic data: Privacy-preserving or inherently synthetic."
    ))

    # Minimal other sections for demonstration
    card.set_features_outputs(FeaturesOutputs(
        input_features=[InputFeature("demo", "numeric", True, "Demo")],
        output_features=[OutputFeature("demo", "classification")],
        feature_type_distribution="Demo",
        uncertainty_quantification="Demo",
        output_interpretability="Demo"
    ))

    card.set_performance_validation(PerformanceValidation(
        validation_datasets=[ValidationDataset("Demo", "Demo", "Demo", "Demo")],
        claimed_metrics=[PerformanceMetric("AUC", 0.85, "Claimed")],
        validated_metrics=[PerformanceMetric("AUC", 0.83, "Validated")]
    ))

    card.set_methodology(Methodology(
        model_development_workflow="Multi-source data integration",
        training_procedure="Ensemble training across sources",
        data_preprocessing="Source-specific normalization",
        synthetic_data_usage=f"MedSynth ({medsynth.num_subjects} subjects) and Synthea ({synthea.num_subjects} subjects) used for testing and augmentation"
    ))

    card.set_additional_info(AdditionalInfo(
        benefit_risk_summary="Multi-source training improves robustness",
        ethical_considerations="Appropriate use of synthetic data documented",
        caveats_limitations="Synthetic data characteristics differ from real data",
        recommendations_for_safe_use="Validate on target population"
    ))

    # Export
    html_path = HTMLExporter.export(card, "./output/mixed_sources_model_card.html")
    print(f"\n✓ Model card created: {html_path}")
    print(f"  Training sources: {len(all_datasets)}")
    print(f"  Total subjects: {sum(d.size for d in all_datasets)}")


def main():
    """Run all flexibility examples"""
    print("=" * 60)
    print("Flexible Data Source Integration Examples")
    print("=" * 60)

    # Show different synthetic packages
    example_medsynth_integration()
    example_synthea_integration()
    example_custom_synthetic_package()

    # Show proprietary and public datasets
    example_proprietary_database()
    example_publicly_available_dataset()

    # Show combined approach
    create_model_card_mixed_sources()

    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("=" * 60)
    print("✓ Support for ANY synthetic data package (MedSynth, Synthea, custom)")
    print("✓ Support for proprietary clinical databases")
    print("✓ Support for publicly available datasets (MIMIC, eICU)")
    print("✓ Support for mixed/multi-source training")
    print("✓ Flexible adapters maintain standardized documentation")
    print("✓ smart-omop integration for OMOP CDM standardization")


if __name__ == "__main__":
    main()
