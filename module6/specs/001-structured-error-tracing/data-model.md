# Data Model: Structured Error Tracing

## Overview

This document outlines the data structures and models used for structured error tracing in the Configuration Service. The primary focus is on defining how error information is structured, captured, and propagated throughout the system.

## Core Entities

### ErrorLog

Represents a single error occurrence with structured fields.

**Attributes**:

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| trace_id | string | Unique identifier for the trace (hexadecimal) | "4bf92f3577b34da6a3ce929d0e0e4736" |
| span_id | string | Identifier for the specific span (hexadecimal) | "00f067aa0ba902b7" |
| timestamp | datetime | When the error occurred | "2025-10-11T14:23:45.123456Z" |
| error_type | string | Exception class name | "ValidationError" |
| error_message | string | Human-readable error description | "Invalid configuration format" |
| stack_trace | string | Truncated stack trace information | "File main.py, line 42, in validate_config..." |
| http_context | object | HTTP-related information | See below |
| application_context | object | Application-specific context | See below |
| severity | string | Error severity level | "ERROR", "CRITICAL" |
| metadata | object | Additional system metadata | See below |

**HTTP Context**:

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| method | string | HTTP method | "POST", "GET" |
| path | string | Request URL path | "/api/v1/configurations" |
| status_code | integer | HTTP status code | 400, 500 |
| client_ip | string | Client IP address (anonymized) | "192.168.x.x" |
| user_agent | string | User agent string | "Mozilla/5.0..." |
| request_id | string | Unique request identifier | "req_123456" |

**Application Context**:

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| application_id | string | ID of the affected application (if relevant) | "app_123456" |
| configuration_id | string | ID of the affected configuration (if relevant) | "conf_123456" |
| user_context | object | User information (sanitized) | `{"id": "usr_123", "role": "admin"}` |
| operation | string | Operation being performed | "create_configuration" |

**Metadata**:

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| service_version | string | Version of the service | "1.0.0" |
| environment | string | Deployment environment | "development", "production" |
| host | string | Server hostname | "config-service-1" |
| payload_truncated | boolean | Indicates if payload was truncated | true, false |

### RequestTrace

Represents the collection of all logs (errors and operations) associated with a single request ID.

**Attributes**:

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| request_id | string | Unique identifier for the request | "req_123456" |
| trace_id | string | OpenTelemetry trace ID | "4bf92f3577b34da6a3ce929d0e0e4736" |
| spans | array | Collection of span references | See below |
| start_time | datetime | When the request started | "2025-10-11T14:23:45.000000Z" |
| end_time | datetime | When the request completed | "2025-10-11T14:23:45.234567Z" |
| duration_ms | float | Request duration in milliseconds | 234.567 |
| status | string | Final status (success/error) | "error", "success" |
| error_count | integer | Number of errors in this trace | 2 |

## API Response Format for Errors

When errors occur, the API returns a consistent error response format that includes trace information:

```json
{
  "error": {
    "message": "Invalid configuration format",
    "type": "ValidationError",
    "details": [
      {"field": "value", "issue": "Must be a valid JSON object"}
    ],
    "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
    "request_id": "req_123456"
  },
  "status_code": 400
}
```

## OpenTelemetry Span Attributes

When recording errors to OpenTelemetry spans, the following attributes are set:

| Attribute | Description |
|-----------|-------------|
| error | Boolean flag (true) indicating an error occurred |
| error.type | Exception class name |
| error.message | Error message |
| error.stack | Stack trace (truncated if needed) |
| http.request.method | HTTP method |
| http.request.path | Request path |
| http.response.status_code | HTTP status code |
| service.name | Name of the service |
| service.version | Version of the service |
| application.id | ID of the related application (if applicable) |
| configuration.id | ID of the related configuration (if applicable) |

## Data Size Constraints

To manage storage and performance:

1. **Stack Traces**: Limited to 4KB (approximately 50-100 lines)
2. **Error Messages**: Limited to 1KB
3. **Request/Response Payloads**: Limited to 4KB in logs
4. **Total Error Log Size**: Limited to 10KB per entry

## Data Flow

1. **Error Capture**: Errors are captured in the error handling middleware
2. **Span Recording**: Error details are recorded to the current span
3. **Log Storage**: Error logs are persisted via the OTLP exporter
4. **Response Generation**: Error responses include trace IDs from the current span
5. **Trace Query**: Errors can be queried by trace ID, error type, or time range

## Trace Context Propagation

Trace context is propagated using the W3C TraceContext standard, which includes:

1. **traceparent**: Contains trace ID, span ID, and trace flags
2. **tracestate**: Vendor-specific trace information (if any)

Example HTTP headers:

```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
tracestate: congo=t61rcWkgMzE
```