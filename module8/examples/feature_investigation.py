"""Example: Feature Investigation with Memory System (Phase 5).

This example demonstrates how the Investigator Agent uses memory to learn from
past feature assessments and provide more consistent, informed decisions.

Key Capabilities Demonstrated:
1. JIRA metadata retrieval
2. Analysis data gathering
3. Documentation reading with sub-conversations
4. **Memory storage after assessments**
5. **Memory retrieval for similar features**
6. **Learning from past decisions**

This builds on Phase 4 by adding memory capabilities for continuous learning.
"""

import asyncio
import os
import uuid
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from investigator_agent import Agent, AnthropicProvider, Config, ConversationStore
from investigator_agent.memory import FileMemoryStore, Memory
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
    """Run feature investigation example with memory system."""
    print("=" * 80)
    print("Phase 5: Feature Investigation with Memory System")
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

    # Initialize memory store (NEW!)
    memory_dir = Path("memory_store")
    memory_store = FileMemoryStore(memory_dir)
    print(f"💾 Memory store initialized at: {memory_dir}")
    print(f"   Existing memories: {len(memory_store.list_all())}")
    print()

    # Register all investigation tools
    tool_registry = ToolRegistry()
    tool_registry.register(
        name="get_jira_data",
        description=(
            "Retrieves metadata for all features in the system. Returns an array with "
            "folder, jira_key, feature_id, summary, status, and data_quality for each feature. "
            "Call this at the start of an assessment to identify which feature the user is asking about."
        ),
        input_schema={"type": "object", "properties": {}, "required": []},
        handler=get_jira_data,
    )

    tool_registry.register(
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

    tool_registry.register(
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

    tool_registry.register(
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

    # Create agent with memory (NEW!)
    agent = Agent(
        provider=provider,
        store=store,
        config=config,
        tool_registry=tool_registry,
        memory_store=memory_store,  # Memory enabled!
    )

    print("🤖 Investigator Agent initialized with Phase 5 capabilities:")
    print("   ✓ JIRA metadata retrieval")
    print("   ✓ Analysis data gathering")
    print("   ✓ Documentation access with sub-conversations")
    print("   ✓ Memory system for learning from past assessments (NEW!)")
    print()

    # Example 1: First assessment (no memory available yet)
    print("=" * 80)
    print("Example 1: First Assessment - Maintenance Scheduling Feature")
    print("(No prior memory available)")
    print("=" * 80)
    print()

    conversation1 = agent.new_conversation()
    query1 = "Is the Maintenance Scheduling & Alert System feature ready for production?"

    # Check for memories before assessment
    memories1 = agent.retrieve_relevant_memories(query1)
    print(f"📚 Memories retrieved: {len(memories1)}")
    if memories1:
        for mem in memories1:
            print(f"   {mem}")
    else:
        print("   (No relevant memories found)")
    print()

    print(f"User: {query1}")
    print()

    response1 = await agent.send_message(conversation1, query1)
    print(f"Agent: {response1}")
    print()

    # Store memory of this assessment (simulated - in real system, agent would do this)
    memory1 = Memory(
        id=str(uuid.uuid4()),
        feature_id="FEAT-MS-001",
        decision="ready",
        justification="All quality gates passed: 95% test coverage, UAT approved, security review complete",
        key_findings={
            "test_coverage": 95,
            "uat_status": "approved",
            "security_issues": 0,
            "performance": "excellent",
        },
        timestamp=datetime.now(),
        metadata={"conversation_id": conversation1.id},
    )
    memory_store.store(memory1)
    print("💾 Assessment stored in memory")
    print(f"   Memory ID: {memory1.id}")
    print(f"   Decision: {memory1.decision}")
    print()

    # Example 2: Second assessment with memory available
    print("=" * 80)
    print("Example 2: Re-Assessment - Same Feature After Changes")
    print("(Now we have memory of the previous assessment)")
    print("=" * 80)
    print()

    conversation2 = agent.new_conversation()
    query2 = "We made some updates to the Maintenance Scheduling feature. Is it still ready for production?"

    # Check for memories
    memories2 = agent.retrieve_relevant_memories(query2)
    print(f"📚 Memories retrieved: {len(memories2)}")
    for mem in memories2:
        print(f"   {mem}")
    print()

    # Include memory context in message (in a real system, this would be automatic)
    if memories2:
        context = "\n\n".join(memories2)
        enhanced_query = f"{query2}\n\nRELEVANT PAST ASSESSMENTS:\n{context}"
    else:
        enhanced_query = query2

    print(f"User: {query2}")
    print()

    response2 = await agent.send_message(conversation2, enhanced_query)
    print(f"Agent: {response2}")
    print()

    # Example 3: Third assessment - Different feature but similar
    print("=" * 80)
    print("Example 3: Assessment of Similar Feature")
    print("(Memory helps inform assessment of related features)")
    print("=" * 80)
    print()

    # First, store a memory for another feature to demonstrate similarity matching
    memory_similar = Memory(
        id=str(uuid.uuid4()),
        feature_id="FEAT-QR-002",
        decision="not_ready",
        justification="Test failures in UAT: 15% failure rate, security scan found 3 medium-severity issues",
        key_findings={
            "test_coverage": 78,
            "uat_pass_rate": 85,
            "security_issues": 3,
        },
        timestamp=datetime.now(),
        metadata={},
    )
    memory_store.store(memory_similar)

    conversation3 = agent.new_conversation()
    query3 = "What about the QR Code Check-in feature? Is it production-ready?"

    memories3 = agent.retrieve_relevant_memories(query3)
    print(f"📚 Memories retrieved: {len(memories3)}")
    for mem in memories3:
        print(f"   {mem}")
    print()

    print(f"User: {query3}")
    print()

    response3 = await agent.send_message(conversation3, query3)
    print(f"Agent: {response3}")
    print()

    # Final Statistics
    print("=" * 80)
    print("📊 Memory System Statistics")
    print("=" * 80)
    all_memories = memory_store.list_all()
    print(f"Total memories stored: {len(all_memories)}")
    print()

    for mem in all_memories:
        print(f"Memory {mem.id[:8]}...")
        print(f"  Feature: {mem.feature_id}")
        print(f"  Decision: {mem.decision}")
        print(f"  When: {mem.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    print("✅ Phase 5 example complete!")
    print()
    print("Key Takeaways:")
    print("1. Memory system stores past feature assessments")
    print("2. Relevant memories are retrieved for new assessments")
    print("3. Past decisions inform current analysis")
    print("4. Memory enables consistency across similar features")
    print("5. System learns and improves over time")
    print()
    print(f"💾 Memories saved to: {memory_dir}/")
    print(f"📝 Conversations saved to: conversations/")
    print(f"📈 Traces saved to: traces/")


if __name__ == "__main__":
    asyncio.run(main())
