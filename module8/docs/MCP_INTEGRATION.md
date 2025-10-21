# MCP Integration Guide

## Overview

The Investigator Agent supports the **Model Context Protocol (MCP)** for connecting to external knowledge backends like vector databases and knowledge graphs. This provides a standardized, interchangeable approach to memory and knowledge management.

### Why MCP?

- **Interchangeable Backends**: Switch between ChromaDB, Graphiti, Neo4j without code changes
- **Standard Protocol**: Industry-standard communication with AI tool servers
- **Separation of Concerns**: Memory logic separate from storage implementation
- **Future-Proof**: Easy to add new backends as MCP servers become available

### Supported Backends

| Backend | Type | Use Case | MCP Server |
|---------|------|----------|------------|
| **ChromaDB** | Vector Database | Semantic search over documents, memories | `chroma-mcp-server` |
| **Graphiti** | Knowledge Graph | Temporal relationships, entity extraction | `graphiti-mcp` (Zep) |
| **Neo4j** | Graph Database | Code AST, complex relationships | Via Graphiti or custom |
| **File** | JSON Files | Simple storage, no dependencies | Built-in (legacy) |

## Architecture

```
┌─────────────────────────────────────────┐
│      Investigator Agent                  │
│  ┌────────────────────────────────────┐ │
│  │  Agent Core                         │ │
│  │  - Tool execution                   │ │
│  │  - Memory retrieval                 │ │
│  │  - Sub-conversations                │ │
│  └────────────┬───────────────────────┘ │
│               │                          │
│  ┌────────────┴───────────────────────┐ │
│  │  MCP Adapter Layer                  │ │
│  │  - MCPClient                        │ │
│  │  - MCPToolAdapter                   │ │
│  │  - MCPMemoryStore                   │ │
│  └────────────┬───────────────────────┘ │
└───────────────┼─────────────────────────┘
                │ MCP Protocol (SSE/stdio)
       ┌────────┴────────┐
       │                 │
   ┌───▼────┐      ┌────▼──────┐
   │ Chroma │      │ Graphiti  │
   │  MCP   │      │   MCP     │
   │ Server │      │  Server   │
   └───┬────┘      └────┬──────┘
       │                │
   ┌───▼─────┐     ┌───▼────┐
   │ChromaDB │     │ Neo4j  │
   │  Vector │     │ Graph  │
   │   DB    │     │   DB   │
   └─────────┘     └────────┘
```

## Setup

### 1. Docker Compose Setup (Recommended)

The easiest way to run MCP servers is with Docker Compose:

```bash
# Start ChromaDB MCP server
docker-compose up chroma-mcp chroma

# Start Graphiti MCP server (optional)
docker-compose --profile graphiti up

# Start all services
docker-compose --profile graphiti up
```

### 2. Environment Configuration

Create/update `.env` file:

```bash
# ============================================================================
# MCP Configuration
# ============================================================================

# Global MCP Settings
MCP_ENABLED=true
MCP_MEMORY_BACKEND=chroma  # Options: file, chroma, graphiti, none

# ChromaDB MCP Server
MCP_CHROMA_ENABLED=true
MCP_CHROMA_URL=http://localhost:8001/sse
MCP_CHROMA_TRANSPORT=sse
MCP_CHROMA_COLLECTION=agent_memories

# Graphiti MCP Server (Optional)
MCP_GRAPHITI_ENABLED=false
MCP_GRAPHITI_URL=http://localhost:8000/sse
MCP_GRAPHITI_TRANSPORT=sse

# Neo4j (for Graphiti backend)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# OpenAI (for embeddings in ChromaDB/Graphiti)
OPENAI_API_KEY=your_openai_key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=384
```

### 3. Install Dependencies

```bash
# Install MCP dependencies
uv sync

# Verify MCP packages installed
uv pip list | grep mcp
```

### 4. Ingest Data (Optional)

