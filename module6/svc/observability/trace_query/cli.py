"""
Command-line interface for trace queries.

This module provides a CLI for querying traces stored by the file-based
span processor, making it easy to search and analyze traces from the
command line.

Available Commands:
- trace: Get all spans for a specific trace ID
- failures: Show recent spans with ERROR status
- status: Filter spans by status (OK or ERROR)
- time: Filter spans by time range
- error-type: Filter spans by error type
- attribute: Filter spans by attribute key-value pair
- query: Advanced query with multiple filters

Common Options:
- --json: Output results in JSON format
- --all-attributes: Include all span attributes in output
- --limit: Maximum number of results to return

Examples:
    # Get a trace by ID
    trace-query trace 01234567890123456789012345678901

    # Show the 5 most recent failures
    trace-query failures --hours 1 --limit 5

    # Filter by status with time window
    trace-query status ERROR --duration 30m

    # Filter by time range
    trace-query time --start "2023-06-01T12:00:00" --end "2023-06-01T13:00:00"
    trace-query time --duration 15m --status ERROR

    # Filter by error type
    trace-query error-type ConnectionError

    # Filter by attribute
    trace-query attribute http.status_code 500
    trace-query attribute http.method GET --limit 10

    # Advanced query with multiple filters
    trace-query query --status ERROR --service auth-service --attr error.type ConnectionError

    # Output in JSON format
    trace-query failures --json
"""

import argparse
import json
import sys
import time
from datetime import datetime
from typing import List, Optional

from ..trace_storage.models import AttributeFilter, SpanQuery, StoredSpan
from . import (
    get_trace,
    recent_failures,
    filter_by_error_type,
    filter_by_attribute,
    filter_by_status,
    filter_by_time,
    query_spans,
)


def format_span(span: StoredSpan, include_attributes: bool = False) -> str:
    """
    Format a span for display on the command line.

    Args:
        span: The span to format
        include_attributes: Whether to include all attributes

    Returns:
        Formatted string representation of the span
    """
    # Format timestamps as human-readable
    start_time = datetime.fromtimestamp(span.start_time / 1e9).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    end_time = datetime.fromtimestamp(span.end_time / 1e9).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    duration_ms = span.duration_ns / 1e6

    # Format the basic span info
    result = [
        f"Span: {span.name}",
        f"  ID: {span.span_id}",
        f"  Trace: {span.trace_id}",
        f"  Parent: {span.parent_span_id or 'None (root span)'}",
        f"  Status: {span.status}" + (f" ({span.status_description})" if span.status_description else ""),
        f"  Service: {span.service_name}",
        f"  Timing: {start_time} -> {end_time} ({duration_ms:.3f} ms)",
    ]

    # Add selected attributes that are usually important
    attr_lines = []
    if "http.method" in span.attributes and "http.url" in span.attributes:
        attr_lines.append(f"  HTTP: {span.attributes['http.method']} {span.attributes['http.url']}")

    if "http.status_code" in span.attributes:
        attr_lines.append(f"  Status Code: {span.attributes['http.status_code']}")

    if "error.type" in span.attributes:
        error_msg = span.attributes.get("error.message", "")
        attr_lines.append(f"  Error: {span.attributes['error.type']} - {error_msg}")

    # Include all attributes if requested
    if include_attributes:
        if span.attributes and not attr_lines:
            attr_lines.append("  Attributes:")
            for key, value in span.attributes.items():
                attr_lines.append(f"    {key}: {value}")

    # Add events if there are any
    if span.events:
        attr_lines.append(f"  Events: {len(span.events)}")
        for event in span.events[:3]:  # Show first 3 events only
            event_time = datetime.fromtimestamp(event["timestamp"] / 1e9).strftime("%H:%M:%S.%f")[:-3]
            attr_lines.append(f"    [{event_time}] {event['name']}")
        if len(span.events) > 3:
            attr_lines.append(f"    ... {len(span.events) - 3} more events")

    return "\n".join(result + attr_lines)


