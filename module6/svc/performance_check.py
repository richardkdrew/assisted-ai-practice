"""Performance check for refactored observability module."""

import time
import statistics
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from observability import ErrorTrackingMiddleware, error_span


def run_middleware_benchmark(iterations=100):
    """Benchmark the performance of the error tracking middleware."""
    app = FastAPI()
    app.add_middleware(ErrorTrackingMiddleware)
    client = TestClient(app)

    # Add test endpoints
    @app.get("/success")
    async def success_endpoint():
        return {"message": "success"}

    @app.get("/error")
    async def error_endpoint():
        raise ValueError("Test error")

    # Run benchmark
    success_durations = []
    error_durations = []

    # Test success path
    for _ in range(iterations):
        start_time = time.time()
        response = client.get("/success")
        assert response.status_code == 200
        duration = time.time() - start_time
        success_durations.append(duration)

    # Test error path
    for _ in range(iterations):
        start_time = time.time()
        response = client.get("/error")
        assert response.status_code == 500
        duration = time.time() - start_time
        error_durations.append(duration)

    return {
        "success": {
            "min": min(success_durations),
            "max": max(success_durations),
            "avg": statistics.mean(success_durations),
            "p95": statistics.quantiles(success_durations, n=20)[18],  # ~95th percentile
        },
        "error": {
            "min": min(error_durations),
            "max": max(error_durations),
            "avg": statistics.mean(error_durations),
            "p95": statistics.quantiles(error_durations, n=20)[18],  # ~95th percentile
        }
    }


def run_error_span_benchmark(iterations=1000):
    """Benchmark the performance of the error_span context manager."""
    durations = []

    # Mock tracer and span for testing
    mock_span = MagicMock()

    with patch("observability.spans.tracer") as mock_tracer:
        mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

        # Test normal operation (no exception)
        for _ in range(iterations):
            start_time = time.time()
            with error_span("test_operation", attribute1="value1"):
                pass
            duration = time.time() - start_time
            durations.append(duration)

    return {
        "min": min(durations),
        "max": max(durations),
        "avg": statistics.mean(durations),
        "p95": statistics.quantiles(durations, n=20)[18],  # ~95th percentile
    }


if __name__ == "__main__":
    print("Running performance benchmarks for refactored observability module...")

    print("\nError Tracking Middleware Performance:")
    middleware_results = run_middleware_benchmark(iterations=50)

    print(f"Success path:")
    print(f"  Min: {middleware_results['success']['min']*1000:.2f}ms")
    print(f"  Max: {middleware_results['success']['max']*1000:.2f}ms")
    print(f"  Avg: {middleware_results['success']['avg']*1000:.2f}ms")
    print(f"  P95: {middleware_results['success']['p95']*1000:.2f}ms")

    print(f"\nError path:")
    print(f"  Min: {middleware_results['error']['min']*1000:.2f}ms")
    print(f"  Max: {middleware_results['error']['max']*1000:.2f}ms")
    print(f"  Avg: {middleware_results['error']['avg']*1000:.2f}ms")
    print(f"  P95: {middleware_results['error']['p95']*1000:.2f}ms")

    print("\nError Span Context Manager Performance:")
    span_results = run_error_span_benchmark(iterations=500)
    print(f"  Min: {span_results['min']*1000:.2f}ms")
    print(f"  Max: {span_results['max']*1000:.2f}ms")
    print(f"  Avg: {span_results['avg']*1000:.2f}ms")
    print(f"  P95: {span_results['p95']*1000:.2f}ms")

    print("\nConclusions:")
    print("  - These benchmarks show the performance of the refactored observability module")
    print("  - For a true regression test, compare these numbers with pre-refactoring measurements")
    print("  - Middleware performance is critical as it affects every request")
    print("  - Error span performance matters for operations using error tracking")