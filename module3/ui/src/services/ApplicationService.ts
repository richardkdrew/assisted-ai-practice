/**
 * Service for managing applications via the Configuration Service API
 */

import { BaseService } from './BaseService';
import type {
  Application,
  ApplicationCreate,
  ApplicationUpdate,
  PaginatedResponse,
  PaginationParams
} from '@/types/domain';

export class ApplicationService extends BaseService {
  /**
   * Get all applications with pagination
   */
  async getApplications(params: PaginationParams = {}): Promise<PaginatedResponse<Application>> {
    const queryString = this.buildQueryString(params);
    return this.get<PaginatedResponse<Application>>(`/applications${queryString}`);
  }

  /**
   * Get a single application by ID
   */
  async getApplication(id: string): Promise<Application> {
    return this.get<Application>(`/applications/${id}`);
  }

  /**
   * Create a new application
   */
  async createApplication(data: ApplicationCreate): Promise<Application> {
    return this.post<Application>('/applications/', data);
  }

  /**
   * Update an existing application
   */
  async updateApplication(id: string, data: ApplicationUpdate): Promise<Application> {
    return this.put<Application>(`/applications/${id}`, data);
  }

  /**
   * Delete an application
   */
  async deleteApplication(id: string): Promise<void> {
    return this.delete(`/applications/${id}`);
  }
}

// Create singleton instance
export const applicationService = new ApplicationService();