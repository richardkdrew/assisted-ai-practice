"""Basic usage example for Detective Agent."""

import asyncio

from detective_agent import Agent, Config
from detective_agent.persistence.store import ConversationStore
from detective_agent.providers.anthropic import AnthropicProvider
from detective_agent.tools.registry import ToolRegistry
from detective_agent.tools.release_tools import (
    FILE_RISK_REPORT_SCHEMA,
    GET_RELEASE_SUMMARY_SCHEMA,
    file_risk_report,
    get_release_summary,
)


async def main():
    """Run a basic conversation with the Detective Agent."""
    # Load configuration from environment
    config = Config.from_env()

    # Initialize provider and store
    provider = AnthropicProvider(config.api_key, config.model)
    store = ConversationStore(config.conversations_dir)

    # Setup tool registry
    registry = ToolRegistry()
    registry.register(
        name="get_release_summary",
        description="Retrieve release information including version, changes, tests, and metrics",
        input_schema=GET_RELEASE_SUMMARY_SCHEMA,
        handler=get_release_summary,
    )
    registry.register(
        name="file_risk_report",
        description="File a risk assessment report with severity and findings",
        input_schema=FILE_RISK_REPORT_SCHEMA,
        handler=file_risk_report,
    )

    # Create agent with tools
    agent = Agent(provider, store, config, tool_registry=registry)

    # Start a new conversation
    conversation = agent.new_conversation()
    print(f"Started conversation: {conversation.id}")
    print()

    # Ask the agent to assess a release
    print("User: Assess the risk of deploying release rel-003")
    print()

    response = await agent.send_message(
        conversation, "Assess the risk of deploying release rel-003"
    )

    print("Agent:")
    print(response)
    print()

    # Check conversation history
    print(f"Total messages: {len(conversation.messages)}")
    print(f"Trace ID: {conversation.trace_id}")

    # Conversation is automatically saved
    print(f"\nConversation saved to: {config.conversations_dir}/{conversation.id}.json")
    print(f"Trace saved to: data/traces/{conversation.trace_id}.json")


if __name__ == "__main__":
    asyncio.run(main())
