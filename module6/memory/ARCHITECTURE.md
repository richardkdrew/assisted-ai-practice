# Configuration Service - Technical Architecture

## Overview

The Configuration Service is a centralized configuration management system providing dynamic, flexible configuration handling for software applications. It enables runtime configuration updates without requiring redeployment and supports multiple application types with a unified management approach.

**Current Status**: Working baseline with full-stack implementation including backend API, frontend Admin UI, and comprehensive observability integration.

## Technology Stack

### Backend Stack
- **Language**: Python 3.13.5
- **Web Framework**: FastAPI 0.116.1 (async/await, automatic OpenAPI docs)
- **Database**: PostgreSQL 16 (JSONB for flexible configuration storage)
- **Database Adapter**: psycopg2-binary 2.9.10 (connection pooling with RealDictCursor)
- **Validation**: Pydantic 2.11.7 + pydantic-settings 2.6.1
- **Testing**: pytest 8.4.1, pytest-cov 6.2.1, pytest-asyncio, httpx 0.28.1
- **Package Management**: uv (fast Python package management)
- **Primary Keys**: ULID via pydantic-extra-types + python-ulid
- **ASGI Server**: uvicorn (with standard extras)

### Frontend Stack
- **Language**: TypeScript 5.0+ (strict mode, zero external frameworks)
- **Components**: Native Web Components with Shadow DOM encapsulation
- **Build System**: Vite 5.0+ (fast dev server and build tooling)
- **Testing**: Vitest 1.0+ (unit tests) + Playwright 1.40+ (E2E tests)
- **Styling**: CSS Custom Properties with responsive design patterns
- **Architecture**: SOLID principles, dependency inversion, interface segregation

### Observability Stack
- **Metrics Collection**: Prometheus (time-series metrics storage)
- **Visualization**: Grafana (auto-loaded dashboards, admin/admin)
- **Telemetry Pipeline**: OpenTelemetry Collector (traces, metrics, logs)
- **Container Metrics**: cAdvisor v0.52.0 (Docker container monitoring)
- **Instrumentation**: OpenTelemetry FastAPI + psycopg2 + requests
- **Service Discovery**: Docker Compose networking

## Key Design Decisions

### Backend Architecture
- **No ORM**: Direct SQL queries with Repository pattern for performance and SQL control
- **ULID Primary Keys**: Universally Unique Lexicographically Sortable Identifiers for better performance than UUIDs
- **String Storage**: ULIDs stored as VARCHAR(26), validated at API boundaries
- **Connection Pooling**: ThreadedConnectionPool for efficient database resource management (min: 1, max: 20)
- **Async/Await**: Full async support throughout application stack

### Frontend Architecture
- **Zero External Frameworks**: Native Web Components for framework independence and longevity
- **Shadow DOM Encapsulation**: True CSS and JavaScript isolation between components
- **TypeScript Only**: No JavaScript files, strict type checking throughout
- **Single Responsibility**: Each component handles one concern

### Full-Stack Integration
- **Docker Compose**: Complete development environment with single command startup
- **Auto-Loading Dashboards**: Grafana dashboards provision automatically on startup
- **Service Discovery**: Container-to-container communication via Docker networking
- **Environment Configuration**: Complete .env support for all services

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Full Stack Architecture                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Admin UI      │    │   FastAPI App   │    │   PostgreSQL    │
│  (TypeScript)   │    │   (Python)      │    │   Database      │
│                 │    │                 │    │                 │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │Web        │  │◄──►│  │ Routers   │  │◄──►│  │applications│  │
│  │Components │  │    │  └───────────┘  │    │  │   table    │  │
│  └───────────┘  │    │  ┌───────────┐  │    │  └───────────┘  │
│  ┌───────────┐  │    │  │Repository │  │    │  ┌───────────┐  │
│  │API Client │  │    │  │  Layer    │  │    │  │configurations│
│  └───────────┘  │    │  └───────────┘  │    │  │   table    │  │
└─────────────────┘    │  ┌───────────┐  │    │  └───────────┘  │
                       │  │ Database  │  │    │  ┌───────────┐  │
                       │  │   Pool    │  │    │  │migrations │  │
                       │  └───────────┘  │    │  │   table   │  │
                       └─────────────────┘    └─────────────────┘
                                 │
                                 ▼
                       ┌─────────────────┐
                       │  Observability  │
                       │      Stack      │
                       │                 │
                       │  Prometheus     │
                       │  Grafana        │
                       │  OTel Collector │
                       │  cAdvisor       │
                       └─────────────────┘
