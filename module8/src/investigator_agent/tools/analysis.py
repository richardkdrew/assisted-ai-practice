"""Analysis tools for feature investigation (metrics and reviews)."""

import json
from pathlib import Path
from typing import Any

from investigator_agent.tools.jira import get_folder_by_feature_id


# All valid analysis types (5 metrics + 3 reviews)
METRICS_TYPES = [
    "performance_benchmarks",
    "pipeline_results",
    "security_scan_results",
    "test_coverage_report",
    "unit_test_results",
]

REVIEW_TYPES = [
    "security",
    "stakeholders",
    "uat",
]

ALL_ANALYSIS_TYPES = METRICS_TYPES + REVIEW_TYPES


def get_analysis_category(analysis_type: str) -> str:
    """
    Determine which category (metrics or reviews) an analysis type belongs to.

    Args:
        analysis_type: The analysis type

    Returns:
        'metrics' or 'reviews'

    Raises:
        ValueError: If analysis_type is not valid
    """
    if analysis_type in METRICS_TYPES:
        return "metrics"
    elif analysis_type in REVIEW_TYPES:
        return "reviews"
    else:
        raise ValueError(
            f"Invalid analysis_type '{analysis_type}'. "
            f"Valid types: {', '.join(ALL_ANALYSIS_TYPES)}"
        )


async def get_analysis(feature_id: str, analysis_type: str) -> dict[str, Any]:
    """
    Retrieve analysis data for a specific feature.

    This tool fetches detailed analysis data including metrics (test results,
    performance, security scans) and reviews (security reviews, stakeholder
    feedback, UAT results).

    Args:
        feature_id: Feature identifier (e.g., 'FEAT-MS-001')
        analysis_type: Type of analysis to retrieve. Valid types:
            METRICS:
            - performance_benchmarks: Performance test results
            - pipeline_results: CI/CD pipeline execution results
            - security_scan_results: Automated security scan findings
            - test_coverage_report: Code coverage analysis
            - unit_test_results: Unit test execution results
            REVIEWS:
            - security: Security review findings and approval
            - stakeholders: Stakeholder review and sign-off
            - uat: User Acceptance Testing results

    Returns:
        Dictionary containing the requested analysis data

    Raises:
        ValueError: If feature_id or analysis_type is invalid
        FileNotFoundError: If analysis data file is missing
    """
    # Validate analysis type
    if analysis_type not in ALL_ANALYSIS_TYPES:
        raise ValueError(
            f"Invalid analysis_type '{analysis_type}'. "
            f"Valid types: {', '.join(ALL_ANALYSIS_TYPES)}"
        )

    # Get folder for feature
    folder = get_folder_by_feature_id(feature_id)

    # Determine category and build path
    category = get_analysis_category(analysis_type)
    file_path = Path(f"incoming_data/{folder}/{category}/{analysis_type}.json")

    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError(
            f"Analysis data not found: {file_path}. "
            f"Feature '{feature_id}' may not have '{analysis_type}' data available."
        )

    # Load and return data
    with open(file_path) as f:
        data = json.load(f)

    return data


# Tool schema for get_analysis
GET_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "feature_id": {
            "type": "string",
            "description": "Feature identifier (e.g., 'FEAT-MS-001')",
        },
        "analysis_type": {
            "type": "string",
            "enum": ALL_ANALYSIS_TYPES,
            "description": (
                "Type of analysis to retrieve. "
                "METRICS: performance_benchmarks, pipeline_results, security_scan_results, "
                "test_coverage_report, unit_test_results. "
                "REVIEWS: security, stakeholders, uat."
            ),
        },
    },
    "required": ["feature_id", "analysis_type"],
}
