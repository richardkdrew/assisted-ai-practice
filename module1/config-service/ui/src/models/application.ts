export interface ApplicationCreate {
  name: string;
  comments?: string;
}

export interface ApplicationUpdate {
  name?: string;
  comments?: string;
}

export interface ApplicationResponse {
  id: string;
  name: string;
  comments?: string;
  configuration_ids: string[];
  created_at: string;
  updated_at: string;
}

export interface ApplicationListItem {
  id: string;
  name: string;
  comments?: string;
  configurationCount: number;
  created_at: string;
  updated_at: string;
}
