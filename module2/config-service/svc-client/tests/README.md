# Configuration Service Client - Integration Tests

This directory contains integration tests for the Configuration Service Client library. These tests verify the client's functionality against a running Configuration Service API.

## Overview

The integration tests are designed to:
- Test configuration filtering by application ID
- Verify pagination functionality
- Test CRUD operations with proper application association
- Validate error handling and edge cases
- Ensure cross-application isolation

## Test Structure

```
tests/
├── integration/
│   └── configurations-service.integration.test.ts  # Main integration tests
├── setup.ts                                        # Global test setup
└── README.md                                       # This file
```

## Prerequisites

⚠️ **IMPORTANT**: The integration tests require a running Configuration Service API server.

Before running the integration tests, ensure you have:

1. **Configuration Service API running**: The tests expect the API to be available at `http://localhost:8000/api` by default
2. **Database access**: The API should have access to a test database
3. **Clean test environment**: Tests create and clean up their own data, but a clean environment is recommended

### Starting the API Server

To start the Configuration Service API:

```bash
# Navigate to the service directory
cd ../svc

# Install dependencies (if not already done)
pip install -r requirements.txt

# Start the server
python main.py
```

The server should be running on `http://localhost:8000` before running the integration tests.

## Environment Variables

The tests support the following environment variables:

- `CONFIG_SERVICE_API_URL`: Base URL for the Configuration Service API (default: `http://localhost:8000/api`)

Example:
```bash
export CONFIG_SERVICE_API_URL=http://localhost:8000/api
```

## Running Tests

### All Tests
```bash
npm test
```

### Integration Tests Only
```bash
npm run test:integration
```

### With Coverage
```bash
npm run test:coverage
```

### Watch Mode (for development)
```bash
npm test -- --watch
```

## Test Categories

### 1. Basic Configuration Filtering (`getByApplicationId`)
- Verifies configurations are filtered by application ID
- Tests pagination with limit and offset
- Validates empty results for non-existent applications
- Tests error handling for invalid application IDs

### 2. Cross-Application Filtering
- Creates multiple applications with configurations
- Verifies no cross-contamination between applications
- Tests consistency across multiple API calls

### 3. CRUD Operations with Filtering
- Tests configuration creation and retrieval
- Verifies configurations maintain application association after updates
- Validates proper cleanup and isolation

### 4. Error Handling and Edge Cases
- Tests behavior with empty applications
- Validates error responses for malformed IDs
- Tests network error handling

## Test Data Management

The tests follow these principles:
- **Self-contained**: Each test creates its own test data
- **Cleanup**: All created data is cleaned up after tests complete
- **Isolation**: Tests don't interfere with each other
- **Deterministic**: Tests use timestamps to ensure unique names

## Configuration

The test suite uses Vitest with the following configuration:
- **Timeout**: 30 seconds for test operations
- **Environment**: Node.js
- **Globals**: Enabled for describe/it/expect
- **Setup**: Global setup file for environment configuration

## Debugging Tests

### Verbose Output
```bash
npm test -- --reporter=verbose
```

### Run Specific Test
```bash
npm test -- --grep "should retrieve configurations for a specific application"
```

### Debug Mode
```bash
npm test -- --inspect-brk
```

## Common Issues and Solutions

### 1. Connection Refused
**Problem**: Tests fail with connection refused errors
**Solution**: Ensure the Configuration Service API is running on the expected port

### 2. Database Errors
**Problem**: Tests fail with database-related errors
**Solution**: Verify the API has proper database access and migrations are applied

### 3. Timeout Errors
**Problem**: Tests timeout during execution
**Solution**: Check API performance or increase timeout in `vitest.config.ts`

### 4. Cleanup Failures
**Problem**: Warning messages about cleanup failures
**Solution**: These are usually harmless but may indicate API issues during teardown

## Adding New Tests

When adding new integration tests:

1. **Follow the existing pattern**: Use the same setup/teardown approach
2. **Clean up resources**: Add created IDs to `createdConfigIds` for automatic cleanup
3. **Use unique names**: Include timestamps to avoid naming conflicts
4. **Test both success and error cases**: Verify expected behavior and error handling
5. **Document the test purpose**: Use descriptive test names and comments

Example test structure:
```typescript
describe('New Feature Tests', () => {
  it('should handle new feature correctly', async () => {
    // Arrange
    const testData = { /* test data */ };
    
    // Act
    const result = await client.configurations.newFeature(testData);
    
    // Assert
    expect(result).toBeDefined();
    // Add cleanup if needed
    createdConfigIds.push(result.id);
  });
});
```

## Performance Considerations

- Tests run sequentially to avoid database conflicts
- Each test suite creates minimal test data
- Cleanup is performed asynchronously where possible
- Network timeouts are set appropriately for CI/CD environments

## CI/CD Integration

The tests are designed to work in CI/CD environments:
- No external dependencies beyond the API
- Configurable via environment variables
- Proper exit codes for success/failure
- Detailed error reporting

For CI/CD, ensure:
1. Configuration Service API is available
2. Database is properly initialized
3. Environment variables are set correctly
4. Sufficient timeout values for slower environments
