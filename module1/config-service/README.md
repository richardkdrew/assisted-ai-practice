# Config Service

A complete application configuration management system with REST API service and modern web admin interface.

## Components

### Backend API Service
A REST API service for managing application configurations built with Python 3.13.5 and FastAPI 0.116.1.

### Admin Web Interface
A modern web-based admin interface built with TypeScript, Web Components, and native browser APIs.

## Features

### Backend Features
- **Applications Management**: Create, read, update, and delete applications
- **Configurations Management**: Manage configuration data for applications with JSONB storage
- **ULID Primary Keys**: Uses ULID (Universally Unique Lexicographically Sortable Identifier) for all entities
- **Direct SQL Management**: No ORM - uses direct SQL with repository pattern for optimal performance
- **Database Migrations**: Automated migration system for schema evolution
- **Comprehensive Testing**: 80% test coverage with co-located unit tests
- **Connection Pooling**: Efficient database connection management with ThreadedConnectionPool
- **Clean Architecture**: Separation of concerns with repository, service, and API layers
- **Docker Support**: PostgreSQL database with pgAdmin for easy database management

### Frontend Features
- **Application Management**: Create, read, update, and delete applications via web interface
- **Configuration Management**: Manage key-value configuration pairs for each application
- **Dynamic Configuration Editor**: Support for string, number, boolean, and JSON object types
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Validation**: Client-side form validation with helpful error messages
- **Pagination**: Efficient handling of large datasets
- **Modern Architecture**: Built with Web Components and Shadow DOM

## Tech Stack

- **Language**: Python 3.13.5
- **Web Framework**: FastAPI 0.116.1
- **Validation**: Pydantic 2.11.7
- **Database**: PostgreSQL v16
- **Database Adapter**: psycopg2 2.9.10
- **Testing**: pytest 8.4.1 with pytest-cov 6.2.1
- **HTTP Testing**: httpx 0.28.1
- **Configuration**: pydantic-settings
- **ULID Support**: python-ulid
- **Containerization**: Docker & Docker Compose

## API Endpoints

All endpoints are prefixed with `/api/v1`.

### Applications

- `POST /applications` - Create a new application
- `GET /applications/{id}` - Get application by ID (includes related configuration IDs)
- `PUT /applications/{id}` - Update application by ID
- `GET /applications` - List all applications
- `DELETE /applications/{id}` - Delete application by ID

### Configurations

- `POST /configurations` - Create a new configuration
- `GET /configurations/{id}` - Get configuration by ID
- `PUT /configurations/{id}` - Update configuration by ID
- `GET /configurations` - List all configurations
- `GET /applications/{id}/configurations` - List configurations for a specific application
- `DELETE /configurations/{id}` - Delete configuration by ID

## Quick Start

### Prerequisites

- Python 3.13.5
- Docker and Docker Compose
- uv (Python package installer)

### Installation

1. Clone the repository and navigate to the service directory:
   ```bash
   cd config-service/svc
   ```

2. Install uv if you haven't already:
   ```bash
   pip install uv
   ```

3. Create and activate a virtual environment with uv:
   ```bash
   uv venv
   source .venv/bin/activate  # On Unix/macOS
   # .venv\Scripts\activate   # On Windows
   ```

4. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

4. Copy the environment template and configure your database:
   ```bash
   cp .env.example .env
   # Edit .env with your database configuration
   ```

### Database Setup with Docker

#### Starting the Database

To start the PostgreSQL database and pgAdmin:

```bash
docker-compose up -d
```

This will:
- Pull the lightweight `postgres:15-alpine` image
- Start pgAdmin web interface on port 5050
- Create a custom network `config-service-network`
- Set up persistent data storage with named volumes
- Start the database on port 5432

#### Accessing pgAdmin

Once the containers are running, you can access pgAdmin at `http://localhost:5050`:

- **Email**: `admin@example.com` (configurable via `PGADMIN_EMAIL` env var)
- **Password**: `admin` (configurable via `PGADMIN_PASSWORD` env var)

To connect to your PostgreSQL database in pgAdmin:
- **Host**: `postgres` (the service name)
- **Port**: `5432`
- **Database**: `config_service` (or your `DATABASE_DB` env var value)
- **Username**: `config_user` (or your `DATABASE_USER` env var value)
- **Password**: `config_password` (or your `DATABASE_PASSWORD` env var value)

#### Stopping the Database

To stop the database:

```bash
docker-compose down
```

To stop and remove all data:

```bash
docker-compose down -v
```

### Running the Application

5. Run database migrations:
   ```bash
   python -c "from database.migrations import run_migrations; run_migrations()"
   ```

6. Start the development server:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`.

### Environment Variables

Create a `.env` file based on `.env.example`:

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

# pgAdmin Configuration (for Docker)
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=admin
```

## Development

### Available Scripts

With uv, you can run scripts directly or use the project scripts defined in pyproject.toml:

- `python main.py` - Start development server with auto-reload
- `pytest` - Run tests
- `pytest --cov=. --cov-report=html --cov-report=term` - Run tests with coverage report
- `python -c "from database.migrations import run_migrations; run_migrations()"` - Run database migrations

