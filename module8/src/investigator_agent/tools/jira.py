"""JIRA integration tools for feature investigation."""

import json
from pathlib import Path
from typing import Any


# Feature ID to folder mapping
FEATURE_FOLDERS = {
    "FEAT-MS-001": "feature1",
    "FEAT-QR-002": "feature2",
    "FEAT-RS-003": "feature3",
    "FEAT-CT-004": "feature4",
}


def get_folder_by_feature_id(feature_id: str) -> str:
    """
    Get the data folder path for a given feature ID.

    Args:
        feature_id: Feature identifier (e.g., 'FEAT-MS-001')

    Returns:
        Folder name for the feature

    Raises:
        ValueError: If feature_id is not found
    """
    if feature_id not in FEATURE_FOLDERS:
        available = ", ".join(FEATURE_FOLDERS.keys())
        raise ValueError(
            f"Feature '{feature_id}' not found. Available: {available}"
        )

    return FEATURE_FOLDERS[feature_id]


async def get_jira_data() -> list[dict[str, Any]]:
    """
    Retrieve JIRA metadata for all features.

    This tool returns high-level information about all features being
    investigated, including their JIRA keys, summaries, status, and
    data quality indicators.

    Returns:
        List of dictionaries containing feature metadata:
        - folder: Directory name for feature data
        - jira_key: JIRA issue key (e.g., 'PLAT-1523')
        - feature_id: Feature identifier (e.g., 'FEAT-MS-001')
        - summary: Feature description
        - status: Current JIRA status
        - data_quality: Quality of test data (COMPLETE, PARTIAL, INCOMPLETE)

    Raises:
        FileNotFoundError: If JIRA metadata file is missing
    """
    metadata_path = Path("incoming_data/jira_metadata.json")

    if not metadata_path.exists():
        raise FileNotFoundError(
            f"JIRA metadata file not found at {metadata_path}. "
            "Please ensure test data is properly set up."
        )

    with open(metadata_path) as f:
        features = json.load(f)

    return features


# Tool schema for get_jira_data
GET_JIRA_DATA_SCHEMA = {
    "type": "object",
    "properties": {},  # No parameters - returns all features
    "required": [],
}
