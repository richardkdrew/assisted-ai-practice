"""Command-line interface for the AI agent."""

import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from detective_agent.agent import Agent
from detective_agent.config import Config
from detective_agent.observability.tracer import setup_tracer
from detective_agent.persistence.store import ConversationStore
from detective_agent.providers.anthropic import AnthropicProvider

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

    provider = AnthropicProvider(config.api_key, config.model)
    store = ConversationStore(config.conversations_dir)
    agent = Agent(provider, store, config)

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