Populate the knowledge backends with test data:

```bash
# Ingest documents to ChromaDB vector store
./scripts/vector_store_cli.sh ingest

# Ingest code to Neo4j graph (for Graphiti)
./scripts/neo4j_code_cli.sh ingest --reset

# Verify ingestion
./scripts/vector_store_cli.sh stats
./scripts/neo4j_code_cli.sh query stats
```

## Usage

### Basic MCP Setup

```python
import asyncio
from investigator_agent import Agent, Config
from investigator_agent.mcp import MCPClient, MCPToolAdapter, get_mcp_config

async def main():
    # 1. Load MCP configuration from environment
    mcp_config = get_mcp_config()
    mcp_config.validate()

    # 2. Connect to ChromaDB MCP server
    chroma_client = MCPClient(
        server_url=mcp_config.chroma.url,
        transport=mcp_config.chroma.transport
    )
    await chroma_client.connect()

    # 3. Register MCP tools with agent
    tool_registry = ToolRegistry()
    mcp_adapter = MCPToolAdapter(tool_registry)
    await mcp_adapter.register_mcp_server(chroma_client, prefix="")

    # 4. Create agent with MCP memory
    from investigator_agent.memory.mcp_store import MCPChromaMemoryStore

    memory_store = MCPChromaMemoryStore(chroma_client)
    await memory_store.initialize()

    agent = Agent(
        provider=provider,
        store=store,
        config=config,
        tool_registry=tool_registry,
        memory_store=memory_store
    )

    # 5. Use the agent
    conversation = agent.new_conversation()
    response = await agent.send_message(
        conversation,
        "Is FEAT-MS-001 ready for production? Check similar past assessments."
    )

    # 6. Cleanup
    await mcp_adapter.disconnect_all()

asyncio.run(main())
```

### Using Configuration Helper

```python
from investigator_agent.mcp import setup_mcp_tools

# Automatic setup based on environment
mcp_adapter = await setup_mcp_tools(
    tool_registry,
    chroma_url=os.getenv("MCP_CHROMA_URL"),
    graphiti_url=os.getenv("MCP_GRAPHITI_URL")
)
```

### Memory Backend Selection

```python
from investigator_agent.mcp import get_mcp_config, MemoryBackend
from investigator_agent.memory.file_store import FileMemoryStore
from investigator_agent.memory.mcp_store import MCPChromaMemoryStore, MCPGraphitiMemoryStore

mcp_config = get_mcp_config()

# Select memory backend based on configuration
if mcp_config.memory_backend == MemoryBackend.CHROMA:
    chroma_client = MCPClient(server_url=mcp_config.chroma.url)
    await chroma_client.connect()
    memory_store = MCPChromaMemoryStore(chroma_client)
    await memory_store.initialize()

elif mcp_config.memory_backend == MemoryBackend.GRAPHITI:
    graphiti_client = MCPClient(server_url=mcp_config.graphiti.url)
    await graphiti_client.connect()
    memory_store = MCPGraphitiMemoryStore(graphiti_client)

elif mcp_config.memory_backend == MemoryBackend.FILE:
    memory_store = FileMemoryStore(Path("./data/memory_store"))

else:  # MemoryBackend.NONE
    memory_store = None

agent = Agent(..., memory_store=memory_store)
```

## MCP Servers

### ChromaDB MCP Server

**Purpose**: Vector database for semantic search

**Tools Provided**:
- `chroma_create_collection`: Create a new collection
- `chroma_list_collections`: List all collections
- `chroma_delete_collection`: Delete a collection
- `chroma_add_documents`: Add documents with embeddings
- `chroma_query`: Semantic search over documents
- `chroma_get_documents`: Get documents by ID
- `chroma_delete_documents`: Delete documents

**Configuration**:
```python
MCPServerConfig(
    name="chroma",
    enabled=True,
    url="http://localhost:8001/sse",
    transport=MCPTransport.SSE,
    collection_name="agent_memories"
)
```

