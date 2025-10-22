"""Graphiti MCP Server with SSE (Server-Sent Events) transport.

This server exposes Graphiti temporal knowledge graph capabilities via the Model Context Protocol (MCP)
using SSE transport for real-time communication with AI agents.

Graphiti provides:
- Temporal knowledge graph (time-aware relationships)
- Automatic entity and relationship extraction
- Hybrid search (vector + graph structure)
- Episode-based memory organization
- Entity-centric queries

Features:
- Episode management (add, retrieve, delete)
- Entity extraction and linking
- Temporal search with time constraints
- Graph-based reasoning
- SSE transport for streaming responses
"""

import argparse
import logging
import os
from datetime import datetime
from typing import Any

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import TextContent, Tool
from starlette.applications import Starlette
from starlette.routing import Route

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("graphiti-mcp-server")

# Environment configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
GRAPHITI_MCP_HOST = os.getenv("GRAPHITI_MCP_HOST", "0.0.0.0")
GRAPHITI_MCP_PORT = int(os.getenv("GRAPHITI_MCP_PORT", "8000"))

# Validate required configuration
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize Graphiti client
logger.info(f"Initializing Graphiti client (Neo4j={NEO4J_URI}, Model={MODEL_NAME})")

try:
    graphiti_client = Graphiti(
        neo4j_uri=NEO4J_URI,
        neo4j_user=NEO4J_USER,
        neo4j_password=NEO4J_PASSWORD,
    )
    logger.info("Graphiti client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Graphiti client: {e}")
    raise

# Initialize MCP server
mcp_server = Server("graphiti-mcp")


# Tool definitions
@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available Graphiti tools."""
    return [
        Tool(
            name="graphiti_add_episode",
            description="Add an episode (memory/event) to the knowledge graph with automatic entity extraction",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Episode content/text to add to the graph",
                    },
                    "source_description": {
                        "type": "string",
                        "description": "Description of the source (e.g., 'user conversation', 'system log')",
                        "default": "mcp_client",
                    },
                    "reference_time": {
                        "type": "string",
                        "description": "ISO timestamp for when this episode occurred (defaults to now)",
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional metadata to attach to the episode",
                    },
                },
                "required": ["content"],
            },
        ),
        Tool(
            name="graphiti_search",
            description="Search the knowledge graph using hybrid search (semantic + graph structure)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10,
                    },
                    "start_time": {
                        "type": "string",
                        "description": "ISO timestamp - only return episodes after this time",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "ISO timestamp - only return episodes before this time",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="graphiti_get_episode",
            description="Retrieve a specific episode by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "episode_id": {
                        "type": "string",
                        "description": "UUID of the episode to retrieve",
                    }
                },
                "required": ["episode_id"],
            },
        ),
        Tool(
            name="graphiti_delete_episode",
            description="Delete an episode from the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "episode_id": {
                        "type": "string",
                        "description": "UUID of the episode to delete",
                    }
                },
                "required": ["episode_id"],
            },
        ),
        Tool(
            name="graphiti_get_entities",
            description="Get entities extracted from the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_type": {
                        "type": "string",
                        "description": "Filter by entity type (e.g., 'person', 'feature', 'system')",
                    },
                    "limit": {"type": "integer", "description": "Maximum results", "default": 20},
                },
            },
        ),
        Tool(
            name="graphiti_entity_search",
            description="Search for entities by name or attributes",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Entity name or search query",
                    },
                    "limit": {"type": "integer", "description": "Maximum results", "default": 10},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="graphiti_get_relationships",
            description="Get relationships between entities",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Get relationships for a specific entity UUID",
                    },
                    "relationship_type": {
                        "type": "string",
                        "description": "Filter by relationship type",
                    },
                    "limit": {"type": "integer", "description": "Maximum results", "default": 20},
                },
            },
        ),
        Tool(
            name="graphiti_clear_graph",
            description="Clear all data from the knowledge graph (use with caution)",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


# Helper functions
def format_episode(episode: Any) -> str:
    """Format an episode for display."""
    return f"""Episode ID: {episode.uuid}
Name: {episode.name}
Content: {episode.content}
Source: {episode.source_description}
Created: {episode.created_at}
Valid From: {episode.valid_at}
"""


def format_entity(entity: Any) -> str:
    """Format an entity for display."""
    return f"""Entity ID: {entity.uuid}
Name: {entity.name}
Type: {getattr(entity, 'entity_type', 'unknown')}
Summary: {getattr(entity, 'summary', 'N/A')}
Created: {entity.created_at}
"""


def format_relationship(rel: Any) -> str:
    """Format a relationship for display."""
    return f"""Relationship: {rel.name}
