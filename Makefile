.PHONY: help install install-dev test lint format clean coverage docs build run

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

lint: ## Run linting
	flake8 src/ tests/
	mypy src/ --ignore-missing-imports

format: ## Format code
	black src/ tests/
	isort src/ tests/ --profile black

clean: ## Clean cache and temporary files
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

coverage: ## Generate coverage report
	pytest tests/ --cov=src --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

docs: ## Build documentation
	cd docs && make html

build: ## Build package
	python -m build

run-user: ## Run user application
	streamlit run src/apps/app_user.py

run-admin: ## Run admin application
	streamlit run src/apps/app_admin.py

run: ## Run main application
	streamlit run src/apps/app.py

security: ## Run security checks
	bandit -r src/
	safety check

pre-commit: ## Run pre-commit hooks
	pre-commit run --all-files

setup-dev: install-dev ## Setup development environment
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make run' to start the application"
