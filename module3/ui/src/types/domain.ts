/**
 * Domain models matching the Configuration Service API
 */

export interface Application {
  id: string;
  name: string;
  comments?: string;
  created_at: string;
  updated_at: string;
  configuration_ids: string[];
}

export interface ApplicationCreate {
  name: string;
  comments?: string;
}

export interface ApplicationUpdate {
  name?: string;
  comments?: string;
}

export interface Configuration {
  id: string;
  application_id: string;
  name: string;
  comments?: string;
  config: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface ConfigurationCreate {
  application_id: string;
  name: string;
  comments?: string;
  config: Record<string, any>;
}

export interface ConfigurationUpdate {
  name?: string;
  comments?: string;
  application_id?: string;
  config?: Record<string, any>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface PaginationParams {
  limit?: number;
  offset?: number;
}