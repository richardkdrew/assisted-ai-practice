/**
 * Error handling types and classes for the Configuration Service Client
 */

/**
 * Base error class for all Configuration Service Client errors
 */
export class ConfigServiceClientError extends Error {
  public readonly code: string;
  public readonly statusCode?: number;
  public readonly originalError?: Error;

  constructor(
    code: string,
    message: string,
    statusCode?: number,
    originalError?: Error
  ) {
    super(message);
    this.name = 'ConfigServiceClientError';
    this.code = code;
    this.statusCode = statusCode;
    this.originalError = originalError;

    // Maintains proper stack trace for where our error was thrown (only available on V8)
    if ((Error as any).captureStackTrace) {
      (Error as any).captureStackTrace(this, ConfigServiceClientError);
    }
  }
}

/**
 * Error thrown when validation fails
 */
export class ValidationError extends ConfigServiceClientError {
  public readonly details: Record<string, string>;

  constructor(details: Record<string, string>, message = 'Validation failed') {
    super('VALIDATION_ERROR', message, 400);
    this.name = 'ValidationError';
    this.details = details;
  }
}

/**
 * Error thrown when a resource is not found
 */
export class NotFoundError extends ConfigServiceClientError {
  constructor(resource: string, id: string) {
    super(
      'NOT_FOUND',
      `${resource} with id '${id}' not found`,
      404
    );
    this.name = 'NotFoundError';
  }
}

/**
 * Error thrown when there's a conflict (e.g., duplicate names)
 */
export class ConflictError extends ConfigServiceClientError {
  constructor(message: string) {
    super('CONFLICT', message, 409);
    this.name = 'ConflictError';
  }
}

/**
 * Error thrown when authentication fails
 */
export class AuthenticationError extends ConfigServiceClientError {
  constructor(message = 'Authentication failed') {
    super('AUTHENTICATION_ERROR', message, 401);
    this.name = 'AuthenticationError';
  }
}

/**
 * Error thrown when authorization fails
 */
export class AuthorizationError extends ConfigServiceClientError {
  constructor(message = 'Authorization failed') {
    super('AUTHORIZATION_ERROR', message, 403);
    this.name = 'AuthorizationError';
  }
}

/**
 * Error thrown when there's a network or connection issue
 */
export class NetworkError extends ConfigServiceClientError {
  constructor(message: string, originalError?: Error) {
    super('NETWORK_ERROR', message, undefined, originalError);
    this.name = 'NetworkError';
  }
}

/**
 * Error thrown when the server returns an unexpected error
 */
export class ServerError extends ConfigServiceClientError {
  constructor(message: string, statusCode: number) {
    super('SERVER_ERROR', message, statusCode);
    this.name = 'ServerError';
  }
}

/**
 * Error thrown when request timeout occurs
 */
export class TimeoutError extends ConfigServiceClientError {
  constructor(message = 'Request timeout') {
    super('TIMEOUT_ERROR', message);
    this.name = 'TimeoutError';
  }
}

/**
 * Standard API error response structure
 */
export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

/**
 * Creates appropriate error instance based on HTTP status code and response
 */
export function createErrorFromResponse(
  statusCode: number,
  response?: ApiErrorResponse,
  originalError?: Error
): ConfigServiceClientError {
  const errorMessage = response?.error?.message || 'Unknown error occurred';
  const errorCode = response?.error?.code || 'UNKNOWN_ERROR';

  switch (statusCode) {
    case 400:
      if (response?.error?.details) {
        return new ValidationError(
          response.error.details as Record<string, string>,
          errorMessage
        );
      }
      return new ConfigServiceClientError(errorCode, errorMessage, statusCode, originalError);

    case 401:
      return new AuthenticationError(errorMessage);

    case 403:
      return new AuthorizationError(errorMessage);

    case 404:
      // Try to extract resource and ID from message for better error handling
      return new ConfigServiceClientError(errorCode, errorMessage, statusCode, originalError);

    case 409:
      return new ConflictError(errorMessage);

    case 408:
    case 504:
      return new TimeoutError(errorMessage);

    case 500:
    case 502:
    case 503:
      return new ServerError(errorMessage, statusCode);

    default:
      if (statusCode >= 400 && statusCode < 500) {
        return new ConfigServiceClientError(errorCode, errorMessage, statusCode, originalError);
      } else if (statusCode >= 500) {
        return new ServerError(errorMessage, statusCode);
      }
      return new ConfigServiceClientError(errorCode, errorMessage, statusCode, originalError);
  }
}

/**
 * Type guard to check if an error is a ConfigServiceClientError
 */
export function isConfigServiceClientError(error: unknown): error is ConfigServiceClientError {
  return error instanceof ConfigServiceClientError;
}

/**
 * Type guard to check if an error is a ValidationError
 */
export function isValidationError(error: unknown): error is ValidationError {
  return error instanceof ValidationError;
}

/**
 * Type guard to check if an error is a NotFoundError
 */
export function isNotFoundError(error: unknown): error is NotFoundError {
  return error instanceof NotFoundError;
}

/**
 * Type guard to check if an error is a NetworkError
 */
export function isNetworkError(error: unknown): error is NetworkError {
  return error instanceof NetworkError;
}
