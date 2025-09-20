.PHONY: install test run lint format coverage clean help

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install dependencies
	cd svc && uv sync --dev

test:  ## Run tests with coverage
	cd svc && uv run python -m pytest

test-verbose:  ## Run tests with verbose output
	cd svc && uv run python -m pytest -v

test-integration:  ## Run integration tests only
	cd svc && uv run python -m pytest test_integration.py -v

coverage:  ## Generate coverage report
	cd svc && uv run python -m pytest --cov-report=html
	@echo "Coverage report generated in svc/htmlcov/"

run:  ## Run the development server
	cd svc && uv run python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

format:  ## Format code with black
	cd svc && uv run python -m black .

lint:  ## Run linting
	cd svc && uv run python -m flake8 .

clean:  ## Clean temporary files
	rm -rf svc/__pycache__/ svc/.pytest_cache/ svc/htmlcov/ svc/.coverage
	find svc -type d -name __pycache__ -delete
	find svc -type f -name "*.pyc" -delete

db-up:  ## Start PostgreSQL database with Docker Compose
	cd svc && docker-compose up -d postgres

db-down:  ## Stop PostgreSQL database
	cd svc && docker-compose down

db-reset:  ## Reset database (stop, remove, start fresh)
	cd svc && docker-compose down -v
	cd svc && docker-compose up -d postgres
	@echo "Waiting for database to be ready..."
	@sleep 10

migrate:  ## Run database migrations
	cd svc && uv run python -m migrations

db-shell:  ## Connect to database shell
	cd svc && docker-compose exec postgres psql -U user -d configservice