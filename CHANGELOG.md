# Changelog

Each module is merged with a pull request and tagged.

## [v0.1.0] — Module 1: Repo skeleton and data discovery — 2026-11-04

### Added
- Repository layout for the full platform (`src/`, `tests/`, `infra/`, `adf/`, `notebooks/`, `powerbi/`, `docs/`).
- Tooling: `pyproject.toml`, ruff, pre-commit hooks (including private-key detection), Makefile, GitHub Actions CI running lint and tests.
- `dubai_property.profiling` package and `dld-profile` CLI: reads raw CSVs as strings (UTF-8, BOM-safe), profiles nulls, distinct counts, numeric/date castability, Arabic text and duplicate business keys, and writes a Markdown report.
- Synthetic fixture with one planted example of each data problem, and 21 unit tests.
- `notebooks/01_data_profiling.ipynb` — thin notebook over the package.
- Docs: data sources, data dictionary (expected schema, to confirm), business questions, ADR 0001.

### Fixed
- Date parsing with `dayfirst=True` misread ISO dates (2024-03-01 → 3 January). ISO and day-first strings are now parsed separately; regression test added.
