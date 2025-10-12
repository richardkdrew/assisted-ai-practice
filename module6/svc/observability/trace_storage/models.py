"""
Data models for span storage and querying.

This module defines the data models for spans that are stored by the
file-based span processor and used for querying.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class StoredSpan:
    """
    Represents a stored OpenTelemetry span.

    This class contains all the information from an OpenTelemetry span
    in a serializable format suitable for storage and querying.
    """

    trace_id: str  # Trace identifier (32-character hex string)
    span_id: str  # Span identifier (16-character hex string)
    parent_span_id: Optional[str] = None  # Parent span ID (or None for root spans)
    name: str = ""  # Operation name
    status: str = "OK"  # "OK" or "ERROR"
    status_description: Optional[str] = None  # Status description (for errors)
    start_time: int = 0  # Start time (nanoseconds since epoch)
    end_time: int = 0  # End time (nanoseconds since epoch)
    duration_ns: int = 0  # Duration in nanoseconds
    attributes: Dict[str, Any] = field(default_factory=dict)  # Span attributes
    events: List[Dict[str, Any]] = field(default_factory=list)  # Time-stamped events
    links: List[Dict[str, Any]] = field(default_factory=list)  # Links to other spans
    service_name: str = ""  # Service that created the span
    resource_attributes: Dict[str, Any] = field(default_factory=dict)  # Resource attributes

    def __post_init__(self):
        """Validate span data after initialization."""
        self._validate()

        # Calculate duration if not explicitly provided
        if self.duration_ns == 0 and self.start_time > 0 and self.end_time > 0:
            self.duration_ns = self.end_time - self.start_time

    def _validate(self):
        """Validate the span data."""
        if not self.trace_id or len(self.trace_id) != 32:
            raise ValueError(f"Invalid trace_id: {self.trace_id}. Must be 32-character hex string.")

        if not self.span_id or len(self.span_id) != 16:
            raise ValueError(f"Invalid span_id: {self.span_id}. Must be 16-character hex string.")

        if self.parent_span_id is not None and len(self.parent_span_id) != 16:
            raise ValueError(f"Invalid parent_span_id: {self.parent_span_id}. Must be 16-character hex string or None.")

        if self.status not in ["OK", "ERROR"]:
            raise ValueError(f"Invalid status: {self.status}. Must be 'OK' or 'ERROR'.")

        if self.end_time < self.start_time:
            raise ValueError(f"Invalid timestamps: end_time ({self.end_time}) before start_time ({self.start_time}).")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the span to a dictionary for serialization."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "status": self.status,
            "status_description": self.status_description,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ns": self.duration_ns,
            "attributes": self.attributes,
            "events": self.events,
            "links": self.links,
            "service_name": self.service_name,
            "resource_attributes": self.resource_attributes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoredSpan":
        """Create a StoredSpan from a dictionary."""
        return cls(**data)


@dataclass
class AttributeFilter:
    """
    Filter for span attributes.

    Used to filter spans based on attribute key-value pairs with
    comparison operators.
    """

    key: str  # Attribute key
    value: Any  # Value to match
    operator: str = "EQUALS"  # Comparison operator

    VALID_OPERATORS = ["EQUALS", "NOT_EQUALS", "CONTAINS", "GREATER_THAN", "LESS_THAN"]

    def __post_init__(self):
        """Validate filter after initialization."""
        if not self.key:
            raise ValueError("Attribute key cannot be empty")

        if self.operator not in self.VALID_OPERATORS:
            raise ValueError(f"Invalid operator: {self.operator}. Must be one of {self.VALID_OPERATORS}")

    def matches(self, span: StoredSpan) -> bool:
        """
        Check if the span matches this filter.

        Args:
            span: The span to check

        Returns:
            True if the span matches the filter, False otherwise
        """
        # Check if the key exists in span attributes
        if self.key not in span.attributes:
            return False

        span_value = span.attributes[self.key]

        if self.operator == "EQUALS":
            return span_value == self.value
        elif self.operator == "NOT_EQUALS":
            return span_value != self.value
        elif self.operator == "CONTAINS":
            # Handle string contains and list/dict contains
            if isinstance(span_value, str) and isinstance(self.value, str):
                return self.value in span_value
            elif isinstance(span_value, (list, tuple, set)):
                return self.value in span_value
            elif isinstance(span_value, dict) and isinstance(self.value, str):
                return self.value in span_value
            return False
        elif self.operator == "GREATER_THAN":
            try:
                return span_value > self.value
            except TypeError:
                return False
        elif self.operator == "LESS_THAN":
            try:
                return span_value < self.value
            except TypeError:
                return False

        return False


@dataclass
class SpanQuery:
    """
    Query parameters for span filtering.

    This class defines the criteria for filtering spans in queries.
    Multiple criteria can be combined (with AND logic).
    """

    trace_id: Optional[str] = None  # Filter by trace ID
    span_ids: Optional[List[str]] = None  # Filter by span IDs
    status: Optional[str] = None  # Filter by status ("OK" or "ERROR")
    service_name: Optional[str] = None  # Filter by service name
    operation_name: Optional[str] = None  # Filter by operation name
    start_time_min: Optional[int] = None  # Min start time (nanoseconds)
    start_time_max: Optional[int] = None  # Max start time (nanoseconds)
    attribute_filters: Optional[List[AttributeFilter]] = None  # Attribute filters
    max_spans: int = 100  # Max results to return
    order_by: str = "start_time"  # Field to sort by
    order_direction: str = "DESC"  # Sort direction

    VALID_ORDER_FIELDS = ["start_time", "end_time", "duration_ns"]
    VALID_DIRECTIONS = ["ASC", "DESC"]

    def __post_init__(self):
        """Validate query parameters after initialization."""
        if self.span_ids is None:
            self.span_ids = []

        if self.attribute_filters is None:
            self.attribute_filters = []

        # Initialize empty lists
        if isinstance(self.span_ids, list) and not self.span_ids:
            self.span_ids = None

        if isinstance(self.attribute_filters, list) and not self.attribute_filters:
            self.attribute_filters = None

        self._validate()

    def _validate(self):
        """Validate query parameters."""
        if self.trace_id is not None and len(self.trace_id) != 32:
            raise ValueError(f"Invalid trace_id: {self.trace_id}. Must be 32-character hex string.")

        if self.span_ids is not None:
            for span_id in self.span_ids:
                if len(span_id) != 16:
                    raise ValueError(f"Invalid span_id in span_ids: {span_id}. Must be 16-character hex string.")

        if self.status is not None and self.status not in ["OK", "ERROR"]:
            raise ValueError(f"Invalid status: {self.status}. Must be 'OK' or 'ERROR'.")

        if self.max_spans <= 0:
            raise ValueError(f"Invalid max_spans: {self.max_spans}. Must be positive.")

        if self.order_by not in self.VALID_ORDER_FIELDS:
            raise ValueError(f"Invalid order_by: {self.order_by}. Must be one of {self.VALID_ORDER_FIELDS}.")

        if self.order_direction not in self.VALID_DIRECTIONS:
            raise ValueError(f"Invalid order_direction: {self.order_direction}. Must be 'ASC' or 'DESC'.")

        if self.start_time_min is not None and self.start_time_max is not None:
            if self.start_time_min > self.start_time_max:
                raise ValueError(
                    f"Invalid time range: start_time_min ({self.start_time_min}) > "
                    f"start_time_max ({self.start_time_max})."
                )