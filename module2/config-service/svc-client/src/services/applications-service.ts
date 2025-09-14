/**
 * Applications service for the Configuration Service Client
 */

import { BaseService } from './base-service.js';
import {
  type Application,
  type CreateApplicationDTO,
  type UpdateApplicationDTO,
  type ListApplicationsParams,
  type ListApplicationsResponse,
  transformApplication,
  serializeApplication
} from '../models/application.js';
import { type Configuration, transformConfiguration } from '../models/configuration.js';

/**
 * Service for managing applications in the Configuration Service
 */
export class ApplicationsService extends BaseService {
  private readonly basePath = '/v1/applications';

  /**
   * Creates a new application
   * @param data - Application data
   * @returns Promise resolving to the created application
   */
  async create(data: CreateApplicationDTO): Promise<Application> {
    return this.safeExecute(async () => {
      // Validate input
      this.validateNonEmptyString(data.name, 'name');

      // Serialize data for API
      const serializedData = serializeApplication(data);

      // Make API request
      const response = await this.httpClient.post<any>(this.basePath, serializedData);

      // Transform and return response
      return transformApplication(response);
    }, 'Failed to create application');
  }

  /**
   * Retrieves an application by ID
   * @param id - Application ID (ULID)
   * @returns Promise resolving to the application
   */
  async getById(id: string): Promise<Application> {
    return this.safeExecute(async () => {
      // Validate input
      this.validateULID(id, 'id');

      // Make API request
      const response = await this.httpClient.get<any>(`${this.basePath}/${id}`);

      // Transform and return response
      return transformApplication(response);
    }, `Failed to get application with id '${id}'`);
  }

  /**
   * Updates an existing application
   * @param id - Application ID (ULID)
   * @param data - Updated application data
   * @returns Promise resolving to the updated application
   */
  async update(id: string, data: UpdateApplicationDTO): Promise<Application> {
    return this.safeExecute(async () => {
      // Validate input
      this.validateULID(id, 'id');
      
      if (data.name !== undefined) {
        this.validateNonEmptyString(data.name, 'name');
      }

      // Serialize data for API
      const serializedData = serializeApplication(data);

      // Make API request
      const response = await this.httpClient.put<any>(`${this.basePath}/${id}`, serializedData);

      // Transform and return response
      return transformApplication(response);
    }, `Failed to update application with id '${id}'`);
  }

  /**
   * Deletes an application
   * @param id - Application ID (ULID)
   * @returns Promise resolving when deletion is complete
   */
  async delete(id: string): Promise<void> {
    return this.safeExecute(async () => {
      // Validate input
      this.validateULID(id, 'id');

      // Make API request
      await this.httpClient.delete<void>(`${this.basePath}/${id}`);
    }, `Failed to delete application with id '${id}'`);
  }

  /**
   * Lists applications with optional pagination
   * @param params - Query parameters for filtering and pagination
   * @returns Promise resolving to paginated list of applications
   */
  async list(params?: ListApplicationsParams): Promise<ListApplicationsResponse> {
    return this.safeExecute(async () => {
      // Validate pagination parameters
      const validatedParams = this.validatePaginationParams(params?.limit, params?.offset);

      // Make API request
      const response = await this.httpClient.get<any>(this.basePath, {
        params: validatedParams
      });

      // Handle different response formats
      if (Array.isArray(response)) {
        // Simple array response
        return {
          applications: response.map(transformApplication),
          total: response.length,
          count: response.length,
          offset: 0
        };
      }

      // Paginated response
      return {
        applications: (response.applications || response.items || []).map(transformApplication),
        total: response.total || response.applications?.length || 0,
        count: response.count || response.applications?.length || 0,
        offset: response.offset || 0
      };
    }, 'Failed to list applications');
  }

  /**
   * Gets all configurations for a specific application
   * @param applicationId - Application ID (ULID)
   * @param params - Query parameters for pagination
   * @returns Promise resolving to list of configurations
   */
  async getConfigurations(
    applicationId: string,
    params?: { limit?: number; offset?: number }
  ): Promise<Configuration[]> {
    return this.safeExecute(async () => {
      // Validate input
      this.validateULID(applicationId, 'applicationId');
      
      // Validate pagination parameters
      const validatedParams = this.validatePaginationParams(params?.limit, params?.offset);

      // Make API request
      const response = await this.httpClient.get<any>(
        `${this.basePath}/${applicationId}/configurations`,
        { params: validatedParams }
      );

      // Handle different response formats
      if (Array.isArray(response)) {
        return response.map(transformConfiguration);
      }

      // Extract configurations from paginated response
      const configurations = response.configurations || response.items || [];
      return configurations.map(transformConfiguration);
    }, `Failed to get configurations for application with id '${applicationId}'`);
  }

  /**
   * Checks if an application exists
   * @param id - Application ID (ULID)
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
   * Searches applications by name (case-insensitive partial match)
   * Note: This is a client-side implementation. For better performance,
   * the API should support server-side search.
   * @param searchTerm - Search term to match against application names
   * @param params - Query parameters for pagination
   * @returns Promise resolving to matching applications
   */
  async searchByName(
    searchTerm: string,
    params?: ListApplicationsParams
  ): Promise<ListApplicationsResponse> {
    return this.safeExecute(async () => {
      // Validate input
      this.validateNonEmptyString(searchTerm, 'searchTerm');

      // Get all applications (this could be optimized with server-side search)
      const allApplications = await this.list(params);

      // Filter applications by name (case-insensitive)
      const searchTermLower = searchTerm.toLowerCase();
      const filteredApplications = allApplications.applications.filter(app =>
        app.name.toLowerCase().includes(searchTermLower) ||
        (app.description && app.description.toLowerCase().includes(searchTermLower))
      );

      return {
        applications: filteredApplications,
        total: filteredApplications.length,
        count: filteredApplications.length,
        offset: allApplications.offset
      };
    }, `Failed to search applications by name '${searchTerm}'`);
  }
}
