"""Example: Feature Investigation with Sub-Conversation Context Management (Phase 4).

This example demonstrates how the Investigator Agent uses sub-conversations to analyze
large documentation without overwhelming the main conversation context.

Key Capabilities Demonstrated:
1. JIRA metadata retrieval
2. Analysis data gathering
3. Documentation listing and reading
4. **Automatic sub-conversation creation for large documents**
5. **Context window management with summarization**
6. Production readiness assessment

This builds on Phase 3 by adding sub-conversation support for large tool results.
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from investigator_agent import Agent, AnthropicProvider, Config, ConversationStore
from investigator_agent.observability import setup_tracer
from investigator_agent.system_prompt import DEFAULT_SYSTEM_PROMPT
from investigator_agent.tools import (
    get_analysis,
    get_jira_data,
    list_docs,
    read_doc,
)
from investigator_agent.tools.registry import ToolRegistry

# Load environment variables
load_dotenv()


async def main():
    """Run feature investigation example with sub-conversation support."""
    print("=" * 80)
    print("Phase 4: Feature Investigation with Sub-Conversation Context Management")
    print("=" * 80)
    print()

    # Setup
    traces_dir = Path("traces")
    traces_dir.mkdir(exist_ok=True)
    setup_tracer(traces_dir)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found in environment")
        print("Please set it in .env file or environment variables")
        return

    # Initialize components
    provider = AnthropicProvider(api_key=api_key, model="claude-3-5-sonnet-20241022")
    store = ConversationStore(Path("conversations"))
    config = Config(system_prompt=DEFAULT_SYSTEM_PROMPT, max_tokens=4096)

    # Register all investigation tools
    tool_registry = ToolRegistry()
    tool_registry.register_tool(
        name="get_jira_data",
        description=(
            "Retrieves metadata for all features in the system. Returns an array with "
            "folder, jira_key, feature_id, summary, status, and data_quality for each feature. "
            "Call this at the start of an assessment to identify which feature the user is asking about."
        ),
        input_schema={"type": "object", "properties": {}, "required": []},
        handler=get_jira_data,
    )

    tool_registry.register_tool(
        name="get_analysis",
        description=(
            "Retrieves analysis and metrics data for a feature. "
            "Available analysis types: "
            "performance_benchmarks, pipeline_results, security_scan_results, "
            "test_coverage_report, unit_test_results, security, stakeholders, uat"
        ),
        input_schema={
            "type": "object",
            "properties": {
                "feature_id": {
                    "type": "string",
                    "description": "The feature identifier from get_jira_data",
                },
                "analysis_type": {
                    "type": "string",
                    "description": "Type of analysis to retrieve",
                },
            },
            "required": ["feature_id", "analysis_type"],
        },
        handler=get_analysis,
    )

    tool_registry.register_tool(
        name="list_docs",
        description=(
            "Lists available planning documentation files for a feature. "
            "Returns metadata about each document including path, name, and size."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "feature_id": {
                    "type": "string",
                    "description": "The feature identifier from get_jira_data",
                }
            },
            "required": ["feature_id"],
        },
        handler=list_docs,
    )

    tool_registry.register_tool(
        name="read_doc",
        description=(
            "Retrieves the contents of a documentation file. "
            "Use list_docs first to see available documents. "
            "Large documents (>10K tokens) will be automatically analyzed in sub-conversations."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the document (from list_docs output)"}
            },
            "required": ["path"],
        },
        handler=read_doc,
    )

    # Create agent
    agent = Agent(provider=provider, store=store, config=config, tool_registry=tool_registry)

    print("🤖 Investigator Agent initialized with Phase 4 capabilities:")
    print("   ✓ JIRA metadata retrieval")
    print("   ✓ Analysis data gathering")
    print("   ✓ Documentation access")
    print("   ✓ Sub-conversation context management (NEW!)")
    print("   ✓ Automatic summarization for large documents")
    print()

    # Create conversation
    conversation = agent.new_conversation()
    print(f"📝 Conversation ID: {conversation.id}")
    print()

    # Example 1: Investigate feature with large documentation
    print("=" * 80)
    print("Example 1: Investigate Maintenance Scheduling Feature")
    print("This feature has large documentation files (ARCHITECTURE.md, DESIGN_DOC.md)")
    print("that will trigger sub-conversations.")
    print("=" * 80)
    print()

    query1 = """Is the Maintenance Scheduling & Alert System feature ready for production?
