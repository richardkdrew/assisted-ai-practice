.PHONY: install test run lint format coverage clean help dev dev-full dev-backend dev-ui-only dev-stop

help:  ## Show this help message
	@echo 'Configuration Service - Development Commands'
	@echo ''
	@echo 'Quick Start:'
	@echo '  make dev           Start complete stack (DB + API + Observability + UI)'
	@echo '  make dev-stop      Stop all services'
	@echo ''
	@echo 'All Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install dependencies
	cd svc && uv sync --dev

test:  ## Run tests with coverage
	cd svc && uv run python -m pytest

test-verbose:  ## Run tests with verbose output
	cd svc && uv run python -m pytest -v

test-integration:  ## Run integration tests only
	cd svc && uv run python -m pytest integration_test.py -v

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

# Backend targets
backend-up:  ## Start full backend stack
	cd svc && docker-compose up -d

backend-down:  ## Stop backend stack
	cd svc && docker-compose down

backend-logs:  ## Show backend stack logs
	cd svc && docker-compose logs -f

# Observability targets
install-observability:  ## Install observability dependencies
	cd svc && uv sync --extra observability

test-observability:  ## Run observability integration tests
	cd svc && uv run python -m pytest observability/observability_integration_test.py -v

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

observability-up:  ## Start observability stack (Prometheus, Grafana, cAdvisor)
	cd svc && docker-compose up -d otel-collector prometheus grafana cadvisor

observability-down:  ## Stop observability stack
	cd svc && docker-compose stop otel-collector prometheus grafana cadvisor

observability-status:  ## Check status of observability stack
	@echo "Checking observability stack status..."
	@cd svc && docker-compose ps
	@echo ""
	@echo "Service endpoints:"
	@echo "  Configuration Service: http://localhost:8000"
	@echo "  Prometheus:           http://localhost:9090"
	@echo "  Grafana:              http://localhost:3001"
	@echo "  cAdvisor:             http://localhost:8080"

# UI targets
ui-install:  ## Install UI dependencies
	cd ui && npm install

ui-dev:  ## Start UI development server
	cd ui && npm run dev

ui-build:  ## Build UI for production
	cd ui && npm run build

ui-test:  ## Run UI unit tests
	cd ui && npm run test

ui-test-e2e:  ## Run UI end-to-end tests
	cd ui && npm run test:e2e

ui-clean:  ## Clean UI build artifacts
	cd ui && rm -rf dist/ node_modules/.vite/

ui-lint:  ## Lint UI code
	cd ui && npm run lint

ui-format:  ## Format UI code
	cd ui && npm run format

# Development workflow targets
dev:  ## Start complete development stack (database + backend + observability + UI)
	@echo "=== Starting Complete Development Stack ==="
	@echo "1. Starting backend stack (DB + API + Observability)..."
	make backend-up
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Running migrations..."
	make migrate
	@echo ""
	@echo "2. Backend stack ready!"
	@echo "   - API:        http://localhost:8000"
	@echo "   - API Docs:   http://localhost:8000/docs"
	@echo "   - Prometheus: http://localhost:9090"
	@echo "   - Grafana:    http://localhost:3001 (admin/admin)"
	@echo ""
	@echo "3. Starting UI development server..."
	@echo "   - UI:         http://localhost:5173"
	@echo ""
	cd ui && npm run dev

dev-full:  ## Alias for 'dev' (complete development stack)
	make dev

dev-backend:  ## Start backend stack only (database + API + observability)
	@echo "Starting backend stack..."
	make backend-up
	@echo "Waiting for services..."
	@sleep 10
	make migrate
	@echo ""
	@echo "Backend stack ready!"
	@echo "  API:        http://localhost:8000"
	@echo "  Prometheus: http://localhost:9090"
	@echo "  Grafana:    http://localhost:3001"

dev-ui-only:  ## Start UI only (assumes backend running)
	@echo "Starting UI development server..."
	cd ui && npm run dev

dev-stop:  ## Stop all development services
	@echo "Stopping all services..."
	@pkill -f "vite" || true
	make backend-down
	@echo "All services stopped."

# Quality validation targets
quality:  ## Run complete quality validation (Stage 2 requirement)
	@echo "=== Running Complete Quality Validation ==="
	@echo "1. Backend linting..."
	make lint
	@echo "2. Backend formatting..."
	make format
	@echo "3. Backend tests..."
	make test
	@echo "4. UI linting..."
	make ui-lint
	@echo "5. UI formatting..."
	make ui-format
	@echo "6. UI unit tests..."
	make ui-test
	@echo "7. UI E2E tests (full stack)..."
	make ui-test-e2e
	@echo "=== Quality Validation Complete! ==="

quality-backend:  ## Run backend quality validation only
	@echo "Running backend quality checks..."
	make lint
	make format
	make test

quality-ui:  ## Run UI quality validation only
	@echo "Running UI quality checks..."
	make ui-lint
	make ui-format
	make ui-test

# Stack management
stack-up:  ## Start complete stack (database + backend + UI)
	make dev-full

stack-down:  ## Stop complete stack
	make dev-stop