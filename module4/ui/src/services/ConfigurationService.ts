/**
 * Service for managing configurations via the Configuration Service API
 */

import { BaseService } from './BaseService';
import type {
  Configuration,
  ConfigurationCreate,
  ConfigurationUpdate,
  PaginatedResponse,
  PaginationParams
} from '@/types/domain';

export interface ConfigurationListParams extends PaginationParams {
  application_id?: string;
}

export class ConfigurationService extends BaseService {
  /**
   * Get all configurations with optional filtering by application
   */
  async getConfigurations(params: ConfigurationListParams = {}): Promise<PaginatedResponse<Configuration>> {
    const queryString = this.buildQueryString(params);
    return this.get<PaginatedResponse<Configuration>>(`/configurations${queryString}`);
  }

  /**
   * Get a single configuration by ID
   */
  async getConfiguration(id: string): Promise<Configuration> {
    return this.get<Configuration>(`/configurations/${id}`);
  }

  /**
   * Create a new configuration
   */
  async createConfiguration(data: ConfigurationCreate): Promise<Configuration> {
    return this.post<Configuration>('/configurations/', data);
  }

  /**
   * Update an existing configuration
   */
  async updateConfiguration(id: string, data: ConfigurationUpdate): Promise<Configuration> {
    return this.put<Configuration>(`/configurations/${id}`, data);
  }

  /**
   * Delete a configuration
   */
  async deleteConfiguration(id: string): Promise<void> {
    return this.delete(`/configurations/${id}`);
  }
}

// Create singleton instance
export const configurationService = new ConfigurationService();