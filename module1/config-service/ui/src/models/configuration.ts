export interface ConfigurationCreate {
  application_id: string;
  name: string;
  comments?: string;
  config: Record<string, any>;
}

export interface ConfigurationUpdate {
  name?: string;
  comments?: string;
  config?: Record<string, any>;
}

export interface ConfigurationResponse {
  id: string;
  application_id: string;
  name: string;
  comments?: string;
  config: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface ConfigurationListItem {
  id: string;
  application_id: string;
  name: string;
  comments?: string;
  configKeyCount: number;
  created_at: string;
  updated_at: string;
}

export interface ConfigKeyValue {
  key: string;
  value: any;
  type: 'string' | 'number' | 'boolean' | 'object';
}
