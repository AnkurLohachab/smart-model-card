# Contributing to smart-model-card

Thank you for your interest in contributing to smart-model-card. This guide will help you get started.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/ankurlohachab/smart-model-card.git
cd smart-model-card
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Verify setup:
```bash
python -m pytest tests/ -v
```

## Project Structure

```
src/smart_model_card/
    __init__.py          # Public API exports
    model_card.py        # Core ModelCard class
    sections.py          # 7 section dataclasses and sub-types
    schema.py            # JSON Schema (Draft 07)
    templates.py         # Domain templates, regulatory presets, quick_card()
    interactive.py       # Interactive creation wizard (3 modes)
    exporters.py         # JSON, Markdown, HTML export
    cli.py               # Command-line interface
    integrations.py      # OMOP CDM integration
    data_sources.py      # Data source adapters
    provenance.py        # Hashing, diffing, fairness checks
    cac.py               # Computer-assisted coding (GMDN/ICD)
    visualizations.py    # Chart generation for HTML exports
    section_formatters.py # HTML section formatting
    html_template.py     # Base HTML template
    omop_reports.py      # OMOP report parsing
    athena_api.py        # Athena vocabulary API client
tests/
    test_model_card.py   # Core ModelCard tests
    test_cac.py          # Computer-assisted coding tests
    test_provenance.py   # Provenance and hashing tests
    test_from_dict.py    # Round-trip deserialization tests
    test_templates.py    # Template, quick_card, regulatory preset tests
```

## Code Standards

### Style
- Follow PEP 8 conventions
- Line length: 100 characters (configured in pyproject.toml)
- Use type hints on all public function signatures
- Format with `black`: `black src/ tests/`
- Lint with `flake8`: `flake8 src/ tests/`

### Docstrings
- All public classes and functions must have docstrings
- Use triple-quoted strings for docstrings
- Keep docstrings concise and factual

### Naming
- Section dataclasses use PascalCase: `ModelDetails`, `IntendedUse`
- Sub-type dataclasses use PascalCase: `SourceDataset`, `InputFeature`
- Serialized keys use human-readable format: `"Model Name"`, `"Clinical Function"`
- Factory functions use snake_case: `quick_card()`, `performance_from_dict()`

## Testing

### Running Tests

Run the full test suite:
```bash
python -m pytest tests/ -v
```

Run a specific test file:
```bash
python -m pytest tests/test_templates.py -v
```

Run with coverage:
```bash
python -m pytest tests/ --cov=smart_model_card --cov-report=term-missing
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_<module>.py`
- Name test functions `test_<behavior_being_tested>`
- Test both valid and invalid inputs
- Include round-trip serialization tests for any new dataclass fields
- Verify that `ModelCard.validate()` catches invalid input

### Test Coverage Requirements

- Maintain minimum 80% code coverage
- All new public API functions must have corresponding tests
- All new dataclass fields must be tested in round-trip serialization

## Making Changes

### Adding a New Field to a Section

1. Add the field to the dataclass in `sections.py` with a default value
2. Add the key mapping in `to_dict()` (use human-readable key names)
3. Add the reverse mapping in `from_dict()`
4. Update `get_model_card_json_schema()` in `schema.py`
5. Update the interactive wizard in `interactive.py` if the field should be user-facing
6. Add tests for round-trip serialization in `test_from_dict.py`

### Adding a New Template

1. Add the template definition in `templates.py` under the `TEMPLATES` dict
2. Include all 7 section defaults with realistic placeholder content
3. Add the template ID to the `_required_overrides` list for fields that must be customized
4. Add tests in `test_templates.py` verifying the template produces a valid card

### Adding a New Export Format

1. Create an exporter class in `exporters.py` following the pattern of `HTMLExporter` or `MarkdownExporter`
2. Add the format option to `cmd_export()` in `cli.py`
3. Export the class from `__init__.py`
4. Add tests covering the export output

## Pull Request Process

1. Fork the repository
2. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes following the code standards above
4. Add or update tests as needed
5. Run the full test suite and confirm all tests pass:
   ```bash
   python -m pytest tests/ -v
   ```
6. Submit a pull request against `main`

### PR Requirements

- All tests must pass
- New code must have test coverage
- Commit messages should be descriptive
- One logical change per pull request

## Reporting Issues

When reporting issues, include:

- Python version (`python --version`)
- Library version (`python -c "import smart_model_card; print(smart_model_card.__version__)"`)
- Operating system
- Minimal code to reproduce the issue
- Expected behavior vs actual behavior
- Full error traceback if applicable

## Code of Conduct

- Be respectful and constructive in all interactions
- Focus on technical merit and code quality
- Help maintain a welcoming environment for all contributors
