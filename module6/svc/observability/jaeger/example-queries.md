# Example Jaeger Queries for Error Tracing

This document provides example queries to help you efficiently search for and debug errors using Jaeger UI.

## Basic Error Queries

### All Errors in the Last Hour

- Service: `configuration-service`
- Tags: `error=true`
- Lookback: `1h`

### Specific Error Types

- Service: `configuration-service`
- Tags: `error.type=ValidationError`
- Lookback: `6h`

## Application Context Queries

### Errors for a Specific Application

- Service: `configuration-service`
- Tags: `application.id=app_123456`
- Lookback: `12h`

### Errors for a Specific Configuration

- Service: `configuration-service`
- Tags: `configuration.id=conf_123456`
- Lookback: `12h`

## HTTP Context Queries

### Errors for a Specific Endpoint

- Service: `configuration-service`
- Tags: `http.request.path=/api/v1/configurations`
- Tags: `error=true`
- Lookback: `24h`

### Errors with Specific HTTP Status Code

- Service: `configuration-service`
- Tags: `error.http.status_code=400`
- Lookback: `24h`

## Performance Analysis

### Slow Errors (>1s)

- Service: `configuration-service`
- Tags: `error=true`
- Min Duration: `1s`
- Lookback: `24h`

### High-Severity Errors

- Service: `configuration-service`
- Tags: `error.severity=CRITICAL`
- Lookback: `24h`

## Trace ID Correlation

To find a specific trace using a trace ID from an error response:

1. Copy the `trace_id` value from the error response
2. Paste it in the Jaeger UI search box
3. Click "Find Traces"

Example trace ID format: `4bf92f3577b34da6a3ce929d0e0e4736`

## Request ID Correlation

To find all traces for a specific request ID:

- Service: `configuration-service`
- Tags: `request_id=req_123456`
- Lookback: `24h`

## Advanced Filtering

You can combine multiple tag conditions to narrow down search results:

- Service: `configuration-service`
- Tags: `error=true error.type=ValidationError http.request.method=POST`
- Lookback: `24h`

This will find all validation errors that occurred during POST requests in the last 24 hours.