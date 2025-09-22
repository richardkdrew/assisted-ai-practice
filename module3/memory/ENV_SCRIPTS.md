# Environment Setup & Scripts

## Overview

This document provides comprehensive instructions for setting up the Configuration Service development environment, including all scripts, commands, and procedures needed to run, test, and deploy the service.

### ⚡ Quick Start (Recommended Workflow)
```bash
# 1. Start complete backend stack (database + API + observability)
make backend-up

# 2. Open monitoring dashboards
make grafana  # Auto-loaded dashboards at http://localhost:3001

# 3. Run tests
make test

# 4. Stop when done
make backend-down
```

**Default Backend Interface**: Use `make backend-up` and `make backend-down` as the primary way to interact with the backend stack. This provides a complete development environment with observability out of the box.

## Prerequisites

### System Requirements
- **Python**: 3.13.5 or higher
- **Docker**: For PostgreSQL database
- **uv**: Fast Python package manager

### Installing uv Package Manager
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

## Environment Setup

### 1. Project Structure
```bash
module3/
├── svc/                    # Service code directory
│   ├── .env.example       # Environment template
│   ├── docker-compose.yml # Database services
│   ├── pyproject.toml     # Python dependencies
│   └── [application files]
├── Makefile               # Development commands
└── memory/                # Context files
```

### 2. Initial Setup Commands
```bash
# Navigate to project directory
cd /path/to/module3

# Install Python dependencies
make install

# Copy environment template
cp svc/.env.example svc/.env

# Edit environment variables as needed
# Default values work for local development
```

### 3. Environment Configuration (.env)
**File**: `svc/.env`
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/configservice
DB_HOST=localhost
DB_PORT=5432
DB_NAME=configservice
DB_USER=user
DB_PASSWORD=password

# Application Configuration
LOG_LEVEL=INFO
API_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8000

# Connection Pool Settings (optional)
DB_POOL_MIN_CONN=1
DB_POOL_MAX_CONN=20
```

## Backend Stack Management (Primary Interface)

### 1. Full Backend Stack (Database + API + Observability)
```bash
# Start complete backend stack (RECOMMENDED)
make backend-up

# Stop complete backend stack
make backend-down

# View all backend logs
make backend-logs
```

### 2. Database-Only Operations
```bash
# Start database only
make db-up

# Stop database
make db-down

# Reset database (clean slate)
make db-reset

# Connect to database shell
make db-shell
```

### 3. Run Database Migrations
```bash
# Apply database schema migrations
make migrate

# Expected output:
# INFO:__main__:Found 1 pending migrations
# INFO:__main__:Executing migration: 001_initial_schema.sql
# INFO:__main__:Migration 001_initial_schema.sql executed successfully
# INFO:__main__:All migrations executed successfully
```

## Observability & Monitoring

### 1. Observability Stack Commands
```bash
# Open Grafana dashboards (auto-loaded)
make grafana  # Opens http://localhost:3001 (admin/admin)

# Open Prometheus metrics
make prometheus  # Opens http://localhost:9090

# View current service metrics
make metrics

# Check observability stack status
docker ps  # View all running containers
```

### 2. Available Monitoring Dashboards
- **Configuration Service - Application Metrics**: Application-level metrics
- **Configuration Service - Container Metrics**: Container and infrastructure metrics

### 3. Observability Stack Components
- **Grafana** (port 3001): Dashboards and visualization
- **Prometheus** (port 9090): Metrics collection and storage
- **OpenTelemetry Collector** (ports 4317/4318/8889): Telemetry pipeline
- **cAdvisor** (port 8080): Container metrics

## Development Workflow

### 1. Quick Start (Recommended)
```bash
# Start complete backend stack
make backend-up

# Open Grafana to view metrics
make grafana

# Run development server locally (optional, for local development)
make run  # Only needed if developing outside Docker
```

### 2. Daily Development Commands
```bash
# Run tests
make test

# Run tests with coverage
make coverage

# Run integration tests only
make test-integration

# Run observability integration tests
make test-observability
```

### 2. Code Quality Commands
```bash
# Format code (if formatter available)
make format

# Run linting (if linter available)
make lint

