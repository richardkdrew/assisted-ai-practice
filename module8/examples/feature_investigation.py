"""Feature investigation example for Investigator Agent (Module 8 - Phase 1)."""

import asyncio

from investigator_agent import Agent, Config
from investigator_agent.persistence.store import ConversationStore
from investigator_agent.providers.anthropic import AnthropicProvider
from investigator_agent.tools.jira import GET_JIRA_DATA_SCHEMA, get_jira_data
from investigator_agent.tools.registry import ToolRegistry


async def main():
    """Run a feature investigation with the Investigator Agent."""
    # Load configuration from environment
    config = Config.from_env()

    # Initialize provider and store
    provider = AnthropicProvider(config.api_key, config.model)
    store = ConversationStore(config.conversations_dir)

    # Setup tool registry with JIRA tool
    registry = ToolRegistry()
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

    # Create agent with tools
    agent = Agent(provider, store, config, tool_registry=registry)

    # Start a new conversation
    conversation = agent.new_conversation()
    print(f"🔍 Started investigation session: {conversation.id}")
    print()

    # Example 1: Ask about the maintenance scheduling feature (should be READY)
    print("=" * 70)
    print("User: Is the maintenance scheduling feature ready for production?")
    print("=" * 70)
    print()

    response = await agent.send_message(
        conversation, "Is the maintenance scheduling feature ready for production?"
    )

    print("Agent:")
    print(response)
    print()

    # Example 2: Ask about all features
    print("=" * 70)
    print("User: What features are currently being developed?")
    print("=" * 70)
    print()

    response = await agent.send_message(
        conversation, "What features are currently being developed?"
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


if __name__ == "__main__":
    asyncio.run(main())
