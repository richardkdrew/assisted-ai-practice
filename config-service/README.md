# Config Service - Docker Setup

This project uses Docker Compose to run PostgreSQL as the database runtime.

## Prerequisites

- Docker and Docker Compose installed on your system

## Database Setup

### Starting the Database

To start the PostgreSQL database:

```bash
docker-compose up -d
```

This will:
- Pull the lightweight `postgres:15-alpine` image
- Create a custom network `config-service-network`
- Set up persistent data storage with a named volume
- Initialize the database with migrations from `config-service/database/migrations/`
- Start the database on port 5432

### Stopping the Database

To stop the database:

```bash
docker-compose down
```

To stop and remove all data:

```bash
docker-compose down -v
```

### Database Configuration

The database configuration is managed through environment variables in the `.env` file:

- `POSTGRES_DB`: Database name (default: config_service)
- `POSTGRES_USER`: Database user (default: config_user)
- `POSTGRES_PASSWORD`: Database password (default: config_password)
- `POSTGRES_HOST`: Database host (default: localhost)
- `POSTGRES_PORT`: Database port (default: 5432)

### Connecting to the Database

You can connect to the database using any PostgreSQL client:

- **Host**: localhost
- **Port**: 5432
- **Database**: config_service
- **Username**: config_user
- **Password**: config_password

### Health Check

The container includes a health check that verifies the database is ready to accept connections. You can check the status with:

```bash
docker-compose ps
```

### Viewing Logs

To view database logs:

```bash
docker-compose logs postgres
```

To follow logs in real-time:

```bash
docker-compose logs -f postgres
```

## Network

The setup creates a custom bridge network `config-service-network` that allows easy communication between services if you add more containers to the stack later.

## Data Persistence

Database data is persisted using a Docker named volume `postgres_data`, ensuring your data survives container restarts and updates.