# Type checking (if available)
make typecheck
```

## Makefile Commands Reference

### Backend Stack Management (Primary Commands)
```bash
# Full stack operations (RECOMMENDED)
make backend-up      # Start complete backend stack (DB + API + Observability)
make backend-down    # Stop complete backend stack
make backend-logs    # View backend stack logs

# Database operations
make db-up           # Start PostgreSQL only
make db-down         # Stop PostgreSQL
make db-reset        # Reset database with fresh data
make migrate         # Run database migrations
make db-shell        # Connect to database shell
```

### Development & Testing Commands
```bash
# Installation and setup
make install         # Install dependencies with uv

# Application development
make run             # Start FastAPI development server (local)
make test            # Run all tests with coverage
make test-integration # Run integration tests only
make test-observability # Run observability integration tests
make coverage        # Generate coverage report

# Code quality
make format          # Format code with black
make lint            # Run linting with flake8

# Cleanup
make clean           # Remove temporary files and directories
```

### Observability Commands
```bash
# Monitoring access
make grafana         # Open Grafana dashboards (admin/admin)
make prometheus      # Open Prometheus metrics
make metrics         # Show current service metrics

# Load testing and observability validation
make load-test       # Run load testing for observability validation
```

### UI Development Commands
```bash
# UI operations
make ui-install      # Install UI dependencies
make ui-dev          # Start UI development server
make ui-build        # Build UI for production
make ui-test         # Run UI unit tests
make ui-test-e2e     # Run UI end-to-end tests
make ui-lint         # Lint UI code
make ui-format       # Format UI code
make ui-clean        # Clean UI build artifacts
```

### Quality Validation (Stage 2 Requirements)
```bash
# Complete quality validation suite
make quality         # Run complete quality validation (backend + UI)
make quality-backend # Run backend quality validation only
make quality-ui      # Run UI quality validation only
```

### Makefile Implementation
**File**: `Makefile`
```makefile
.PHONY: help install db-up db-down db-reset migrate db-shell run test test-integration coverage clean

help:
	@echo "Available commands:"
	@echo "  install         Install dependencies"
	@echo "  db-up          Start PostgreSQL database"
	@echo "  db-down        Stop PostgreSQL database"
	@echo "  db-reset       Reset database"
	@echo "  migrate        Run database migrations"
	@echo "  db-shell       Connect to database"
	@echo "  run            Start development server"
	@echo "  test           Run tests with coverage"
	@echo "  test-integration Run integration tests"
	@echo "  coverage       Generate coverage report"
	@echo "  clean          Clean temporary files"

install:
	cd svc && uv sync

db-up:
	cd svc && docker-compose up -d

db-down:
	cd svc && docker-compose down

db-reset:
	cd svc && docker-compose down -v
	cd svc && docker-compose up -d
	sleep 10
	$(MAKE) migrate

migrate:
	cd svc && uv run python -m migrations

db-shell:
	cd svc && docker-compose exec postgres psql -U user -d configservice

run:
	cd svc && uv run python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
	cd svc && uv run pytest --cov=. --cov-report=term-missing

test-integration:
	cd svc && uv run pytest test_integration.py -v

coverage:
	cd svc && uv run pytest --cov=. --cov-report=html
	@echo "Coverage report generated in svc/htmlcov/index.html"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	cd svc && rm -rf htmlcov .coverage
```

## Testing & Validation

### 1. Running Tests
```bash
# Full test suite with coverage
make test

# Integration tests only
make test-integration

# Generate HTML coverage report
make coverage
```

### 2. Manual API Testing
```bash
# Health check
curl http://localhost:8000/health

# Create application
curl -X POST http://localhost:8000/api/v1/applications/ \
  -H "Content-Type: application/json" \
  -d '{"name":"test-app","comments":"Test application"}'

# List applications
curl http://localhost:8000/api/v1/applications/

# Create configuration
curl -X POST http://localhost:8000/api/v1/configurations/ \
  -H "Content-Type: application/json" \
  -d '{"application_id":"<app-id>","name":"test-config","comments":"Test config","config":{"key":"value"}}'
```

### 3. API Documentation
```bash
# Start the service
make run

# Access interactive API documentation
open http://localhost:8000/docs

