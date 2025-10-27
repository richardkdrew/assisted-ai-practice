"""Tests for Documentation tools."""

import pytest
from pathlib import Path

from investigator_agent.tools.docs import list_docs, read_doc


@pytest.mark.asyncio
async def test_list_docs_feature1():
    """Test listing docs for feature1 (maintenance scheduling)."""
    docs = await list_docs("FEAT-MS-001")

    # Should return 6 docs
    assert len(docs) == 6

    # Check structure of first doc
    assert "path" in docs[0]
    assert "name" in docs[0]
    assert "size" in docs[0]
    assert "modified" in docs[0]

    # Verify specific files exist
    doc_names = [d["name"] for d in docs]
    assert "ARCHITECTURE.md" in doc_names
    assert "API_SPECIFICATION.md" in doc_names
    assert "DATABASE_SCHEMA.md" in doc_names
    assert "DEPLOYMENT_PLAN.md" in doc_names
    assert "DESIGN_DOC.md" in doc_names
    assert "USER_STORY.md" in doc_names

    # Verify sizes are reasonable (not empty)
    for doc in docs:
        assert doc["size"] > 0


@pytest.mark.asyncio
async def test_list_docs_feature2():
    """Test listing docs for feature2 (QR code - has 8 docs)."""
    docs = await list_docs("FEAT-QR-002")

    # Should return 8 docs (more than feature1)
    assert len(docs) == 8

    doc_names = [d["name"] for d in docs]
    assert "MOBILE_APP_SPEC.md" in doc_names
    assert "SECURITY_CONSIDERATIONS.md" in doc_names


@pytest.mark.asyncio
async def test_list_docs_sorted():
    """Test that docs are returned in sorted order."""
    docs = await list_docs("FEAT-MS-001")

    doc_names = [d["name"] for d in docs]
    # Should be alphabetically sorted
    assert doc_names == sorted(doc_names)


@pytest.mark.asyncio
async def test_list_docs_invalid_feature():
    """Test list_docs with invalid feature ID."""
    with pytest.raises(ValueError) as exc_info:
        await list_docs("FEAT-INVALID-999")

    assert "FEAT-INVALID-999" in str(exc_info.value)
    assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_list_docs_missing_directory(tmp_path, monkeypatch):
    """Test list_docs when planning directory doesn't exist."""
    # Change to temp directory
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError) as exc_info:
        await list_docs("FEAT-MS-001")

    error_msg = str(exc_info.value).lower()
    assert "planning" in error_msg
    assert "not found" in error_msg


@pytest.mark.asyncio
async def test_read_doc_architecture():
    """Test reading ARCHITECTURE.md for feature1."""
    # First list docs to get the path
    docs = await list_docs("FEAT-MS-001")
    arch_doc = next(d for d in docs if d["name"] == "ARCHITECTURE.md")

    # Read the doc
    contents = await read_doc(arch_doc["path"])

    # Verify it's the right content
    assert isinstance(contents, str)
    assert len(contents) > 0
    assert "Architecture" in contents or "ARCHITECTURE" in contents.upper()
    assert "Maintenance Scheduling" in contents
    # Note: File size on disk may differ from string length due to encoding


@pytest.mark.asyncio
async def test_read_doc_user_story():
    """Test reading smaller USER_STORY.md file."""
    docs = await list_docs("FEAT-MS-001")
    user_story = next(d for d in docs if d["name"] == "USER_STORY.md")

    contents = await read_doc(user_story["path"])

    assert isinstance(contents, str)
    assert len(contents) > 0
    # User story should be smaller
    assert len(contents) < 10000


@pytest.mark.asyncio
async def test_read_doc_all_features():
    """Test reading docs from all features."""
    for feature_id in ["FEAT-MS-001", "FEAT-QR-002", "FEAT-RS-003", "FEAT-CT-004"]:
        docs = await list_docs(feature_id)
        # Read first doc from each feature
        if docs:
            contents = await read_doc(docs[0]["path"])
            assert isinstance(contents, str)
            assert len(contents) > 0


@pytest.mark.asyncio
async def test_read_doc_file_not_found():
    """Test read_doc with non-existent file."""
    with pytest.raises(FileNotFoundError) as exc_info:
        await read_doc("incoming_data/feature1/planning/NONEXISTENT.md")

    error_msg = str(exc_info.value).lower()
    assert "not found" in error_msg
    assert "nonexistent" in error_msg


@pytest.mark.asyncio
async def test_read_doc_security_check_path_traversal():
    """Test read_doc rejects paths outside incoming_data/."""
    # Try to read outside incoming_data
    with pytest.raises(ValueError) as exc_info:
        await read_doc("../../etc/passwd")

    error_msg = str(exc_info.value).lower()
    assert "invalid path" in error_msg
    assert "incoming_data" in error_msg


@pytest.mark.asyncio
async def test_read_doc_security_check_absolute_path():
    """Test read_doc rejects absolute paths outside incoming_data/."""
    with pytest.raises(ValueError) as exc_info:
        await read_doc("/etc/passwd")

    error_msg = str(exc_info.value).lower()
    assert "invalid path" in error_msg


@pytest.mark.asyncio
async def test_read_doc_large_file():
    """Test reading large documentation file (ARCHITECTURE.md)."""
    docs = await list_docs("FEAT-QR-002")
    # feature2 has larger DEPLOYMENT_PLAN.md (27KB)
    large_doc = next(d for d in docs if d["name"] == "DEPLOYMENT_PLAN.md")

    contents = await read_doc(large_doc["path"])

    # Should successfully read large file
    assert isinstance(contents, str)
    assert len(contents) > 25000  # Should be > 25KB
