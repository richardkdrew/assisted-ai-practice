# Config Service Implementation Plan

## Project Overview
This document provides a comprehensive implementation plan for a Config Service REST Web API built with Python 3.13.5 and FastAPI 0.116.1, following strict architectural requirements and using direct SQL management without an ORM.

## 1. Project Directory Structure

```
config-service/
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore file
├── Pipfile                         # Pipenv dependencies
├── Pipfile.lock                    # Locked dependencies
├── README.md                       # Project documentation
├── main.py                         # FastAPI application entry point
├── main_test.py                    # Main application tests
├── config/
│   ├── __init__.py
│   ├── settings.py                 # Application configuration
│   └── settings_test.py            # Configuration tests
├── database/
│   ├── __init__.py
│   ├── connection.py               # Database connection pool
│   ├── connection_test.py          # Connection tests
│   ├── migrations.py               # Migration system
│   ├── migrations_test.py          # Migration tests
│   └── migrations/                 # SQL migration files
│       ├── 001_create_migrations_table.sql
│       ├── 002_create_applications_table.sql
│       └── 003_create_configurations_table.sql
├── models/
│   ├── __init__.py
│   ├── application.py              # Application Pydantic models
│   ├── application_test.py         # Application model tests
│   ├── configuration.py            # Configuration Pydantic models
│   ├── configuration_test.py       # Configuration model tests
│   ├── base.py                     # Base model classes
│   └── base_test.py                # Base model tests
├── repositories/
│   ├── __init__.py
│   ├── base_repository.py          # Base repository pattern
│   ├── base_repository_test.py     # Base repository tests
│   ├── application_repository.py   # Application data access
│   ├── application_repository_test.py
│   ├── configuration_repository.py # Configuration data access
│   └── configuration_repository_test.py
├── services/
│   ├── __init__.py
│   ├── application_service.py      # Application business logic
│   ├── application_service_test.py
│   ├── configuration_service.py    # Configuration business logic
│   └── configuration_service_test.py
└── api/
    ├── __init__.py
    ├── v1/
    │   ├── __init__.py
    │   ├── applications.py          # Application endpoints
    │   ├── applications_test.py     # Application API tests
    │   ├── configurations.py        # Configuration endpoints
    │   └── configurations_test.py   # Configuration API tests
    └── dependencies.py              # FastAPI dependencies
```

## 2. Technology Stack Implementation

### 2.1 Pipfile Configuration
```toml
[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
fastapi = "==0.116.1"
pydantic = "==2.11.7"
pytest = "==8.4.1"
pytest-cov = "==6.2.1"
httpx = "==0.28.1"
psycopg2 = "==2.9.10"
pydantic-settings = ">=2.0.0,<3.0.0"
python-ulid = ">=2.0.0,<3.0.0"
uvicorn = {extras = ["standard"], version = "*"}

[dev-packages]

[requires]
python_version = "3.13"

[scripts]
dev = "uvicorn main:app --reload --host 0.0.0.0 --port 8000"
test = "pytest --cov=. --cov-report=html --cov-report=term-missing"
migrate = "python -m database.migrations"
```

## 3. Database Schema Design

### 3.1 Migration System
- **migrations** table tracks applied migrations
- Sequential SQL files in `migrations/` folder
- Python migration runner with rollback capability

### 3.2 Database Tables

#### Applications Table
```sql
CREATE TABLE applications (
    id VARCHAR(26) PRIMARY KEY,  -- ULID format
    name VARCHAR(256) UNIQUE NOT NULL,
    comments VARCHAR(1024),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Configurations Table
```sql
CREATE TABLE configurations (
    id VARCHAR(26) PRIMARY KEY,  -- ULID format
    application_id VARCHAR(26) NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    name VARCHAR(256) NOT NULL,
    comments VARCHAR(1024),
    config JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(application_id, name)
);
```

## 4. Architecture Patterns

### 4.1 Repository Pattern
- Direct SQL management without ORM
- Separation of data access logic
- Testable database operations
- Connection pooling with ThreadedConnectionPool

### 4.2 Service Layer
- Business logic encapsulation
- Transaction management
- Data validation and transformation
- Error handling and logging

### 4.3 API Layer
- FastAPI routers for endpoint organization
- Request/response model validation
- Dependency injection for services
- Comprehensive error handling

## 5. Data Models (Pydantic)

### 5.1 Application Models
```python
# Request Models
class ApplicationCreate(BaseModel):
    name: str = Field(..., max_length=256)
    comments: Optional[str] = Field(None, max_length=1024)

class ApplicationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=256)
    comments: Optional[str] = Field(None, max_length=1024)

# Response Models
class ApplicationResponse(BaseModel):
    id: ULID
    name: str
    comments: Optional[str]
    configuration_ids: List[ULID] = []
    created_at: datetime
    updated_at: datetime
```

### 5.2 Configuration Models
```python
# Request Models
class ConfigurationCreate(BaseModel):
    application_id: ULID
    name: str = Field(..., max_length=256)
    comments: Optional[str] = Field(None, max_length=1024)
    config: Dict[str, Any]

class ConfigurationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=256)
    comments: Optional[str] = Field(None, max_length=1024)
    config: Optional[Dict[str, Any]] = None

