"""
Unit tests for span storage and indexing.

This module tests the thread-safe span storage defined in trace_storage.span_store,
including adding spans, querying spans, and thread safety.
"""

import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor
from typing import List

import pytest

from observability.trace_storage.models import AttributeFilter, SpanQuery, StoredSpan
from observability.trace_storage.span_store import ReadLock, ReadWriteLock, SpanStore, WriteLock


class TestReadWriteLock:
    """Tests for the ReadWriteLock class."""

    def test_multiple_readers(self):
        """Test that multiple readers can acquire the lock simultaneously."""
        rwlock = ReadWriteLock()
        reader_count = 5
        readers_running = 0
        readers_done = 0
        lock = threading.Lock()
        reader_event = threading.Event()
        results = []

        def reader():
            nonlocal readers_running, readers_done
            # Acquire read lock
            with ReadLock(rwlock):
                # Increment readers_running
                with lock:
                    readers_running += 1
                    if readers_running == reader_count:
                        reader_event.set()

                # Wait for all readers to start
                reader_event.wait(2)

                # Record that all readers are running simultaneously
                with lock:
                    results.append(readers_running)

                # Sleep to ensure overlap
                time.sleep(0.1)

                # Decrement readers_running
                with lock:
                    readers_running -= 1
                    readers_done += 1

        # Start multiple readers
        threads = []
        for _ in range(reader_count):
            t = threading.Thread(target=reader)
            threads.append(t)
            t.start()

        # Wait for all readers to finish
        for t in threads:
            t.join()

        # Verify all readers ran simultaneously
        assert readers_done == reader_count
        assert all(count == reader_count for count in results)

    def test_exclusive_writer(self):
        """Test that writers have exclusive access."""
        rwlock = ReadWriteLock()
        writer_running = False
        reader_running = False
        lock = threading.Lock()
        writer_start = threading.Event()
        writer_working = threading.Event()
        reader_waiting = threading.Event()
        reader_done = threading.Event()
        results = []

        def writer():
            nonlocal writer_running
            # Acquire write lock
            with WriteLock(rwlock):
                # Signal that writer has started
                writer_start.set()

                # Set writer_running
                with lock:
                    writer_running = True

                # Signal that writer is working
                writer_working.set()

                # Wait for reader to try to acquire
                reader_waiting.wait(2)

                # Sleep to ensure reader waits
                time.sleep(0.2)

                # Record that reader is not running simultaneously
                with lock:
                    results.append(reader_running)

                # Unset writer_running
                with lock:
                    writer_running = False

            # Wait for reader to finish
            reader_done.wait(2)

        def reader():
            nonlocal reader_running
            # Wait for writer to start
            writer_start.wait(2)

            # Signal that reader is waiting
            reader_waiting.set()

            # Try to acquire read lock
            with ReadLock(rwlock):
                # Set reader_running
                with lock:
                    reader_running = True

                # Record writer_running state
                with lock:
                    results.append(writer_running)

                # Unset reader_running
                with lock:
                    reader_running = False

            # Signal reader is done
            reader_done.set()

        # Start writer and reader
        writer_thread = threading.Thread(target=writer)
        reader_thread = threading.Thread(target=reader)

        writer_thread.start()
        reader_thread.start()

        writer_thread.join()
        reader_thread.join()

        # Verify writer and reader did not run simultaneously
        assert len(results) == 2
        assert results[0] is False  # Reader should not see writer running
        assert results[1] is False  # Writer should not see reader running

    def test_writer_priority(self):
        """Test that writers have priority over readers."""
        rwlock = ReadWriteLock()
        reader_acquired = threading.Event()
        writer_waiting = threading.Event()
        writer_acquired = threading.Event()
        execution_order = []

        def initial_reader():
            with ReadLock(rwlock):
                execution_order.append("initial_reader_start")
                reader_acquired.set()
                writer_waiting.wait(2)
                time.sleep(0.1)  # Hold the lock for a while
                execution_order.append("initial_reader_end")

        def waiting_writer():
            reader_acquired.wait(2)
            execution_order.append("writer_waiting")
            writer_waiting.set()

            with WriteLock(rwlock):
                execution_order.append("writer_acquired")
                writer_acquired.set()
                time.sleep(0.1)  # Hold the lock for a while
                execution_order.append("writer_end")

        def waiting_reader():
            reader_acquired.wait(2)
            time.sleep(0.05)  # Give writer a chance to start waiting
            execution_order.append("reader_waiting")

            with ReadLock(rwlock):
                execution_order.append("reader_acquired")
                time.sleep(0.1)  # Hold the lock for a while
                execution_order.append("reader_end")

        # Start threads
        threads = [
            threading.Thread(target=initial_reader),
            threading.Thread(target=waiting_writer),
            threading.Thread(target=waiting_reader),
        ]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # Verify execution order
        # Writer should acquire the lock before the waiting reader
        writer_pos = execution_order.index("writer_acquired")
        reader_pos = execution_order.index("reader_acquired")
        assert writer_pos < reader_pos


