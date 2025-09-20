.PHONY: install test run lint format coverage clean help

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install dependencies
	uv sync --dev

test:  ## Run tests with coverage
	uv run python -m pytest

test-verbose:  ## Run tests with verbose output
	uv run python -m pytest -v

coverage:  ## Generate coverage report
	uv run python -m pytest --cov-report=html
	@echo "Coverage report generated in htmlcov/"

run:  ## Run the development server
	uv run python -m uvicorn svc.main:app --reload --host 0.0.0.0 --port 8000

format:  ## Format code with black
	uv run python -m black svc/

lint:  ## Run linting
	uv run python -m flake8 svc/

clean:  ## Clean temporary files
	rm -rf __pycache__/ .pytest_cache/ htmlcov/ .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

db-up:  ## Start PostgreSQL database with Docker
	docker run --name configservice-db -e POSTGRES_DB=configservice -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:16

db-down:  ## Stop and remove PostgreSQL database
	docker stop configservice-db || true
	docker rm configservice-db || true

db-reset:  ## Reset database (stop, remove, start fresh)
	$(MAKE) db-down
	$(MAKE) db-up
	@echo "Waiting for database to be ready..."
	@sleep 5

migrate:  ## Run database migrations
	uv run python -m svc.migrations