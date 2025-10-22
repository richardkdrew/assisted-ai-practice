# Graphiti MCP Server

Model Context Protocol (MCP) server exposing [Graphiti](https://github.com/getzep/graphiti) temporal knowledge graph capabilities.

## Features

- **Episode Management**: Add, retrieve, and delete episodic memories
- **Automatic Entity Extraction**: Entities and relationships extracted automatically from text
- **Hybrid Search**: Combines semantic search with graph structure
- **Temporal Queries**: Time-aware search with start/end time constraints
- **Graph Reasoning**: Entity-centric queries and relationship traversal
- **SSE Transport**: Real-time streaming via Server-Sent Events

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Set required environment variables
export OPENAI_API_KEY=your_key_here
export OPENAI_BASE_URL=https://api.openai.com/v1  # Optional
export OPENAI_MODEL_NAME=gpt-4o-mini              # Optional

# Start Graphiti + Neo4j
docker-compose up graphiti-mcp neo4j
```

The server will be available at `http://localhost:8000/sse`

### Local Development

```bash
# Install dependencies
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
uv pip install -r ../requirements.txt

# Set environment variables
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=password123
export OPENAI_API_KEY=your_key_here

# Run server
python graphiti_mcp_server.py --transport sse
```

## Available Tools

### `graphiti_add_episode`
Add an episode to the knowledge graph with automatic entity extraction.

```json
{
  "content": "User John reported a bug in the authentication module",
  "source_description": "user_report",
  "reference_time": "2025-01-15T10:30:00Z",
  "metadata": {"priority": "high"}
}
```

### `graphiti_search`
Search using hybrid semantic + graph search.

```json
{
  "query": "authentication bugs",
  "limit": 10,
  "start_time": "2025-01-01T00:00:00Z",
  "end_time": "2025-01-31T23:59:59Z"
}
```

### `graphiti_get_episode`
Retrieve a specific episode by UUID.

```json
{
  "episode_id": "uuid-here"
}
```

### `graphiti_delete_episode`
Delete an episode from the graph.

```json
{
  "episode_id": "uuid-here"
}
```

### `graphiti_entity_search`
Search for entities by name.

```json
{
  "query": "John",
  "limit": 10
}
```

### `graphiti_clear_graph`
Clear all data from the graph (use with caution).

```json
{}
```

## Architecture

```
┌─────────────────┐
│  MCP Client     │ (Investigator Agent)
│  (SSE)          │
└────────┬────────┘
         │ HTTP/SSE
         ▼
┌─────────────────┐
│ Graphiti MCP    │ (This Server)
│ Server          │
└────────┬────────┘
         │ Bolt Protocol
         ▼
┌─────────────────┐
│ Neo4j Database  │
│ (Graph Store)   │
└─────────────────┘
         │ OpenAI API
         ▼
┌─────────────────┐
│ Entity Extract  │
│ & Embeddings    │
└─────────────────┘
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `password123` |
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `OPENAI_BASE_URL` | OpenAI API base URL | `https://api.openai.com/v1` |
| `MODEL_NAME` | LLM model for entity extraction | `gpt-4o-mini` |
| `GRAPHITI_MCP_HOST` | Server host | `0.0.0.0` |
| `GRAPHITI_MCP_PORT` | Server port | `8000` |

## Use Cases

### Agent Memory Store
Store agent decisions, assessments, and reasoning as episodes.

```python
# Via MCP client
await mcp_client.call_tool("graphiti_add_episode", {
    "content": f"Feature {feature_id} assessed as ready. Tests pass, docs complete.",
    "metadata": {"feature_id": feature_id, "decision": "ready"}
})
```

### Temporal Queries
Find all memories from a specific time period.

```python
results = await mcp_client.call_tool("graphiti_search", {
    "query": "feature assessments",
    "start_time": "2025-01-01T00:00:00Z",
    "end_time": "2025-01-31T23:59:59Z"
})
```

### Entity-Centric Analysis
Retrieve all episodes mentioning a specific entity.

```python
results = await mcp_client.call_tool("graphiti_entity_search", {
    "query": "authentication module"
})
```

## Advantages Over Vector Stores

1. **Temporal Reasoning**: Understands when things happened and how they relate
2. **Relationship Modeling**: Explicit links between entities (e.g., "Feature A depends on Feature B")
3. **Entity Consolidation**: Automatically merges references to the same entity
4. **Graph Traversal**: Answer questions like "What features did user X work on?"
5. **Richer Context**: Preserves semantic structure beyond embeddings

## Troubleshooting

### Connection Refused
Ensure Neo4j is running:
```bash
docker-compose up neo4j
# Wait for health check to pass
```

### OpenAI API Errors
Check your API key and quota:
```bash
echo $OPENAI_API_KEY
```

### Episode Not Found
Episodes use UUIDs - ensure you're using the correct format.

## Testing

```bash
# Test the SSE endpoint
curl -X POST http://localhost:8000/sse \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'
```

## Learn More

- [Graphiti Documentation](https://docs.getzep.com/graphiti/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Neo4j Graph Database](https://neo4j.com/)