class TestSpanStore:
    """Tests for the SpanStore class."""

    def create_test_spans(self, count: int = 5) -> List[StoredSpan]:
        """Create a list of test spans."""
        return [
            StoredSpan(
                trace_id=f"{i:032x}",
                span_id=f"{i:016x}",
                name=f"test_span_{i}",
                status="OK" if i % 2 == 0 else "ERROR",
                start_time=1000000000 + i * 1000,
                end_time=1000000100 + i * 1000,
                attributes={
                    "service.name": f"service_{i % 3}",
                    "operation.name": f"operation_{i % 2}",
                    "http.status_code": 200 + i % 3,
                    "error.type": f"error_type_{i}" if i % 2 == 1 else None,
                },
                service_name=f"service_{i % 3}",
            )
            for i in range(count)
        ]

    def test_add_span(self):
        """Test adding spans to the store."""
        store = SpanStore(max_spans=100)
        spans = self.create_test_spans(5)

        # Add spans
        for span in spans:
            store.add_span(span)

        # Verify span count
        assert store.get_span_count() == 5

        # Query all spans
        stored_spans = store.get_spans()
        assert len(stored_spans) == 5

        # Verify spans are returned in descending start_time order (default)
        for i, span in enumerate(stored_spans):
            expected_index = 4 - i  # 4, 3, 2, 1, 0
            assert span.trace_id == spans[expected_index].trace_id
            assert span.span_id == spans[expected_index].span_id

    def test_query_by_trace_id(self):
        """Test querying spans by trace ID."""
        store = SpanStore(max_spans=100)
        spans = self.create_test_spans(10)

        # Add spans
        for span in spans:
            store.add_span(span)

        # Query for a specific trace ID
        trace_id = spans[5].trace_id
        query = SpanQuery(trace_id=trace_id)
        results = store.get_spans(query)

        # Verify results
        assert len(results) == 1
        assert results[0].trace_id == trace_id
        assert results[0].span_id == spans[5].span_id

    def test_query_by_span_ids(self):
        """Test querying spans by span IDs."""
        store = SpanStore(max_spans=100)
        spans = self.create_test_spans(10)

        # Add spans
        for span in spans:
            store.add_span(span)

        # Query for specific span IDs
        span_ids = [spans[2].span_id, spans[5].span_id, spans[8].span_id]
        query = SpanQuery(span_ids=span_ids)
        results = store.get_spans(query)

        # Verify results
        assert len(results) == 3
        result_span_ids = [span.span_id for span in results]
        for span_id in span_ids:
            assert span_id in result_span_ids

    def test_query_by_status(self):
        """Test querying spans by status."""
        store = SpanStore(max_spans=100)
        spans = self.create_test_spans(10)

        # Add spans
        for span in spans:
            store.add_span(span)

        # Query for ERROR spans
        query = SpanQuery(status="ERROR")
        results = store.get_spans(query)

        # Verify results (odd indices have ERROR status)
        assert len(results) == 5
        for span in results:
            assert span.status == "ERROR"

    def test_query_by_service_name(self):
        """Test querying spans by service name."""
        store = SpanStore(max_spans=100)
        spans = self.create_test_spans(10)

        # Add spans
        for span in spans:
            store.add_span(span)

        # Query for a specific service name
        query = SpanQuery(service_name="service_1")
        results = store.get_spans(query)

        # Verify results
        assert len(results) > 0
        for span in results:
            assert span.service_name == "service_1"

    def test_query_by_operation_name(self):
        """Test querying spans by operation name."""
        store = SpanStore(max_spans=100)
        spans = self.create_test_spans(10)

        # Add spans
        for span in spans:
            store.add_span(span)

        # Query for a specific operation name
        query = SpanQuery(operation_name="test_span_5")
        results = store.get_spans(query)

        # Verify results
        assert len(results) == 1
        assert results[0].name == "test_span_5"

    def test_query_by_time_range(self):
        """Test querying spans by time range."""
        store = SpanStore(max_spans=100)
        spans = self.create_test_spans(10)

        # Add spans
        for span in spans:
            store.add_span(span)

        # Query for spans within a time range
        query = SpanQuery(
            start_time_min=1000003000,
            start_time_max=1000006000,
        )
        results = store.get_spans(query)

        # Verify results (spans 3, 4, 5, 6)
        assert len(results) == 4
        for span in results:
            assert span.start_time >= 1000003000
            assert span.start_time <= 1000006000

    def test_query_by_attribute(self):
        """Test querying spans by attributes."""
        store = SpanStore(max_spans=100)
        spans = self.create_test_spans(10)

        # Add spans
        for span in spans:
            store.add_span(span)

        # Query for spans with a specific attribute
        query = SpanQuery(
            attribute_filters=[
                AttributeFilter(key="http.status_code", value=201)
            ]
        )
        results = store.get_spans(query)

        # Verify results
        assert len(results) > 0
        for span in results:
            assert span.attributes["http.status_code"] == 201

    def test_query_with_multiple_filters(self):
        """Test querying spans with multiple filters."""
        store = SpanStore(max_spans=100)
        spans = self.create_test_spans(10)

        # Add spans
        for span in spans:
            store.add_span(span)

        # Query for spans with multiple filters
        query = SpanQuery(
            status="ERROR",
            service_name="service_1",
            attribute_filters=[
                AttributeFilter(key="http.status_code", value=201)
            ]
        )
        results = store.get_spans(query)

        # Verify results
        for span in results:
            assert span.status == "ERROR"
            assert span.service_name == "service_1"
            assert span.attributes["http.status_code"] == 201

    def test_query_with_limit(self):
        """Test querying spans with a limit."""
        store = SpanStore(max_spans=100)
        spans = self.create_test_spans(10)

        # Add spans
        for span in spans:
            store.add_span(span)

        # Query with a limit
        query = SpanQuery(max_spans=3)
        results = store.get_spans(query)

        # Verify results
        assert len(results) == 3

    def test_query_with_custom_ordering(self):
        """Test querying spans with custom ordering."""
        store = SpanStore(max_spans=100)
        spans = self.create_test_spans(10)

        # Add spans
        for span in spans:
            store.add_span(span)

        # Query with custom ordering
        query = SpanQuery(order_by="duration_ns", order_direction="ASC")
        results = store.get_spans(query)

        # Verify results are ordered by duration
        for i in range(len(results) - 1):
            assert results[i].duration_ns <= results[i + 1].duration_ns

    def test_max_spans_limit(self):
        """Test that the max_spans limit is enforced."""
        max_spans = 5
        store = SpanStore(max_spans=max_spans)
        spans = self.create_test_spans(10)

        # Add spans
        for span in spans:
            store.add_span(span)

        # Verify span count
        assert store.get_span_count() == max_spans

        # Verify oldest spans are removed (first 5 spans should be gone)
        query = SpanQuery(max_spans=100)  # Get all spans
        results = store.get_spans(query)
        result_span_ids = [span.span_id for span in results]

        # Should contain last 5 span IDs (5-9)
        for i in range(5, 10):
            assert spans[i].span_id in result_span_ids

        # Should not contain first 5 span IDs (0-4)
        for i in range(5):
            assert spans[i].span_id not in result_span_ids

    def test_clear(self):
        """Test clearing the store."""
        store = SpanStore(max_spans=100)
        spans = self.create_test_spans(5)

        # Add spans
        for span in spans:
            store.add_span(span)
        assert store.get_span_count() == 5

        # Clear the store
        store.clear()
        assert store.get_span_count() == 0

        # Verify no spans are returned
        results = store.get_spans()
        assert len(results) == 0

    def test_get_trace(self):
        """Test getting all spans for a trace."""
        store = SpanStore(max_spans=100)

        # Create spans with the same trace ID
        trace_id = "01234567890123456789012345678901"
        spans = [
            StoredSpan(
                trace_id=trace_id,
                span_id=f"{i:016x}",
                name=f"test_span_{i}",
                status="OK",
                start_time=1000000000 + i * 1000,
                end_time=1000000100 + i * 1000,
            )
            for i in range(5)
        ]

        # Add some spans with a different trace ID
        other_spans = [
            StoredSpan(
                trace_id="98765432109876543210987654321098",
                span_id=f"9{i:015x}",
                name=f"other_span_{i}",
                status="OK",
                start_time=2000000000 + i * 1000,
                end_time=2000000100 + i * 1000,
            )
            for i in range(3)
        ]

        # Add all spans
        for span in spans + other_spans:
            store.add_span(span)

        # Get all spans for the trace
        trace_spans = store.get_trace(trace_id)

        # Verify results
        assert len(trace_spans) == 5
        for span in trace_spans:
            assert span.trace_id == trace_id

        # Verify spans are ordered by start time (ASC)
        for i in range(len(trace_spans) - 1):
            assert trace_spans[i].start_time <= trace_spans[i + 1].start_time

    def test_thread_safety(self):
        """Test thread safety with concurrent readers and writers."""
        store = SpanStore(max_spans=1000)
        span_count = 100
        thread_count = 10
        spans = self.create_test_spans(span_count)

        # Function to add spans
        def add_spans(thread_spans):
            for span in thread_spans:
                store.add_span(span)

        # Function to query spans
        def query_spans():
            # Random query to exercise various code paths
            query_type = random.randint(0, 5)
            if query_type == 0:
                # Query all spans
                return store.get_spans()
            elif query_type == 1:
                # Query by trace ID
                trace_id = spans[random.randint(0, span_count - 1)].trace_id
                return store.get_trace(trace_id)
            elif query_type == 2:
                # Query by status
                return store.get_spans(SpanQuery(status=random.choice(["OK", "ERROR"])))
            elif query_type == 3:
                # Query by time range
                start_min = 1000000000 + random.randint(0, span_count - 10) * 1000
                start_max = start_min + 10000
                return store.get_spans(SpanQuery(start_time_min=start_min, start_time_max=start_max))
            elif query_type == 4:
                # Query by service name
                service_name = f"service_{random.randint(0, 2)}"
                return store.get_spans(SpanQuery(service_name=service_name))
            else:
                # Query by attribute
                return store.get_spans(
                    SpanQuery(
                        attribute_filters=[
                            AttributeFilter(
                                key="http.status_code",
                                value=200 + random.randint(0, 2)
                            )
                        ]
                    )
                )

        # Split spans among writer threads
        spans_per_thread = span_count // thread_count
        thread_spans = [
            spans[i * spans_per_thread : (i + 1) * spans_per_thread]
            for i in range(thread_count)
        ]

        # Create writer and reader futures
        with ThreadPoolExecutor(max_workers=thread_count * 2) as executor:
            # Start writer threads
            writer_futures = [
                executor.submit(add_spans, thread_spans[i])
                for i in range(thread_count)
            ]

            # Start reader threads (more readers than writers)
            reader_futures = [
                executor.submit(query_spans)
                for _ in range(thread_count * 2)
            ]

            # Wait for all writers to complete
            for future in writer_futures:
                future.result()

            # Wait for all readers to complete
            for future in reader_futures:
                future.result()

        # Verify span count
        assert store.get_span_count() == min(span_count, store.max_spans)