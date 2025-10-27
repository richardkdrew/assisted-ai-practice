"""Tests for JIRA tool."""

import pytest

from investigator_agent.tools.jira import (
    FEATURE_FOLDERS,
    get_folder_by_feature_id,
    get_jira_data,
)


def test_feature_folders_mapping():
    """Test that feature ID to folder mapping is defined."""
    assert len(FEATURE_FOLDERS) == 4
    assert "FEAT-MS-001" in FEATURE_FOLDERS
    assert FEATURE_FOLDERS["FEAT-MS-001"] == "feature1"


def test_get_folder_by_feature_id_success():
    """Test successful folder lookup by feature ID."""
    folder = get_folder_by_feature_id("FEAT-MS-001")
    assert folder == "feature1"

    folder = get_folder_by_feature_id("FEAT-QR-002")
    assert folder == "feature2"


def test_get_folder_by_feature_id_not_found():
    """Test folder lookup with invalid feature ID."""
    with pytest.raises(ValueError) as exc_info:
        get_folder_by_feature_id("FEAT-INVALID-999")

    assert "FEAT-INVALID-999" in str(exc_info.value)
    assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_jira_data_success():
    """Test successful retrieval of all feature metadata."""
    features = await get_jira_data()

    # Should return all 4 features
    assert len(features) == 4

    # Check first feature (maintenance scheduling)
    feature1 = next(f for f in features if f["feature_id"] == "FEAT-MS-001")
    assert feature1["folder"] == "feature1"
    assert feature1["jira_key"] == "PLAT-1523"
    assert "Maintenance Scheduling" in feature1["summary"]
    assert feature1["status"] == "Production Ready"
    assert feature1["data_quality"] == "COMPLETE"

    # Check second feature (QR code)
    feature2 = next(f for f in features if f["feature_id"] == "FEAT-QR-002")
    assert feature2["folder"] == "feature2"
    assert feature2["jira_key"] == "PLAT-1687"
    assert "QR Code" in feature2["summary"]
    assert feature2["status"] == "Development"

    # Verify all expected fields are present
    for feature in features:
        assert "folder" in feature
        assert "jira_key" in feature
        assert "feature_id" in feature
        assert "summary" in feature
        assert "status" in feature
        assert "data_quality" in feature


@pytest.mark.asyncio
async def test_get_jira_data_file_not_found(tmp_path, monkeypatch):
    """Test handling of missing JIRA metadata file."""
    # Change to a directory where the file doesn't exist
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError) as exc_info:
        await get_jira_data()

    assert "jira_metadata.json" in str(exc_info.value).lower()
    assert "not found" in str(exc_info.value).lower()
