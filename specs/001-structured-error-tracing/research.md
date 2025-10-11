# Research: Structured Error Tracing

## Overview

This document summarizes research findings on implementing structured error tracing with OpenTelemetry in the Configuration Service project. The research was conducted as part of the feature implementation planning process.

## Current State Assessment

### OpenTelemetry Installation

**Decision**: Use the existing OpenTelemetry packages defined in pyproject.toml.

**Rationale**: The project already has all necessary OpenTelemetry packages defined as optional dependencies in the `observability` group. These include:

```python
observability = [
    "opentelemetry-api>=1.20.0",
    "opentelemetry-sdk>=1.20.0",
    "opentelemetry-instrumentation-fastapi>=0.41b0",
    "opentelemetry-exporter-otlp>=1.20.0",
    "opentelemetry-instrumentation-requests>=0.41b0",
    "opentelemetry-instrumentation-psycopg2>=0.41b0",
    "prometheus-client>=0.17.0",
]
```

**Alternatives considered**: Creating a separate error-tracing dependency group was considered but rejected as it would fragment the observability infrastructure.

### Existing OpenTelemetry Configuration

**Decision**: Extend the existing observability.py file with error-specific tracing enhancements.

**Rationale**: The project has a well-structured observability module that already:
1. Sets up a TracerProvider with appropriate resource attributes
2. Configures OTLP exporters for traces and metrics
3. Instruments FastAPI, Requests, and Psycopg2
4. Adds Prometheus metrics and middleware

**Findings**:
- The Python service connects to the collector using `http://otel-collector:4317` (GRPC)
- No OTEL-specific environment variables are configured in docker-compose.yml
- Current setup does not include any error-specific tracing enhancements

### Container Interaction Analysis

**Decision**: Use existing container network and add Jaeger container.

**Rationale**:
- Both services are on the same Docker network called `observability`
- The OTEL collector is configured to expose ports for GRPC (4317) and HTTP (4318)
- Network connectivity is already established and functional

**Issues to address**:
- OTEL collector configuration only has a debug exporter, not a proper backend
- No trace visualization tool (Jaeger/Zipkin) is included in the stack
- No proper configuration for error-specific tracing is present

## Error Tracing Best Practices

### Error Attributes in OpenTelemetry

**Decision**: Implement a standard set of error attributes for all captured errors.

**Rationale**: Standardized attributes improve searchability and analysis of errors.

**Recommended error attributes**:
- `error` (boolean): true for spans with errors
- `error.type`: Exception class name
- `error.message`: Human-readable error message
- `error.stack`: Stack trace (truncated to fit size limits)
- `error.http.status_code`: HTTP status for API errors
- `error.request.path`: Path of the request causing the error
- `error.request.method`: HTTP method of the request
- `error.severity`: ERROR, CRITICAL, etc.
- `error.context`: JSON serialized contextual data (truncated to fit limits)

### FastAPI Integration Patterns

**Decision**: Use both middleware and exception handlers for comprehensive error tracing.

**Rationale**:
- Middleware captures the full request context
- Exception handlers provide specific error formatting in responses

**Implementation approach**:
1. Create middleware that wraps request processing in try/except
2. Capture request context before execution
3. Record errors to current span when exceptions occur
4. Use exception handlers to format error responses with trace IDs

### Context Propagation

**Decision**: Use W3C TraceContext and Baggage propagators.

**Rationale**: These propagators are industry standard and ensure interoperability.

**Implementation details**:
```python
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.propagators.tracecontext import TraceContextTextMapPropagator
from opentelemetry.propagators.baggage import BaggagePropagator

# Set propagators for context propagation
set_global_textmap(CompositePropagator([
    TraceContextTextMapPropagator(),
    BaggagePropagator()
]))
```

### OTEL Collector Configuration

**Decision**: Update collector configuration with Jaeger exporter.

**Rationale**: Jaeger provides excellent trace visualization and is widely used.

**Recommended configuration**:
```yaml
exporters:
  # Keep debug exporter for development
  debug:
    verbosity: detailed
  # Add proper exporters
  prometheus:
    endpoint: "0.0.0.0:8889"
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, resource, batch]
      exporters: [debug, jaeger]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, resource, batch]
      exporters: [debug, prometheus]
```

### Load Impact & Performance

**Decision**: Use sampling for high-volume production environments.

**Rationale**: Full tracing of all requests can impact performance and storage.

**Recommendations**:
- Use head-based sampling for non-error traces (sample 10-20% of normal traffic)
- Always capture 100% of error traces
- Set up separate exporters for errors vs. normal traces if needed
- Implement size limits (10KB) on error payloads to prevent storage issues

## Conclusion

The Configuration Service has a solid foundation for OpenTelemetry instrumentation but needs enhancements for structured error tracing. The implementation should focus on:

1. Adding error-specific middleware and exception handlers
2. Properly configuring the OTEL collector for trace storage
3. Adding Jaeger for trace visualization
4. Implementing proper context propagation
5. Ensuring error responses include trace IDs for correlation

These changes can be implemented by extending the existing observability.py module and updating the Docker compose configuration.