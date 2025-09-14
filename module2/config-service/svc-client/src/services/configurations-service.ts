/**
 * Configurations service for the Configuration Service Client
 */

import { BaseService } from './base-service.js';
import {
  type Configuration,
  type CreateConfigurationDTO,
  type UpdateConfigurationDTO,
  type ListConfigurationsParams,
  type ListConfigurationsResponse,
  transformConfiguration,
  serializeConfiguration,
  validateConfiguration
} from '../models/configuration.js';

/**
 * Service for managing configurations in the Configuration Service
 */
export class ConfigurationsService extends BaseService {
  private readonly basePath = '/v1/configurations';

  /**
   * Creates a new configuration
   * @param data - Configuration data
   * @returns Promise resolving to the created configuration
   */
  async create(data: CreateConfigurationDTO): Promise<Configuration> {
    return this.safeExecute(async () => {
      // Validate input
      this.validateULID(data.applicationId, 'applicationId');
      this.validateNonEmptyString(data.name, 'name');
      this.validateRequired(data.configuration, 'configuration');

      // Validate configuration structure
      if (!validateConfiguration(data.configuration)) {
        throw new Error('Configuration must be a valid object');
      }

      // Serialize data for API
      const serializedData = serializeConfiguration(data);

      // Make API request
      const response = await this.httpClient.post<any>(this.basePath, serializedData);

      // Transform and return response
      return transformConfiguration(response);
    }, 'Failed to create configuration');
  }

  /**
   * Retrieves a configuration by ID
   * @param id - Configuration ID (ULID)
   * @returns Promise resolving to the configuration
   */
  async getById(id: string): Promise<Configuration> {
    return this.safeExecute(async () => {
      // Validate input
      this.validateULID(id, 'id');

      // Make API request
      const response = await this.httpClient.get<any>(`${this.basePath}/${id}`);

      // Transform and return response
      return transformConfiguration(response);
    }, `Failed to get configuration with id '${id}'`);
  }

  /**
   * Updates an existing configuration
   * @param id - Configuration ID (ULID)
   * @param data - Updated configuration data
   * @returns Promise resolving to the updated configuration
   */
  async update(id: string, data: UpdateConfigurationDTO): Promise<Configuration> {
    return this.safeExecute(async () => {
      // Validate input
      this.validateULID(id, 'id');
      
      if (data.name !== undefined) {
        this.validateNonEmptyString(data.name, 'name');
      }

      if (data.configuration !== undefined) {
        if (!validateConfiguration(data.configuration)) {
          throw new Error('Configuration must be a valid object');
        }
      }

      // Serialize data for API
      const serializedData = serializeConfiguration(data);

      // Make API request
      const response = await this.httpClient.put<any>(`${this.basePath}/${id}`, serializedData);

      // Transform and return response
      return transformConfiguration(response);
    }, `Failed to update configuration with id '${id}'`);
  }

  /**
   * Deletes a configuration
   * @param id - Configuration ID (ULID)
   * @returns Promise resolving when deletion is complete
   */
  async delete(id: string): Promise<void> {
    return this.safeExecute(async () => {
      // Validate input
      this.validateULID(id, 'id');

      // Make API request
      await this.httpClient.delete<void>(`${this.basePath}/${id}`);
    }, `Failed to delete configuration with id '${id}'`);
  }

  /**
   * Lists configurations with optional pagination and filtering
   * @param params - Query parameters for filtering and pagination
   * @returns Promise resolving to paginated list of configurations
   */
  async list(params?: ListConfigurationsParams): Promise<ListConfigurationsResponse> {
    return this.safeExecute(async () => {
      // Validate pagination parameters
      const validatedParams = this.validatePaginationParams(params?.limit, params?.offset);

      // Add application filter if provided
      const queryParams: Record<string, unknown> = { ...validatedParams };
      if (params?.applicationId) {
        this.validateULID(params.applicationId, 'applicationId');
        queryParams.application_id = params.applicationId;
      }

      // Make API request
      const response = await this.httpClient.get<any>(this.basePath, {
        params: queryParams
      });

      // Handle different response formats
      if (Array.isArray(response)) {
        // Simple array response
        return {
          configurations: response.map(transformConfiguration),
          total: response.length,
          count: response.length,
          offset: 0
        };
      }

      // Paginated response
      return {
        configurations: (response.configurations || response.items || []).map(transformConfiguration),
        total: response.total || response.configurations?.length || 0,
        count: response.count || response.configurations?.length || 0,
        offset: response.offset || 0
      };
    }, 'Failed to list configurations');
  }

