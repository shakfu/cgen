# Makefile for CGen development

.PHONY: help install test test-unit test-integration test-py2c test-benchmark clean lint format type-check build docs

# Default target
help:
	@echo "CGen Development Commands"
	@echo "========================="
	@echo ""
	@echo "Setup:"
	@echo "  install       Install development dependencies"
	@echo "  install-dev   Install with all development extras"
	@echo ""
	@echo "Testing:"
	@echo "  test          Run all tests (unittest + pytest)"
	@echo "  test-unit     Run unit tests only"
	@echo "  test-integration  Run integration tests only"
	@echo "  test-py2c     Run Python-to-C conversion tests"
	@echo "  test-benchmark    Run performance benchmarks"
	@echo "  test-legacy   Run original unittest tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint          Run flake8 linting"
	@echo "  format        Format code with black and isort"
	@echo "  type-check    Run mypy type checking"
	@echo "  pre-commit    Install and run pre-commit hooks"
	@echo ""
	@echo "Build:"
	@echo "  build         Build package for distribution"
	@echo "  clean         Clean build artifacts"
	@echo ""
	@echo "Documentation:"
	@echo "  docs          Build documentation"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e .[dev,intelligence,ml,verification,docs,all]

# Testing
test: test-legacy test-pytest

test-legacy:
	python -m unittest discover -v tests

test-pytest:
	pytest tests/ -v

test-unit:
	pytest -m "unit" tests/ -v

test-integration:
	pytest -m "integration" tests/ -v

test-py2c:
	pytest -m "py2c" tests/ -v

test-benchmark:
	pytest -m "benchmark" tests/ -v
	python tests/benchmarks.py

test-coverage:
	pytest --cov=src/cgen --cov-report=html --cov-report=term-missing tests/

# Code quality
lint:
	flake8 --max-line-length=120 --ignore=D107,D200,D205,D400,D401 src
	flake8 --max-line-length=120 --ignore=D101,D102,D107,D200,D205,D400,D401,E402 tests

format:
	black --line-length=120 src tests
	isort --profile=black --line-length=120 src tests

type-check:
	mypy src/cgen

pre-commit:
	pre-commit install
	pre-commit run --all-files

# Build and distribution
build: clean
	python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Documentation
docs:
	@echo "Documentation build not yet implemented"
	@echo "Planned: Sphinx documentation in doc/ directory"

# Development utilities
run-examples:
	@echo "Running example scripts..."
	python examples/hello_world.py
	python examples/variables.py

# CI simulation
ci-test: install-dev lint type-check test

# Performance monitoring
perf-monitor:
	python scripts/run_tests.py --category benchmark --verbose

# Package verification
verify-package: build
	python -m twine check dist/*
	pip install dist/*.whl
	python -c "import cgen; print(f'CGen version: {cgen.__version__}')"

# Development server (for future web interface)
dev-server:
	@echo "Development server not yet implemented"
	@echo "Planned: Web interface for code generation and testing"