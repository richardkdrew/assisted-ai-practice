# Structured Error Tracing - Quickstart Guide

This guide provides a quick overview of how to use the structured error tracing system in the Configuration Service.

## Getting Started

### Prerequisites

1. Ensure you have the required dependencies installed:
   ```bash
   cd svc/
   uv pip install -e ".[observability]"
   ```

2. Start the full observability stack:
   ```bash
   make dev
   ```

## Using Structured Error Tracing

### 1. Accessing Error Traces

When an error occurs in the system, you can view the complete trace in the Jaeger UI:

1. Open Jaeger UI: http://localhost:16686
2. Select "configuration-service" from the Service dropdown
3. Filter by:
   - Tags: `error=true`
   - Operation: The specific endpoint or operation
   - Time Range: Select appropriate time window
4. Click "Find Traces" to view error traces
5. Click on a trace to see the detailed span information

### 2. Reading Error Responses

Error responses from the API now include trace information:

```json
{
  "error": {
    "message": "Invalid configuration format",
    "type": "ValidationError",
    "details": [...],
    "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
    "request_id": "req_123456"
  },
  "status_code": 400
}
```

To look up the full trace:
1. Copy the `trace_id` value
2. Paste it in the Jaeger UI search box
3. Click "Find Traces"

### 3. Adding Custom Error Context

To add custom context to error traces in your code:

```python
from opentelemetry import trace

# Get the current span
current_span = trace.get_current_span()

try:
    # Your code that might raise an exception
    process_configuration(config_data)
except ValidationError as e:
    # Add custom attributes to the current span
    current_span.set_attribute("error", True)
    current_span.set_attribute("error.type", e.__class__.__name__)
    current_span.set_attribute("error.message", str(e))
    current_span.set_attribute("configuration.id", config_id)

    # Re-raise the exception (will be caught by middleware)
    raise
```

### 4. Creating Manual Error Spans

For more detailed error tracing, you can create explicit error spans:

```python
from opentelemetry import trace
from contextlib import contextmanager

tracer = trace.get_tracer(__name__)

@contextmanager
def error_span(operation_name, **attributes):
    with tracer.start_as_current_span(operation_name) as span:
        # Set initial span attributes
        for key, value in attributes.items():
            span.set_attribute(key, value)

        try:
            yield span
        except Exception as e:
            # Record error to span
            span.set_attribute("error", True)
            span.set_attribute("error.type", e.__class__.__name__)
            span.set_attribute("error.message", str(e))
            span.record_exception(e)
            raise

# Usage
try:
    with error_span("validate_configuration", configuration_id="conf_123"):
        # Code that might raise an exception
        validate_config(config_data)
except ValidationError as e:
    # Handle or re-raise as needed
    raise
```

## Debugging Common Issues

### Missing Trace IDs in Responses

If trace IDs are not appearing in error responses:

1. Check that the middleware is correctly registered in main.py
2. Verify that the custom exception handlers are registered
3. Ensure that OpenTelemetry is properly initialized before the FastAPI app

### Traces Not Appearing in Jaeger

If traces are not showing up in the Jaeger UI:

1. Check that the Jaeger container is running: `docker ps | grep jaeger`
2. Verify the OTEL collector configuration has the proper exporters
3. Check that the Python service has the correct OTEL environment variables
4. Look for errors in the collector logs: `docker logs configservice-otel-collector`

### Connection Issues

If the service cannot connect to the OTEL collector:

1. Verify network connectivity between containers
2. Check that the collector is running on the expected port
3. Ensure the OTLP exporter is configured with the correct endpoint

## Trace Query Examples

### Finding All Validation Errors

In Jaeger UI:
- Service: "configuration-service"
- Tags: `error=true error.type=ValidationError`
- Min Duration: Leave empty to see all traces
- Limit Results: 20 (adjust as needed)

### Finding Errors for a Specific Application

In Jaeger UI:
- Service: "configuration-service"
- Tags: `error=true application.id=app_123456`
- Time Range: Last 1 hour

### Finding Slow Requests with Errors

In Jaeger UI:
- Service: "configuration-service"
- Tags: `error=true`
- Min Duration: 1s
- Max Duration: Leave empty

## Additional Resources

- [OpenTelemetry Python Documentation](https://opentelemetry-python.readthedocs.io/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/1.47/)
- [FastAPI Middleware Documentation](https://fastapi.tiangolo.com/tutorial/middleware/)