def format_trace(spans: List[StoredSpan], include_attributes: bool = False) -> str:
    """
    Format a trace (collection of spans) for display on the command line.

    Args:
        spans: The spans to format
        include_attributes: Whether to include all attributes

    Returns:
        Formatted string representation of the trace
    """
    if not spans:
        return "No spans found"

    # Create a map of span_id to children
    children = {}
    for span in spans:
        if span.parent_span_id:
            if span.parent_span_id not in children:
                children[span.parent_span_id] = []
            children[span.parent_span_id].append(span)

    # Find root spans (those without parents or with parents outside this trace)
    parent_ids = {span.parent_span_id for span in spans if span.parent_span_id}
    span_ids = {span.span_id for span in spans}
    root_span_ids = span_ids - parent_ids

    if not root_span_ids:
        # If we can't find root spans, just use all spans
        return "\n\n".join(format_span(span, include_attributes) for span in spans)

    # Format the trace in a tree structure
    result = []

    def format_span_tree(span_id: str, depth: int = 0):
        """Recursively format a span and its children."""
        span = next((s for s in spans if s.span_id == span_id), None)
        if not span:
            return

        # Add this span with proper indentation
        indent = "  " * depth
        formatted = format_span(span, include_attributes)
        result.append("\n".join(f"{indent}{line}" if i > 0 else line
                               for i, line in enumerate(formatted.split("\n"))))

        # Add children
        for child in children.get(span_id, []):
            format_span_tree(child.span_id, depth + 1)

    # Start with root spans
    for root_id in root_span_ids:
        root_span = next(s for s in spans if s.span_id == root_id)
        format_span_tree(root_span.span_id)

    return "\n\n".join(result)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Command-line interface for querying OpenTelemetry traces"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Get trace by ID
    trace_parser = subparsers.add_parser("trace", help="Get a trace by ID")
    trace_parser.add_argument("trace_id", help="32-character hex trace ID")
    trace_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    trace_parser.add_argument("--all-attributes", action="store_true", help="Include all attributes")

    # Recent failures
    failures_parser = subparsers.add_parser("failures", help="Show recent failures")
    failures_parser.add_argument("--hours", type=float, default=1, help="Hours to look back (default: 1)")
    failures_parser.add_argument("--limit", type=int, default=10, help="Maximum number of results (default: 10)")
    failures_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    failures_parser.add_argument("--all-attributes", action="store_true", help="Include all attributes")

    # Filter by status
    status_parser = subparsers.add_parser("status", help="Filter by status")
    status_parser.add_argument("status", choices=["OK", "ERROR"], help="Status to filter by")
    status_parser.add_argument("--duration", default="1h", help="Time duration to look back (e.g., 1h, 30m, 2d)")
    status_parser.add_argument("--limit", type=int, default=10, help="Maximum number of results (default: 10)")
    status_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    status_parser.add_argument("--all-attributes", action="store_true", help="Include all attributes")

    # Filter by time
    time_parser = subparsers.add_parser("time", help="Filter by time range")
    time_parser.add_argument("--start", help="Start time (ISO format or relative time)")
    time_parser.add_argument("--end", help="End time (ISO format or relative time)")
    time_parser.add_argument("--duration", help="Duration (e.g., 1h, 30m, 2d)")
    time_parser.add_argument("--status", choices=["OK", "ERROR"], help="Status to filter by")
    time_parser.add_argument("--limit", type=int, default=10, help="Maximum number of results (default: 10)")
    time_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    time_parser.add_argument("--all-attributes", action="store_true", help="Include all attributes")

    # Filter by error type
    error_parser = subparsers.add_parser("error-type", help="Filter by error type")
    error_parser.add_argument("error_type", help="Error type to filter by")
    error_parser.add_argument("--limit", type=int, default=10, help="Maximum number of results (default: 10)")
    error_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    error_parser.add_argument("--all-attributes", action="store_true", help="Include all attributes")

    # Filter by attribute
    attr_parser = subparsers.add_parser("attribute", help="Filter by attribute")
    attr_parser.add_argument("key", help="Attribute key")
    attr_parser.add_argument("value", help="Attribute value")
    attr_parser.add_argument("--limit", type=int, default=10, help="Maximum number of results (default: 10)")
    attr_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    attr_parser.add_argument("--all-attributes", action="store_true", help="Include all attributes")

    # Generic query
    query_parser = subparsers.add_parser("query", help="Advanced query with multiple filters")
    query_parser.add_argument("--trace-id", help="Trace ID to filter by")
    query_parser.add_argument("--status", choices=["OK", "ERROR"], help="Status to filter by")
    query_parser.add_argument("--service", help="Service name to filter by")
    query_parser.add_argument("--operation", help="Operation name to filter by")
    query_parser.add_argument("--start", help="Start time (ISO format or relative time)")
    query_parser.add_argument("--end", help="End time (ISO format or relative time)")
    query_parser.add_argument("--attr", nargs=2, action="append", metavar=("KEY", "VALUE"),
                             help="Attribute filter (can be specified multiple times)")
    query_parser.add_argument("--limit", type=int, default=10, help="Maximum number of results (default: 10)")
    query_parser.add_argument("--order-by", choices=["start_time", "end_time", "duration_ns"],
                             default="end_time", help="Field to sort by (default: end_time)")
    query_parser.add_argument("--direction", choices=["ASC", "DESC"],
                             default="DESC", help="Sort direction (default: DESC)")
    query_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    query_parser.add_argument("--all-attributes", action="store_true", help="Include all attributes")

    return parser.parse_args()


