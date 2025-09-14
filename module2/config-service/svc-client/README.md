# Configuration Service Client

A TypeScript client library for interacting with the Configuration Service API. This library provides type-safe methods for managing applications and configurations with comprehensive error handling and validation.

## Features

- 🔒 **Type Safety**: Full TypeScript support with comprehensive type definitions
- 🚀 **Easy to Use**: Simple, intuitive API design
- 🛡️ **Error Handling**: Comprehensive error handling with custom error types
- 📦 **Lightweight**: Minimal dependencies
- 🔧 **Configurable**: Flexible configuration options
- 🧪 **Well Tested**: Comprehensive unit and integration tests
- 📚 **Well Documented**: Complete API documentation with examples

## Installation

```bash
npm install @config-service/client
```

## Quick Start

```typescript
import { ConfigServiceClient } from '@config-service/client';

// Create a client instance
const client = new ConfigServiceClient({
  baseUrl: 'http://localhost:8000'
});

// Create an application
const app = await client.applications.create({
  name: 'my-web-app',
  description: 'My web application'
});

// Create a configuration
const config = await client.configurations.create({
  applicationId: app.id,
  name: 'database',
  configuration: {
    host: 'localhost',
    port: 5432,
    database: 'myapp',
    username: 'user',
    password: 'password'
  },
  comment: 'Database configuration for production'
});

// Get configuration data
const dbConfig = await client.getConfigByName('my-web-app', 'database');
console.log(dbConfig.host); // 'localhost'
```

## API Reference

### ConfigServiceClient

The main client class for interacting with the Configuration Service.

#### Constructor

```typescript
new ConfigServiceClient(options: ConfigServiceClientOptions)
```

**Options:**
- `baseUrl` (string): Base URL of the Configuration Service API
- `timeout?` (number): Request timeout in milliseconds (default: 30000)
- `headers?` (Record<string, string>): Default headers to include with requests
- `apiVersion?` (string): API version to use (default: 'v1')

#### Methods

##### Applications Management

```typescript
// Create an application
const app = await client.applications.create({
  name: 'my-app',
  description: 'My application'
});

// Get application by ID
const app = await client.applications.getById('01ARZ3NDEKTSV4RRFFQ69G5FAV');

// Update an application
const updatedApp = await client.applications.update('01ARZ3NDEKTSV4RRFFQ69G5FAV', {
  name: 'updated-app-name',
  description: 'Updated description'
});

// List applications with pagination
const response = await client.applications.list({
  limit: 10,
  offset: 0
});

// Delete an application
await client.applications.delete('01ARZ3NDEKTSV4RRFFQ69G5FAV');

// Search applications by name
const results = await client.applications.searchByName('my-app');

// Check if application exists
const exists = await client.applications.exists('01ARZ3NDEKTSV4RRFFQ69G5FAV');
```

##### Configurations Management

```typescript
// Create a configuration
const config = await client.configurations.create({
  applicationId: '01ARZ3NDEKTSV4RRFFQ69G5FAV',
  name: 'api-settings',
  configuration: {
    apiUrl: 'https://api.example.com',
    timeout: 5000,
    retries: 3
  },
  comment: 'API configuration settings'
});

// Get configuration by ID
const config = await client.configurations.getById('01ARZ3NDEKTSV4RRFFQ69G5FAV');

// Update a configuration
const updatedConfig = await client.configurations.update('01ARZ3NDEKTSV4RRFFQ69G5FAV', {
  configuration: {
    apiUrl: 'https://api-v2.example.com',
    timeout: 10000,
    retries: 5
  }
});

// List configurations
const response = await client.configurations.list({
  limit: 20,
  offset: 0,
  applicationId: '01ARZ3NDEKTSV4RRFFQ69G5FAV' // Optional filter
});

// Get configurations by application ID
const configs = await client.configurations.getByApplicationId('01ARZ3NDEKTSV4RRFFQ69G5FAV');

// Get configuration by name within an application
const config = await client.configurations.getByName('01ARZ3NDEKTSV4RRFFQ69G5FAV', 'api-settings');

// Get only the configuration data (without metadata)
const configData = await client.configurations.getConfigurationData('01ARZ3NDEKTSV4RRFFQ69G5FAV');

// Delete a configuration
await client.configurations.delete('01ARZ3NDEKTSV4RRFFQ69G5FAV');
```

##### Convenience Methods

```typescript
// Get configuration data by application and configuration name
const configData = await client.getConfigByName('my-app', 'database');

// Create application with initial configurations
const result = await client.createApplicationWithConfigurations(
  { name: 'new-app', description: 'New application' },
  [
    {
      name: 'database',
      configuration: { host: 'localhost', port: 5432 },
      comment: 'Database settings'
    },
    {
      name: 'cache',
      configuration: { host: 'redis-server', port: 6379 },
      comment: 'Cache settings'
    }
  ]
);

// Get application with all its configurations
const appWithConfigs = await client.getApplicationWithConfigurations('01ARZ3NDEKTSV4RRFFQ69G5FAV');

// Delete application and all its configurations
await client.deleteApplicationWithConfigurations('01ARZ3NDEKTSV4RRFFQ69G5FAV');

// Health check
const health = await client.healthCheck();
console.log(health.status); // 'healthy' or 'unhealthy'
```

