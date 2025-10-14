"""Command-line interface for the AI agent."""

import sys

from agent import Agent
from models.config import Config
from observability.tracer import setup_tracer
from persistence.store import ConversationStore
from providers.anthropic import AnthropicProvider


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


def run_conversation(agent: Agent, conversation_id: str | None = None) -> None:
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

            response = agent.send_message(conversation, user_input)
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
            run_conversation(agent, sys.argv[2])
        else:
            print("Usage:")
            print("  python cli.py              - Start a new conversation")
            print("  python cli.py list         - List all conversations")
            print("  python cli.py continue ID  - Continue a conversation")
            sys.exit(1)
    else:
        run_conversation(agent)


if __name__ == "__main__":
    main()
