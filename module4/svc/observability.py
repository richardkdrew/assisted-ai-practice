"""OpenTelemetry instrumentation for Configuration Service."""

import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response


# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status_code'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
DB_CONNECTIONS = Gauge('database_connections_active', 'Active database connections')
CONFIG_COUNT = Gauge('configurations_total', 'Total number of configurations')
APP_COUNT = Gauge('applications_total', 'Total number of applications')


def setup_observability(app):
    """Set up OpenTelemetry and Prometheus metrics for the FastAPI application."""

    # Resource identification
    resource = Resource.create({
        "service.name": "configuration-service",
        "service.version": "1.0.0",
        "service.environment": os.getenv("ENVIRONMENT", "development"),
    })

    # Configure tracing
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer_provider = trace.get_tracer_provider()

    # OTLP exporter for traces
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317"),
        insecure=True
    )
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    # Configure metrics
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317"),
            insecure=True
        ),
        export_interval_millis=5000,
    )
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Instrument requests library
    RequestsInstrumentor().instrument()

    # Instrument psycopg2 for database monitoring
    Psycopg2Instrumentor().instrument()

    # Add Prometheus metrics endpoint
    @app.get("/metrics")
    async def metrics_endpoint():
        """Prometheus metrics endpoint."""
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    # Add middleware for request metrics
    @app.middleware("http")
    async def metrics_middleware(request, call_next):
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


def update_business_metrics(applications_count: int, configurations_count: int, active_connections: int):
    """Update business and infrastructure metrics."""
    APP_COUNT.set(applications_count)
    CONFIG_COUNT.set(configurations_count)
    DB_CONNECTIONS.set(active_connections)


# Tracer instance for manual instrumentation
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)