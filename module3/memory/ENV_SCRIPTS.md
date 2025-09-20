# Environment Setup & Scripts

## Overview

This document provides comprehensive instructions for setting up the Configuration Service development environment, including all scripts, commands, and procedures needed to run, test, and deploy the service.

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

## Database Setup

### 1. Start PostgreSQL Database
```bash
# Start database with Docker Compose
make db-up

# Wait for database to be ready (usually 5-10 seconds)
# You can check with:
make db-status
```

### 2. Run Database Migrations
```bash
# Apply database schema migrations
make migrate

# Expected output:
# INFO:__main__:Found 1 pending migrations
# INFO:__main__:Executing migration: 001_initial_schema.sql
# INFO:__main__:Migration 001_initial_schema.sql executed successfully
# INFO:__main__:All migrations executed successfully
```

### 3. Database Management Commands
```bash
# Start database
make db-up

# Stop database
make db-down

# Reset database (clean slate)
make db-reset

# Connect to database shell
make db-shell

# Check database status
make db-status
```

## Development Workflow

### 1. Daily Development Commands
```bash
# Start the development server
make run

# In another terminal, run tests
make test

# Run tests with coverage
make coverage

# Run integration tests only
make test-integration
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

### Core Development Commands
```bash
# Installation and setup
make install          # Install dependencies with uv

# Database management
make db-up           # Start PostgreSQL with Docker Compose
make db-down         # Stop PostgreSQL
make db-reset        # Reset database with fresh data
make migrate         # Run database migrations
make db-shell        # Connect to database shell

# Application lifecycle
make run             # Start FastAPI development server
make test            # Run all tests with coverage
make test-integration # Run integration tests only
make coverage        # Generate coverage report

# Code quality (if implemented)
make format          # Format code
make lint            # Run linting
make typecheck       # Run type checking

# Cleanup
make clean           # Remove temporary files and directories
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

### Docker Compose Setup
**File**: `svc/docker-compose.yml`
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16
    container_name: configservice-db
    environment:
      POSTGRES_DB: configservice
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d configservice"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### Container Management
```bash
# Start database container
docker-compose -f svc/docker-compose.yml up -d

# View container logs
docker-compose -f svc/docker-compose.yml logs -f postgres

# Stop and remove containers
docker-compose -f svc/docker-compose.yml down

# Stop and remove containers with volumes (complete reset)
docker-compose -f svc/docker-compose.yml down -v
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