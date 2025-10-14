"""
Retry strategy implementation with exponential backoff.

This module provides retry logic for handling transient failures
in API calls and network operations.
"""

import asyncio
import random
from dataclasses import dataclass
from typing import Callable, TypeVar

import httpx
from opentelemetry.trace import Status, StatusCode

from ..observability.tracer import get_tracer


T = TypeVar("T")


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: bool = True


def is_retryable_error(exc: Exception) -> bool:
    """
    Determine if an error should trigger a retry.

    Retryable errors:
    - 429 (rate limit)
    - 500, 502, 503 (server errors)
    - Network/timeout errors

    Non-retryable (fail fast):
    - 400 (bad request)
    - 401 (unauthorized)
    - 403 (forbidden)
    - 404 (not found)
    - Other client errors (4xx)
    """
    if isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code
        # Retry on rate limits and server errors
        if status_code in (429, 500, 502, 503, 504):
            return True
        # Don't retry on client errors
        if 400 <= status_code < 500:
            return False
        return True

    # Retry on network errors
    if isinstance(exc, (httpx.TimeoutException, httpx.NetworkError, httpx.ConnectError)):
        return True

    # Don't retry unknown errors by default
    return False


async def with_retry(
    operation: Callable[[], T],
    config: RetryConfig,
    operation_name: str = "operation",
) -> T:
    """
    Execute an async operation with retry logic.

    Args:
        operation: Async callable to execute
        config: Retry configuration
        operation_name: Name for tracing/logging

    Returns:
        Result from operation

    Raises:
        Last exception if all retries exhausted
    """
    tracer = get_tracer()
    last_exception = None

    for attempt in range(1, config.max_attempts + 1):
        try:
            # Try the operation
            result = await operation()
            return result

        except Exception as exc:
            last_exception = exc

            # Check if we should retry
            should_retry = is_retryable_error(exc)

            # Create span for this retry attempt
            with tracer.start_as_current_span(f"retry.{operation_name}") as span:
                span.set_attribute("retry.attempt", attempt)
                span.set_attribute("retry.max_attempts", config.max_attempts)
                span.set_attribute("retry.will_retry", should_retry and attempt < config.max_attempts)
                span.set_attribute("retry.error_type", type(exc).__name__)
                span.set_attribute("retry.error_message", str(exc))

                # If not retryable, fail fast
                if not should_retry:
                    span.set_status(Status(StatusCode.ERROR, "Non-retryable error"))
                    raise

                # If we've exhausted attempts, raise
                if attempt >= config.max_attempts:
                    span.set_status(Status(StatusCode.ERROR, "Max retries exhausted"))
                    raise

                # Calculate backoff delay with exponential growth
                base_delay = config.initial_delay * (config.backoff_factor ** (attempt - 1))
                delay = min(base_delay, config.max_delay)

                # Add jitter to prevent thundering herd
                if config.jitter:
                    delay = delay * (0.5 + random.random() * 0.5)

                span.set_attribute("retry.delay_seconds", delay)
                span.set_status(Status(StatusCode.OK, f"Retrying after {delay:.2f}s"))

            # Wait before retrying
            await asyncio.sleep(delay)

    # This should never be reached due to the raise in the loop,
    # but just in case...
    if last_exception:
        raise last_exception
    raise RuntimeError("Retry loop exited unexpectedly")
