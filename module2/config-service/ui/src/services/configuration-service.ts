import { apiService, ApiResponse } from './api-service';
import { ConfigurationCreate, ConfigurationUpdate, ConfigurationResponse, ConfigurationListItem } from '../models/configuration';

export class ConfigurationService {
  async getAll(limit?: number, offset?: number): Promise<ApiResponse<ConfigurationResponse[]>> {
    const params: Record<string, number> = {};
    if (limit !== undefined) params.limit = limit;
    if (offset !== undefined) params.offset = offset;
    
    return apiService.get<ConfigurationResponse[]>('/configurations', params);
  }

  async getByApplicationId(applicationId: string, limit?: number, offset?: number): Promise<ApiResponse<ConfigurationResponse[]>> {
    const params: Record<string, number> = {};
    if (limit !== undefined) params.limit = limit;
    if (offset !== undefined) params.offset = offset;
    
    return apiService.get<ConfigurationResponse[]>(`/applications/${applicationId}/configurations`, params);
  }

  async getById(id: string): Promise<ApiResponse<ConfigurationResponse>> {
    return apiService.get<ConfigurationResponse>(`/configurations/${id}`);
  }

  async create(data: ConfigurationCreate): Promise<ApiResponse<ConfigurationResponse>> {
    return apiService.post<ConfigurationResponse>('/configurations', data);
  }

  async update(id: string, data: ConfigurationUpdate): Promise<ApiResponse<ConfigurationResponse>> {
    return apiService.put<ConfigurationResponse>(`/configurations/${id}`, data);
  }

  async delete(id: string): Promise<ApiResponse<void>> {
    return apiService.delete(`/configurations/${id}`);
  }

  transformToListItem(config: ConfigurationResponse): ConfigurationListItem {
    return {
      id: config.id,
      application_id: config.application_id,
      name: config.name,
      comments: config.comments,
      configKeyCount: Object.keys(config.config).length,
      created_at: config.created_at,
      updated_at: config.updated_at,
    };
  }

  transformToListItems(configs: ConfigurationResponse[]): ConfigurationListItem[] {
    return configs.map(config => this.transformToListItem(config));
  }
}

export const configurationService = new ConfigurationService();
