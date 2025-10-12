"""
Thread-safe span storage and indexing.

This module provides a thread-safe container for storing spans in memory
with efficient indexing for various query patterns. It implements a
read-write lock pattern and copy-on-read functionality.
"""

import copy
import threading
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set

from .models import AttributeFilter, SpanQuery, StoredSpan


class ReadWriteLock:
    """
    A read-write lock implementation.

    This lock allows multiple readers to access the data simultaneously,
    but writers must have exclusive access. Writers are prioritized over
    readers to prevent writer starvation.
    """

    def __init__(self):
        """Initialize the read-write lock."""
        self._read_ready = threading.Condition(threading.RLock())
        self._readers = 0
        self._writers = 0
        self._write_waiting = 0
        self._promoting = False

    def acquire_read(self):
        """
        Acquire a read lock.

        Multiple threads can hold the read lock simultaneously as long as
        no thread holds the write lock.
        """
        with self._read_ready:
            while self._writers > 0 or self._write_waiting > 0:
                self._read_ready.wait()
            self._readers += 1

    def release_read(self):
        """Release a read lock."""
        with self._read_ready:
            self._readers -= 1
            if self._readers == 0:
                self._read_ready.notify_all()

    def acquire_write(self):
        """
        Acquire a write lock.

        Only one thread can hold the write lock, and no thread can hold
        the read lock while a thread holds the write lock.
        """
        with self._read_ready:
            self._write_waiting += 1
            while self._readers > 0 or self._writers > 0:
                self._read_ready.wait()
            self._write_waiting -= 1
            self._writers += 1

    def release_write(self):
        """Release a write lock."""
        with self._read_ready:
            self._writers -= 1
            self._read_ready.notify_all()

    def __enter__(self):
        """Context manager entry for write lock."""
        self.acquire_write()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit for write lock."""
        self.release_write()


class ReadLock:
    """Context manager for read lock."""

    def __init__(self, rwlock):
        """Initialize with a ReadWriteLock instance."""
        self.rwlock = rwlock

    def __enter__(self):
        """Acquire read lock on enter."""
        self.rwlock.acquire_read()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release read lock on exit."""
        self.rwlock.release_read()