def main():
    """Main entry point for the CLI."""
    args = parse_args()

    if args.command is None:
        print("No command specified. Use --help for usage information.")
        sys.exit(1)

    try:
        spans = []

        # Execute the requested command
        if args.command == "trace":
            spans = get_trace(args.trace_id)

        elif args.command == "failures":
            spans = recent_failures(hours=args.hours, max_results=args.limit)

        elif args.command == "status":
            spans = filter_by_status(
                status=args.status,
                time_range=args.duration,
                max_results=args.limit
            )

        elif args.command == "time":
            spans = filter_by_time(
                start_time=args.start,
                end_time=args.end,
                duration=args.duration,
                status=args.status,
                max_results=args.limit
            )

        elif args.command == "error-type":
            spans = filter_by_error_type(
                error_type=args.error_type,
                max_results=args.limit
            )

        elif args.command == "attribute":
            spans = filter_by_attribute(
                key=args.key,
                value=args.value,
                max_results=args.limit
            )

        elif args.command == "query":
            # Build attribute filters if specified
            attribute_filters = None
            if args.attr:
                attribute_filters = [
                    AttributeFilter(key=key, value=value)
                    for key, value in args.attr
                ]

            # Create query
            query = SpanQuery(
                trace_id=args.trace_id,
                status=args.status,
                service_name=args.service,
                operation_name=args.operation,
                start_time_min=args.start,
                start_time_max=args.end,
                attribute_filters=attribute_filters,
                max_spans=args.limit,
                order_by=args.order_by,
                order_direction=args.direction,
            )

            spans = query_spans(query)

        # Output the results
        if args.json:
            # JSON output
            span_dicts = [span.__dict__ for span in spans]
            print(json.dumps({"count": len(spans), "spans": span_dicts}, indent=2))
        else:
            # Human-readable output
            if args.command == "trace":
                # Format as a trace with parent-child relationships
                print(format_trace(spans, args.all_attributes))
            else:
                # Format as a list of spans
                if spans:
                    print(f"Found {len(spans)} spans:")
                    for i, span in enumerate(spans):
                        if i > 0:
                            print("\n" + "-" * 80 + "\n")
                        print(format_span(span, args.all_attributes))
                else:
                    print("No spans found")

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()