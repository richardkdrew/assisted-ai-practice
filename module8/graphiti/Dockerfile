# Graphiti MCP Server Dockerfile
# Provides Graphiti temporal knowledge graph via MCP protocol

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies using uv
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install \
    graphiti-core \
    mcp \
    starlette \
    uvicorn \
    python-dotenv

# Activate virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Copy server script
COPY graphiti_mcp_server.py ./

# Expose SSE port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/sse || exit 1

# Run server with SSE transport
CMD ["python", "graphiti_mcp_server.py", "--transport", "sse"]
