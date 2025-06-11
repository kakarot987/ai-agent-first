.PHONY: setup setup-dev test test-cov lint format clean run docker-build docker-run

# Setup
setup:
	python -m pip install --upgrade pip
	pip install -e .

setup-dev:
	python -m pip install --upgrade pip
	pip install -e .[dev]
	pre-commit install

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src/ai_agent --cov-report=html --cov-report=term

# Code Quality
lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

# Running
run:
	python -m ai_agent.cli.main

# Docker
docker-build:
	docker-compose build

docker-run:
	docker-compose up ai-agent

docker-dev:
	docker-compose up ai-agent-dev

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/

# Help
help:
	@echo "Available commands:"
	@echo "  setup      - Install package"
	@echo "  setup-dev  - Install with dev dependencies"
	@echo "  test       - Run tests"
	@echo "  test-cov   - Run tests with coverage"
	@echo "  lint       - Run linting"
	@echo "  format     - Format code"
	@echo "  run        - Run the agent"
	@echo "  clean      - Clean build artifacts"