import { ConfigServiceClient, type Configuration, type CreateConfigurationDTO, type UpdateConfigurationDTO } from '@config-service/client';
import { ConfigurationCreate, ConfigurationUpdate, ConfigurationResponse, ConfigurationListItem } from '../models/configuration';

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

export class ConfigurationService {
  private client: ConfigServiceClient;

  constructor() {
    this.client = new ConfigServiceClient({
      baseUrl: '/api'
    });
  }

  async getAll(limit?: number, offset?: number): Promise<ApiResponse<ConfigurationResponse[]>> {
    try {
      const response = await this.client.configurations.list({ limit, offset });
      
      // Transform the new client response to match the old interface
      const configurations = response.configurations.map(this.transformToResponse);
      
      return {
        data: configurations,
        status: 200
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to fetch configurations',
        status: 500
      };
    }
  }

  async getByApplicationId(applicationId: string, limit?: number, offset?: number): Promise<ApiResponse<ConfigurationResponse[]>> {
    try {
      const configurations = await this.client.configurations.getByApplicationId(applicationId, { limit, offset });
      
      // Transform the new client response to match the old interface
      const transformedConfigurations = configurations.map(this.transformToResponse);
      
      return {
        data: transformedConfigurations,
        status: 200
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to fetch configurations for application',
        status: 500
      };
    }
  }

  async getById(id: string): Promise<ApiResponse<ConfigurationResponse>> {
    try {
      const configuration = await this.client.configurations.getById(id);
      
      return {
        data: this.transformToResponse(configuration),
        status: 200
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to fetch configuration',
        status: error instanceof Error && error.message.includes('not found') ? 404 : 500
      };
    }
  }

  async create(data: ConfigurationCreate): Promise<ApiResponse<ConfigurationResponse>> {
    try {
      const createData: CreateConfigurationDTO = {
        applicationId: data.application_id,
        name: data.name,
        configuration: data.config,
        comment: data.comments
      };
      
      const configuration = await this.client.configurations.create(createData);
      
      return {
        data: this.transformToResponse(configuration),
        status: 201
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to create configuration',
        status: 400
      };
    }
  }

  async update(id: string, data: ConfigurationUpdate): Promise<ApiResponse<ConfigurationResponse>> {
    try {
      const updateData: UpdateConfigurationDTO = {
        name: data.name,
        configuration: data.config,
        comment: data.comments
      };
      
      const configuration = await this.client.configurations.update(id, updateData);
      
      return {
        data: this.transformToResponse(configuration),
        status: 200
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to update configuration',
        status: error instanceof Error && error.message.includes('not found') ? 404 : 400
      };
    }
  }

  async delete(id: string): Promise<ApiResponse<void>> {
    try {
      await this.client.configurations.delete(id);
      
      return {
        status: 204
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to delete configuration',
        status: error instanceof Error && error.message.includes('not found') ? 404 : 500
      };
    }
  }

  // Transform new client Configuration to old ConfigurationResponse format
  private transformToResponse(config: Configuration): ConfigurationResponse {
    return {
      id: config.id,
      application_id: config.applicationId,
      name: config.name,
      comments: config.comment || '',
      config: config.configuration || {},
      created_at: config.createdAt.toISOString(),
      updated_at: config.updatedAt.toISOString()
    };
  }

  transformToListItem(config: ConfigurationResponse): ConfigurationListItem {
    // Ensure config.config is properly handled
    const configData = config.config || {};
    const configKeyCount = configData && typeof configData === 'object' && !Array.isArray(configData)
      ? Object.keys(configData).length 
      : 0;

    return {
      id: config.id,
      application_id: config.application_id,
      name: config.name,
      comments: config.comments || '',
      configKeyCount,
      created_at: config.created_at,
      updated_at: config.updated_at,
    };
  }

  transformToListItems(configs: ConfigurationResponse[]): ConfigurationListItem[] {
    return configs.map(config => this.transformToListItem(config));
  }
}

export const configurationService = new ConfigurationService();
