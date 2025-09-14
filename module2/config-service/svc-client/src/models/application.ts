/**
 * Application data model and related types for the Configuration Service Client
 */

/**
 * Represents an application in the Configuration Service
 */
export interface Application {
  /** Unique identifier (ULID) */
  id: string;
  /** Application name */
  name: string;
  /** Optional application description */
  description?: string;
  /** Creation timestamp */
  createdAt: Date;
  /** Last update timestamp */
  updatedAt: Date;
}

/**
 * Data Transfer Object for creating a new application
 */
export interface CreateApplicationDTO {
  /** Application name */
  name: string;
  /** Optional application description */
  description?: string;
}

/**
 * Data Transfer Object for updating an existing application
 */
export interface UpdateApplicationDTO {
  /** Application name */
  name?: string;
  /** Optional application description */
  description?: string;
}

/**
 * Query parameters for listing applications
 */
export interface ListApplicationsParams {
  /** Maximum number of applications to return */
  limit?: number;
  /** Number of applications to skip */
  offset?: number;
}

/**
 * Response structure for paginated application lists
 */
export interface ListApplicationsResponse {
  /** Array of applications */
  applications: Application[];
  /** Total number of applications available */
  total: number;
  /** Number of applications returned */
  count: number;
  /** Offset used for this request */
  offset: number;
}

/**
 * Transforms raw API response data to Application interface
 */
export function transformApplication(data: any): Application {
  return {
    id: data.id,
    name: data.name,
    description: data.description,
    createdAt: new Date(data.created_at),
    updatedAt: new Date(data.updated_at)
  };
}

/**
 * Transforms Application data for API requests
 */
export function serializeApplication(data: CreateApplicationDTO | UpdateApplicationDTO): any {
  return {
    name: data.name,
    description: data.description
  };
}
