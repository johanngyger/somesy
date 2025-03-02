#\!/bin/bash
set -e

echo "Running code formatting check..."
ruff format --check .

echo "Running linting checks..."
ruff check .

echo "Running type checking..."
mypy --ignore-missing-imports .

echo "Running tests with coverage..."
pytest --cov=. --cov-report=term --cov-fail-under=90

echo "All checks passed!"
