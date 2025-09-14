import { ConfigServiceClient, type Application, type CreateApplicationDTO, type UpdateApplicationDTO } from '@config-service/client';
import { ApplicationCreate, ApplicationUpdate, ApplicationResponse, ApplicationListItem } from '../models/application';

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

export class ApplicationService {
  private client: ConfigServiceClient;

  constructor() {
    this.client = new ConfigServiceClient({
      baseUrl: '/api'
    });
  }

  async getAll(limit?: number, offset?: number): Promise<ApiResponse<ApplicationResponse[]>> {
    try {
      const response = await this.client.applications.list({ limit, offset });
      
      // Transform the new client response to match the old interface
      const applications = response.applications.map(this.transformToResponse);
      
      return {
        data: applications,
        status: 200
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to fetch applications',
        status: 500
      };
    }
  }

  async getAllWithCounts(limit?: number, offset?: number): Promise<ApiResponse<ApplicationListItem[]>> {
    try {
      const response = await this.client.applications.list({ limit, offset });
      
      // Transform the new client response to match the old interface
      const applications = response.applications.map(this.transformToResponse);
      
      // Transform to list items with configuration counts
      const listItems = await this.transformToListItems(applications);
      
      return {
        data: listItems,
        status: 200
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to fetch applications',
        status: 500
      };
    }
  }

  async getById(id: string): Promise<ApiResponse<ApplicationResponse>> {
    try {
      const application = await this.client.applications.getById(id);
      
      return {
        data: this.transformToResponse(application),
        status: 200
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to fetch application',
        status: error instanceof Error && error.message.includes('not found') ? 404 : 500
      };
    }
  }

  async create(data: ApplicationCreate): Promise<ApiResponse<ApplicationResponse>> {
    try {
      const createData: CreateApplicationDTO = {
        name: data.name,
        description: data.comments
      };
      
      const application = await this.client.applications.create(createData);
      
      return {
        data: this.transformToResponse(application),
        status: 201
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to create application',
        status: 400
      };
    }
  }

  async update(id: string, data: ApplicationUpdate): Promise<ApiResponse<ApplicationResponse>> {
    try {
      const updateData: UpdateApplicationDTO = {
        name: data.name,
        description: data.comments
      };
      
      const application = await this.client.applications.update(id, updateData);
      
      return {
        data: this.transformToResponse(application),
        status: 200
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to update application',
        status: error instanceof Error && error.message.includes('not found') ? 404 : 400
      };
    }
  }

  async delete(id: string): Promise<ApiResponse<void>> {
    try {
      await this.client.applications.delete(id);
      
      return {
        status: 204
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to delete application',
        status: error instanceof Error && error.message.includes('not found') ? 404 : 500
      };
    }
  }

  // Transform new client Application to old ApplicationResponse format
  private transformToResponse(app: Application): ApplicationResponse {
    return {
      id: app.id,
      name: app.name,
      comments: app.description || '',
      configuration_ids: [], // This would need to be populated separately if needed
      created_at: app.createdAt.toISOString(),
      updated_at: app.updatedAt.toISOString()
    };
  }

  async transformToListItem(app: ApplicationResponse): Promise<ApplicationListItem> {
    // Get configuration count for this application
    let configurationCount = 0;
    try {
      const configurations = await this.client.applications.getConfigurations(app.id);
      configurationCount = configurations.length;
    } catch (error) {
      // If we can't get configurations, default to 0
      configurationCount = 0;
    }

    return {
      id: app.id,
      name: app.name,
      comments: app.comments || '',
      configurationCount,
      created_at: app.created_at,
      updated_at: app.updated_at,
    };
  }

  async transformToListItems(apps: ApplicationResponse[]): Promise<ApplicationListItem[]> {
    const transformPromises = apps.map(app => this.transformToListItem(app));
    return Promise.all(transformPromises);
  }
}

export const applicationService = new ApplicationService();
