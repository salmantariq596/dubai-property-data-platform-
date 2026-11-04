.PHONY: setup lint format test profile-sample

setup:
	python -m venv .venv
	.venv/bin/pip install -e ".[dev]"
	.venv/bin/pre-commit install

lint:
	ruff check src tests
	ruff format --check src tests

format:
	ruff check --fix src tests
	ruff format src tests

test:
	pytest --cov=dubai_property --cov-report=term-missing

# Profile the bundled synthetic fixture (proves the tool works without real data)
profile-sample:
	dld-profile tests/fixtures/sample_transactions.csv \
		--key transaction_id --name "Sample transactions (synthetic)" \
		--output docs/profiles/sample_transactions.md