class WriteLock:
    """Context manager for write lock."""

    def __init__(self, rwlock):
        """Initialize with a ReadWriteLock instance."""
        self.rwlock = rwlock

    def __enter__(self):
        """Acquire write lock on enter."""
        self.rwlock.acquire_write()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release write lock on exit."""
        self.rwlock.release_write()


class SpanStore:
    """
    Thread-safe in-memory span storage with indexing.

    This class maintains an in-memory store of spans with indices for
    efficient querying by trace ID, span ID, time ranges, status, and
    attributes. It implements a read-write lock pattern for thread safety
    and uses copy-on-read to avoid concurrency issues.
    """

    def __init__(self, max_spans: int = 1000):
        """
        Initialize the span store.

        Args:
            max_spans: Maximum number of spans to retain

        Raises:
            ValueError: If max_spans <= 0
        """
        if max_spans <= 0:
            raise ValueError(f"Invalid max_spans: {max_spans}. Must be positive.")

        self.max_spans = max_spans
        self._spans: List[StoredSpan] = []
        self._trace_index: Dict[str, List[int]] = defaultdict(list)  # trace_id -> [indices]
        self._span_index: Dict[str, int] = {}  # span_id -> index
        self._status_index: Dict[str, List[int]] = defaultdict(list)  # status -> [indices]
        self._time_index: List[int] = []  # indices sorted by start_time
        self._end_time_index: List[int] = []  # indices sorted by end_time

        # Enhanced time-based indexing
        self._time_buckets: Dict[int, List[int]] = defaultdict(list)  # hour bucket -> [indices]
        self._status_time_index: Dict[str, Dict[int, List[int]]] = {  # status -> hour bucket -> [indices]
            "OK": defaultdict(list),
            "ERROR": defaultdict(list),
        }

        self._attribute_index: Dict[str, Dict[Any, List[int]]] = defaultdict(lambda: defaultdict(list))  # key -> value -> [indices]
        self._service_index: Dict[str, List[int]] = defaultdict(list)  # service_name -> [indices]
        self._operation_index: Dict[str, List[int]] = defaultdict(list)  # operation_name -> [indices]
        self._lock = ReadWriteLock()

    def add_span(self, span: StoredSpan) -> None:
        """
        Add a span to the store.

        This method adds a span to the in-memory store and updates all
        indices. If the store contains more than max_spans, the oldest
        spans are removed.

        Args:
            span: The span to add

        Raises:
            ValueError: If the span is invalid
        """
        # Make a defensive copy of the span
        span_copy = copy.deepcopy(span)

        with WriteLock(self._lock):
            # Add the span to the store
            index = len(self._spans)
            self._spans.append(span_copy)

            # Update indices
            self._update_indices(index, span_copy)

            # Enforce the maximum span limit
            self._enforce_max_spans()

    def _update_indices(self, index: int, span: StoredSpan) -> None:
        """
        Update all indices for a span.

        Args:
            index: The index of the span in the store
            span: The span to index
        """
        # Update trace index
        self._trace_index[span.trace_id].append(index)

        # Update span index
        self._span_index[span.span_id] = index

        # Update status index
        self._status_index[span.status].append(index)

        # Update time indices
        # For start time
        self._time_index.append(index)
        self._time_index.sort(key=lambda i: self._spans[i].start_time)

        # For end time
        self._end_time_index.append(index)
        self._end_time_index.sort(key=lambda i: self._spans[i].end_time)

        # Update time buckets (hourly granularity)
        # Convert nanoseconds to hour buckets (integer division by 3.6e12)
        start_hour_bucket = span.start_time // 3_600_000_000_000
        self._time_buckets[start_hour_bucket].append(index)

        # Update combined status-time index
        self._status_time_index[span.status][start_hour_bucket].append(index)

        # Update attribute index
        for key, value in span.attributes.items():
            self._attribute_index[key][value].append(index)

        # Update service index
        self._service_index[span.service_name].append(index)

        # Update operation index
        self._operation_index[span.name].append(index)

    def _enforce_max_spans(self) -> None:
        """
        Enforce the maximum span limit using FIFO eviction.

        This method removes the oldest spans when the number of spans
        exceeds the maximum limit, and updates all indices accordingly.

        For better performance, it removes spans in batches when the list
        grows significantly beyond the limit, which reduces the number of
        reindexing operations needed.
        """
        current_size = len(self._spans)

        # If we're only slightly over the limit, remove one at a time
        if current_size <= self.max_spans * 1.1:  # Up to 10% over limit
            while len(self._spans) > self.max_spans:
                self._remove_span(0)
            return

        # For larger overages, calculate how many spans to remove
        spans_to_remove = current_size - self.max_spans

        # Remove spans in batches for better performance
        # We'll remove from oldest to newest (index 0 to spans_to_remove-1)

        # First, collect all the spans we'll remove
        spans_to_keep = self._spans[spans_to_remove:]
        spans_being_removed = self._spans[:spans_to_remove]

        # Then update all indices at once
        # We need to remove these spans from all indices

        # Clear the span list and rebuild it
        self._spans = []
        self._trace_index.clear()
        self._span_index.clear()
        self._status_index.clear()
        self._time_index.clear()
        self._end_time_index.clear()
        self._time_buckets.clear()
        for status in self._status_time_index:
            self._status_time_index[status].clear()
        self._attribute_index.clear()
        self._service_index.clear()
        self._operation_index.clear()

        # Re-add the spans we're keeping
        for span in spans_to_keep:
            index = len(self._spans)
            self._spans.append(span)
            self._update_indices(index, span)

    def _remove_span(self, index: int) -> None:
        """
        Remove a span from the store and update all indices.

        Args:
            index: The index of the span to remove
        """
        span = self._spans[index]

        # Remove from trace index
        self._trace_index[span.trace_id].remove(index)
        if not self._trace_index[span.trace_id]:
            del self._trace_index[span.trace_id]

        # Remove from span index
        del self._span_index[span.span_id]

        # Remove from status index
        self._status_index[span.status].remove(index)
        if not self._status_index[span.status]:
            del self._status_index[span.status]

        # Remove from time indices
        self._time_index.remove(index)
        self._end_time_index.remove(index)

        # Remove from time buckets
        start_hour_bucket = span.start_time // 3_600_000_000_000
        if index in self._time_buckets[start_hour_bucket]:
            self._time_buckets[start_hour_bucket].remove(index)
        if not self._time_buckets[start_hour_bucket]:
            del self._time_buckets[start_hour_bucket]

        # Remove from status-time index
        if index in self._status_time_index[span.status][start_hour_bucket]:
            self._status_time_index[span.status][start_hour_bucket].remove(index)
        if not self._status_time_index[span.status][start_hour_bucket]:
            del self._status_time_index[span.status][start_hour_bucket]

        # Remove from attribute index
        for key, value in span.attributes.items():
            self._attribute_index[key][value].remove(index)
            if not self._attribute_index[key][value]:
                del self._attribute_index[key][value]
            if not self._attribute_index[key]:
                del self._attribute_index[key]

        # Remove from service index
        self._service_index[span.service_name].remove(index)
        if not self._service_index[span.service_name]:
            del self._service_index[span.service_name]

        # Remove from operation index
        self._operation_index[span.name].remove(index)
        if not self._operation_index[span.name]:
            del self._operation_index[span.name]

        # Remove the span from the store
        self._spans.pop(index)

        # Update indices for spans after the removed one
        self._reindex_spans(index)

    def _reindex_spans(self, start_index: int) -> None:
        """
        Update all indices after a span is removed.

        Args:
            start_index: The index where the span was removed
        """
        # For each index, update references to account for the shift
        for trace_indices in self._trace_index.values():
            for i, idx in enumerate(trace_indices):
                if idx > start_index:
                    trace_indices[i] = idx - 1

        for span_id, idx in list(self._span_index.items()):
            if idx > start_index:
                self._span_index[span_id] = idx - 1

        for status_indices in self._status_index.values():
            for i, idx in enumerate(status_indices):
                if idx > start_index:
                    status_indices[i] = idx - 1

        # Update time indices
        for i, idx in enumerate(self._time_index):
            if idx > start_index:
                self._time_index[i] = idx - 1

        for i, idx in enumerate(self._end_time_index):
            if idx > start_index:
                self._end_time_index[i] = idx - 1

        # Update time buckets
        for bucket_indices in self._time_buckets.values():
            for i, idx in enumerate(bucket_indices):
                if idx > start_index:
                    bucket_indices[i] = idx - 1

        # Update status-time index
        for status, buckets in self._status_time_index.items():
            for bucket, indices in buckets.items():
                for i, idx in enumerate(indices):
                    if idx > start_index:
                        indices[i] = idx - 1

        # Update attribute index
        for key_dict in self._attribute_index.values():
            for value_indices in key_dict.values():
                for i, idx in enumerate(value_indices):
                    if idx > start_index:
                        value_indices[i] = idx - 1

        # Update service and operation indices
        for service_indices in self._service_index.values():
            for i, idx in enumerate(service_indices):
                if idx > start_index:
                    service_indices[i] = idx - 1

        for operation_indices in self._operation_index.values():
            for i, idx in enumerate(operation_indices):
                if idx > start_index:
                    operation_indices[i] = idx - 1

    def get_spans(self, query: SpanQuery = None) -> List[StoredSpan]:
        """
        Get spans that match the given query.

        This method uses copy-on-read to avoid concurrency issues.

        Args:
            query: The query to filter spans by (returns all spans if None)

        Returns:
            List of spans that match the query

        Raises:
            ValueError: If the query is invalid
        """
        with ReadLock(self._lock):
            # Use a query with default values if None is provided
            if query is None:
                query = SpanQuery()

            # Find matching indices
            matching_indices = self._get_matching_indices(query)

            # Sort the results
            matching_indices = self._sort_indices(matching_indices, query)

            # Limit the results
            if len(matching_indices) > query.max_spans:
                matching_indices = matching_indices[:query.max_spans]

            # Return copies of the matching spans
            return [copy.deepcopy(self._spans[i]) for i in matching_indices]

    def _get_matching_indices(self, query: SpanQuery) -> Set[int]:
        """
        Get the indices of spans that match the query.

        Args:
            query: The query to filter spans by

        Returns:
            Set of indices of matching spans
        """
        # Start with all spans as candidates
        candidates = set(range(len(self._spans)))

        # Filter by trace ID (most specific filter first)
        if query.trace_id is not None:
            trace_indices = set(self._trace_index.get(query.trace_id, []))
            candidates &= trace_indices
            if not candidates:
                return set()  # Early exit if no matches

        # Filter by span IDs
        if query.span_ids is not None and query.span_ids:
            span_indices = {self._span_index.get(span_id) for span_id in query.span_ids if span_id in self._span_index}
            candidates &= span_indices
            if not candidates:
                return set()  # Early exit if no matches

        # Filter by status
        if query.status is not None:
            status_indices = set(self._status_index.get(query.status, []))
            candidates &= status_indices
            if not candidates:
                return set()  # Early exit if no matches

        # Filter by time range - use optimized time buckets when possible
        if query.start_time_min is not None or query.start_time_max is not None:
            # If we have both a time range and status filter, use the combined index
            if query.status is not None and query.start_time_min is not None:
                time_indices = set()

                # Convert min time to hour buckets
                min_hour_bucket = query.start_time_min // 3_600_000_000_000

                # Get max hour bucket if max time is specified
                max_hour_bucket = None
                if query.start_time_max is not None:
                    max_hour_bucket = (query.start_time_max // 3_600_000_000_000) + 1

                # Get all spans from appropriate buckets
                status_buckets = self._status_time_index[query.status]
                for bucket, indices in status_buckets.items():
                    if bucket >= min_hour_bucket and (max_hour_bucket is None or bucket <= max_hour_bucket):
                        # For buckets fully within range, add all spans
                        time_indices.update(indices)

                # For spans in partial buckets, do exact time filtering
                time_indices = {idx for idx in time_indices if
                    (query.start_time_min is None or self._spans[idx].start_time >= query.start_time_min) and
                    (query.start_time_max is None or self._spans[idx].start_time <= query.start_time_max)}

                candidates &= time_indices
            else:
                # If just time filtering (no status), use time buckets
                if query.start_time_min is not None:
                    min_hour_bucket = query.start_time_min // 3_600_000_000_000

                    # Collect spans from all relevant buckets
                    time_indices = set()
                    for bucket, indices in self._time_buckets.items():
                        if bucket >= min_hour_bucket:
                            time_indices.update(indices)

                    # Do exact filtering on the reduced set
                    time_indices = {idx for idx in time_indices if self._spans[idx].start_time >= query.start_time_min}
                    candidates &= time_indices

                # Apply max time filter if specified
                if query.start_time_max is not None:
                    time_indices = {idx for idx in candidates if self._spans[idx].start_time <= query.start_time_max}
                    candidates &= time_indices

            if not candidates:
                return set()  # Early exit if no matches

        # Filter by service name
        if query.service_name is not None:
            service_indices = set(self._service_index.get(query.service_name, []))
            candidates &= service_indices
            if not candidates:
                return set()  # Early exit if no matches

        # Filter by operation name
        if query.operation_name is not None:
            operation_indices = set(self._operation_index.get(query.operation_name, []))
            candidates &= operation_indices
            if not candidates:
                return set()  # Early exit if no matches

        # Filter by attributes
        if query.attribute_filters is not None and query.attribute_filters:
            for attr_filter in query.attribute_filters:
                attr_indices = set()
                if attr_filter.key in self._attribute_index:
                    key_index = self._attribute_index[attr_filter.key]

                    # Handle different operators
                    if attr_filter.operator == "EQUALS":
                        attr_indices = set(key_index.get(attr_filter.value, []))
                    else:
                        # For other operators, we need to check each span
                        for idx in candidates.copy():
                            if idx < len(self._spans) and attr_filter.matches(self._spans[idx]):
                                attr_indices.add(idx)

                candidates &= attr_indices
                if not candidates:
                    return set()  # Early exit if no matches

        return candidates

    def _sort_indices(self, indices: Set[int], query: SpanQuery) -> List[int]:
        """
        Sort the indices according to the query.

        Args:
            indices: The indices to sort
            query: The query containing sorting criteria

        Returns:
            Sorted list of indices
        """
        indices_list = list(indices)

        # Get the sort key function based on the order_by field
        if query.order_by == "start_time":
            key_func = lambda idx: self._spans[idx].start_time
        elif query.order_by == "end_time":
            key_func = lambda idx: self._spans[idx].end_time
        elif query.order_by == "duration_ns":
            key_func = lambda idx: self._spans[idx].duration_ns
        else:
            # Fallback to start_time
            key_func = lambda idx: self._spans[idx].start_time

        # Sort the indices
        reverse = query.order_direction == "DESC"
        indices_list.sort(key=key_func, reverse=reverse)

        return indices_list

    def clear(self) -> None:
        """
        Clear all spans and indices from the store.
        """
        with WriteLock(self._lock):
            self._spans.clear()
            self._trace_index.clear()
            self._span_index.clear()
            self._status_index.clear()
            self._time_index.clear()
            self._attribute_index.clear()
            self._service_index.clear()
            self._operation_index.clear()

    def get_span_count(self) -> int:
        """
        Get the number of spans in the store.

        Returns:
            Number of spans
        """
        with ReadLock(self._lock):
            return len(self._spans)

    def get_trace(self, trace_id: str) -> List[StoredSpan]:
        """
        Get all spans for a trace.

        Args:
            trace_id: The trace ID to retrieve

        Returns:
            List of spans that belong to the trace, ordered by start time

        Raises:
            ValueError: If trace_id is not a valid format
        """
        query = SpanQuery(trace_id=trace_id, max_spans=self.max_spans, order_by="start_time", order_direction="ASC")
        return self.get_spans(query)