"""Tests for Analysis tool."""

import pytest

from investigator_agent.tools.analysis import (
    ALL_ANALYSIS_TYPES,
    METRICS_TYPES,
    REVIEW_TYPES,
    get_analysis,
    get_analysis_category,
)


def test_analysis_types_defined():
    """Test that all analysis types are properly defined."""
    assert len(METRICS_TYPES) == 5
    assert len(REVIEW_TYPES) == 3
    assert len(ALL_ANALYSIS_TYPES) == 8

    # Verify specific types exist
    assert "test_coverage_report" in METRICS_TYPES
    assert "security" in REVIEW_TYPES


def test_get_analysis_category_metrics():
    """Test category determination for metrics types."""
    assert get_analysis_category("performance_benchmarks") == "metrics"
    assert get_analysis_category("pipeline_results") == "metrics"
    assert get_analysis_category("test_coverage_report") == "metrics"


def test_get_analysis_category_reviews():
    """Test category determination for review types."""
    assert get_analysis_category("security") == "reviews"
    assert get_analysis_category("stakeholders") == "reviews"
    assert get_analysis_category("uat") == "reviews"


def test_get_analysis_category_invalid():
    """Test category determination with invalid type."""
    with pytest.raises(ValueError) as exc_info:
        get_analysis_category("invalid_type")

    assert "invalid_type" in str(exc_info.value).lower()
    assert "valid types" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_analysis_test_coverage():
    """Test retrieving test coverage analysis."""
    data = await get_analysis("FEAT-MS-001", "test_coverage_report")

    # Verify structure
    assert "overall_coverage" in data
    assert "coverage_by_type" in data
    assert "threshold" in data
    assert "passed" in data

    # Verify values
    assert data["overall_coverage"] == 87
    assert data["threshold"] == 80
    assert data["passed"] is True


@pytest.mark.asyncio
async def test_get_analysis_security_review():
    """Test retrieving security review analysis."""
    data = await get_analysis("FEAT-MS-001", "security")

    # Verify structure
    assert "review_metadata" in data
    assert "status" in data
    assert "overall_risk_level" in data
    assert "findings" in data

    # Verify values
    assert data["status"] == "APPROVED"
    assert data["overall_risk_level"] == "LOW"
    assert isinstance(data["findings"], list)


@pytest.mark.asyncio
async def test_get_analysis_all_metrics_types():
    """Test all metrics types for feature1."""
    for metrics_type in METRICS_TYPES:
        data = await get_analysis("FEAT-MS-001", metrics_type)
        assert isinstance(data, dict)
        assert len(data) > 0  # Should have some content


@pytest.mark.asyncio
async def test_get_analysis_all_review_types():
    """Test all review types for feature1."""
    for review_type in REVIEW_TYPES:
        data = await get_analysis("FEAT-MS-001", review_type)
        assert isinstance(data, dict)
        assert len(data) > 0  # Should have some content


@pytest.mark.asyncio
async def test_get_analysis_invalid_analysis_type():
    """Test get_analysis with invalid analysis type."""
    with pytest.raises(ValueError) as exc_info:
        await get_analysis("FEAT-MS-001", "invalid_analysis")

    error_msg = str(exc_info.value).lower()
    assert "invalid" in error_msg
    assert "invalid_analysis" in error_msg
    assert "valid types" in error_msg


@pytest.mark.asyncio
async def test_get_analysis_invalid_feature_id():
    """Test get_analysis with invalid feature ID."""
    with pytest.raises(ValueError) as exc_info:
        await get_analysis("FEAT-INVALID-999", "test_coverage_report")

    error_msg = str(exc_info.value)
    assert "FEAT-INVALID-999" in error_msg
    assert "not found" in error_msg.lower()


@pytest.mark.asyncio
async def test_get_analysis_missing_file(tmp_path, monkeypatch):
    """Test get_analysis when analysis file is missing."""
    # Change to temp directory
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError) as exc_info:
        await get_analysis("FEAT-MS-001", "test_coverage_report")

    error_msg = str(exc_info.value).lower()
    assert "not found" in error_msg
    assert "test_coverage_report" in error_msg


@pytest.mark.asyncio
async def test_get_analysis_different_features():
    """Test retrieving analysis for different features."""
    # Feature 1 - Production Ready
    data1 = await get_analysis("FEAT-MS-001", "security")
    assert data1["status"] == "APPROVED"

    # Feature 2 - Development (different security status expected)
    data2 = await get_analysis("FEAT-QR-002", "test_coverage_report")
    assert "overall_coverage" in data2
