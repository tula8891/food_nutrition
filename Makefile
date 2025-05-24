# Development Commands
.PHONY: setup setup-conda run test-imports format lint type-check pre-commit test test-coverage test-async get-version release clean help

setup-conda:
	conda env create -f environment.yml
	@echo "Conda environment created. Activate it with: conda activate food-nutrition"

setup:
	@if [ -z "$$CONDA_DEFAULT_ENV" ]; then \
		echo "Please activate the conda environment first: conda activate food-nutrition"; \
		exit 1; \
	fi
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install pre-commit
	pre-commit install
	pre-commit install --hook-type commit-msg
	@if [ ! -f .streamlit/secrets.toml ]; then \
		echo "Creating .streamlit/secrets.toml template..."; \
		mkdir -p .streamlit; \
		echo "# Add your API keys and secrets here" > .streamlit/secrets.toml; \
		echo "# Example:" >> .streamlit/secrets.toml; \
		echo "# api_key = \"your-api-key-here\"" >> .streamlit/secrets.toml; \
	fi

run:
	streamlit run app.py

test-imports:
	python -c "import streamlit; import httpx; import base64; import re"

# Code Quality Commands
format:
	black . --line-length 130
	isort .

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=130 --statistics

type-check:
	mypy . --strict --ignore-missing-imports

pre-commit: format lint type-check test-imports

# Testing Commands
test:
	pytest --html=reports/test-report.html --junitxml=reports/test-report.xml

test-coverage:
	pytest --cov=. --cov-report=html:reports/coverage --cov-report=xml:reports/coverage.xml

test-async:
	pytest --asyncio-mode=auto

# Release Commands
get-version:
	@echo "Current version: $$(git describe --tags --abbrev=0 2>/dev/null || echo '0.0.0')"
	@echo "Next version: $$(git describe --tags --abbrev=0 2>/dev/null | awk -F. '{print $$1"."$$2"."$$3+1}' || echo '0.0.1')"

release:
	@if [ -z "$(VERSION)" ]; then \
		echo "Please specify a version: make release VERSION=x.y.z"; \
		exit 1; \
	fi
	git tag -a v$(VERSION) -m "Release version $(VERSION)"
	git push origin v$(VERSION)

# Maintenance Commands
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name "reports" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	find . -type f -name "*.log" -delete

help:
	@echo "Available commands:"
	@echo "  make setup    - Install dependencies and set up the development environment."
	@echo "  make run      - Run the Streamlit application locally."
	@echo "  make test     - Run tests with HTML and XML reports."
	@echo "  make format   - Format code with black and isort."
	@echo "  make lint     - Run flake8 code quality checks."
	@echo "  make type-check - Run type checking with mypy."
	@echo "  make pre-commit - Run all pre-commit checks (format, lint, test)."
	@echo "  make clean    - Clean up cache files and test reports."