## Error Handling

The client library provides comprehensive error handling with custom error types:

```typescript
import {
  ConfigServiceClientError,
  ValidationError,
  NotFoundError,
  ConflictError,
  NetworkError,
  isValidationError,
  isNotFoundError
} from '@config-service/client';

try {
  const app = await client.applications.create({
    name: '', // Invalid: empty name
    description: 'Test app'
  });
} catch (error) {
  if (isValidationError(error)) {
    console.log('Validation failed:', error.details);
  } else if (isNotFoundError(error)) {
    console.log('Resource not found:', error.message);
  } else if (error instanceof NetworkError) {
    console.log('Network error:', error.message);
  } else {
    console.log('Unknown error:', error);
  }
}
```

### Error Types

- `ConfigServiceClientError`: Base error class
- `ValidationError`: Input validation failures
- `NotFoundError`: Resource not found (404)
- `ConflictError`: Resource conflicts (409)
- `AuthenticationError`: Authentication failures (401)
- `AuthorizationError`: Authorization failures (403)
- `NetworkError`: Network connectivity issues
- `ServerError`: Server-side errors (5xx)
- `TimeoutError`: Request timeouts

## Configuration

### Environment Variables

You can configure the client using environment variables:

```bash
CONFIG_SERVICE_BASE_URL=http://localhost:8000
CONFIG_SERVICE_TIMEOUT=30000
```

```typescript
const client = new ConfigServiceClient({
  baseUrl: process.env.CONFIG_SERVICE_BASE_URL || 'http://localhost:8000',
  timeout: parseInt(process.env.CONFIG_SERVICE_TIMEOUT || '30000')
});
```

### Custom Headers

```typescript
const client = new ConfigServiceClient({
  baseUrl: 'http://localhost:8000',
  headers: {
    'Authorization': 'Bearer your-token',
    'X-Custom-Header': 'custom-value'
  }
});
```

### Custom Fetch Implementation

For testing or special environments:

```typescript
import fetch from 'node-fetch';

const client = new ConfigServiceClient({
  baseUrl: 'http://localhost:8000',
  fetch: fetch as any
});
```

## TypeScript Support

The library is written in TypeScript and provides comprehensive type definitions:

```typescript
import type {
  Application,
  Configuration,
  CreateApplicationDTO,
  CreateConfigurationDTO,
  ListApplicationsResponse,
  ConfigServiceClientOptions
} from '@config-service/client';

// All types are fully typed and provide IntelliSense support
const createApp = async (data: CreateApplicationDTO): Promise<Application> => {
  return await client.applications.create(data);
};
```

## Examples

### Basic CRUD Operations

```typescript
import { ConfigServiceClient } from '@config-service/client';

const client = new ConfigServiceClient({
  baseUrl: 'http://localhost:8000'
});

async function example() {
  // Create application
  const app = await client.applications.create({
    name: 'ecommerce-api',
    description: 'E-commerce API service'
  });

  // Create configurations
  const dbConfig = await client.configurations.create({
    applicationId: app.id,
    name: 'database',
    configuration: {
      host: 'db.example.com',
      port: 5432,
      database: 'ecommerce',
      ssl: true
    }
  });

  const apiConfig = await client.configurations.create({
    applicationId: app.id,
    name: 'api',
    configuration: {
      port: 3000,
      cors: true,
      rateLimit: 1000
    }
  });

  // List all configurations for the application
  const configs = await client.configurations.getByApplicationId(app.id);
  console.log(`Found ${configs.length} configurations`);

  // Update configuration
  await client.configurations.update(dbConfig.id, {
    configuration: {
      ...dbConfig.configuration,
      pool: { min: 2, max: 10 }
    }
  });

  // Get configuration data directly
  const dbSettings = await client.getConfigByName('ecommerce-api', 'database');
  console.log('Database host:', dbSettings.host);
}
```

### Error Handling Example

```typescript
import {
  ConfigServiceClient,
  ValidationError,
  NotFoundError,
  NetworkError
} from '@config-service/client';

const client = new ConfigServiceClient({
  baseUrl: 'http://localhost:8000'
});

async function robustExample() {
  try {
    const app = await client.applications.getById('invalid-id');
  } catch (error) {
    if (error instanceof ValidationError) {
      console.error('Invalid ID format:', error.details);
    } else if (error instanceof NotFoundError) {
      console.error('Application not found');
    } else if (error instanceof NetworkError) {
      console.error('Network issue:', error.message);
      // Maybe retry or use cached data
    } else {
      console.error('Unexpected error:', error);
    }
  }
}
```

## Development

### Building

```bash
npm run build
```

### Testing

```bash
npm test
npm run test:coverage
npm run test:integration
```

### Linting

```bash
npm run lint
```

## License

MIT

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues and questions, please use the GitHub issue tracker.