Please check the architecture documentation to understand the implementation."""

    print(f"User: {query1}")
    print()
    print("Agent: (Processing with sub-conversation support...)")
    print()

    response1 = await agent.send_message(conversation, query1)
    print(f"Agent: {response1}")
    print()

    # Show sub-conversation details
    if conversation.sub_conversations:
        print("📊 Sub-Conversation Summary:")
        print(f"   Total sub-conversations created: {len(conversation.sub_conversations)}")
        for i, sub_conv in enumerate(conversation.sub_conversations, 1):
            print(f"\n   Sub-conversation {i}:")
            print(f"   - ID: {sub_conv.id}")
            print(f"   - Purpose: {sub_conv.purpose}")
            print(f"   - Tokens used: {sub_conv.token_count}")
            print(f"   - Summary length: {len(sub_conv.summary)} chars")
            print(f"   - Created: {sub_conv.created_at.strftime('%H:%M:%S')}")
            print(f"   - Completed: {sub_conv.completed_at.strftime('%H:%M:%S') if sub_conv.completed_at else 'In progress'}")
        print()

    print("=" * 80)
    print()

    # Example 2: Compare with small document (no sub-conversation)
    print("=" * 80)
    print("Example 2: Read a Small Document")
    print("This will demonstrate that small documents DON'T trigger sub-conversations.")
    print("=" * 80)
    print()

    query2 = "Can you also check the user stories for this feature?"

    print(f"User: {query2}")
    print()

    sub_conv_count_before = len(conversation.sub_conversations)
    response2 = await agent.send_message(conversation, query2)
    sub_conv_count_after = len(conversation.sub_conversations)

    print(f"Agent: {response2}")
    print()

    if sub_conv_count_after == sub_conv_count_before:
        print("✓ No new sub-conversation created (document was small enough)")
    else:
        print(f"ℹ️ New sub-conversation created (document was large)")
    print()

    print("=" * 80)
    print()

    # Example 3: Final assessment
    print("=" * 80)
    print("Example 3: Make Final Assessment")
    print("=" * 80)
    print()

    query3 = "Based on all the information you've gathered, provide your final production readiness assessment."

    print(f"User: {query3}")
    print()

    response3 = await agent.send_message(conversation, query3)
    print(f"Agent: {response3}")
    print()

    # Final statistics
    print("=" * 80)
    print("📊 Session Statistics")
    print("=" * 80)
    print(f"Total messages in conversation: {len(conversation.messages)}")
    print(f"Total sub-conversations created: {len(conversation.sub_conversations)}")
    print(f"Trace ID: {conversation.trace_id}")
    print()

    if conversation.sub_conversations:
        total_sub_tokens = sum(sc.token_count for sc in conversation.sub_conversations)
        total_summary_chars = sum(len(sc.summary) for sc in conversation.sub_conversations)
        print("Sub-conversation details:")
        print(f"  - Total tokens in sub-conversations: {total_sub_tokens}")
        print(f"  - Total summary characters: {total_summary_chars}")
        print(f"  - Average tokens per sub-conversation: {total_sub_tokens // len(conversation.sub_conversations)}")
        print()

    print(f"💾 Conversation saved to: conversations/{conversation.id}.json")
    print(f"📈 Traces saved to: traces/")
    print()
    print("✅ Phase 4 example complete!")
    print()
    print("Key Takeaways:")
    print("1. Large documents (>10K tokens) automatically trigger sub-conversations")
    print("2. Sub-conversations isolate the analysis to prevent context overflow")
    print("3. The main conversation receives concise summaries")
    print("4. Small documents are processed directly without sub-conversations")
    print("5. This enables analysis of extensive documentation without limits")


if __name__ == "__main__":
    asyncio.run(main())
