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

# Observability targets
install-observability:  ## Install observability dependencies
	cd svc && uv sync --extra observability

observability-up:  ## Start full observability stack
	cd svc && docker-compose up -d

observability-down:  ## Stop observability stack
	cd svc && docker-compose down

observability-logs:  ## Show observability stack logs
	cd svc && docker-compose logs -f

test-observability:  ## Run observability integration tests
	cd svc && uv run python -m pytest test_observability_integration.py -v

load-test:  ## Run load testing for observability validation
	cd svc && uv run python load_testing.py --report load_test_report.md

prometheus:  ## Open Prometheus in browser
	@echo "Opening Prometheus at http://localhost:9090"
	@open http://localhost:9090 || echo "Please open http://localhost:9090 manually"

grafana:  ## Open Grafana in browser
	@echo "Opening Grafana at http://localhost:3001 (admin/admin)"
	@open http://localhost:3001 || echo "Please open http://localhost:3001 manually"

metrics:  ## Show current service metrics
	@curl -s http://localhost:8000/metrics | head -20

observability-status:  ## Check status of observability stack
	@echo "Checking observability stack status..."
	@cd svc && docker-compose ps
	@echo ""
	@echo "Service endpoints:"
	@echo "  Configuration Service: http://localhost:8000"
	@echo "  Prometheus:           http://localhost:9090"
	@echo "  Grafana:              http://localhost:3001"
	@echo "  cAdvisor:             http://localhost:8080"