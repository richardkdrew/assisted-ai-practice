"""Feature investigation with Analysis tool (Module 8 - Phase 2)."""

import asyncio

from investigator_agent import Agent, Config
from investigator_agent.persistence.store import ConversationStore
from investigator_agent.providers.anthropic import AnthropicProvider
from investigator_agent.tools.analysis import GET_ANALYSIS_SCHEMA, get_analysis
from investigator_agent.tools.jira import GET_JIRA_DATA_SCHEMA, get_jira_data
from investigator_agent.tools.registry import ToolRegistry


async def main():
    """Run a comprehensive feature investigation with both JIRA and Analysis tools."""
    # Load configuration from environment
    config = Config.from_env()

    # Initialize provider and store
    provider = AnthropicProvider(config.api_key, config.model)
    store = ConversationStore(config.conversations_dir)

    # Setup tool registry with Phase 1 + Phase 2 tools
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

    # Create agent with tools
    agent = Agent(provider, store, config, tool_registry=registry)

    # Start a new conversation
    conversation = agent.new_conversation()
    print(f"🔍 Started investigation session: {conversation.id}")
    print()

    # Example 1: Comprehensive assessment of maintenance scheduling feature
    print("=" * 70)
    print("User: Give me a comprehensive assessment of the maintenance scheduling")
    print("      feature. Is it ready for production?")
    print("=" * 70)
    print()

    response = await agent.send_message(
        conversation,
        "Give me a comprehensive assessment of the maintenance scheduling feature. "
        "Is it ready for production?",
    )

    print("Agent:")
    print(response)
    print()

    # Example 2: Ask about QR code feature (in development)
    print("=" * 70)
    print("User: What about the QR code check-in feature?")
    print("=" * 70)
    print()

    response = await agent.send_message(
        conversation, "What about the QR code check-in feature? Is it ready?"
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
    print("   - Which analysis types the agent chose to investigate")
    print("   - How it used the data to make its decision")
    print("   - Token usage for each tool call")


if __name__ == "__main__":
    asyncio.run(main())
