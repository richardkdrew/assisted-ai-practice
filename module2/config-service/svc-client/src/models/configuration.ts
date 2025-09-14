/**
 * Configuration data model and related types for the Configuration Service Client
 */

/**
 * Represents a configuration in the Configuration Service
 */
export interface Configuration {
  /** Unique identifier (ULID) */
  id: string;
  /** ID of the application this configuration belongs to */
  applicationId: string;
  /** Configuration name (unique within application scope) */
  name: string;
  /** Configuration data as key-value pairs */
  configuration: Record<string, unknown>;
  /** Optional comment describing the configuration */
  comment?: string;
  /** Creation timestamp */
  createdAt: Date;
  /** Last update timestamp */
  updatedAt: Date;
}

/**
 * Data Transfer Object for creating a new configuration
 */
export interface CreateConfigurationDTO {
  /** ID of the application this configuration belongs to */
  applicationId: string;
  /** Configuration name (unique within application scope) */
  name: string;
  /** Configuration data as key-value pairs */
  configuration: Record<string, unknown>;
  /** Optional comment describing the configuration */
  comment?: string;
}

/**
 * Data Transfer Object for updating an existing configuration
 */
export interface UpdateConfigurationDTO {
  /** Configuration name (unique within application scope) */
  name?: string;
  /** Configuration data as key-value pairs */
  configuration?: Record<string, unknown>;
  /** Optional comment describing the configuration */
  comment?: string;
}

/**
 * Query parameters for listing configurations
 */
export interface ListConfigurationsParams {
  /** Maximum number of configurations to return */
  limit?: number;
  /** Number of configurations to skip */
  offset?: number;
  /** Filter by application ID */
  applicationId?: string;
}

/**
 * Response structure for paginated configuration lists
 */
export interface ListConfigurationsResponse {
  /** Array of configurations */
  configurations: Configuration[];
  /** Total number of configurations available */
  total: number;
  /** Number of configurations returned */
  count: number;
  /** Offset used for this request */
  offset: number;
}

/**
 * Transforms raw API response data to Configuration interface
 */
export function transformConfiguration(data: any): Configuration {
  return {
    id: data.id,
    applicationId: data.application_id,
    name: data.name,
    configuration: data.config,  // Map 'config' to 'configuration'
    comment: data.comments,      // Map 'comments' to 'comment'
    createdAt: new Date(data.created_at),
    updatedAt: new Date(data.updated_at)
  };
}

/**
 * Transforms Configuration data for API requests
 */
export function serializeConfiguration(data: CreateConfigurationDTO | UpdateConfigurationDTO): any {
  const serialized: any = {};
  
  if ('applicationId' in data) {
    serialized.application_id = data.applicationId;
  }
  
  if (data.name !== undefined) {
    serialized.name = data.name;
  }
  
  if (data.configuration !== undefined) {
    serialized.config = data.configuration;  // Map 'configuration' to 'config'
  }
  
  if (data.comment !== undefined) {
    serialized.comments = data.comment;  // Map 'comment' to 'comments'
  }
  
  return serialized;
}

/**
 * Validates configuration data structure
 */
export function validateConfiguration(configuration: Record<string, unknown>): boolean {
  // Basic validation - ensure it's a valid object
  if (typeof configuration !== 'object' || configuration === null || Array.isArray(configuration)) {
    return false;
  }
  
  // Additional validation can be added here
  return true;
}
