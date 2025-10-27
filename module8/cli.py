"""Command-line interface for the AI agent."""

import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from investigator_agent.agent import Agent
from investigator_agent.config import Config
from investigator_agent.observability.tracer import setup_tracer
from investigator_agent.persistence.store import ConversationStore
from investigator_agent.providers.anthropic import AnthropicProvider
from investigator_agent.tools.registry import ToolRegistry
from investigator_agent.tools.release_tools import (
    get_release_summary,
    file_risk_report,
    GET_RELEASE_SUMMARY_SCHEMA,
    FILE_RISK_REPORT_SCHEMA,
)
from investigator_agent.tools.jira import (
    get_jira_data,
    GET_JIRA_DATA_SCHEMA,
)
from investigator_agent.tools.analysis import (
    get_analysis,
    GET_ANALYSIS_SCHEMA,
)
from investigator_agent.tools.docs import (
    list_docs,
    read_doc,
    LIST_DOCS_SCHEMA,
    READ_DOC_SCHEMA,
)

# Load environment variables from .env file
load_dotenv()


def print_conversations(agent: Agent) -> None:
    """Print list of conversations."""
    conversations = agent.list_conversations()
    if not conversations:
        print("No conversations found.")
        return

    print("\nConversations:")
    for conv_id, timestamp in conversations:
        print(f"  {conv_id[:8]}... (Last updated: {timestamp})")
    print()


def print_traces(conversation_id: str, config: Config) -> None:
    """Print all traces for a given conversation ID."""
    # Load the conversation to get its full ID
    store = ConversationStore(config.conversations_dir)
    try:
        conversation = store.load(conversation_id)
    except FileNotFoundError:
        print(f"Conversation {conversation_id} not found.")
        sys.exit(1)

    # Find all trace files and filter by session.id
    traces_dir = Path(config.traces_dir)
    if not traces_dir.exists():
        print(f"No traces directory found at {traces_dir}")
        sys.exit(1)

    matching_traces = []
    for trace_file in traces_dir.glob("*.json"):
        try:
            with open(trace_file) as f:
                spans = json.load(f)
                # Check if any span has matching session.id
                for span in spans:
                    if span.get("attributes", {}).get("session.id") == conversation.id:
                        matching_traces.append((trace_file, spans))
                        break
        except (json.JSONDecodeError, IOError):
            continue

    if not matching_traces:
        print(f"No traces found for conversation {conversation_id[:8]}...")
        return

    print(f"\nTraces for conversation {conversation_id[:8]}... (session.id: {conversation.id})")
    print(f"Found {len(matching_traces)} trace file(s)\n")

    for trace_file, spans in matching_traces:
        print(f"=== {trace_file.name} ===")
        print(json.dumps(spans, indent=2))
        print()


async def run_conversation(agent: Agent, conversation_id: str | None = None) -> None:
    """Run an interactive conversation."""
    if conversation_id:
        try:
            conversation = agent.load_conversation(conversation_id)
            print(f"\nContinuing conversation {conversation_id[:8]}...")
            print("\nPrevious messages:")
            for msg in conversation.messages:
                print(f"{msg.role.upper()}: {msg.content}")
            print()
        except FileNotFoundError:
            print(f"Conversation {conversation_id} not found. Starting new conversation.")
            conversation = agent.new_conversation()
    else:
        conversation = agent.new_conversation()
        print(f"\nStarted new conversation: {conversation.id[:8]}...")

    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            response = await agent.send_message(conversation, user_input)
            print(f"\nAssistant: {response}\n")

        except EOFError:
            print("\n\nGoodbye!")
            break
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


def main() -> None:
    """Main CLI entry point."""
    try:
        config = Config.from_env()
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    # Initialize observability
    setup_tracer(config.traces_dir)

    # Initialize tool registry and register tools
    tool_registry = ToolRegistry()

    # Release tools (Module 7)
    tool_registry.register(
        name="get_release_summary",
        description="Retrieve detailed information about a specific release, including changes, test results, and deployment metrics",
        input_schema=GET_RELEASE_SUMMARY_SCHEMA,
        handler=get_release_summary,
    )
    tool_registry.register(
        name="file_risk_report",
        description="File a risk assessment report for a release with severity level and findings",
        input_schema=FILE_RISK_REPORT_SCHEMA,
        handler=file_risk_report,
    )

    # JIRA tools (Module 8)
    tool_registry.register(
        name="get_jira_data",
        description="Retrieve JIRA metadata for all features, including their IDs, summaries, status, and data quality indicators",
        input_schema=GET_JIRA_DATA_SCHEMA,
        handler=get_jira_data,
    )

    # Analysis tools (Module 8)
    tool_registry.register(
        name="get_analysis",
        description="Retrieve analysis data (metrics or reviews) for a specific feature. Available types: performance_benchmarks, pipeline_results, security_scan_results, test_coverage_report, unit_test_results, security, stakeholders, uat",
        input_schema=GET_ANALYSIS_SCHEMA,
        handler=get_analysis,
    )

    # Documentation tools (Module 8)
    tool_registry.register(
        name="list_docs",
        description="List all documentation files available for a specific feature",
        input_schema=LIST_DOCS_SCHEMA,
        handler=list_docs,
    )
    tool_registry.register(
        name="read_doc",
        description="Read the contents of a documentation file for a feature",
        input_schema=READ_DOC_SCHEMA,
        handler=read_doc,
    )

    provider = AnthropicProvider(config.api_key, config.model)
    store = ConversationStore(config.conversations_dir)
    agent = Agent(provider, store, config, tool_registry=tool_registry)

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "list":
            print_conversations(agent)
        elif command == "continue" and len(sys.argv) > 2:
            asyncio.run(run_conversation(agent, sys.argv[2]))
        elif command == "trace" and len(sys.argv) > 2:
            print_traces(sys.argv[2], config)
        else:
            print("Usage:")
            print("  python cli.py              - Start a new conversation")
            print("  python cli.py list         - List all conversations")
            print("  python cli.py continue ID  - Continue a conversation")
            print("  python cli.py trace ID     - View all traces for a conversation")
            sys.exit(1)
    else:
        asyncio.run(run_conversation(agent))


if __name__ == "__main__":
    main()
