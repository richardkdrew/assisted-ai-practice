# Retry Logic: Quickstart Guide

## Overview

The Retry Logic feature adds intelligent retry capability to the Configuration Service by analyzing OpenTelemetry trace data to determine whether failed operations should be retried.

## Key Components

- **should_retry function**: Analyzes a trace to determine if retry is appropriate
- **RetryDecision**: Object returned by should_retry with decision details
- **Error Classification**: Logic to categorize errors as permanent or transient

## Usage Examples

### Basic Usage

```python
from observability.trace_retry import should_retry

# After an operation fails, analyze the trace
result = should_retry(trace_id)

if result["decision"] == "RETRY":
    # Wait and retry
    time.sleep(result["wait_seconds"])
    # Retry the operation
    retry_operation()
elif result["decision"] == "ABORT":
    # Log permanent failure
    logger.error(f"Operation failed permanently: {result['reason']}")
    # Handle permanent failure (e.g., notify user)
    handle_permanent_failure()
elif result["decision"] == "WAIT":
    # Apply more cautious retry strategy for unknown errors
    time.sleep(result["wait_seconds"])
    # Maybe retry with backoff or limited attempts
    cautious_retry_operation()
```

### Integration with Retry Policies

```python
from observability.trace_retry import should_retry

def retry_with_backoff(operation, max_retries=3, initial_wait=1):
    """Retry an operation with exponential backoff."""
    attempt = 0
    last_trace_id = None

    while attempt <= max_retries:
        try:
            return operation()
        except Exception as e:
            # Get trace ID from the current span
            current_span = trace.get_current_span()
            trace_id = format(current_span.get_span_context().trace_id, "032x")
            last_trace_id = trace_id

            # Analyze trace for retry decision
            if attempt < max_retries:  # Don't check on last attempt
                result = should_retry(trace_id)

                if result["decision"] == "ABORT":
                    # Don't retry permanent errors
                    logger.error(f"Operation failed permanently: {result['reason']}")
                    raise

                # Wait based on decision and attempt number
                wait_time = result["wait_seconds"] * (2 ** attempt)
                time.sleep(wait_time)
                attempt += 1
            else:
                # Max retries exceeded
                raise

    # If we got here, max retries exceeded
    raise Exception(f"Max retries exceeded. Last trace ID: {last_trace_id}")
```

### Error Logging with Decision Context

```python
from observability.trace_retry import should_retry

def log_error_with_retry_info(exception, trace_id):
    """Log an error with retry decision information."""
    try:
        # Get retry decision
        retry_info = should_retry(trace_id)

        # Log with appropriate level based on decision
        if retry_info["decision"] == "ABORT":
            logger.error(
                f"Permanent error: {exception}. Retry decision: {retry_info['decision']}. "
                f"Reason: {retry_info['reason']}. Trace ID: {retry_info['trace_id']}"
            )
        elif retry_info["decision"] == "RETRY":
            logger.warning(
                f"Transient error: {exception}. Retry decision: {retry_info['decision']}. "
                f"Reason: {retry_info['reason']}. Retry in {retry_info['wait_seconds']}s. "
                f"Trace ID: {retry_info['trace_id']}"
            )
        else:
            logger.warning(
                f"Unknown error: {exception}. Retry decision: {retry_info['decision']}. "
                f"Reason: {retry_info['reason']}. Wait time: {retry_info['wait_seconds']}s. "
                f"Trace ID: {retry_info['trace_id']}"
            )
    except ValueError:
        # Fallback if trace analysis fails
        logger.error(f"Error: {exception}. Trace ID: {trace_id}")
```

## Implementation Notes

### Key Decisions

- **Dictionary Return Value**: The function returns a dictionary rather than a formal class for simplicity
- **Leveraging Existing Attributes**: Uses the error.retriable attribute already set by middleware
- **Decision Priorities**: Permanent errors take precedence over transient or unknown errors
- **Default Wait Time**: Uses 5 seconds as the default wait time for transient errors

### Testing

To test the function with different error types:

1. Create a trace with a validation error (permanent):
   ```python
   # The function should return ABORT
   result = should_retry(trace_id_with_validation_error)
   assert result["decision"] == "ABORT"
   ```

2. Create a trace with a connection error (transient):
   ```python
   # The function should return RETRY
   result = should_retry(trace_id_with_connection_error)
   assert result["decision"] == "RETRY"
   assert result["wait_seconds"] == 5
   ```

3. Create a trace with an unknown error:
   ```python
   # The function should return WAIT
   result = should_retry(trace_id_with_unknown_error)
   assert result["decision"] == "WAIT"
   ```

## Resources

- [Trace Storage Documentation](link_to_trace_storage_docs)
- [Error Tracking Middleware Documentation](link_to_error_tracking_docs)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)