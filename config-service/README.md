# Config Service

A REST API service for managing application configurations built with Python 3.13.5 and FastAPI 0.116.1.

## Features

- **Applications Management**: Create, read, update, and delete applications
- **Configurations Management**: Manage configuration data for applications with JSONB storage
- **ULID Primary Keys**: Uses ULID (Universally Unique Lexicographically Sortable Identifier) for all entities
- **Direct SQL Management**: No ORM - uses direct SQL with repository pattern for optimal performance
- **Database Migrations**: Automated migration system for schema evolution
- **Comprehensive Testing**: 80% test coverage with co-located unit tests
- **Connection Pooling**: Efficient database connection management with ThreadedConnectionPool
- **Clean Architecture**: Separation of concerns with repository, service, and API layers
- **Docker Support**: PostgreSQL database with pgAdmin for easy database management

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
- pipenv

### Installation

1. Clone the repository and navigate to the service directory:
   ```bash
   cd config-service/svc
   ```

2. Install dependencies using pipenv:
   ```bash
   pipenv install
   ```

3. Activate the virtual environment:
   ```bash
   pipenv shell
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
   pipenv run migrate
   ```

6. Start the development server:
   ```bash
   pipenv run dev
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

- `pipenv run dev` - Start development server with auto-reload
- `pipenv run test` - Run tests with coverage report
- `pipenv run migrate` - Run database migrations

### Running Tests

```bash
pipenv run test
```

This will run all tests with coverage reporting. Test files are co-located with their corresponding source files using the `_test.py` suffix.

### Database Migrations

The migration system automatically tracks and applies database schema changes:

```bash
# Run pending migrations
pipenv run migrate

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

## API Documentation

Once the server is running, you can access:

- **Interactive API Documentation**: `http://localhost:8000/docs`
- **Alternative API Documentation**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

## Architecture

The application follows clean architecture principles with clear separation of concerns:

```
config-service/
├── README.md               # Documentation
├── .gitignore             # Git ignore rules
└── svc/                   # All service code
    ├── main.py            # Application entry point
    ├── docker-compose.yml # Docker configuration
    ├── Pipfile            # Python dependencies
    ├── config/            # Application configuration
    ├── database/          # Database connection and migrations
    ├── models/            # Pydantic data models
    ├── api/               # API layer (FastAPI routers)
    ├── services/          # Business logic layer
    └── repositories/      # Data access layer
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

1. Ensure all tests pass: `pipenv run test`
2. Follow the existing code style and patterns
3. Add tests for new functionality
4. Update documentation as needed

## License

This project is part of the Config Service implementation following the specified requirements.
