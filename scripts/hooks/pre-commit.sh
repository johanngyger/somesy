#!/bin/bash
set -e

echo "Running pre-commit checks..."

# Format code
echo "Running Ruff formatter..."
ruff format .
if [ $? -ne 0 ]; then
    echo "Ruff formatting failed. Please fix the issues before committing."
    exit 1
fi

# Run linting
echo "Running Ruff linter..."
ruff check .
if [ $? -ne 0 ]; then
    echo "Linting failed. Please fix the issues before committing."
    exit 1
fi

# Run type checking
echo "Running mypy type checker..."
mypy --ignore-missing-imports .
if [ $? -ne 0 ]; then
    echo "Type checking failed. Please fix the issues before committing."
    exit 1
fi

# Add any modified files from formatting
git add -u

echo "All checks passed!"
exit 0
