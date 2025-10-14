"""OpenTelemetry tracer setup and utilities."""

from pathlib import Path

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from observability.exporter import FileSpanExporter

_tracer_provider: TracerProvider | None = None
_tracer: trace.Tracer | None = None


def setup_tracer(traces_dir: Path) -> None:
    """Initialize the tracer provider with file-based export."""
    global _tracer_provider, _tracer

    _tracer_provider = TracerProvider()
    exporter = FileSpanExporter(traces_dir)
    processor = BatchSpanProcessor(exporter)
    _tracer_provider.add_span_processor(processor)
    trace.set_tracer_provider(_tracer_provider)
    _tracer = trace.get_tracer(__name__)


def get_tracer() -> trace.Tracer:
    """Get the configured tracer instance."""
    if _tracer is None:
        raise RuntimeError("Tracer not initialized. Call setup_tracer() first.")
    return _tracer


def get_trace_id() -> str:
    """Get the current trace ID as a hex string."""
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().trace_id, "032x")
    return ""


def flush_traces() -> None:
    """Force flush all pending traces to disk."""
    if _tracer_provider:
        _tracer_provider.force_flush()