# Access OpenAPI specification
curl http://localhost:8000/openapi.json
```

## Docker Configuration

### Complete Stack Architecture
**File**: `svc/docker-compose.yml`

The docker-compose configuration includes:

#### Core Services
- **PostgreSQL 16**: Database with health checks
- **Configuration Service**: FastAPI application (containerized)
- **OpenTelemetry Collector**: Telemetry data pipeline

#### Observability Stack
- **Prometheus**: Metrics storage and querying
- **Grafana**: Dashboard visualization (with auto-loaded dashboards)
- **cAdvisor**: Container metrics collection

#### Network & Volumes
- **observability** network: Connects all services
- **postgres_data**: Persistent database storage
- **prometheus_data**: Metrics storage
- **grafana_data**: Dashboard and config storage

### Key Features
- **Auto-loaded Dashboards**: Grafana automatically provisions monitoring dashboards
- **Health Checks**: All services include proper health monitoring
- **Service Discovery**: Services communicate by container name
- **Persistent Storage**: Data survives container restarts

### Container Management
```bash
# Start complete backend stack (RECOMMENDED)
make backend-up

# View all backend logs
make backend-logs

# Stop complete backend stack
make backend-down

# Alternative: Direct docker-compose commands (if needed)
cd svc && docker-compose up -d      # Start all services
cd svc && docker-compose down       # Stop all services
cd svc && docker-compose down -v    # Stop and remove volumes (complete reset)

# View individual service logs
docker logs configservice-app       # Application logs
docker logs configservice-db        # Database logs
docker logs configservice-grafana   # Grafana logs
docker logs configservice-prometheus # Prometheus logs
```

### Service Endpoints (All Auto-configured)
```bash
# Core services
Configuration Service API: http://localhost:8000
PostgreSQL Database:       localhost:5432

# Observability stack
Grafana Dashboards:       http://localhost:3001 (admin/admin)
Prometheus Metrics:       http://localhost:9090
cAdvisor Container Stats: http://localhost:8080
OpenTelemetry Collector:  localhost:4317 (gRPC), localhost:4318 (HTTP)
```

## Migration Management

### Running Migrations
```bash
# Run pending migrations
cd svc && uv run python -m migrations

# Check migration status (manual verification)
make db-shell
configservice=# SELECT * FROM migrations;
```

### Creating New Migrations
1. Create new SQL file in `svc/migrations/` directory
2. Use sequential numbering: `002_description.sql`, `003_description.sql`, etc.
3. Include both schema changes and data modifications as needed
4. Run migrations with `make migrate`

**Example Migration**: `svc/migrations/002_add_index.sql`
```sql
-- Add performance index for configuration queries
CREATE INDEX idx_configurations_created_at ON configurations(created_at);
```

## Performance Monitoring

### Health Check Endpoint
```bash
# Basic health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","service":"configuration-service"}
```

### Database Performance
```bash
# Connect to database for performance queries
make db-shell

# Check connection status
configservice=# SELECT count(*) FROM pg_stat_activity WHERE datname = 'configservice';

# Check table sizes
configservice=# SELECT schemaname,tablename,pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables WHERE schemaname = 'public';
```

## Troubleshooting

### Common Issues & Solutions

1. **Port 8000 already in use**
   ```bash
   lsof -ti:8000 | xargs kill -9
   make run
   ```

2. **Database connection failed**
   ```bash
   make db-down
   make db-up
   sleep 10
   make migrate
   ```

3. **Import/module errors**
   ```bash
   cd svc
   uv sync  # Reinstall dependencies
   ```

4. **Migration errors**
   ```bash
   make db-reset  # Complete database reset
   ```

### Log Analysis
```bash
# View application logs (when running in background)
# Application logs appear in terminal where `make run` was executed

# View database logs
cd svc && docker-compose logs postgres

# View detailed migration logs
cd svc && uv run python -m migrations  # Verbose migration output
```

## Production Considerations

### Environment Variables for Production
```bash
# Production environment settings
LOG_LEVEL=WARNING
DB_POOL_MIN_CONN=5
DB_POOL_MAX_CONN=50
HOST=0.0.0.0
PORT=8000

# Security settings (not implemented yet)
# JWT_SECRET_KEY=<secure-random-key>
# CORS_ORIGINS=https://yourdomain.com
```

### Deployment Checklist
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Health check endpoint accessible
- [ ] Database connection pool sized appropriately
- [ ] Logging level set appropriately
- [ ] CORS origins configured for production

---

*This environment setup guide should be updated as the deployment and infrastructure requirements evolve.*