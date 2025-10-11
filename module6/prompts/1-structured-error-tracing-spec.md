# OpenTelemetry Implementation Requirements for FastAPI Application

## Overview

Implement comprehensive OpenTelemetry tracing for a FastAPI application with automatic instrumentation, custom attributes, structured error handling, and integration with existing observability stack.

---

## 1. Core Requirements

### 1.1 Automatic Instrumentation

- Capture all FastAPI HTTP requests/responses as spans automatically
- Record HTTP method, path, status code, and duration
- Capture request/response headers (sanitized for sensitive data)
- Minimal code changes to existing route handlers

### 1.2 Custom Attributes

All spans must support the following custom attributes:

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `operation_name` | string | Business operation identifier | `"create_application"`, `"process_payment"` |
| `error_type` | string | Exception class name (when errors occur) | `"ValidationError"` |
| `error.message` | string | Human-readable error description | `"Invalid email format"` |
| `error.retriable` | boolean | Whether error is transient and safe to retry | `true` or `false` |
| Custom parameters | varies | Sanitized input parameters as key-value pairs | `user_id: "123"` |

### 1.3 Error Handling

Implement comprehensive error recording with categorization:

**Retriable Errors (Transient):**

- `ConnectionError`
- `TimeoutError`
- `ServiceUnavailableError`
- HTTP 5xx errors
- Network-related exceptions

**Permanent Errors (Non-retriable):**

- `ValidationError`
- `NotFoundError`
- `AuthenticationError`
- `PermissionError`
- HTTP 4xx errors (except 429 Too Many Requests)

**Error Recording Process:**

1. Set span status to `ERROR`
2. Call `span.record_exception(exception)` to capture full stack trace
3. Add custom error attributes (`error.type`, `error.message`, `error.retriable`)

---

## 2. Required Packages

```bash
pip install opentelemetry-api
pip install opentelemetry-sdk
pip install opentelemetry-instrumentation-fastapi
pip install opentelemetry-exporter-otlp-proto-grpc  # For OTLP collector
# OR
pip install opentelemetry-exporter-otlp-proto-http  # HTTP variant
```

---

## 3. Configuration Requirements

### 3.1 Exporter Configuration

**Priority 1:** OTLP exporter to existing observability stack

- Export to OTEL Collector endpoint (typically `http://otel-collector:4317` for gRPC)
- Alternative: HTTP endpoint (typically `http://otel-collector:4318`)

**Priority 2 (if needed):** Filesystem exporter for debugging

- Export traces as JSON files to local directory
- Configure file rotation and naming strategy

### 3.2 Resource Attributes

Configure the following resource attributes:

- `service.name`: Service identifier
- `service.version`: Application version
- `deployment.environment`: Environment name (dev/staging/prod)

### 3.3 Sampling (Optional)

- Configure sampling rate if needed for high-traffic services
- Default: 100% sampling for development

---

## 4. Data Sanitization Requirements

### 4.1 Sensitive Data to Remove

Automatically sanitize before adding to span attributes:

- Passwords and API keys
- Authentication tokens (Bearer, JWT, etc.)
- Credit card numbers
- Social Security Numbers
- Private keys and certificates

### 4.2 Sensitive Data to Mask

Hash or partially mask:

- Email addresses (show domain only or hash)
- Phone numbers (show last 4 digits)
- IP addresses (optional, depending on privacy requirements)

### 4.3 Safe Data to Preserve

Keep for debugging:

- User IDs (non-PII identifiers)
- Request IDs and correlation IDs
- Resource names and paths
- Timestamps and durations
- Non-sensitive query parameters

---

## 5. Implementation Deliverables

### 5.1 Code Structure

```
app/
├── telemetry/
│   ├── __init__.py          # OpenTelemetry initialization
│   ├── config.py            # Configuration management
│   ├── error_handling.py    # Error categorization and recording
│   └── sanitization.py      # Parameter sanitization utilities
├── main.py                  # FastAPI app with instrumentation
└── traces/                  # Output directory (if filesystem export used)
```

### 5.2 Required Functions

**Error Handling:**

```python
def categorize_error(exception: Exception) -> bool:
    """Returns True if error is retriable, False otherwise"""
    pass

def record_error_on_span(span, exception: Exception) -> None:
    """Records error on span with all required attributes"""
    pass
```

**Sanitization:**

```python
def sanitize_parameters(params: dict) -> dict:
    """Removes/masks sensitive data from parameters"""
    pass
```

### 5.3 Documentation

Provide:

1. Installation commands with all required packages
2. Initialization code with comments explaining key decisions
3. Example FastAPI route showing custom attribute usage
4. Example error handling in try/except blocks
5. Sample trace output showing expected structure
6. Testing instructions to verify tracing works correctly

---

## 6. Integration Requirements

### 6.1 Existing Stack Compatibility

Must integrate cleanly with:

- Existing OTEL Collector (if present)
- Prometheus for metrics
- Grafana for visualization
- Jaeger/Tempo or similar traces backend

### 6.2 Non-Breaking Changes

- Must not interfere with existing instrumentation
- Must not duplicate auto-instrumentation already in place
- Should extend, not replace, existing OpenTelemetry configuration
- Must handle gracefully if tracing initialization fails

---

## 7. Success Criteria

The implementation must:

- ✅ Require minimal changes to existing FastAPI route handlers
- ✅ Automatically trace all HTTP requests without manual span creation
- ✅ Export traces to appropriate backend (OTLP collector or filesystem)
- ✅ Correctly categorize errors as retriable/permanent
- ✅ Sanitize sensitive data before adding to spans
- ✅ Provide clear examples for adding custom business attributes
- ✅ Include error handling that doesn't break the application if tracing fails
- ✅ Integrate with existing Docker-based observability stack
- ✅ Support both automatic instrumentation and custom span attributes

---

## 8. Optional Enhancements

### 8.1 Metrics Integration

- Add OpenTelemetry metrics for request counts, latencies
- Export metrics to Prometheus

### 8.2 Advanced Features

- Distributed tracing with context propagation (W3C Trace Context)
- Custom span processors for additional processing
- Sampling strategies for high-volume services
- Baggage propagation for cross-service metadata

---

## Next Steps

1. **Audit existing setup** using the audit prompt
2. **Review findings** to identify what's already in place
3. **Design integration approach** that extends existing configuration
4. **Implement** with provided code examples
5. **Test** to verify traces appear in your observability backend
6. **Iterate** on custom attributes and error handling as needed
