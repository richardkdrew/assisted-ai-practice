"""OpenTelemetry setup and configuration.

This module handles setting up OpenTelemetry instrumentation for the application,
including trace providers, exporters, and instrumentation.
"""

import os
from fastapi import FastAPI

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
from opentelemetry.propagate import set_global_textmap
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from observability.trace_storage.file_span_processor import FileBasedSpanProcessor
from observability.middleware import ErrorTrackingMiddleware
from observability.metrics import metrics_endpoint, metrics_middleware
from observability.routes import register_trace_routes


def setup_observability(app: FastAPI):
    """Set up OpenTelemetry and Prometheus metrics for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    # Resource identification
    resource = Resource.create({
        "service.name": "configuration-service",
        "service.version": "1.0.0",
        "service.environment": os.getenv("ENVIRONMENT", "development"),
    })

    # Configure tracing
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer_provider = trace.get_tracer_provider()

    # Configure propagator for distributed tracing
    # Using only the TraceContextTextMapPropagator which is standard and should be available
    set_global_textmap(TraceContextTextMapPropagator())

    # OTLP exporter for traces
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317"),
        insecure=True
    )
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    # File-based span processor for local trace storage and querying
    trace_storage_path = os.getenv("TRACE_STORAGE_PATH", "data/traces/trace_storage.jsonl")
    max_spans = int(os.getenv("TRACE_MAX_SPANS", "1000"))

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(trace_storage_path), exist_ok=True)

    # Add file-based span processor
    file_span_processor = FileBasedSpanProcessor(
        file_path=trace_storage_path,
        max_spans=max_spans
    )
    tracer_provider.add_span_processor(file_span_processor)

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
    app.get("/metrics")(metrics_endpoint)

    # Add trace API endpoints
    register_trace_routes(app)

    # Add middleware for request metrics
    app.middleware("http")(metrics_middleware)

    # Add error tracking middleware
    app.add_middleware(ErrorTrackingMiddleware)