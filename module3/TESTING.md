# Testing Guide for Configuration Service

This document provides instructions for testing the Configuration Service API manually and programmatically.

## Quick Testing

### Option 1: Using the Original PostgreSQL Setup

If you have Docker available:

```bash
# Start database
make db-up

# Wait for database to be ready
sleep 10

# Run migrations
make migrate

# Start the service
make run
```

Then test with:
```bash
# Test health endpoint
curl http://localhost:8000/health

# Create an application
curl -X POST http://localhost:8000/api/v1/applications/ \
  -H "Content-Type: application/json" \
  -d '{"name":"test-app","comments":"Test application"}'

# List applications
curl http://localhost:8000/api/v1/applications/
```

### Option 2: Using Test Scripts (No Docker Required)

For environments without Docker, we've created test scripts that demonstrate the API functionality:

```bash
# Run the simple curl-based test
cd svc && python test_simple.py

# Or run the comprehensive test
cd svc && python test_manual.py

# Run the test server
cd svc && python run_test_app.py
```

## API Testing Scenarios

### 1. Application Management

**Create Application:**
```bash
curl -X POST http://localhost:8000/api/v1/applications/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-web-app",
    "comments": "Main web application"
  }'
```

**Get Application:**
```bash
curl http://localhost:8000/api/v1/applications/{application_id}
```

**List Applications:**
```bash
curl "http://localhost:8000/api/v1/applications/?limit=10&offset=0"
```

**Update Application:**
```bash
curl -X PUT http://localhost:8000/api/v1/applications/{application_id} \
  -H "Content-Type: application/json" \
  -d '{
    "name": "updated-app-name",
    "comments": "Updated comments"
  }'
```

### 2. Configuration Management

**Create Configuration:**
```bash
curl -X POST http://localhost:8000/api/v1/configurations/ \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
    "name": "database-config",
    "comments": "Database connection settings",
    "config": {
      "host": "localhost",
      "port": 5432,
      "ssl": true,
      "pool_size": 20
    }
  }'
```

**Get Configuration:**
```bash
curl http://localhost:8000/api/v1/configurations/{configuration_id}
```

**Update Configuration:**
```bash
curl -X PUT http://localhost:8000/api/v1/configurations/{configuration_id} \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
    "name": "updated-config",
    "comments": "Updated configuration",
    "config": {
      "host": "production-db",
      "port": 5432,
      "ssl": true,
      "pool_size": 50
    }
  }'
```

## Expected Responses

### Successful Application Creation
```json
{
  "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
  "name": "my-web-app",
  "comments": "Main web application",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "configuration_ids": []
}
```

### Successful Configuration Creation
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

### Application List with Pagination
```json
{
  "items": [...],
  "total": 5,
  "limit": 50,
  "offset": 0,
  "has_more": false
}
```

## Integration Testing

For comprehensive testing, use the integration test suite:

```bash
# Run all tests including integration tests
make test

# Run only integration tests
make test-integration

# Generate coverage report
make coverage
```

## API Documentation

Once the service is running, comprehensive API documentation is available at:
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Error Scenarios to Test

### 1. Validation Errors
```bash
# Missing required fields
curl -X POST http://localhost:8000/api/v1/applications/ \
  -H "Content-Type: application/json" \
  -d '{}'

# Invalid ULID format
curl http://localhost:8000/api/v1/applications/invalid-id
```

### 2. Constraint Violations
```bash
# Duplicate application name
curl -X POST http://localhost:8000/api/v1/applications/ \
  -H "Content-Type: application/json" \
  -d '{"name":"existing-app"}'

# Duplicate configuration name within application
curl -X POST http://localhost:8000/api/v1/configurations/ \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
    "name": "existing-config",
    "config": {}
  }'
```

### 3. Not Found Scenarios
```bash
# Non-existent application
curl http://localhost:8000/api/v1/applications/01ARZ3NDEKTSV4RRFFQ69G5XXX

# Non-existent configuration
curl http://localhost:8000/api/v1/configurations/01ARZ3NDEKTSV4RRFFQ69G5XXX
```

## Health Monitoring

The service provides a health check endpoint for monitoring:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "configuration-service"
}
```

## Performance Testing

For load testing, you can use tools like Apache Bench or wrk:

```bash
# Simple load test on health endpoint
ab -n 1000 -c 10 http://localhost:8000/health

# Test application creation under load
ab -n 100 -c 5 -p app_data.json -T application/json \
   http://localhost:8000/api/v1/applications/
```

Where `app_data.json` contains:
```json
{"name":"load-test-app","comments":"Load testing application"}
```