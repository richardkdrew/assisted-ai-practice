"""Feature investigation with Documentation tools (Module 8 - Phase 3)."""

import asyncio

from investigator_agent import Agent, Config
from investigator_agent.persistence.store import ConversationStore
from investigator_agent.providers.anthropic import AnthropicProvider
from investigator_agent.tools.analysis import GET_ANALYSIS_SCHEMA, get_analysis
from investigator_agent.tools.docs import LIST_DOCS_SCHEMA, READ_DOC_SCHEMA, list_docs, read_doc
from investigator_agent.tools.jira import GET_JIRA_DATA_SCHEMA, get_jira_data
from investigator_agent.tools.registry import ToolRegistry


async def main():
    """Run a comprehensive investigation with JIRA, Analysis, and Documentation tools."""
    # Load configuration from environment
    config = Config.from_env()

    # Initialize provider and store
    provider = AnthropicProvider(config.api_key, config.model)
    store = ConversationStore(config.conversations_dir)

    # Setup tool registry with Phase 1 + Phase 2 + Phase 3 tools
    registry = ToolRegistry()

    # Phase 1: JIRA tool
    registry.register(
        name="get_jira_data",
        description=(
            "Retrieve JIRA metadata for ALL features being investigated. "
            "Returns feature_id, jira_key, summary, status, and data_quality for each feature. "
            "Use this first to see what features are available and their current state."
        ),
        input_schema=GET_JIRA_DATA_SCHEMA,
        handler=get_jira_data,
    )

    # Phase 2: Analysis tool
    registry.register(
        name="get_analysis",
        description=(
            "Retrieve detailed analysis data for a specific feature. "
            "Provides metrics (test_coverage_report, unit_test_results, pipeline_results, "
            "performance_benchmarks, security_scan_results) and reviews (security, stakeholders, uat). "
            "Use after identifying the feature with get_jira_data."
        ),
        input_schema=GET_ANALYSIS_SCHEMA,
        handler=get_analysis,
    )

    # Phase 3: Documentation tools
    registry.register(
        name="list_docs",
        description=(
            "List available documentation files for a feature. "
            "Returns metadata (path, name, size, modified) for each document. "
            "Use this before read_doc to see what documentation exists."
        ),
        input_schema=LIST_DOCS_SCHEMA,
        handler=list_docs,
    )

    registry.register(
        name="read_doc",
        description=(
            "Read the contents of a documentation file. "
            "Takes the path from list_docs output. Large files (15-25KB) may be substantial. "
            "Be selective - only read documents you actually need for your assessment."
        ),
        input_schema=READ_DOC_SCHEMA,
        handler=read_doc,
    )

    # Create agent with all tools
    agent = Agent(provider, store, config, tool_registry=registry)

    # Start a new conversation
    conversation = agent.new_conversation()
    print(f"🔍 Started investigation session: {conversation.id}")
    print()

    # Example: Deep investigation of maintenance scheduling feature
    print("=" * 70)
    print("User: I need a thorough assessment of the maintenance scheduling")
    print("      feature including review of the deployment plan. Is it ready?")
    print("=" * 70)
    print()

    response = await agent.send_message(
        conversation,
        "I need a thorough assessment of the maintenance scheduling feature including "
        "review of the deployment plan. Is it production ready?",
    )

    print("Agent:")
    print(response)
    print()

    # Summary
    print("=" * 70)
    print(f"📊 Session Summary")
    print("=" * 70)
    print(f"Total messages: {len(conversation.messages)}")
    print(f"Trace ID: {conversation.trace_id}")
    print(f"Conversation saved: {config.conversations_dir}/{conversation.id}.json")
    print(f"Trace saved: data/traces/{conversation.trace_id}.json")
    print()
    print("💡 Check the trace file to see:")
    print("   - Tool calls made (JIRA, Analysis, Documentation)")
    print("   - Which documents were read and their sizes")
    print("   - Context window usage (Phase 4 will address this!)")
    print("   - Token counts for each operation")


if __name__ == "__main__":
    asyncio.run(main())
