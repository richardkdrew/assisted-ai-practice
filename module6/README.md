# Configuration Service

A complete full-stack configuration management system with a modern Python backend, TypeScript Admin UI, and comprehensive observability stack. Provides dynamic, flexible configuration handling for software applications with runtime updates and professional monitoring dashboards.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Development Workflow](#development-workflow)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Admin UI](#admin-ui)
- [Observability](#observability)
- [Testing](#testing)
- [Documentation](#documentation)
- [Project Structure](#project-structure)

## Overview

The Configuration Service consists of three main components:

1. **Backend API**: FastAPI-based REST service with PostgreSQL
2. **Admin UI**: TypeScript Web Components frontend (zero external frameworks)
3. **Observability Stack**: Prometheus, Grafana, OpenTelemetry, and cAdvisor

All components are integrated via Docker Compose for a complete development environment.

## Features

### 🔧 Backend API
- **Centralized Configuration Management**: Single source of truth for application configurations
- **Dynamic Updates**: Runtime configuration changes without service interruption
- **Multi-Application Support**: Manage configurations for multiple applications
- **RESTful API**: Complete CRUD operations via REST endpoints
- **ULID Primary Keys**: Universally unique, lexicographically sortable identifiers
- **Repository Pattern**: Direct SQL queries without ORM overhead

### 🎨 Admin UI
- **TypeScript Web Components**: Zero external framework dependencies
- **Professional Design**: Responsive, modern admin interface
- **Real-time Updates**: Live data synchronization with backend
- **CRUD Operations**: Complete application and configuration management
- **Cross-browser Support**: Modern browsers with Shadow DOM

### 📊 Observability
- **Auto-loading Dashboards**: Grafana dashboards provision automatically
- **Application Metrics**: Request rates, response times, error tracking
- **Container Metrics**: Resource usage, health monitoring
- **Telemetry Pipeline**: OpenTelemetry for traces, metrics, and logs
- **Real-time Monitoring**: Live system health and performance data

### 🧪 Testing & Quality
- **87% E2E Test Coverage**: Comprehensive Playwright testing
- **Backend Test Coverage**: 80%+ with pytest
- **Integration Testing**: Full API-to-database flow validation
- **Quality Gates**: Automated validation pipeline

## Tech Stack

### 🐍 Backend Stack
- **Language**: Python 3.13.5
- **Web Framework**: FastAPI 0.116.1 (async/await, auto OpenAPI docs)
- **Database**: PostgreSQL 16 (JSONB support for flexible configurations)
- **Validation**: Pydantic 2.11.7 (request/response validation)
- **Database Adapter**: psycopg2-binary 2.9.10 (connection pooling)
- **Testing**: pytest 8.4.1, pytest-cov 6.2.1, httpx 0.28.1
- **Package Management**: uv (fast Python package management)

### 🎨 Frontend Stack
- **Language**: TypeScript 5.0+ (strict type checking, zero JavaScript)
- **Components**: Native Web Components with Shadow DOM
- **Build System**: Vite 5.0+ (fast development server and builds)
- **Testing**: Vitest 1.0+ (unit tests) + Playwright 1.40+ (E2E tests)
- **Styling**: CSS Custom Properties with responsive design

### 📊 Observability Stack
- **Metrics**: Prometheus (time-series database)
- **Visualization**: Grafana (dashboards and alerting)
- **Telemetry**: OpenTelemetry Collector (traces, metrics, logs)
- **Container Monitoring**: cAdvisor (Docker resource monitoring)
- **Service Discovery**: Docker Compose networking

### 🛠️ Development Tools
- **Containerization**: Docker Compose (complete environment)
- **Build Automation**: Make (standardized commands)
- **Code Quality**: ESLint, Prettier, Black, Flake8
- **Version Control**: Git with conventional commits

## Quick Start

### Prerequisites

- **Python**: 3.13.5+
- **Node.js**: 18+ (for frontend build tools)
- **Docker**: 20+ (for complete stack)
- **uv**: Python package manager
- **Git**: For version control

### 🚀 Complete Stack Setup (Recommended)

```bash
# 1. Clone and setup
git clone <repository-url>
cd configuration-service
make install

# 2. Start complete backend stack (API + DB + Observability)
make backend-up

# 3. Verify services are running
curl http://localhost:8000/health  # API health check
```

**🎉 You're ready!** Access these services:

- **API Documentation**: http://localhost:8000/docs
- **Grafana Dashboards**: http://localhost:3001 (admin/admin)
- **Prometheus Metrics**: http://localhost:9090
- **Container Monitoring**: http://localhost:8080

### 🎨 Admin UI Development (Optional)

```bash
# Install UI dependencies
make ui-install

# Start UI development server
make ui-dev

# Access Admin UI at http://localhost:3000
```

### 🧪 Run Tests

```bash
# Backend tests
make test

# Frontend E2E tests (requires backend + UI running)
make ui-test-e2e

# Complete quality validation
make quality
```

## Development Workflow

The project follows a **Four-Stage Development Process** for consistent, high-quality delivery:

1. **Stage 1: PLAN** - Story planning with Given-When-Then acceptance criteria
2. **Stage 2: BUILD & ASSESS** - Implementation with continuous quality validation
3. **Stage 3: REFLECT & ADAPT** - Process improvement and learning capture
4. **Stage 4: COMMIT & PICK NEXT** - Finalize work and select next task

### 📋 Essential Commands

```bash
# Complete stack management (RECOMMENDED)
make backend-up      # Start backend + observability stack
make backend-down    # Stop complete stack
make backend-logs    # View all service logs

# Individual service management
make db-up          # Start PostgreSQL only
make run            # Start API server locally
make ui-dev         # Start UI development server

# Testing and quality
make test           # Backend tests with coverage
make ui-test        # Frontend unit tests
make ui-test-e2e    # E2E tests (requires full stack)
make quality        # Complete validation suite

# Observability access
make grafana        # Open Grafana dashboards
make prometheus     # Open Prometheus metrics
make metrics        # Show current API metrics
```

**📖 For complete development workflow**: See [ENV_SCRIPTS.md](memory/ENV_SCRIPTS.md)

## Admin UI

The Admin UI is a professional TypeScript Web Components application with zero external framework dependencies.

### ✨ Key Features
- **Native Web Components**: Shadow DOM encapsulation, framework independence
- **TypeScript Only**: Strict typing, no JavaScript files
- **CRUD Operations**: Complete application and configuration management
- **Responsive Design**: Professional admin interface with CSS custom properties
- **Real-time Data**: Live synchronization with backend API

### 🚀 Getting Started with UI

```bash
# Install UI dependencies
make ui-install

# Start UI development server (port 3000)
make ui-dev

# Run UI tests
make ui-test          # Unit tests with Vitest
make ui-test-e2e      # E2E tests with Playwright (requires backend)
```

### 🧪 E2E Testing
- **87% Test Coverage**: 34/39 tests passing
- **Cross-browser**: Chrome and Firefox support
- **Full Integration**: Tests complete user workflows

**Note**: 5 E2E tests are currently failing and documented for refinement in the next iteration.

## Observability

Comprehensive monitoring and observability stack with auto-loading dashboards.

### 📊 Monitoring Components

1. **Grafana Dashboards** (http://localhost:3001)
   - Configuration Service Application Metrics
   - Container and Infrastructure Metrics
   - Auto-provisioned on startup

2. **Prometheus Metrics** (http://localhost:9090)
   - Time-series metrics collection
   - API performance monitoring
   - Custom application metrics

3. **OpenTelemetry Collector**
   - Traces, metrics, and logs pipeline
   - Service discovery and routing
   - Structured error tracing with span context

4. **cAdvisor** (http://localhost:8080)
   - Container resource monitoring
   - Docker performance metrics

### 📈 Structured Error Tracing

The observability module was recently refactored for improved structure and maintainability:

- **Clear Module Boundaries**: Proper separation of concerns in dedicated modules
- **Improved Package Structure**: Follows Python best practices for module organization
- **Optimized Performance**: Middleware and error tracking with minimal overhead
- **Enhanced Maintainability**: Proper package exports with `__all__` declarations

See [observability/README.md](svc/observability/README.md) and [REFACTORING.md](svc/REFACTORING.md) for details.

### 🔧 Access Monitoring

```bash
# Start observability stack
make backend-up

# Open dashboards
make grafana     # Grafana at localhost:3001 (admin/admin)
make prometheus  # Prometheus at localhost:9090

# View current metrics
make metrics     # CLI output of current API metrics
```

**🎯 All dashboards auto-load on startup** - no manual configuration required!

## API Documentation

Once running, visit:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### API Endpoints

**Applications** (`/api/v1/applications`):
- `POST /` - Create application
- `GET /{id}` - Get application (includes configuration IDs)
- `PUT /{id}` - Update application
- `GET /` - List applications (paginated)
- `DELETE /{id}` - Delete application

**Configurations** (`/api/v1/configurations`):
- `POST /` - Create configuration
- `GET /{id}` - Get configuration
- `PUT /{id}` - Update configuration
- `DELETE /{id}` - Delete configuration

## Data Models

### Application
```json
{
  "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
  "name": "my-web-app",
  "comments": "Main web application",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "configuration_ids": ["01ARZ3NDEKTSV4RRFFQ69G5FAV"]
}
```

### Configuration
```json
{
  "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
  "application_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
  "name": "database-config",
  "comments": "Database connection settings",
  "config": {
    "host": "localhost",
    "port": 5432,
    "ssl": true,
    "pool_size": 20
  },
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

## Configuration

Copy `svc/.env.example` to `svc/.env` and adjust settings:

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
```

## Architecture

The Configuration Service follows a **full-stack architecture** with clear separation of concerns:

### 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Admin UI      │    │   Backend API   │    │   Database      │
│                 │    │                 │    │                 │
│ TypeScript      │◄──►│ FastAPI         │◄──►│ PostgreSQL 16   │
│ Web Components  │    │ Python 3.13     │    │ JSONB Support   │
│ Shadow DOM      │    │ Repository      │    │ Connection Pool │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │ Observability   │              │
         │              │                 │              │
         └──────────────►│ Prometheus      │◄─────────────┘
                        │ Grafana         │
                        │ OpenTelemetry   │
                        │ cAdvisor        │
                        └─────────────────┘
```

### 🔧 Backend Architecture
- **No ORM**: Direct SQL queries with Repository pattern for performance
- **Connection Pooling**: ThreadedConnectionPool with RealDictCursor
- **ULID Primary Keys**: Universally unique, lexicographically sortable identifiers
- **Async/Await**: Full async support with AsyncContextManager
- **Migration System**: SQL-based migrations with automatic tracking

### 🎨 Frontend Architecture
- **Zero External Frameworks**: Native Web Components for longevity
- **Shadow DOM Encapsulation**: True CSS and JavaScript isolation
- **SOLID Principles**: Single responsibility, dependency inversion
- **Component Registry**: Centralized component management system

### 📊 Observability Architecture
- **Auto-loading Dashboards**: Grafana provisions dashboards on startup
- **Service Discovery**: Docker Compose networking for container communication
- **Telemetry Pipeline**: OpenTelemetry Collector for unified observability
- **Container Monitoring**: cAdvisor for Docker resource metrics
- **Modular Design**: Properly structured observability module with clear package boundaries
- **Structured Error Tracing**: Comprehensive exception tracking with OpenTelemetry spans
- **Performance Optimized**: Middleware with minimal overhead (<5ms per request)

**📖 For detailed architecture**: See [ARCHITECTURE.md](memory/ARCHITECTURE.md)

## Testing

Comprehensive testing strategy with backend unit tests, integration tests, and frontend E2E testing.

### 🧪 Backend Testing

```bash
# Run all backend tests with coverage
make test

# Run integration tests only
make test-integration

# Generate HTML coverage report
make coverage

# Run observability integration tests
make test-observability
```

**Backend Test Coverage**: 80%+ target achieved

**Test Types**:
- **Unit Tests**: All modules with comprehensive coverage
- **Integration Tests**: Complete API-to-database flow validation
- **Model Tests**: Pydantic validation and serialization
- **Migration Tests**: Database schema management
- **API Tests**: FastAPI endpoint and routing validation

### 🎨 Frontend Testing

```bash
# Install UI dependencies first
make ui-install

# Run frontend unit tests
make ui-test

# Run E2E tests (requires backend running)
make backend-up        # Start backend stack
make ui-dev           # Start UI server
make ui-test-e2e      # Run Playwright E2E tests
```

**Frontend Test Coverage**: 87% (34/39 E2E tests passing)

**Test Types**:
- **Unit Tests**: Vitest for component logic testing
- **E2E Tests**: Playwright for complete user workflow testing
- **Cross-browser**: Chrome and Firefox compatibility testing
- **Integration**: Full-stack testing with real backend API

### 🎯 Quality Validation

```bash
# Run complete quality validation suite
make quality

# This runs:
# - Backend tests + linting + formatting
# - Frontend tests + linting + formatting
# - E2E tests + quality gates
```

**Quality Requirements**:
- ✅ All backend tests pass
- ✅ 100% E2E test pass rate required for production
- ✅ No linting warnings
- ✅ Code coverage targets met

**📖 For testing details**: See [IMPLEMENTATION.md](memory/IMPLEMENTATION.md)

## Documentation

Comprehensive documentation covering all aspects of the Configuration Service development and architecture.

### 📚 Core Documentation

#### **[ARCHITECTURE.md](memory/ARCHITECTURE.md)**
- Complete system architecture overview
- Backend, frontend, and observability stack details
- Design decisions and technical rationale
- Component interaction diagrams

#### **[IMPLEMENTATION.md](memory/IMPLEMENTATION.md)**
- Detailed implementation specifics
- Exact dependency versions and configurations
- Technical decisions and lessons learned
- Development environment setup

#### **[ENV_SCRIPTS.md](memory/ENV_SCRIPTS.md)**
- Complete development workflow guide
- Environment setup and configuration
- Command reference and usage examples
- Commit workflow and best practices

#### **[WORKFLOW_STATUS.md](memory/WORKFLOW_STATUS.md)**
- Four-stage development process documentation
- Quality gates and completion criteria
- Commit frequency guidelines
- Process discipline and standards

### 📋 Working Documents

#### **[changes/003-story-admin-ui-implementation.md](changes/003-story-admin-ui-implementation.md)**
- Complete Admin UI implementation story
- Stage-by-stage development progress
- Technical context and lessons learned
- Reflection and future considerations

### 🎯 Development Context

All documentation is maintained to provide:
- **Clear Development Workflow**: Step-by-step guidance for contributors
- **Architectural Understanding**: Complete system knowledge
- **Quality Standards**: Testing and validation requirements
- **Process Discipline**: Four-stage development methodology

## Project Structure

```
module3/
├── Makefile                    # Development commands and automation
├── README.md                   # This file - project overview
├── CLAUDE.md                   # AI assistant context and instructions
│
├── memory/                     # Core documentation
│   ├── ARCHITECTURE.md         # System architecture and design
│   ├── IMPLEMENTATION.md       # Technical implementation details
│   ├── ENV_SCRIPTS.md          # Development workflow and commands
│   └── WORKFLOW_STATUS.md      # Four-stage development process
│
├── changes/                    # Working documents and story tracking
│   └── 003-story-admin-ui-implementation.md
│
├── svc/                        # Backend service
│   ├── docker-compose.yml      # Complete stack configuration
│   ├── pyproject.toml          # Python dependencies and project config
│   ├── .env.example            # Environment configuration template
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Settings and configuration management
│   ├── database.py             # PostgreSQL connection pool
│   ├── models.py               # Pydantic data models
│   ├── repository.py           # Data access layer (Repository pattern)
│   ├── migrations.py           # Database migration system
│   ├── routers/                # API endpoint modules
│   │   ├── applications.py     # Application CRUD endpoints
│   │   └── configurations.py   # Configuration CRUD endpoints
│   ├── migrations/             # SQL migration files
│   ├── observability/          # Monitoring and observability
│   │   ├── README.md         # Observability module documentation
│   │   ├── __init__.py       # Package exports
│   │   ├── setup.py          # OpenTelemetry setup
│   │   ├── spans.py          # Span utilities
│   │   ├── metrics.py        # Prometheus metrics
│   │   ├── routes.py         # Trace API routes
│   │   ├── middleware/       # FastAPI middleware components
│   │   │   └── error_tracking.py # Error tracking middleware
│   │   ├── trace_storage/    # Trace persistence
│   │   │   └── file_span_processor.py # OpenTelemetry span processor
│   │   ├── trace_query/      # Trace querying
│   │   ├── grafana/          # Auto-loading dashboards
│   │   ├── otel-collector.yml # OpenTelemetry configuration
│   │   └── prometheus.yml    # Metrics collection config
│   └── test_*.py              # Backend test suite
│
└── ui/                         # Frontend Admin UI
    ├── package.json            # Node.js dependencies and scripts
    ├── tsconfig.json           # TypeScript configuration
    ├── vite.config.ts          # Build system configuration
    ├── playwright.config.ts    # E2E test configuration
    ├── src/                    # Source code
    │   ├── main.ts             # Application entry point
    │   ├── components/         # Web Components
    │   │   ├── base/           # Base component classes
    │   │   ├── application/    # Application management UI
    │   │   ├── configuration/  # Configuration management UI
    │   │   ├── layout/         # Layout and navigation
    │   │   └── routing/        # Client-side routing
    │   ├── services/           # API service layer
    │   └── types/              # TypeScript type definitions
    └── tests/                  # Frontend test suite
        └── e2e/                # Playwright E2E tests
```

## License

[License details to be added]