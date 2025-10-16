"""Test scenarios for evaluating agent behavior."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Scenario:
    """A test scenario for evaluating agent performance.

    Each scenario defines a release situation and expected agent behavior.
    """

    id: str
    description: str
    release_data: dict[str, Any]
    expected_severity: str  # "high", "medium", or "low"
    expected_tools: list[str]  # Tools that should be called
    expected_findings_keywords: list[str]  # Keywords that should appear in findings
    metadata: dict[str, Any] = field(default_factory=dict)


# Define evaluation scenarios
HIGH_RISK_SCENARIO = Scenario(
    id="high_risk_critical_failures",
    description="Release with critical test failures and high error rate",
    release_data={
        "release_id": "rel-003",
        "version": "v2.3.0",
        "changes": [
            "Major refactor of core authentication system",
            "Migrated to new database schema",
            "Added multi-tenancy support",
        ],
        "tests": {"passed": 135, "failed": 12, "skipped": 8},
        "deployment_metrics": {"error_rate": 0.065, "response_time_p95": 890},
    },
    expected_severity="high",
    expected_tools=["get_release_summary", "file_risk_report"],
    expected_findings_keywords=["test failure", "error rate", "authentication", "risk"],
    metadata={"test_failure_rate": 0.077, "error_rate_percent": 6.5},
)

MEDIUM_RISK_SCENARIO = Scenario(
    id="medium_risk_minor_issues",
    description="Release with minor test failures and moderate metrics",
    release_data={
        "release_id": "rel-004",
        "version": "v2.4.0",
        "changes": [
            "Updated user profile page layout",
            "Fixed several UI bugs",
            "Improved search performance",
        ],
        "tests": {"passed": 156, "failed": 2, "skipped": 4},
        "deployment_metrics": {"error_rate": 0.028, "response_time_p95": 380},
    },
    expected_severity="medium",
    expected_tools=["get_release_summary", "file_risk_report"],
    expected_findings_keywords=["test failure", "error rate", "moderate"],
    metadata={"test_failure_rate": 0.012, "error_rate_percent": 2.8},
)

LOW_RISK_SCENARIO = Scenario(
    id="low_risk_healthy_release",
    description="Release with all tests passing and healthy metrics",
    release_data={
        "release_id": "rel-002",
        "version": "v2.2.0",
        "changes": [
            "Implemented real-time notifications",
            "Optimized database queries",
            "Added admin dashboard",
        ],
        "tests": {"passed": 158, "failed": 0, "skipped": 3},
        "deployment_metrics": {"error_rate": 0.008, "response_time_p95": 320},
    },
    expected_severity="low",
    expected_tools=["get_release_summary", "file_risk_report"],
    expected_findings_keywords=["healthy", "passing", "low risk"],
    metadata={"test_failure_rate": 0.0, "error_rate_percent": 0.8},
)

MISSING_DATA_SCENARIO = Scenario(
    id="missing_data_incomplete_info",
    description="Release with incomplete or missing data",
    release_data={
        "release_id": "rel-999",
        "version": "v3.0.0",
        "changes": ["Major system upgrade"],
        # Missing test results and metrics
    },
    expected_severity="high",  # Should be cautious with missing data
    expected_tools=["get_release_summary"],
    expected_findings_keywords=["missing", "incomplete", "uncertain", "data"],
    metadata={"has_missing_data": True},
)

EDGE_CASE_ZERO_TESTS = Scenario(
    id="edge_case_zero_tests",
    description="Release with zero tests (no test coverage)",
    release_data={
        "release_id": "rel-005",
        "version": "v1.0.0",
        "changes": ["Initial release"],
        "tests": {"passed": 0, "failed": 0, "skipped": 0},
        "deployment_metrics": {"error_rate": 0.0, "response_time_p95": 250},
    },
    expected_severity="high",  # No tests is risky
    expected_tools=["get_release_summary", "file_risk_report"],
    expected_findings_keywords=["no test", "test coverage", "risk"],
    metadata={"test_count": 0},
)


# Collect all scenarios
ALL_SCENARIOS = [
    HIGH_RISK_SCENARIO,
    MEDIUM_RISK_SCENARIO,
    LOW_RISK_SCENARIO,
    MISSING_DATA_SCENARIO,
    EDGE_CASE_ZERO_TESTS,
]


def get_scenario_by_id(scenario_id: str) -> Scenario | None:
    """Get a scenario by its ID."""
    for scenario in ALL_SCENARIOS:
        if scenario.id == scenario_id:
            return scenario
    return None


def get_scenarios_by_severity(severity: str) -> list[Scenario]:
    """Get all scenarios with a specific expected severity."""
    return [s for s in ALL_SCENARIOS if s.expected_severity == severity]
