/**
 * HTTP client utility for the Configuration Service Client
 */

import {
  ConfigServiceClientError,
  NetworkError,
  TimeoutError,
  createErrorFromResponse,
  type ApiErrorResponse
} from '../models/errors.js';

/**
 * Configuration options for the HTTP client
 */
export interface ClientConfig {
  /** Base URL for the Configuration Service API */
  baseUrl: string;
  /** Request timeout in milliseconds (default: 30000) */
  timeout?: number;
  /** Default headers to include with all requests */
  headers?: Record<string, string>;
  /** Custom fetch implementation (useful for testing) */
  fetch?: typeof fetch;
}

/**
 * HTTP request options
 */
export interface RequestOptions {
  /** Additional headers for this request */
  headers?: Record<string, string>;
  /** Request timeout override */
  timeout?: number;
  /** Query parameters */
  params?: Record<string, unknown>;
}

/**
 * HTTP client for making requests to the Configuration Service API
 */
export class HttpClient {
  private readonly config: Required<ClientConfig>;

  constructor(config: ClientConfig) {
    const fetchImpl = config.fetch ?? this.getDefaultFetch();
    
    if (!fetchImpl) {
      throw new ConfigServiceClientError(
        'FETCH_NOT_AVAILABLE',
        'fetch is not available. Please provide a fetch implementation or use in an environment that supports fetch.'
      );
    }

    this.config = {
      baseUrl: config.baseUrl.replace(/\/$/, ''), // Remove trailing slash
      timeout: config.timeout ?? 30000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...config.headers
      },
      fetch: fetchImpl
    };
  }

  /**
   * Gets the default fetch implementation, properly bound to the correct context
   */
  private getDefaultFetch(): typeof fetch | undefined {
    // Try different ways to get fetch, ensuring proper binding
    if (typeof window !== 'undefined' && window.fetch) {
      return window.fetch.bind(window);
    }
    
    if (typeof globalThis !== 'undefined' && globalThis.fetch) {
      return globalThis.fetch.bind(globalThis);
    }
    
    if (typeof global !== 'undefined' && (global as any).fetch) {
      return (global as any).fetch;
    }
    
    if (typeof fetch !== 'undefined') {
      return fetch;
    }
    
    return undefined;
  }

  /**
   * Makes a GET request
   */
  async get<T>(path: string, options?: RequestOptions): Promise<T> {
    const url = this.buildUrl(path, options?.params);
    return this.request<T>(url, {
      method: 'GET',
      headers: this.mergeHeaders(options?.headers),
      signal: this.createAbortSignal(options?.timeout)
    });
  }

  /**
   * Makes a POST request
   */
  async post<T>(path: string, data?: unknown, options?: RequestOptions): Promise<T> {
    const url = this.buildUrl(path);
    return this.request<T>(url, {
      method: 'POST',
      headers: this.mergeHeaders(options?.headers),
      body: data ? JSON.stringify(data) : undefined,
      signal: this.createAbortSignal(options?.timeout)
    });
  }

  /**
   * Makes a PUT request
   */
  async put<T>(path: string, data?: unknown, options?: RequestOptions): Promise<T> {
    const url = this.buildUrl(path);
    return this.request<T>(url, {
      method: 'PUT',
      headers: this.mergeHeaders(options?.headers),
      body: data ? JSON.stringify(data) : undefined,
      signal: this.createAbortSignal(options?.timeout)
    });
  }

  /**
   * Makes a DELETE request
   */
  async delete<T>(path: string, options?: RequestOptions): Promise<T> {
    const url = this.buildUrl(path);
    return this.request<T>(url, {
      method: 'DELETE',
      headers: this.mergeHeaders(options?.headers),
      signal: this.createAbortSignal(options?.timeout)
    });
  }

  /**
   * Makes a raw HTTP request
   */
  private async request<T>(url: string, init: RequestInit): Promise<T> {
    try {
      const response = await this.config.fetch(url, init);
      return await this.handleResponse<T>(response);
    } catch (error) {
      if (error instanceof ConfigServiceClientError) {
        throw error;
      }

      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new TimeoutError('Request timeout');
        }
        throw new NetworkError(`Network request failed: ${error.message}`, error);
      }

      throw new NetworkError('Unknown network error occurred');
    }
  }

  /**
   * Handles HTTP response and error cases
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type');
    const isJson = contentType?.includes('application/json');

    if (response.ok) {
      // Handle successful responses
      if (response.status === 204) {
        // No content response
        return undefined as T;
      }

      if (isJson) {
        return await response.json();
      }

      return await response.text() as T;
    }

    // Handle error responses
    let errorResponse: ApiErrorResponse | undefined;

    if (isJson) {
      try {
        errorResponse = await response.json();
      } catch {
        // Ignore JSON parsing errors for error responses
      }
    }

    throw createErrorFromResponse(response.status, errorResponse);
  }

  /**
   * Builds the full URL with query parameters
   */
  private buildUrl(path: string, params?: Record<string, unknown>): string {
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    let url = `${this.config.baseUrl}${cleanPath}`;

    if (params) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value));
        }
      });

      const queryString = searchParams.toString();
      if (queryString) {
        url += `?${queryString}`;
      }
    }

    return url;
  }

  /**
   * Merges default headers with request-specific headers
   */
  private mergeHeaders(requestHeaders?: Record<string, string>): Record<string, string> {
    return {
      ...this.config.headers,
      ...requestHeaders
    };
  }

  /**
   * Creates an AbortSignal for request timeout
   */
  private createAbortSignal(timeout?: number): AbortSignal {
    const timeoutMs = timeout ?? this.config.timeout;
    const controller = new AbortController();
    
    setTimeout(() => {
      controller.abort();
    }, timeoutMs);

    return controller.signal;
  }

  /**
   * Gets the current configuration
   */
  public getConfig(): Readonly<ClientConfig> {
    return { ...this.config };
  }
}
