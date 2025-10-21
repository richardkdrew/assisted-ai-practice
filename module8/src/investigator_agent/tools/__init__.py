"""Tool abstraction and registry for agent capabilities."""

from investigator_agent.tools.analysis import (
    ALL_ANALYSIS_TYPES,
    GET_ANALYSIS_SCHEMA,
    METRICS_TYPES,
    REVIEW_TYPES,
    get_analysis,
)
from investigator_agent.tools.docs import (
    LIST_DOCS_SCHEMA,
    READ_DOC_SCHEMA,
    list_docs,
    read_doc,
)
from investigator_agent.tools.jira import (
    GET_JIRA_DATA_SCHEMA,
    get_folder_by_feature_id,
    get_jira_data,
)
from investigator_agent.tools.registry import ToolRegistry
from investigator_agent.tools.release_tools import (
    FILE_RISK_REPORT_SCHEMA,
    GET_RELEASE_SUMMARY_SCHEMA,
    file_risk_report,
    get_release_summary,
)

__all__ = [
    "ToolRegistry",
    # Release tools (Module 7)
    "get_release_summary",
    "file_risk_report",
    "GET_RELEASE_SUMMARY_SCHEMA",
    "FILE_RISK_REPORT_SCHEMA",
    # JIRA tools (Module 8 - Phase 1)
    "get_jira_data",
    "get_folder_by_feature_id",
    "GET_JIRA_DATA_SCHEMA",
    # Analysis tools (Module 8 - Phase 2)
    "get_analysis",
    "GET_ANALYSIS_SCHEMA",
    "ALL_ANALYSIS_TYPES",
    "METRICS_TYPES",
    "REVIEW_TYPES",
    # Documentation tools (Module 8 - Phase 3)
    "list_docs",
    "read_doc",
    "LIST_DOCS_SCHEMA",
    "READ_DOC_SCHEMA",
]
