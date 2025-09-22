/**
 * Abstract base service for API communication
 * Provides common HTTP functionality and error handling
 */

export abstract class BaseService {
  protected baseUrl: string;

  constructor(baseUrl: string = '/api/v1') {
    this.baseUrl = baseUrl;
  }

  /**
   * Perform a GET request
   */
  protected async get<T>(endpoint: string): Promise<T> {
    const response = await this.makeRequest(endpoint, {
      method: 'GET'
    });
    return this.handleResponse<T>(response);
  }

  /**
   * Perform a POST request
   */
  protected async post<T>(endpoint: string, data: any): Promise<T> {
    const response = await this.makeRequest(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    return this.handleResponse<T>(response);
  }

  /**
   * Perform a PUT request
   */
  protected async put<T>(endpoint: string, data: any): Promise<T> {
    const response = await this.makeRequest(endpoint, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    return this.handleResponse<T>(response);
  }

  /**
   * Perform a DELETE request
   */
  protected async delete(endpoint: string): Promise<void> {
    const response = await this.makeRequest(endpoint, {
      method: 'DELETE'
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
  }

  /**
   * Make the actual HTTP request
   */
  private async makeRequest(endpoint: string, options: RequestInit): Promise<Response> {
    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, options);
      return response;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Network error: ${error.message}`);
      }
      throw new Error('Unknown network error');
    }
  }

  /**
   * Handle the response and extract JSON data
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;

      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      } catch {
        // If we can't parse error as JSON, use the status text
      }

      throw new Error(errorMessage);
    }

    try {
      return await response.json();
    } catch (error) {
      throw new Error('Failed to parse response as JSON');
    }
  }

  /**
   * Build query string from parameters
   */
  protected buildQueryString(params: Record<string, any>): string {
    const searchParams = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value));
      }
    });

    const queryString = searchParams.toString();
    return queryString ? `?${queryString}` : '';
  }
}