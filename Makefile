.PHONY: install dev test lint format typecheck clean build publish

# Install the package
install:
	pip install -e .

# Install with development dependencies
dev:
	pip install -e ".[dev]"

# Run tests
test:
	pytest

# Run tests with coverage
test-cov:
	pytest --cov=src/ethos --cov-report=html --cov-report=term-missing

# Lint code
lint:
	ruff check src tests

# Format code
format:
	black src tests
	ruff check --fix src tests

# Type check
typecheck:
	mypy src/ethos

# Run all checks
check: lint typecheck test

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +

# Build package
build: clean
	python -m build

# Publish to PyPI (requires authentication)
publish: build
	python -m twine upload dist/*

# Publish to TestPyPI
publish-test: build
	python -m twine upload --repository testpypi dist/*
