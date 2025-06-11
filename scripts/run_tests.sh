#!/bin/bash

# Test runner script
set -e

echo "🧪 Running AI Agent tests..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run linting
echo "🔍 Running linting..."
flake8 src/ tests/

# Run type checking
echo "🔎 Running type checking..."
mypy src/

# Run tests with coverage
echo "🏃 Running tests with coverage..."
pytest tests/ --cov=src/ai_agent --cov-report=html --cov-report=term

echo "✅ All tests passed!"

# Open coverage report if available
if command -v open &> /dev/null && [ -f "htmlcov/index.html" ]; then
    echo "📊 Opening coverage report..."
    open htmlcov/index.html
fi