```

## Directory Structure

```
module6/
├── svc/                          # Backend service code
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Settings management
│   ├── database.py               # Connection pool & utilities
│   ├── models.py                 # Pydantic data models
│   ├── repository.py             # Data access layer (Repository pattern)
│   ├── migrations.py             # Database migration system
│   ├── docker-compose.yml        # Complete stack (DB + API + Observability)
│   ├── pyproject.toml            # Python dependencies
│   ├── .env.example              # Environment template
│   ├── routers/                  # API endpoint modules
│   │   ├── applications.py       # Application CRUD endpoints
│   │   └── configurations.py     # Configuration CRUD endpoints
│   ├── migrations/               # SQL migration files
│   │   └── 001_initial_schema.sql
│   └── *_test.py                 # Test files
├── ui/                           # Frontend Admin UI
│   ├── src/                      # TypeScript source
│   │   ├── components/           # Web Components
│   │   ├── services/             # API client, state management
│   │   ├── types/                # TypeScript interfaces
│   │   └── main.ts               # Application entry point
│   ├── tests/                    # Unit and E2E tests
│   │   ├── unit/                 # Vitest unit tests
│   │   └── e2e/                  # Playwright E2E tests
│   ├── index.html                # Application shell
│   ├── vite.config.ts            # Build configuration
│   ├── tsconfig.json             # TypeScript configuration
│   ├── playwright.config.ts      # E2E test configuration
│   └── package.json              # Node dependencies
├── memory/                       # AI assistant context files
│   ├── ARCHITECTURE.md           # This file - technical reference
│   └── WORKFLOW_STATUS.md        # Four-stage development process
├── changes/                      # Working documents for stories
├── Makefile                      # Development commands
├── CLAUDE.md                     # Project overview & quick reference
└── PRINCIPLES.md                 # Engineering principles (TDD, simplicity)
```

## Database Schema

### Applications Table
```sql
CREATE TABLE applications (
    id VARCHAR(26) PRIMARY KEY,           -- ULID string format
    name VARCHAR(256) UNIQUE NOT NULL,    -- Unique application name
    comments VARCHAR(1024),               -- Optional comments
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

### Configurations Table
```sql
CREATE TABLE configurations (
    id VARCHAR(26) PRIMARY KEY,           -- ULID string format
    application_id VARCHAR(26) NOT NULL   -- Foreign key to applications
        REFERENCES applications(id) ON DELETE CASCADE,
    name VARCHAR(256) NOT NULL,           -- Configuration name
    comments VARCHAR(1024),               -- Optional comments
    config JSONB NOT NULL,                -- Configuration data as JSONB
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(application_id, name)          -- Unique name per application
);
```

### Indexes
```sql
CREATE INDEX idx_configurations_application_id ON configurations(application_id);
CREATE INDEX idx_configurations_name ON configurations(name);
CREATE INDEX idx_configurations_config ON configurations USING GIN(config);
```

## API Architecture

### Endpoint Structure
- **Base Path**: `/api/v1`
- **Applications**: `/api/v1/applications/`
- **Configurations**: `/api/v1/configurations/`
- **Health Check**: `/health`
- **Documentation**: `/docs` (automatic Swagger UI)
- **Metrics**: `/metrics` (Prometheus format)

### Request/Response Flow
1. **Request Validation**: Pydantic models validate incoming JSON
2. **Router Processing**: FastAPI routers handle HTTP routing and parameter extraction
3. **ULID Validation**: String ULIDs validated for format correctness
4. **Repository Operations**: Repository layer executes SQL queries with connection pooling
5. **Response Serialization**: Pydantic models serialize responses to JSON

## Data Access Layer

### Repository Pattern Implementation
- **ApplicationRepository**: All application-related database operations
- **ConfigurationRepository**: All configuration-related database operations
- **Direct SQL**: No ORM - all operations use direct SQL queries
- **Connection Management**: AsyncContextManager pattern for connections
- **Transaction Handling**: Automatic commit/rollback with proper error handling

### Database Operations
```python
# Read operations (no commit)
async def execute_query(self, query: str, params: tuple = None) -> list[Dict[str, Any]]

# Write operations (with commit)
async def execute_command(self, command: str, params: tuple = None) -> int

# Write operations with RETURNING (with commit)
async def execute_returning(self, command: str, params: tuple = None) -> list[Dict[str, Any]]
```

## Configuration Storage Model

### JSONB Storage
- **Flexible Schema**: Configurations stored as JSONB for arbitrary key-value structures
- **Query Capabilities**: GIN index enables efficient querying of configuration content
- **Type Safety**: Pydantic models ensure type validation at API boundaries
- **Serialization**: Automatic JSON serialization/deserialization in repository layer

### Configuration Relationships
- **One-to-Many**: Applications can have multiple configurations
- **Unique Names**: Configuration names must be unique within each application
- **Cascading Deletes**: Deleting an application removes all its configurations
- **Referential Integrity**: Foreign key constraints ensure data consistency

## Critical Implementation Patterns

### 1. ULID Implementation
**Decision**: Use string representations for ULID storage and API responses

```python
# Generation
from ulid import ULID as ULIDGenerator
app_id = str(ULIDGenerator())

# Validation
from pydantic_extra_types.ulid import ULID
def validate_ulid(ulid_str: str) -> ULID:
    try:
        return ULID(ulid_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ULID format")
```

**Why**: Avoids serialization issues, works seamlessly with VARCHAR(26) storage, validates at API boundaries.

### 2. Import Resolution (Dual Pattern)
**Problem**: Module import issues when running files directly vs. as package

```python
# Solution: Dual import pattern
try:
    from .config import settings
    from .database import db_pool
except ImportError:
    from config import settings
    from database import db_pool
```

### 3. JSON Configuration Handling
**Problem**: RealDictCursor may return JSONB as dict or string

```python
# Solution: Type-aware JSON processing
if isinstance(config_dict['config'], str):
    config_dict['config'] = json.loads(config_dict['config']) if config_dict['config'] else {}
elif config_dict['config'] is None:
    config_dict['config'] = {}
# If it's already a dict, leave it as is
```

### 4. Database Transaction Management
**Key Pattern**: Three-tier operation strategy

- `execute_query()` - SELECT operations (no commit)
- `execute_command()` - INSERT/UPDATE/DELETE (with commit)
- `execute_returning()` - INSERT/UPDATE with RETURNING clause (with commit)

## Frontend Architecture

### Web Components Pattern
```typescript
// Base component structure
export class AppComponent extends HTMLElement {
  private shadow: ShadowRoot;

  constructor() {
    super();
    this.shadow = this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.render();
    this.attachEventListeners();
  }

  private render() {
    this.shadow.innerHTML = `
      <style>/* Scoped styles */</style>
      <!-- Component HTML -->
    `;
  }
}
```

### State Management
- **ApiClient**: Centralized HTTP client with error handling
- **Event-driven**: Components communicate via Custom Events
- **No global state**: Each component manages own state
- **Reactive updates**: DOM updates on state changes

## Security & Validation

### Input Validation
- **Pydantic Models**: Type-safe request/response validation
- **ULID Format**: Strict ULID format validation for all ID parameters
- **SQL Injection Prevention**: Parameterized queries throughout
- **Length Limits**: String field length constraints (names: 256 chars, comments: 1024 chars)

### Error Handling
- **HTTP Status Codes**: Proper status codes for different error conditions
- **Validation Errors**: Detailed validation error messages via Pydantic
- **Database Errors**: Constraint violation handling with user-friendly messages
- **404 Handling**: Not found responses for missing resources

## Performance Considerations

### Database Performance
- **Connection Pooling**: ThreadedConnectionPool (configurable min/max connections)
- **Index Strategy**: Strategic indexes on foreign keys, names, and JSONB content
- **Direct SQL**: No ORM overhead for better query performance
- **ULID Benefits**: Lexicographically sortable, better than UUIDs for database performance

### API Performance
- **Async/Await**: Full async support for non-blocking I/O
- **Pagination**: Built-in pagination for list endpoints
- **Minimal Serialization**: Direct dict-to-JSON conversion where possible
- **Health Checks**: Lightweight health endpoint for monitoring

## Observability & Monitoring

### Metrics Collection
- **Application Metrics**: Custom metrics via OpenTelemetry
- **Container Metrics**: cAdvisor monitoring Docker containers
- **Database Metrics**: Connection pool health, query performance
- **HTTP Metrics**: Request/response times, status codes

### Dashboards
- **Configuration Service - Application Metrics**: Application-level metrics
- **Configuration Service - Container Metrics**: Container and infrastructure metrics

### Health Monitoring
- **Health Endpoint**: `/health` provides service status
- **Database Pool Status**: Connection pool health monitoring
- **Application Lifecycle**: Startup/shutdown event handling

## Testing Strategy

### Backend Testing
- **Unit Tests**: Repository and database layer testing
- **Integration Tests**: Complete API-to-database flow testing
- **Coverage Target**: 80%+ (currently achieving 90%+)
- **Test Framework**: pytest with pytest-asyncio for async tests

### Frontend Testing
- **Unit Tests**: Vitest for component logic testing
- **E2E Tests**: Playwright for full user flow testing
- **Coverage Target**: 80%+ for unit tests, 100% pass rate for E2E
- **Test Environment**: Full-stack (UI server + backend + database)

### Test Coverage Results
- **Backend**: 90.44% coverage
- **Frontend E2E**: 87% pass rate (5 tests need fixing)
- **Integration**: Complete CRUD flow coverage

## Development Workflow

### Environment Setup
```bash
# Quick Start - Complete Development Stack
make dev              # Start everything (DB + API + Observability + UI)
make dev-stop         # Stop all services

# Install dependencies
make install          # Backend (Python with uv)
make ui-install       # Frontend (Node.js with npm)

# Start services individually
make dev-backend      # Backend stack only (DB + API + Observability)
make dev-ui-only      # Frontend development server only

# Run tests
make test             # Backend tests
make ui-test          # Frontend unit tests
make ui-test-e2e      # Frontend E2E tests (requires backend running)
```

### Common Commands
```bash
# Testing
make test             # Backend tests with coverage
make ui-test          # Frontend unit tests
make ui-test-e2e      # E2E tests (requires 'make dev-backend' running)
make quality          # Run complete validation suite

# Observability
make grafana          # Open Grafana dashboards (http://localhost:3001)
make prometheus       # Open Prometheus (http://localhost:9090)
make metrics          # View current metrics

# Database
make migrate          # Run database migrations
make db-reset         # Reset database with fresh data
make db-shell         # Connect to PostgreSQL shell
```

### Docker Services
```bash
# Service endpoints
Configuration Service: http://localhost:8000
Admin UI:             http://localhost:5173
PostgreSQL:           localhost:5432
Grafana:              http://localhost:3001 (admin/admin)
Prometheus:           http://localhost:9090
cAdvisor:             http://localhost:8080
```

## Migration Management

### Running Migrations
```bash
make migrate
# OR
cd svc && uv run python -m migrations
```

### Creating New Migrations
1. Create SQL file in `svc/migrations/`
2. Use sequential numbering: `002_description.sql`, `003_description.sql`
3. Include schema changes and data modifications as needed
4. Run `make migrate`

## Configuration Management

### Settings Pattern
```python
# svc/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "configservice"
    db_user: str = "user"
    db_password: str = "password"

    # Connection Pool
    db_pool_min_conn: int = 1
    db_pool_max_conn: int = 20

    # Application
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(env_file=".env")
```

### Environment Variables (.env)
```bash
# Database Configuration
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

# Connection Pool (optional)
DB_POOL_MIN_CONN=1
DB_POOL_MAX_CONN=20
```

## Common Issues & Solutions

### 1. ULID Serialization
**Issue**: `Unable to serialize unknown type: <class 'ulid.ULID'>`
**Solution**: Use strings throughout, validate at API boundary

### 2. Import Resolution
**Issue**: `ImportError: attempted relative import with no known parent package`
**Solution**: Dual import pattern with try/except

### 3. Database Transaction
**Issue**: INSERT operations not committing
**Solution**: Use `execute_returning` for INSERT/UPDATE operations

### 4. JSON Type Issues
**Issue**: `the JSON object must be str, bytes or bytearray, not dict`
**Solution**: Type-aware JSON handling in repository layer

## Extension Points

### Future Considerations
- **Authentication**: JWT/OAuth integration points identified
- **Caching**: Redis integration for configuration caching
- **Message Queue**: Event-driven configuration updates
- **Multi-tenancy**: Tenant isolation patterns
- **Configuration Versioning**: Historical configuration tracking
- **Configuration Templates**: Template-based configuration generation

### API Versioning
- **URL Versioning**: `/api/v1/` prefix for version management
- **Backward Compatibility**: Strategy for maintaining older API versions
- **Migration Paths**: Clear upgrade paths for API consumers

---

*This architecture document reflects the current full-stack implementation including backend API, Admin UI, and observability stack. Last updated: 2025-10-11*