**Example Usage**:
```python
# Query similar past assessments
await mcp_client.call_tool(
    "chroma_query",
    {
        "collection": "agent_memories",
        "query_texts": ["payment processing feature readiness"],
        "n_results": 5
    }
)
```

### Graphiti MCP Server

**Purpose**: Temporal knowledge graph with entity extraction

**Tools Provided**:
- `graphiti_add_episode`: Add episode (auto-extracts entities)
- `graphiti_search`: Hybrid search (semantic + graph)
- `graphiti_get_entity`: Retrieve entity by name
- `graphiti_get_facts`: Get facts about entities
- `graphiti_delete_episode`: Delete episode

**Configuration**:
```python
MCPServerConfig(
    name="graphiti",
    enabled=True,
    url="http://localhost:8000/sse",
    transport=MCPTransport.SSE
)
```

**Example Usage**:
```python
# Add episode (entities extracted automatically)
await mcp_client.call_tool(
    "graphiti_add_episode",
    {
        "content": "Feature FEAT-MS-001 passed all tests. John approved for production.",
        "metadata": {"feature_id": "FEAT-MS-001", "decision": "ready"}
    }
)

# Search with temporal context
await mcp_client.call_tool(
    "graphiti_search",
    {
        "query": "features approved by John",
        "limit": 10
    }
)
```

## Advanced Topics

### Custom MCP Servers

You can add custom MCP servers to the configuration:

```python
mcp_config.servers["custom"] = MCPServerConfig(
    name="custom",
    enabled=True,
    url="http://localhost:9000/sse",
    transport=MCPTransport.SSE,
    tool_prefix="custom_"
)
```

### Stdio Transport (Local Processes)

For local MCP servers running as processes:

```python
MCPServerConfig(
    name="local",
    enabled=True,
    transport=MCPTransport.STDIO,
    command="python",
    args=["scripts/my_mcp_server.py"]
)
```

### Production Deployment

For production, use the configuration factory:

```python
from investigator_agent.mcp import MCPConfig

mcp_config = MCPConfig.production(
    chroma_url="https://chroma-mcp.example.com/sse",
    graphiti_url="https://graphiti-mcp.example.com/sse"
)
```

## Troubleshooting

### Connection Errors

```python
# Check if MCP server is running
curl http://localhost:8001/sse

# Check Docker containers
docker-compose ps

# View logs
docker-compose logs chroma-mcp
```

### Tool Not Found

```python
# List discovered tools
for tool_name in mcp_client.tools:
    print(f"- {tool_name}")

# Verify tool registration
print(tool_registry.get_tool_definitions())
```

### Memory Retrieval Issues

```python
# Test memory store directly
memories = await memory_store.retrieve(query="test", limit=5)
print(f"Found {len(memories)} memories")

# Check collection exists
await mcp_client.call_tool("chroma_list_collections", {})
```

## Performance Considerations

| Operation | ChromaDB | Graphiti | File-based |
|-----------|----------|----------|------------|
| Store memory | ~50ms | ~200ms | ~10ms |
| Semantic search | ~100ms | ~300ms | N/A |
| Retrieve by ID | ~30ms | ~100ms | ~5ms |
| Scale | 100K+ | 10K+ | <1K |

**Recommendations**:
- **Development**: Use file-based for simplicity
- **Production <10K memories**: ChromaDB for semantic search
- **Production >10K memories**: ChromaDB with batching
- **Complex relationships**: Graphiti for temporal/entity reasoning

## Examples

See complete examples in:
- `examples/feature_investigation_mcp.py` - Full MCP integration
- `examples/memory_with_mcp.py` - Memory-focused example
- `scripts/chroma_mcp_sse_server.py` - ChromaDB MCP server implementation

## Reference

- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://gofastmcp.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Graphiti (Zep) Documentation](https://help.getzep.com/graphiti/)
