import { apiService, ApiResponse } from './api-service.js';
import { ApplicationCreate, ApplicationUpdate, ApplicationResponse, ApplicationListItem } from '../models/application.js';

export class ApplicationService {
  async getAll(limit?: number, offset?: number): Promise<ApiResponse<ApplicationResponse[]>> {
    const params: Record<string, number> = {};
    if (limit !== undefined) params.limit = limit;
    if (offset !== undefined) params.offset = offset;
    
    return apiService.get<ApplicationResponse[]>('/applications', params);
  }

  async getById(id: string): Promise<ApiResponse<ApplicationResponse>> {
    return apiService.get<ApplicationResponse>(`/applications/${id}`);
  }

  async create(data: ApplicationCreate): Promise<ApiResponse<ApplicationResponse>> {
    return apiService.post<ApplicationResponse>('/applications', data);
  }

  async update(id: string, data: ApplicationUpdate): Promise<ApiResponse<ApplicationResponse>> {
    return apiService.put<ApplicationResponse>(`/applications/${id}`, data);
  }

  async delete(id: string): Promise<ApiResponse<void>> {
    return apiService.delete(`/applications/${id}`);
  }

  transformToListItem(app: ApplicationResponse): ApplicationListItem {
    return {
      id: app.id,
      name: app.name,
      comments: app.comments,
      configurationCount: app.configuration_ids.length,
      created_at: app.created_at,
      updated_at: app.updated_at,
    };
  }

  transformToListItems(apps: ApplicationResponse[]): ApplicationListItem[] {
    return apps.map(app => this.transformToListItem(app));
  }
}

export const applicationService = new ApplicationService();
