#!/usr/bin/env python3
"""
Verify OpenTelemetry package installation.
"""

def verify_packages():
    """Verify all required OpenTelemetry packages are installed."""
    try:
        print("Verifying OpenTelemetry packages...")

        # Core packages
        import opentelemetry
        from opentelemetry import trace, metrics
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.resources import Resource

        # Exporters
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

        # Processing
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

        # Instrumentation
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

        # Context propagation
        from opentelemetry.propagate import set_global_textmap
        from opentelemetry.propagators.composite import CompositePropagator
        from opentelemetry.propagators.tracecontext import TraceContextTextMapPropagator
        from opentelemetry.propagators.baggage import BaggagePropagator

        # Prometheus
        from prometheus_client import Counter, Histogram, Gauge, generate_latest

        print("✅ All OpenTelemetry packages are installed correctly.")
        return True

    except ImportError as e:
        print(f"❌ Missing package: {e}")
        return False

if __name__ == "__main__":
    verify_packages()