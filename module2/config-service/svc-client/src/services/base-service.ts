/**
 * Base service class for Configuration Service Client services
 */

import { HttpClient } from '../utils/http-client.js';
import { ConfigServiceClientError } from '../models/errors.js';

/**
 * Abstract base class for all service implementations
 * Provides common functionality and error handling
 */
export abstract class BaseService {
  protected readonly httpClient: HttpClient;

  constructor(httpClient: HttpClient) {
    this.httpClient = httpClient;
  }

  /**
   * Handles errors consistently across all services
   * @param error - The error to handle
   * @param context - Additional context for error handling
   */
  protected handleError(error: unknown, context?: string): never {
    if (error instanceof ConfigServiceClientError) {
      // Re-throw Configuration Service Client errors as-is
      throw error;
    }

    if (error instanceof Error) {
      // Wrap other errors in a ConfigServiceClientError
      const message = context 
        ? `${context}: ${error.message}`
        : error.message;
      
      throw new ConfigServiceClientError(
        'SERVICE_ERROR',
        message,
        undefined,
        error
      );
    }

    // Handle unknown error types
    const message = context 
      ? `${context}: Unknown error occurred`
      : 'Unknown error occurred';
    
    throw new ConfigServiceClientError(
      'UNKNOWN_ERROR',
      message
    );
  }

  /**
   * Validates that a required parameter is provided
   * @param value - The value to validate
   * @param paramName - The name of the parameter for error messages
   */
  protected validateRequired<T>(value: T | undefined | null, paramName: string): T {
    if (value === undefined || value === null) {
      throw new ConfigServiceClientError(
        'VALIDATION_ERROR',
        `Required parameter '${paramName}' is missing`
      );
    }
    return value;
  }

  /**
   * Validates that a string parameter is not empty
   * @param value - The string value to validate
   * @param paramName - The name of the parameter for error messages
   */
  protected validateNonEmptyString(value: string | undefined | null, paramName: string): string {
    const validated = this.validateRequired(value, paramName);
    
    if (typeof validated !== 'string' || validated.trim().length === 0) {
      throw new ConfigServiceClientError(
        'VALIDATION_ERROR',
        `Parameter '${paramName}' must be a non-empty string`
      );
    }
    
    return validated.trim();
  }

  /**
   * Validates pagination parameters
   * @param limit - The limit parameter
   * @param offset - The offset parameter
   */
  protected validatePaginationParams(limit?: number, offset?: number): { limit?: number; offset?: number } {
    const result: { limit?: number; offset?: number } = {};

    if (limit !== undefined) {
      if (!Number.isInteger(limit) || limit < 1) {
        throw new ConfigServiceClientError(
          'VALIDATION_ERROR',
          'Limit must be a positive integer'
        );
      }
      if (limit > 1000) {
        throw new ConfigServiceClientError(
          'VALIDATION_ERROR',
          'Limit cannot exceed 1000'
        );
      }
      result.limit = limit;
    }

    if (offset !== undefined) {
      if (!Number.isInteger(offset) || offset < 0) {
        throw new ConfigServiceClientError(
          'VALIDATION_ERROR',
          'Offset must be a non-negative integer'
        );
      }
      result.offset = offset;
    }

    return result;
  }

  /**
   * Validates ULID format
   * @param id - The ID to validate
   * @param paramName - The name of the parameter for error messages
   */
  protected validateULID(id: string, paramName: string): string {
    const validated = this.validateNonEmptyString(id, paramName);
    
    // Basic ULID format validation (26 characters, base32)
    const ulidRegex = /^[0-9A-HJKMNP-TV-Z]{26}$/;
    if (!ulidRegex.test(validated)) {
      throw new ConfigServiceClientError(
        'VALIDATION_ERROR',
        `Parameter '${paramName}' must be a valid ULID`
      );
    }
    
    return validated;
  }

  /**
   * Safely executes an async operation with error handling
   * @param operation - The async operation to execute
   * @param context - Context for error handling
   */
  protected async safeExecute<T>(
    operation: () => Promise<T>,
    context?: string
  ): Promise<T> {
    try {
      return await operation();
    } catch (error) {
      this.handleError(error, context);
    }
  }

  /**
   * Gets the HTTP client configuration
   */
  protected getClientConfig() {
    return this.httpClient.getConfig();
  }
}
