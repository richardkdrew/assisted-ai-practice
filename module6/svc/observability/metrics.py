"""Prometheus metrics for observability.

This module defines Prometheus metrics used for monitoring the application.
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from fastapi import Response

# Use a try/except block to handle metrics registration
try:
    REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status_code'])
    REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
    DB_CONNECTIONS = Gauge('database_connections_active', 'Active database connections')
    CONFIG_COUNT = Gauge('configurations_total', 'Total number of configurations')
    APP_COUNT = Gauge('applications_total', 'Total number of applications')
except ValueError:
    # If metrics already registered, retrieve them from the registry
    # This works because Prometheus client keeps a reference to all created metrics
    from prometheus_client.metrics import Counter as CounterClass
    from prometheus_client.metrics import Histogram as HistogramClass
    from prometheus_client.metrics import Gauge as GaugeClass

    # Get all collectors
    collectors = list(REGISTRY._collector_to_names.keys())

    # Find our metrics
    for collector in collectors:
        if isinstance(collector, CounterClass) and collector._name == 'http_requests_total':
            REQUEST_COUNT = collector
        elif isinstance(collector, HistogramClass) and collector._name == 'http_request_duration_seconds':
            REQUEST_DURATION = collector
        elif isinstance(collector, GaugeClass) and collector._name == 'database_connections_active':
            DB_CONNECTIONS = collector
        elif isinstance(collector, GaugeClass) and collector._name == 'configurations_total':
            CONFIG_COUNT = collector
        elif isinstance(collector, GaugeClass) and collector._name == 'applications_total':
            APP_COUNT = collector


def update_business_metrics(applications_count: int, configurations_count: int, active_connections: int):
    """Update business and infrastructure metrics."""
    APP_COUNT.set(applications_count)
    CONFIG_COUNT.set(configurations_count)
    DB_CONNECTIONS.set(active_connections)


async def metrics_endpoint():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


async def metrics_middleware(request, call_next):
    """Middleware to track request metrics."""
    method = request.method
    path = request.url.path

    # Start timing
    import time
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Record metrics
    duration = time.time() - start_time
    REQUEST_COUNT.labels(method=method, endpoint=path, status_code=response.status_code).inc()
    REQUEST_DURATION.labels(method=method, endpoint=path).observe(duration)

    return response