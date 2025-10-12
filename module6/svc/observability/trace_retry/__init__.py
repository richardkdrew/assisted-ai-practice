"""
Trace Retry module for analyzing OpenTelemetry traces to make retry decisions.

This module provides functionality to analyze OpenTelemetry traces and determine
whether failed operations should be retried based on the error types.

Example:
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
"""

from .retry_logic import should_retry

__all__ = ["should_retry"]