"""File-based span exporter for OpenTelemetry."""

import json
from pathlib import Path
from typing import Sequence

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult


class FileSpanExporter(SpanExporter):
    """Exports spans to JSON files organized by trace ID."""

    def __init__(self, traces_dir: Path):
        """Initialize the exporter with a directory for trace files."""
        self.traces_dir = Path(traces_dir)
        self.traces_dir.mkdir(parents=True, exist_ok=True)
        self._spans_buffer: dict[str, list[dict]] = {}

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export spans to files grouped by trace ID."""
        try:
            for span in spans:
                trace_id = format(span.context.trace_id, "032x")
                span_data = {
                    "name": span.name,
                    "span_id": format(span.context.span_id, "016x"),
                    "trace_id": trace_id,
                    "parent_span_id": (
                        format(span.parent.span_id, "016x") if span.parent else None
                    ),
                    "start_time": span.start_time,
                    "end_time": span.end_time,
                    "duration_ns": span.end_time - span.start_time if span.end_time else 0,
                    "attributes": dict(span.attributes) if span.attributes else {},
                    "status": span.status.status_code.name if span.status else "UNSET",
                }

                if trace_id not in self._spans_buffer:
                    self._spans_buffer[trace_id] = []
                self._spans_buffer[trace_id].append(span_data)

            return SpanExportResult.SUCCESS
        except Exception as e:
            print(f"Error exporting spans: {e}")
            return SpanExportResult.FAILURE

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Write all buffered spans to files."""
        try:
            for trace_id, spans in self._spans_buffer.items():
                file_path = self.traces_dir / f"{trace_id}.json"

                # Load existing spans if file exists
                existing_spans = []
                if file_path.exists():
                    existing_spans = json.loads(file_path.read_text())

                # Append new spans and write back
                all_spans = existing_spans + spans
                file_path.write_text(json.dumps(all_spans, indent=2))

            self._spans_buffer.clear()
            return True
        except Exception as e:
            print(f"Error flushing spans: {e}")
            return False

    def shutdown(self) -> None:
        """Shutdown the exporter and flush remaining spans."""
        self.force_flush()
