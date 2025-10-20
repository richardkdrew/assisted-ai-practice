"""Shared test fixtures and configuration."""

import pytest

from detective_agent.observability.tracer import setup_tracer


@pytest.fixture(scope="session", autouse=True)
def setup_test_tracer(tmp_path_factory):
    """Setup tracer for all tests."""
    traces_dir = tmp_path_factory.mktemp("traces")
    setup_tracer(traces_dir)
