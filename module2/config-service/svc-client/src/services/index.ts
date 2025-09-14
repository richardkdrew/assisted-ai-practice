/**
 * Main Configuration Service Client
 */

import { HttpClient, type ClientConfig } from '../utils/http-client.js';
import { ApplicationsService } from './applications-service.js';
import { ConfigurationsService } from './configurations-service.js';

/**
 * Configuration options for the Configuration Service Client
 */
export interface ConfigServiceClientOptions extends ClientConfig {
  /** API version to use (default: 'v1') */
  apiVersion?: string;
}

/**
 * Main client class for the Configuration Service
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
 *     port: 5432
 *   }
 * });
 * ```
 */
export class ConfigServiceClient {
  private readonly httpClient: HttpClient;
  
  /** Applications service for managing applications */
  public readonly applications: ApplicationsService;
  
  /** Configurations service for managing configurations */
  public readonly configurations: ConfigurationsService;

  /**
   * Creates a new Configuration Service Client instance
   * @param options - Client configuration options
   */
  constructor(options: ConfigServiceClientOptions) {
    // Remove trailing slash from base URL
    const baseUrl = options.baseUrl.replace(/\/$/, '');
    
    // Create HTTP client with base URL (API version is handled in service paths)
    this.httpClient = new HttpClient({
      ...options,
      baseUrl: baseUrl
    });

    // Initialize services
    this.applications = new ApplicationsService(this.httpClient);
    this.configurations = new ConfigurationsService(this.httpClient);
  }

  /**
   * Tests the connection to the Configuration Service
   * @returns Promise resolving to service information
   */
  async healthCheck(): Promise<{ status: string; version?: string; timestamp?: string; error?: string }> {
    try {
      const response = await this.httpClient.get<any>('/health');
      return {
        status: 'healthy',
        ...response
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Gets service information
   * @returns Promise resolving to service information
   */
  async getServiceInfo(): Promise<Record<string, unknown>> {
    try {
      return await this.httpClient.get<Record<string, unknown>>('/');
    } catch (error) {
      throw error;
    }
  }

  /**
   * Gets the current client configuration
   */
  getConfig(): Readonly<ClientConfig> {
    return this.httpClient.getConfig();
  }

  /**
   * Creates a new client instance with updated configuration
   * @param updates - Configuration updates
   * @returns New client instance
   */
  withConfig(updates: Partial<ConfigServiceClientOptions>): ConfigServiceClient {
    const currentConfig = this.getConfig();
    return new ConfigServiceClient({
      ...currentConfig,
      ...updates
    });
  }

  /**
   * Convenience method to get configuration data by application and configuration name
   * @param applicationName - Application name
   * @param configurationName - Configuration name
   * @returns Promise resolving to configuration data
   */
  async getConfigByName(
    applicationName: string,
    configurationName: string
  ): Promise<Record<string, unknown>> {
    // Find application by name
    const appsResponse = await this.applications.searchByName(applicationName);
    const app = appsResponse.applications.find(a => a.name === applicationName);
    
    if (!app) {
      throw new Error(`Application '${applicationName}' not found`);
    }

    // Get configuration data
    return await this.configurations.getConfigurationDataByName(app.id, configurationName);
  }

  /**
   * Convenience method to create an application with initial configurations
   * @param applicationData - Application data
   * @param initialConfigurations - Initial configurations to create
   * @returns Promise resolving to created application and configurations
   */
  async createApplicationWithConfigurations(
    applicationData: { name: string; description?: string },
    initialConfigurations: Array<{
      name: string;
      configuration: Record<string, unknown>;
      comment?: string;
    }>
  ): Promise<{
    application: any;
    configurations: any[];
  }> {
    // Create application
    const application = await this.applications.create(applicationData);

    // Create configurations
    const configurations = [];
    for (const configData of initialConfigurations) {
      const config = await this.configurations.create({
        applicationId: application.id,
        name: configData.name,
        configuration: configData.configuration,
        comment: configData.comment
      });
      configurations.push(config);
    }

    return {
      application,
      configurations
    };
  }

  /**
   * Convenience method to get all data for an application (including configurations)
   * @param applicationId - Application ID
   * @returns Promise resolving to application with its configurations
   */
  async getApplicationWithConfigurations(applicationId: string): Promise<{
    application: any;
    configurations: any[];
  }> {
    const [application, configurations] = await Promise.all([
      this.applications.getById(applicationId),
      this.configurations.getByApplicationId(applicationId)
    ]);

    return {
      application,
      configurations
    };
  }

  /**
   * Convenience method to delete an application and all its configurations
   * @param applicationId - Application ID
   * @returns Promise resolving when deletion is complete
   */
  async deleteApplicationWithConfigurations(applicationId: string): Promise<void> {
    // Get all configurations for the application
    const configurations = await this.configurations.getByApplicationId(applicationId);

    // Delete all configurations first
    await Promise.all(
      configurations.map(config => this.configurations.delete(config.id))
    );

    // Delete the application
    await this.applications.delete(applicationId);
  }
}

// Re-export types and utilities for convenience
export type { ClientConfig };
export { ApplicationsService } from './applications-service.js';
export { ConfigurationsService } from './configurations-service.js';

// Re-export models
export * from '../models/application.js';
export * from '../models/configuration.js';
export * from '../models/errors.js';

// Re-export utilities
export { HttpClient } from '../utils/http-client.js';