  /**
   * Gets all configurations for a specific application
   * @param applicationId - Application ID (ULID)
   * @param params - Query parameters for pagination
   * @returns Promise resolving to list of configurations
   */
  async getByApplicationId(
    applicationId: string,
    params?: { limit?: number; offset?: number }
  ): Promise<Configuration[]> {
    return this.safeExecute(async () => {
      // Use the list method with application filter
      const response = await this.list({
        ...params,
        applicationId
      });

      return response.configurations;
    }, `Failed to get configurations for application with id '${applicationId}'`);
  }

  /**
   * Gets a specific configuration by name within an application
   * @param applicationId - Application ID (ULID)
   * @param configurationName - Configuration name
   * @returns Promise resolving to the configuration
   */
  async getByName(applicationId: string, configurationName: string): Promise<Configuration> {
    return this.safeExecute(async () => {
      // Validate input
      this.validateULID(applicationId, 'applicationId');
      this.validateNonEmptyString(configurationName, 'configurationName');

      // Get all configurations for the application
      const configurations = await this.getByApplicationId(applicationId);

      // Find configuration by name
      const configuration = configurations.find(config => config.name === configurationName);

      if (!configuration) {
        throw new Error(`Configuration '${configurationName}' not found in application '${applicationId}'`);
      }

      return configuration;
    }, `Failed to get configuration '${configurationName}' for application '${applicationId}'`);
  }

  /**
   * Checks if a configuration exists
   * @param id - Configuration ID (ULID)
   * @returns Promise resolving to boolean indicating existence
   */
  async exists(id: string): Promise<boolean> {
    try {
      await this.getById(id);
      return true;
    } catch (error) {
      // If it's a not found error, return false
      if (error instanceof Error && error.message.includes('not found')) {
        return false;
      }
      // Re-throw other errors
      throw error;
    }
  }

  /**
   * Checks if a configuration with a specific name exists in an application
   * @param applicationId - Application ID (ULID)
   * @param configurationName - Configuration name
   * @returns Promise resolving to boolean indicating existence
   */
  async existsByName(applicationId: string, configurationName: string): Promise<boolean> {
    try {
      await this.getByName(applicationId, configurationName);
      return true;
    } catch (error) {
      // If it's a not found error, return false
      if (error instanceof Error && error.message.includes('not found')) {
        return false;
      }
      // Re-throw other errors
      throw error;
    }
  }

  /**
   * Searches configurations by name (case-insensitive partial match)
   * Note: This is a client-side implementation. For better performance,
   * the API should support server-side search.
   * @param searchTerm - Search term to match against configuration names
   * @param params - Query parameters for filtering and pagination
   * @returns Promise resolving to matching configurations
   */
  async searchByName(
    searchTerm: string,
    params?: ListConfigurationsParams
  ): Promise<ListConfigurationsResponse> {
    return this.safeExecute(async () => {
      // Validate input
      this.validateNonEmptyString(searchTerm, 'searchTerm');

      // Get all configurations (this could be optimized with server-side search)
      const allConfigurations = await this.list(params);

      // Filter configurations by name (case-insensitive)
      const searchTermLower = searchTerm.toLowerCase();
      const filteredConfigurations = allConfigurations.configurations.filter(config =>
        config.name.toLowerCase().includes(searchTermLower) ||
        (config.comment && config.comment.toLowerCase().includes(searchTermLower))
      );

      return {
        configurations: filteredConfigurations,
        total: filteredConfigurations.length,
        count: filteredConfigurations.length,
        offset: allConfigurations.offset
      };
    }, `Failed to search configurations by name '${searchTerm}'`);
  }

  /**
   * Gets the raw configuration data (without metadata) for a configuration
   * @param id - Configuration ID (ULID)
   * @returns Promise resolving to the configuration data
   */
  async getConfigurationData(id: string): Promise<Record<string, unknown>> {
    return this.safeExecute(async () => {
      const configuration = await this.getById(id);
      return configuration.configuration;
    }, `Failed to get configuration data for id '${id}'`);
  }

  /**
   * Gets the raw configuration data by name within an application
   * @param applicationId - Application ID (ULID)
   * @param configurationName - Configuration name
   * @returns Promise resolving to the configuration data
   */
  async getConfigurationDataByName(
    applicationId: string,
    configurationName: string
  ): Promise<Record<string, unknown>> {
    return this.safeExecute(async () => {
      const configuration = await this.getByName(applicationId, configurationName);
      return configuration.configuration;
    }, `Failed to get configuration data for '${configurationName}' in application '${applicationId}'`);
  }

  /**
   * Updates only the configuration data (not metadata) for a configuration
   * @param id - Configuration ID (ULID)
   * @param configurationData - New configuration data
   * @returns Promise resolving to the updated configuration
   */
  async updateConfigurationData(
    id: string,
    configurationData: Record<string, unknown>
  ): Promise<Configuration> {
    return this.safeExecute(async () => {
      return this.update(id, { configuration: configurationData });
    }, `Failed to update configuration data for id '${id}'`);
  }
}
