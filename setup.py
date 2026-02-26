from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="smart-model-card",
    version="3.0.0",
    author="Ankur Lohachab",
    author_email="ankur.lohachab@maastrichtuniversity.nl",
    description="Structured, standardized model cards for medical AI systems with OMOP CDM integration and multi-format export",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ankurlohachab/smart-model-card",
    project_urls={
        "Bug Tracker": "https://github.com/ankurlohachab/smart-model-card/issues",
        "Documentation": "https://github.com/ankurlohachab/smart-model-card#readme",
        "Source Code": "https://github.com/ankurlohachab/smart-model-card",
        "Changelog": "https://github.com/ankurlohachab/smart-model-card/releases",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "omop": [
            "smart-omop>=0.1.0",
            "matplotlib>=3.3.0",
        ],
        "viz": [
            "matplotlib>=3.3.0",
        ],
        "validation": [
            "jsonschema>=3.2.0",
        ],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=3.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.900",
            "jsonschema>=3.2.0",
        ],
        "all": [
            "smart-omop>=0.1.0",
            "matplotlib>=3.3.0",
            "jsonschema>=3.2.0",
            "pytest>=6.0",
            "pytest-cov>=3.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.900",
        ],
    },
    entry_points={
        "console_scripts": [
            "smart-model-card=smart_model_card.cli:main",
        ],
    },
)
