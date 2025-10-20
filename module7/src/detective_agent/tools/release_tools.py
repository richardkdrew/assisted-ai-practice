"""Release risk assessment tools."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


# Mock release data for testing
MOCK_RELEASES = {
    "rel-001": {
        "version": "v2.1.0",
        "changes": [
            "Added payment processing feature",
            "Fixed authentication bug in login flow",
            "Updated dependencies to latest versions",
        ],
        "tests": {"passed": 142, "failed": 2, "skipped": 5},
        "deployment_metrics": {"error_rate": 0.02, "response_time_p95": 450},
    },
    "rel-002": {
        "version": "v2.2.0",
        "changes": [
            "Implemented real-time notifications",
            "Optimized database queries",
            "Added admin dashboard",
        ],
        "tests": {"passed": 158, "failed": 0, "skipped": 3},
        "deployment_metrics": {"error_rate": 0.008, "response_time_p95": 320},
    },
    "rel-003": {
        "version": "v2.3.0",
        "changes": [
            "Major refactor of core authentication system",
            "Migrated to new database schema",
            "Added multi-tenancy support",
        ],
        "tests": {"passed": 135, "failed": 12, "skipped": 8},
        "deployment_metrics": {"error_rate": 0.065, "response_time_p95": 890},
    },
}


async def get_release_summary(release_id: str) -> dict[str, Any]:
    """
    Retrieve release information from mock data.

    Args:
        release_id: Unique identifier for the release

    Returns:
        Dictionary with release information including version,
        changes, test results, and deployment metrics

    Raises:
        ValueError: If release_id is not found
    """
    if release_id not in MOCK_RELEASES:
        raise ValueError(
            f"Release '{release_id}' not found. "
            f"Available: {', '.join(MOCK_RELEASES.keys())}"
        )

    return MOCK_RELEASES[release_id]


# Tool schema for get_release_summary
GET_RELEASE_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "release_id": {
            "type": "string",
            "description": "Unique identifier for the release (e.g., 'rel-001')",
        }
    },
    "required": ["release_id"],
}


async def file_risk_report(
    release_id: str, severity: str, findings: list[str]
) -> dict[str, Any]:
    """
    File a risk assessment report for a release.

    Args:
        release_id: Unique identifier for the release
        severity: Risk severity level ('high', 'medium', or 'low')
        findings: List of identified risks or concerns

    Returns:
        Dictionary with report status and generated report ID

    Raises:
        ValueError: If severity is not valid
    """
    # Validate severity
    valid_severities = ["high", "medium", "low"]
    if severity.lower() not in valid_severities:
        raise ValueError(
            f"Severity must be one of {valid_severities}, got '{severity}'"
        )

    # Create report
    report_id = str(uuid.uuid4())
    report = {
        "report_id": report_id,
        "release_id": release_id,
        "severity": severity.lower(),
        "findings": findings,
        "timestamp": datetime.now().isoformat(),
    }

    # Save report to data/reports directory
    reports_dir = Path("./data/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_file = reports_dir / f"{report_id}.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    return {"status": "filed", "report_id": report_id, "location": str(report_file)}


# Tool schema for file_risk_report
FILE_RISK_REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "release_id": {
            "type": "string",
            "description": "Unique identifier for the release being assessed",
        },
        "severity": {
            "type": "string",
            "enum": ["high", "medium", "low"],
            "description": "Risk severity level based on test failures and metrics",
        },
        "findings": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of specific risks, concerns, or issues identified",
        },
    },
    "required": ["release_id", "severity", "findings"],
}
