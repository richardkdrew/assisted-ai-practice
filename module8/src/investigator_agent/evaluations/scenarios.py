"""Test scenarios for evaluating the Investigator Agent.

Based on the 4 features in incoming_data/:
- feature1 (FEAT-MS-001): Maintenance Scheduling - Production Ready
- feature2 (FEAT-QR-002): QR Code Check-in - Not Ready (test failures)
- feature3 (FEAT-RS-003): Resource Reservation - Borderline (UAT issues)
- feature4 (FEAT-CT-004): Contribution Tracking - Not Ready (incomplete)
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class EvaluationScenario:
    """A test scenario for evaluating agent behavior."""

    id: str
    feature_id: str
    user_query: str
    expected_decision: str  # ready, not_ready, borderline
    expected_tools: list[str]  # Tools that should be called
    expected_justification_includes: list[str]  # Key points to mention
    expected_sub_conversations: bool  # Should use sub-conversations
    expected_memory_retrieval: bool  # Should retrieve memories
    description: str  # Human-readable description
    metadata: dict[str, Any] | None = None


# Scenario 1: Production Ready Feature
SCENARIO_READY_FOR_PRODUCTION = EvaluationScenario(
    id="ready_for_production",
    feature_id="FEAT-MS-001",
    user_query="Is the Maintenance Scheduling & Alert System feature ready for production?",
    expected_decision="ready",
    expected_tools=["get_jira_data", "get_analysis"],
    expected_justification_includes=[
        "test",
        "UAT",
        "security",
        "approved",
    ],
    expected_sub_conversations=False,  # Small analysis data
    expected_memory_retrieval=False,  # First assessment
    description="Feature with all quality gates passed - should be approved for production",
    metadata={
        "jira_status": "Production Ready",
        "data_quality": "COMPLETE",
    },
)

# Scenario 2: Not Ready - Test Failures
SCENARIO_NOT_READY_TEST_FAILURES = EvaluationScenario(
    id="not_ready_test_failures",
    feature_id="FEAT-QR-002",
    user_query="Can we promote the QR Code Check-in feature to production?",
    expected_decision="not_ready",
    expected_tools=["get_jira_data", "get_analysis"],
    expected_justification_includes=[
        "test",
        "fail",
        "UAT",
        "not ready",
    ],
    expected_sub_conversations=False,
    expected_memory_retrieval=False,
    description="Feature with test failures - should be rejected",
    metadata={
        "jira_status": "Development",
        "data_quality": "INCOMPLETE",
    },
)

# Scenario 3: Borderline Case
SCENARIO_BORDERLINE_UAT_ISSUES = EvaluationScenario(
    id="borderline_uat_issues",
    feature_id="FEAT-RS-003",
    user_query="What's the production readiness status of the Advanced Resource Reservation System?",
    expected_decision="borderline",
    expected_tools=["get_jira_data", "get_analysis"],
    expected_justification_includes=[
        "UAT",
        "concern",
        "risk",
    ],
    expected_sub_conversations=False,
    expected_memory_retrieval=False,
    description="Feature with mixed signals - should be marked as borderline",
    metadata={
        "jira_status": "UAT",
        "data_quality": "PARTIAL",
    },
)

# Scenario 4: Not Ready - Incomplete Documentation
SCENARIO_NOT_READY_INCOMPLETE = EvaluationScenario(
    id="not_ready_incomplete",
    feature_id="FEAT-CT-004",
    user_query="Is the Contribution Tracking & Community Credits feature production-ready?",
    expected_decision="not_ready",
    expected_tools=["get_jira_data", "get_analysis"],
    expected_justification_includes=[
        "planning",
        "not ready",
        "incomplete",
    ],
    expected_sub_conversations=False,
    expected_memory_retrieval=False,
    description="Feature in early planning stage - should be rejected",
    metadata={
        "jira_status": "Planning",
        "data_quality": "INCOMPLETE",
    },
)

# Scenario 5: With Documentation Check (Large Doc)
SCENARIO_WITH_LARGE_DOCS = EvaluationScenario(
    id="with_large_documentation",
    feature_id="FEAT-MS-001",
    user_query="Review the architecture documentation and assess if Maintenance Scheduling is production-ready.",
    expected_decision="ready",
    expected_tools=["get_jira_data", "list_docs", "read_doc"],
    expected_justification_includes=[
        "architecture",
        "ready",
    ],
    expected_sub_conversations=True,  # Architecture doc is large
    expected_memory_retrieval=False,
    description="Assessment requiring large document review - should trigger sub-conversations",
    metadata={
        "tests_sub_conversations": True,
    },
)

# Scenario 6: Feature Identification Test
SCENARIO_FEATURE_IDENTIFICATION = EvaluationScenario(
    id="feature_identification",
    feature_id="FEAT-QR-002",
    user_query="Tell me about the QR code feature",
    expected_decision="not_ready",
    expected_tools=["get_jira_data"],
    expected_justification_includes=[
        "QR",
        "development",
    ],
    expected_sub_conversations=False,
    expected_memory_retrieval=False,
    description="Test that agent correctly identifies feature from natural language",
    metadata={
        "tests_feature_identification": True,
    },
)

# Scenario 7: Multiple Analysis Types
SCENARIO_COMPREHENSIVE_ANALYSIS = EvaluationScenario(
    id="comprehensive_analysis",
    feature_id="FEAT-RS-003",
    user_query="Do a comprehensive assessment of the Resource Reservation System, checking all quality metrics.",
    expected_decision="borderline",
    expected_tools=["get_jira_data", "get_analysis"],
    expected_justification_includes=[
        "test",
        "security",
        "UAT",
    ],
    expected_sub_conversations=False,
    expected_memory_retrieval=False,
    description="Comprehensive assessment requiring multiple analysis types",
    metadata={
        "tests_multiple_tools": True,
    },
)

# Scenario 8: With Memory (if implemented)
SCENARIO_WITH_MEMORY = EvaluationScenario(
    id="with_memory_retrieval",
    feature_id="FEAT-MS-001",
    user_query="We assessed Maintenance Scheduling before. Has anything changed?",
    expected_decision="ready",
    expected_tools=["get_jira_data"],
    expected_justification_includes=[
        "previous",
        "maintenance",
    ],
    expected_sub_conversations=False,
    expected_memory_retrieval=True,  # Should check memory
    description="Re-assessment that should retrieve and reference past memories",
    metadata={
        "tests_memory": True,
        "requires_memory_setup": True,
    },
)

# All scenarios for evaluation
EVALUATION_SCENARIOS = [
    SCENARIO_READY_FOR_PRODUCTION,
    SCENARIO_NOT_READY_TEST_FAILURES,
    SCENARIO_BORDERLINE_UAT_ISSUES,
    SCENARIO_NOT_READY_INCOMPLETE,
    SCENARIO_WITH_LARGE_DOCS,
    SCENARIO_FEATURE_IDENTIFICATION,
    SCENARIO_COMPREHENSIVE_ANALYSIS,
    SCENARIO_WITH_MEMORY,
]