# Response Models
class ConfigurationResponse(BaseModel):
    id: ULID
    application_id: ULID
    name: str
    comments: Optional[str]
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
```

## 6. API Endpoints Specification

### 6.1 Applications Endpoints (`/api/v1/applications`)

#### POST /applications
- **Purpose**: Create new application
- **Request**: ApplicationCreate
- **Response**: ApplicationResponse
- **Status Codes**: 201 (Created), 400 (Bad Request), 409 (Conflict)

#### PUT /applications/{id}
- **Purpose**: Update existing application
- **Request**: ApplicationUpdate
- **Response**: ApplicationResponse
- **Status Codes**: 200 (OK), 400 (Bad Request), 404 (Not Found)

#### GET /applications/{id}
- **Purpose**: Get application by ID with related configuration IDs
- **Response**: ApplicationResponse (includes configuration_ids list)
- **Status Codes**: 200 (OK), 404 (Not Found)

#### GET /applications
- **Purpose**: List all applications
- **Response**: List[ApplicationResponse]
- **Status Codes**: 200 (OK)

### 6.2 Configurations Endpoints (`/api/v1/configurations`)

#### POST /configurations
- **Purpose**: Create new configuration
- **Request**: ConfigurationCreate
- **Response**: ConfigurationResponse
- **Status Codes**: 201 (Created), 400 (Bad Request), 409 (Conflict)

#### PUT /configurations/{id}
- **Purpose**: Update existing configuration
- **Request**: ConfigurationUpdate
- **Response**: ConfigurationResponse
- **Status Codes**: 200 (OK), 400 (Bad Request), 404 (Not Found)

#### GET /configurations/{id}
- **Purpose**: Get configuration by ID
- **Response**: ConfigurationResponse
- **Status Codes**: 200 (OK), 404 (Not Found)

## 7. Database Connection Implementation

### 7.1 Connection Pool Configuration
```python
from psycopg2.pool import ThreadedConnectionPool
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
import psycopg2.extras

class DatabaseManager:
    def __init__(self, connection_string: str, min_conn: int = 1, max_conn: int = 20):
        self.pool = ThreadedConnectionPool(
            min_conn, max_conn, connection_string,
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        self.executor = ThreadPoolExecutor(max_workers=max_conn)
    
    @asynccontextmanager
    async def get_connection(self):
        # Implementation with proper connection management
```

## 8. Testing Strategy

### 8.1 Unit Testing Approach
- **Coverage Target**: 80% for all code files
- **Test Location**: Co-located with `_test.py` suffix
- **Test Categories**:
  - Model validation tests
  - Repository operation tests
  - Service logic tests
  - API endpoint tests

### 8.2 Test Database Setup
- Separate test database configuration
- Transaction rollback for test isolation
- Mock external dependencies
- Comprehensive error scenario testing

### 8.3 Integration Testing
- End-to-end API testing with httpx
- Database migration testing
- Connection pool testing
- Performance testing for scalability

## 9. Configuration Management

### 9.1 Environment Variables (.env)
```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/config_service
DATABASE_TEST_URL=postgresql://user:password@localhost:5432/config_service_test

# Application Configuration
LOG_LEVEL=INFO
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Connection Pool Settings
DB_MIN_CONNECTIONS=1
DB_MAX_CONNECTIONS=20
```

### 9.2 Settings Implementation
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    database_test_url: str
    log_level: str = "INFO"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    db_min_connections: int = 1
    db_max_connections: int = 20
    
    class Config:
        env_file = ".env"
```

## 10. Implementation Steps

### Phase 1: Project Setup
1. Initialize pipenv environment
2. Install exact dependency versions
3. Create project directory structure
4. Set up .gitignore and basic configuration

### Phase 2: Database Foundation
1. Implement migration system
2. Create database schema migrations
3. Set up connection pooling
4. Implement base repository pattern

### Phase 3: Data Models
1. Create Pydantic models for validation
2. Implement ULID integration
3. Add comprehensive model tests
4. Validate data constraints

### Phase 4: Repository Layer
1. Implement application repository
2. Implement configuration repository
3. Add comprehensive repository tests
4. Optimize SQL queries

### Phase 5: Service Layer
1. Create application service
2. Create configuration service
3. Implement business logic
4. Add service layer tests

### Phase 6: API Layer
1. Implement FastAPI application
2. Create API endpoints
3. Add request/response validation
4. Implement comprehensive API tests

### Phase 7: Integration & Testing
1. End-to-end testing
2. Performance testing
3. Error handling validation
4. Documentation completion

## 11. Development Workflow

### 11.1 Setup Commands
```bash
# Environment setup
pipenv install
pipenv shell

# Database setup
pipenv run migrate

# Development server
pipenv run dev

# Testing
pipenv run test
```

### 11.2 Quality Assurance
- Code coverage monitoring (80% minimum)
- Comprehensive error handling
- Input validation at all layers
- Performance monitoring
- Security best practices

## 12. Scalability Considerations

### 12.1 Performance Optimizations
- Connection pooling for database efficiency
- Async/await patterns for I/O operations
- Efficient SQL queries with proper indexing
- Response caching strategies

### 12.2 Future Growth Planning
- Modular architecture for easy extension
- Clear separation of concerns
- Comprehensive logging and monitoring
- API versioning strategy
- Database migration system for schema evolution

This implementation plan provides a comprehensive roadmap for building a robust, scalable Config Service that strictly adheres to all specified requirements while following clean architecture principles and best practices.
