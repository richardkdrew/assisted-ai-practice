"""ChromaDB MCP Server with SSE (Server-Sent Events) transport.

This server exposes ChromaDB vector database capabilities via the Model Context Protocol (MCP)
using SSE transport for real-time communication with AI agents.

Features:
- Persistent vector storage with ChromaDB
- Semantic search using embeddings
- Collection management (create, list, delete)
- Document operations (add, query, delete)
- Metadata filtering
- SSE transport for streaming responses
"""

import logging
import os
from pathlib import Path

import chromadb
from chromadb.config import Settings
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("chroma-mcp-server")

# Environment configuration
CHROMA_CLIENT_TYPE = os.getenv("CHROMA_CLIENT_TYPE", "persistent")
CHROMA_DATA_DIR = os.getenv("CHROMA_DATA_DIR", "/data/chromadb")
CHROMA_MCP_HOST = os.getenv("CHROMA_MCP_HOST", "0.0.0.0")
CHROMA_MCP_PORT = int(os.getenv("CHROMA_MCP_PORT", "8001"))

# Initialize ChromaDB client
logger.info(f"Initializing ChromaDB client (type={CHROMA_CLIENT_TYPE}, dir={CHROMA_DATA_DIR})")
Path(CHROMA_DATA_DIR).mkdir(parents=True, exist_ok=True)

if CHROMA_CLIENT_TYPE == "persistent":
    chroma_client = chromadb.PersistentClient(
        path=CHROMA_DATA_DIR,
        settings=Settings(anonymized_telemetry=False)
    )
else:
    chroma_client = chromadb.Client(
        settings=Settings(anonymized_telemetry=False)
    )

# Initialize MCP server
mcp_server = Server("chroma-mcp")

# Tool definitions
@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available ChromaDB tools."""
    return [
        Tool(
            name="chroma_create_collection",
            description="Create a new ChromaDB collection for storing embeddings",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Collection name"},
                    "metadata": {"type": "object", "description": "Optional metadata"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="chroma_list_collections",
            description="List all collections in the ChromaDB database",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="chroma_delete_collection",
            description="Delete a ChromaDB collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Collection name"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="chroma_add_documents",
            description="Add documents to a collection with optional metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection": {"type": "string", "description": "Collection name"},
                    "documents": {"type": "array", "items": {"type": "string"}},
                    "metadatas": {"type": "array", "items": {"type": "object"}},
                    "ids": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["collection", "documents"]
            }
        ),
        Tool(
            name="chroma_query",
            description="Query a collection using semantic search",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection": {"type": "string", "description": "Collection name"},
                    "query_texts": {"type": "array", "items": {"type": "string"}},
                    "n_results": {"type": "integer", "description": "Number of results", "default": 5},
                    "where": {"type": "object", "description": "Metadata filter"}
                },
                "required": ["collection", "query_texts"]
            }
        ),
        Tool(
            name="chroma_get_documents",
            description="Get documents from a collection by IDs",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection": {"type": "string", "description": "Collection name"},
                    "ids": {"type": "array", "items": {"type": "string"}},
                    "where": {"type": "object", "description": "Metadata filter"}
                },
                "required": ["collection"]
            }
        ),
        Tool(
            name="chroma_delete_documents",
            description="Delete documents from a collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection": {"type": "string", "description": "Collection name"},
                    "ids": {"type": "array", "items": {"type": "string"}},
                    "where": {"type": "object", "description": "Metadata filter"}
                },
                "required": ["collection"]
            }
        )
    ]

# Tool implementations
@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute ChromaDB operations based on tool name."""
    try:
        logger.info(f"Executing tool: {name} with args: {arguments}")

        if name == "chroma_create_collection":
            collection = chroma_client.create_collection(
                name=arguments["name"],
                metadata=arguments.get("metadata")
            )
            return [TextContent(
                type="text",
                text=f"Created collection '{collection.name}' with {collection.count()} documents"
            )]

        elif name == "chroma_list_collections":
            collections = chroma_client.list_collections()
            result = "\n".join([
                f"- {c.name} ({c.count()} documents)"
                for c in collections
            ])
            return [TextContent(
                type="text",
                text=f"Collections:\n{result}" if result else "No collections found"
            )]

        elif name == "chroma_delete_collection":
            chroma_client.delete_collection(name=arguments["name"])
            return [TextContent(
                type="text",
                text=f"Deleted collection '{arguments['name']}'"
            )]

        elif name == "chroma_add_documents":
            collection = chroma_client.get_collection(name=arguments["collection"])
            collection.add(
                documents=arguments["documents"],
                metadatas=arguments.get("metadatas"),
                ids=arguments.get("ids")
            )
            return [TextContent(
                type="text",
                text=f"Added {len(arguments['documents'])} documents to '{arguments['collection']}'"
            )]

        elif name == "chroma_query":
            collection = chroma_client.get_collection(name=arguments["collection"])
            results = collection.query(
                query_texts=arguments["query_texts"],
                n_results=arguments.get("n_results", 5),
                where=arguments.get("where")
            )

            # Format results
            formatted = []
            for i, (doc, meta, dist) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                formatted.append(f"Result {i+1} (distance={dist:.4f}):\n{doc}\nMetadata: {meta}")

            return [TextContent(
                type="text",
                text="\n\n".join(formatted) if formatted else "No results found"
            )]

        elif name == "chroma_get_documents":
            collection = chroma_client.get_collection(name=arguments["collection"])
            kwargs = {}
            if "ids" in arguments:
                kwargs["ids"] = arguments["ids"]
            if "where" in arguments:
                kwargs["where"] = arguments["where"]

            results = collection.get(**kwargs)
            count = len(results["ids"])
            return [TextContent(
                type="text",
                text=f"Retrieved {count} documents from '{arguments['collection']}'"
            )]

        elif name == "chroma_delete_documents":
            collection = chroma_client.get_collection(name=arguments["collection"])
            kwargs = {}
            if "ids" in arguments:
                kwargs["ids"] = arguments["ids"]
            if "where" in arguments:
                kwargs["where"] = arguments["where"]

            collection.delete(**kwargs)
            return [TextContent(
                type="text",
                text=f"Deleted documents from '{arguments['collection']}'"
            )]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error executing {name}: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]

# SSE endpoint
async def handle_sse(request):
    """Handle SSE transport connection."""
    async with SseServerTransport("/messages") as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )

# Starlette app
app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse, methods=["GET", "POST"])
    ]
)

if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting ChromaDB MCP Server on {CHROMA_MCP_HOST}:{CHROMA_MCP_PORT}")
    logger.info(f"SSE endpoint: http://{CHROMA_MCP_HOST}:{CHROMA_MCP_PORT}/sse")

    uvicorn.run(
        app,
        host=CHROMA_MCP_HOST,
        port=CHROMA_MCP_PORT,
        log_level="info"
    )