Type: {getattr(rel, 'relationship_type', 'unknown')}
From: {getattr(rel, 'source_node_uuid', 'N/A')}
To: {getattr(rel, 'target_node_uuid', 'N/A')}
Created: {rel.created_at}
"""


# Tool implementations
@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute Graphiti operations based on tool name."""
    try:
        logger.info(f"Executing tool: {name} with args: {arguments}")

        if name == "graphiti_add_episode":
            # Parse reference time
            reference_time = arguments.get("reference_time")
            if reference_time:
                reference_time = datetime.fromisoformat(reference_time.replace("Z", "+00:00"))
            else:
                reference_time = datetime.now()

            # Add episode to Graphiti
            episode = await graphiti_client.add_episode(
                name=f"Episode {reference_time.isoformat()}",
                episode_body=arguments["content"],
                source_description=arguments.get("source_description", "mcp_client"),
                reference_time=reference_time,
                episode_type=EpisodeType.message,  # Could be parameterized
            )

            result_text = f"""Added episode to knowledge graph:
{format_episode(episode)}

Entities and relationships have been automatically extracted."""

            return [TextContent(type="text", text=result_text)]

        elif name == "graphiti_search":
            # Parse time constraints
            start_time = arguments.get("start_time")
            if start_time:
                start_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))

            end_time = arguments.get("end_time")
            if end_time:
                end_time = datetime.fromisoformat(end_time.replace("Z", "+00:00"))

            # Perform hybrid search
            results = await graphiti_client.search(
                query=arguments["query"],
                num_results=arguments.get("limit", 10),
                start_time=start_time,
                end_time=end_time,
            )

            if not results:
                return [TextContent(type="text", text="No results found for the query.")]

            # Format results
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(
                    f"""Result {i}:
{format_episode(result) if hasattr(result, 'content') else str(result)}
---"""
                )

            return [
                TextContent(
                    type="text", text=f"Found {len(results)} results:\n\n" + "\n".join(formatted_results)
                )
            ]

        elif name == "graphiti_get_episode":
            # Retrieve specific episode
            episode = await graphiti_client.get_episode(uuid=arguments["episode_id"])

            if not episode:
                return [
                    TextContent(
                        type="text", text=f"Episode {arguments['episode_id']} not found."
                    )
                ]

            return [TextContent(type="text", text=format_episode(episode))]

        elif name == "graphiti_delete_episode":
            # Delete episode
            await graphiti_client.delete_episode(uuid=arguments["episode_id"])

            return [
                TextContent(
                    type="text", text=f"Deleted episode {arguments['episode_id']} from graph."
                )
            ]

        elif name == "graphiti_get_entities":
            # Get entities (requires direct Neo4j query or Graphiti extension)
            # This is a simplified implementation
            query = """
            MATCH (e:Entity)
            RETURN e
            LIMIT $limit
            """
            params = {"limit": arguments.get("limit", 20)}

            # Note: Direct Neo4j queries require accessing graphiti_client's driver
            # For now, return a placeholder message
            return [
                TextContent(
                    type="text",
                    text="Entity listing requires direct Neo4j access. Use graphiti_entity_search instead.",
                )
            ]

        elif name == "graphiti_entity_search":
            # Search for entities by name
            # This would use Graphiti's entity search functionality
            # Simplified implementation
            return [
                TextContent(
                    type="text",
                    text=f"Entity search for '{arguments['query']}' - functionality pending Graphiti API support.",
                )
            ]

        elif name == "graphiti_get_relationships":
            # Get relationships
            # Requires direct Neo4j query or Graphiti API extension
            return [
                TextContent(
                    type="text",
                    text="Relationship listing requires direct Neo4j access or Graphiti API extension.",
                )
            ]

        elif name == "graphiti_clear_graph":
            # Clear the entire graph (dangerous!)
            await graphiti_client.close()
            graphiti_client = Graphiti(
                neo4j_uri=NEO4J_URI, neo4j_user=NEO4J_USER, neo4j_password=NEO4J_PASSWORD
            )

            # Clear all data
            async with graphiti_client.driver.session() as session:
                await session.run("MATCH (n) DETACH DELETE n")

            return [TextContent(type="text", text="Knowledge graph cleared successfully.")]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error executing {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# SSE endpoint
async def handle_sse(request):
    """Handle SSE transport connection."""
    async with SseServerTransport("/messages") as (read_stream, write_stream):
        await mcp_server.run(
            read_stream, write_stream, mcp_server.create_initialization_options()
        )


# Starlette app
app = Starlette(debug=True, routes=[Route("/sse", endpoint=handle_sse, methods=["GET", "POST"])])


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(description="Graphiti MCP Server")
    parser.add_argument(
        "--transport", choices=["sse", "stdio"], default="sse", help="Transport type (default: sse)"
    )
    parser.add_argument("--host", default=GRAPHITI_MCP_HOST, help="Server host")
    parser.add_argument("--port", type=int, default=GRAPHITI_MCP_PORT, help="Server port")
    args = parser.parse_args()

    if args.transport == "stdio":
        # STDIO transport for local development
        import asyncio

        from mcp.server.stdio import stdio_server

        async def run_stdio():
            async with stdio_server() as (read_stream, write_stream):
                await mcp_server.run(
                    read_stream, write_stream, mcp_server.create_initialization_options()
                )

        asyncio.run(run_stdio())

    else:
        # SSE transport for Docker/production
        import uvicorn

        logger.info(f"Starting Graphiti MCP Server on {args.host}:{args.port}")
        logger.info(f"SSE endpoint: http://{args.host}:{args.port}/sse")
        logger.info(f"Neo4j: {NEO4J_URI}")
        logger.info(f"Model: {MODEL_NAME}")

        uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
