/**
 * Configuration Service Client Library
 * 
 * A TypeScript client library for interacting with the Configuration Service API.
 * Provides type-safe methods for managing applications and configurations.
 * 
 * @example
 * ```typescript
 * import { ConfigServiceClient } from '@config-service/client';
 * 
 * const client = new ConfigServiceClient({
 *   baseUrl: 'http://localhost:8000'
 * });
 * 
 * // Create an application
 * const app = await client.applications.create({
 *   name: 'my-app',
 *   description: 'My application'
 * });
 * 
 * // Create a configuration
 * const config = await client.configurations.create({
 *   applicationId: app.id,
 *   name: 'database',
 *   configuration: {
 *     host: 'localhost',
 *     port: 5432,
 *     database: 'myapp'
 *   }
 * });
 * 
 * // Get configuration data
 * const dbConfig = await client.getConfigByName('my-app', 'database');
 * console.log(dbConfig.host); // 'localhost'
 * ```
 */

// Export main client class
export {
  ConfigServiceClient,
  type ConfigServiceClientOptions
} from './services/index.js';

// Export service classes
export {
  ApplicationsService,
  ConfigurationsService
} from './services/index.js';

// Export HTTP client and utilities
export {
  HttpClient,
  type ClientConfig
} from './services/index.js';

// Export all model types and interfaces
export type {
  // Application types
  Application,
  CreateApplicationDTO,
  UpdateApplicationDTO,
  ListApplicationsParams,
  ListApplicationsResponse,
  
  // Configuration types
  Configuration,
  CreateConfigurationDTO,
  UpdateConfigurationDTO,
  ListConfigurationsParams,
  ListConfigurationsResponse
} from './services/index.js';

// Export error classes and types
export {
  // Error classes
  ConfigServiceClientError,
  ValidationError,
  NotFoundError,
  ConflictError,
  AuthenticationError,
  AuthorizationError,
  NetworkError,
  ServerError,
  TimeoutError,
  
  // Error utilities
  createErrorFromResponse,
  isConfigServiceClientError,
  isValidationError,
  isNotFoundError,
  isNetworkError,
  
  // Error types
  type ApiErrorResponse
} from './services/index.js';

// Export transformation utilities
export {
  transformApplication,
  serializeApplication,
  transformConfiguration,
  serializeConfiguration,
  validateConfiguration
} from './services/index.js';

// Default export for convenience
export { ConfigServiceClient as default } from './services/index.js';
