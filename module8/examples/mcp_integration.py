"""Feature Investigation with MCP Integration Example.

This example demonstrates the complete MCP integration for the Investigator Agent:

1. Connecting to MCP servers (ChromaDB, Graphiti)
2. Using vector store for semantic search over artifacts
3. Using knowledge graph for code analysis
4. Storing agent memories in vector database
5. Retrieving relevant past assessments

Architecture:
- ChromaDB MCP Server: Vector search over planning docs/PRDs
- Graphiti MCP Server: Temporal knowledge graph for code relationships
- Agent: Uses both backends for comprehensive feature assessment

Prerequisites:
1. Start MCP servers:
   ```
   docker-compose up chroma-mcp graphiti-mcp neo4j
   ```

2. Ingest test data:
   ```
   ./scripts/vector_store_cli.sh ingest
   ./scripts/neo4j_code_cli.sh ingest --reset
   ```

3. Set environment variables in .env:
   ```
   ANTHROPIC_API_KEY=your_key
   MCP_CHROMA_URL=http://localhost:8001/sse
   MCP_GRAPHITI_URL=http://localhost:8000/sse
   ```
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from investigator_agent.agent import Agent
from investigator_agent.config import Config
from investigator_agent.mcp.client import MCPClient, setup_mcp_tools
from investigator_agent.memory.mcp_store import MCPChromaMemoryStore
from investigator_agent.memory.protocol import Memory
from investigator_agent.models import Conversation
from investigator_agent.persistence.store import ConversationStore
from investigator_agent.providers.anthropic import AnthropicProvider
from investigator_agent.tools.registry import ToolRegistry

# Load environment
load_dotenv()

# MCP server URLs from environment
CHROMA_MCP_URL = os.getenv("MCP_CHROMA_URL", "http://localhost:8001/sse")
GRAPHITI_MCP_URL = os.getenv("MCP_GRAPHITI_URL", "http://localhost:8000/sse")


async def main():
    """Run the MCP-integrated feature investigation agent."""
    print("=" * 80)
    print("Feature Investigation Agent with MCP Integration")
    print("=" * 80)
    print()

    # 1. Initialize core components
    print("📦 Initializing components...")
    config = Config()
    provider = AnthropicProvider(
        api_key=config.api_key,
        model=config.model_name,
    )
    store = ConversationStore(config.conversations_dir)
    tool_registry = ToolRegistry()

    # 2. Connect to MCP servers
    print("\n🔌 Connecting to MCP servers...")

    # Connect to ChromaDB MCP server
    print(f"  - Connecting to ChromaDB MCP: {CHROMA_MCP_URL}")
    chroma_client = MCPClient(server_url=CHROMA_MCP_URL, transport="sse")

    try:
        await chroma_client.connect()
        print("    ✅ ChromaDB MCP connected")
    except Exception as e:
        print(f"    ❌ ChromaDB MCP connection failed: {e}")
        print("    💡 Start with: docker-compose up chroma-mcp")
        chroma_client = None

    # Connect to Graphiti MCP server (optional)
    print(f"  - Connecting to Graphiti MCP: {GRAPHITI_MCP_URL}")
    graphiti_client = MCPClient(server_url=GRAPHITI_MCP_URL, transport="sse")

    try:
        await graphiti_client.connect()
        print("    ✅ Graphiti MCP connected")
    except Exception as e:
        print(f"    ⚠️  Graphiti MCP connection failed: {e}")
        print("    💡 Start with: docker-compose --profile graphiti up")
        graphiti_client = None

    # 3. Set up MCP memory store
    memory_store = None
    if chroma_client:
        print("\n💾 Setting up MCP-backed memory store...")
        memory_store = MCPChromaMemoryStore(
            mcp_client=chroma_client,
            collection_name="agent_memories"
        )
        await memory_store.initialize()
        print("    ✅ Memory store initialized (ChromaDB)")

    # 4. Register MCP tools with agent
    print("\n🔧 Registering MCP tools...")
    mcp_adapter = None

    if chroma_client:
        # Register ChromaDB tools
        from investigator_agent.mcp.client import MCPToolAdapter
        mcp_adapter = MCPToolAdapter(tool_registry)

        chroma_tools = await mcp_adapter.register_mcp_server(
            chroma_client,
            prefix="",  # No prefix, use original tool names
            tool_filter=lambda name: name.startswith("chroma_")
        )
        print(f"    ✅ Registered {chroma_tools} ChromaDB tools")

    if graphiti_client:
        # Register Graphiti tools
        graphiti_tools = await mcp_adapter.register_mcp_server(
            graphiti_client,
            prefix="graph_",
            tool_filter=lambda name: name.startswith("graphiti_")
        )
        print(f"    ✅ Registered {graphiti_tools} Graphiti tools")

    # Also register the legacy tools (JIRA, analysis, docs, vector store)
    from investigator_agent.tools.jira import register_jira_tools
    from investigator_agent.tools.analysis import register_analysis_tools
    from investigator_agent.tools.docs import register_documentation_tools

    # Import vector store tools if available
    try:
        from scripts.vector_store_tools import register_vector_store_tools
        register_vector_store_tools(tool_registry)
        print("    ✅ Registered vector store tools (direct ChromaDB)")
    except ImportError:
        print("    ⚠️  Vector store tools not available")

    register_jira_tools(tool_registry)
    register_analysis_tools(tool_registry)
    register_documentation_tools(tool_registry)
    print(f"    ✅ Registered {len(tool_registry.get_tool_definitions())} total tools")

    # 5. Create agent with MCP memory
    print("\n🤖 Creating agent...")
    agent = Agent(
        provider=provider,
        store=store,
        config=config,
        tool_registry=tool_registry,
        memory_store=memory_store,
    )
    print("    ✅ Agent ready with MCP backends")

    # 6. Run feature investigation
    print("\n" + "=" * 80)
    print("Running Feature Investigation")
    print("=" * 80)

    conversation = Conversation()

    # Example: Investigate a feature using MCP-backed tools
    query = """
    Is the Maintenance Scheduling & Alert System (FEAT-MS-001) ready for production?

    Please:
    1. Check JIRA status
    2. Search the vector store for relevant planning documents and decisions
    3. Analyze test results and code quality
    4. If there are similar past assessments, use them to inform your decision
    5. Provide a clear ready/not-ready recommendation with justification
    """

    print("\n📝 User Query:")
    print(query)
    print("\n🔄 Agent Processing...")
    print("-" * 80)

    response = await agent.send_message(conversation, query)

    print("\n💬 Agent Response:")
    print(response)
    print("-" * 80)

    # 7. Store assessment in memory (if successful)
    if memory_store and "ready" in response.lower():
        print("\n💾 Storing assessment in memory...")

        # Extract decision from response
        decision = "ready" if "production" in response.lower() and "ready" in response.lower() else "not_ready"

        memory = Memory(
            id=f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            feature_id="FEAT-MS-001",
            decision=decision,
            justification=response[:500],  # First 500 chars
            key_findings={
                "timestamp": datetime.now().isoformat(),
                "tools_used": [call.name for call in conversation.messages[-2].content if hasattr(call, 'name')],
                "assessment_type": "production_readiness",
            },
            timestamp=datetime.now(),
            metadata={"conversation_id": conversation.id}
        )

        await memory_store.store(memory)
        print(f"    ✅ Stored memory: {memory.id}")

    # 8. Cleanup
    print("\n🧹 Cleanup...")
    if mcp_adapter:
        await mcp_adapter.disconnect_all()
        print("    ✅ Disconnected MCP clients")

    print("\n✅ Example complete!")
    print("\n" + "=" * 80)
    print("Summary:")
    print("-" * 80)
    print(f"Tools registered: {len(tool_registry.get_tool_definitions())}")
    print(f"MCP backends: ChromaDB {'✅' if chroma_client else '❌'}, Graphiti {'✅' if graphiti_client else '❌'}")
    print(f"Memory stored: {'✅' if memory_store else '❌'}")
    print(f"Messages exchanged: {len(conversation.messages)}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