Or use uv to run project scripts:
- `uv run dev` - Start development server
- `uv run test` - Run tests
- `uv run test-cov` - Run tests with coverage

### Running Tests

```bash
pytest
```

Or with uv:
```bash
uv run test
```

This will run all tests with coverage reporting. Test files are co-located with their corresponding source files using the `_test.py` suffix.

### Database Migrations

The migration system automatically tracks and applies database schema changes:

```bash
# Run pending migrations
python -c "from database.migrations import run_migrations; run_migrations()"

# Check migration status via health endpoint
curl http://localhost:8000/health
```

### Database Management

#### Direct Database Connection

You can connect to the database using any PostgreSQL client:

- **Host**: localhost
- **Port**: 5432
- **Database**: config_service
- **Username**: config_user
- **Password**: config_password

#### Docker Database Logs

To view database logs:

```bash
docker-compose logs postgres
```

To follow logs in real-time:

```bash
docker-compose logs -f postgres
```

#### Health Check

The container includes a health check that verifies the database is ready to accept connections:

```bash
docker-compose ps
```

## Admin Web Interface

The Config Service includes a modern web-based admin interface for managing applications and configurations.

### UI Technology Stack

- **TypeScript**: Strongly typed JavaScript for better development experience
- **Web Components**: Native browser components with Shadow DOM encapsulation
- **Fetch API**: Native browser HTTP client for API communication
- **CSS**: Modern CSS with flexbox and grid layouts
- **Vite**: Fast build tool and development server
- **Vitest**: Unit testing framework
- **Playwright**: End-to-end testing framework

### UI Quick Start

1. Navigate to the UI directory:
   ```bash
   cd config-service/ui
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser to `http://localhost:3001`

### UI Features

- **Application Management**: Create, read, update, and delete applications via web interface
- **Configuration Management**: Manage key-value configuration pairs for each application
- **Dynamic Configuration Editor**: Support for string, number, boolean, and JSON object types
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Validation**: Client-side form validation with helpful error messages
- **Pagination**: Efficient handling of large datasets

### UI Testing

```bash
# Unit tests
npm test

# End-to-end tests
npm run test:e2e

# Type checking
npm run type-check

# Linting
npm run lint
```

## API Documentation

Once the server is running, you can access:

- **Interactive API Documentation**: `http://localhost:8000/docs`
- **Alternative API Documentation**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`
- **Admin Web Interface**: `http://localhost:3001` (when UI server is running)

## Architecture

The application follows clean architecture principles with clear separation of concerns:

```
config-service/
├── README.md               # Documentation
├── .gitignore             # Git ignore rules
├── svc/                   # Backend API service
│   ├── main.py            # Application entry point
│   ├── docker-compose.yml # Docker configuration
│   ├── requirements.txt   # Python dependencies
│   ├── pyproject.toml     # Project configuration and scripts
│   ├── config/            # Application configuration
│   ├── database/          # Database connection and migrations
│   ├── models/            # Pydantic data models
│   ├── api/               # API layer (FastAPI routers)
│   ├── services/          # Business logic layer
│   └── repositories/      # Data access layer
└── ui/                    # Frontend admin interface
    ├── src/               # Source code
    │   ├── components/    # Web Components
    │   ├── services/      # API service layer
    │   ├── models/        # TypeScript interfaces
    │   ├── styles/        # CSS stylesheets
    │   ├── index.html     # Entry point
    │   └── main.ts        # Application bootstrap
    ├── tests/             # Test files
    │   ├── unit/          # Unit tests
    │   ├── e2e/           # End-to-end tests
    │   └── setup.ts       # Test configuration
    ├── package.json       # Dependencies and scripts
    ├── tsconfig.json      # TypeScript configuration
    ├── vite.config.ts     # Build tool configuration
    └── playwright.config.ts # E2E test configuration
```

### Key Design Patterns

- **Repository Pattern**: Abstracts data access logic
- **Service Layer**: Encapsulates business logic and validation
- **Dependency Injection**: Clean separation of concerns
- **ULID Primary Keys**: Sortable, URL-safe unique identifiers
- **Connection Pooling**: Efficient database resource management

## Data Models

### Application
- `id`: ULID (primary key)
- `name`: Unique string (max 256 characters)
- `comments`: Optional string (max 1024 characters)
- `created_at`: Timestamp with timezone
- `updated_at`: Timestamp with timezone

### Configuration
- `id`: ULID (primary key)
- `application_id`: ULID (foreign key to applications)
- `name`: String (max 256 characters, unique per application)
- `comments`: Optional string (max 1024 characters)
- `config`: JSONB dictionary of configuration data
- `created_at`: Timestamp with timezone
- `updated_at`: Timestamp with timezone

## Docker Infrastructure

### Network

The setup creates a custom bridge network `config-service-network` that allows easy communication between services.

### Data Persistence

Database data is persisted using Docker named volumes:
- `postgres_data`: PostgreSQL data
- `pgadmin_data`: pgAdmin configuration

This ensures your data survives container restarts and updates.

## Contributing

1. Ensure all tests pass: `pytest` or `uv run test`
2. Follow the existing code style and patterns
3. Add tests for new functionality
4. Update documentation as needed

## License

This project is part of the Config Service implementation following the specified requirements.
