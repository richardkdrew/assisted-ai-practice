# HTTP MCP Server Implementation Plan

## Overview

This plan outlines the implementation of a Python-based MCP (Model Context Protocol) server using HTTP communication to consume the acme-devops-api REST API. The server will use FastMCP for MCP protocol handling and httpx for asynchronous HTTP client operations.

## Project Structure

```
module5/
├── http-mcp-server/           # Main HTTP server directory
│   ├── server.py              # Single file architecture (initial)
│   ├── pyproject.toml         # UV project configuration
│   ├── Dockerfile             # Container configuration
│   └── README.md              # Server documentation
├── docker-compose.yml         # Top-level container orchestration (update)
├── Makefile                   # Project automation (update)
└── .mcp.json                  # MCP configuration (update)
```

## Implementation Phases

### Phase 1: Project Setup

**Goal**: Initialize the Python project structure with UV

**Tasks**:
1. Create `http-mcp-server` directory
2. Initialize UV project with `uv init`
3. Set Python version to 3.11+ (per constitutional requirement)
4. Add dependencies:
   - FastMCP for MCP protocol handling
   - httpx for async HTTP client
   - Python typing extensions
5. Configure `pyproject.toml` with project metadata and dependencies

**Dependencies Configuration**:
```toml
[project]
name = "http-mcp-server"
version = "0.1.0"
description = "HTTP MCP Server for acme-devops-api integration"
requires-python = ">=3.11"
dependencies = [
    "fastmcp",
    "httpx",
    "typing-extensions",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest",
    "pytest-asyncio",
]
```

**Files to Create**:
- `http-mcp-server/pyproject.toml`
- `http-mcp-server/.python-version` (3.11)
- `http-mcp-server/README.md`

### Phase 2: HTTP MCP Server Implementation

**Goal**: Create a minimal MCP server with HTTP transport and API client

**Tasks**:
1. Create `server.py` with:
   - Import necessary FastMCP components
   - Initialize server instance
   - Configure structured logging to stderr (constitutional requirement)
   - Set up HTTP client with httpx
   - Implement basic error handling
   - Add health check functionality for acme-devops-api

**Key Components**:
```python
# Core structure
import asyncio
import logging
import sys
from typing import Any
from fastmcp import FastMCP
import httpx

# Configure logging to stderr (constitutional requirement)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # CRITICAL: Must be stderr, not stdout
)
logger = logging.getLogger("http-mcp-server")

# Create FastMCP server instance
mcp = FastMCP("http-mcp-server")

# HTTP client configuration
API_BASE_URL = "http://localhost:8000"
HTTP_TIMEOUT = 30.0

async def create_api_client() -> httpx.AsyncClient:
    """Create and configure httpx client for acme-devops-api."""
    try:
        client = httpx.AsyncClient(
            base_url=API_BASE_URL,
            timeout=httpx.Timeout(HTTP_TIMEOUT),
            follow_redirects=True,
        )
        
        # Test connection with health check
        response = await client.get("/health")
        response.raise_for_status()
        
        logger.info("Successfully connected to acme-devops-api")
        return client
    except httpx.HTTPError as e:
        logger.error(f"Failed to connect to API: {e}")
        raise

# Entry point
if __name__ == "__main__":
    logger.info("Starting http-mcp-server with FastMCP")
    mcp.run()
```

**Files to Create**:
- `http-mcp-server/server.py`

### Phase 3: HTTP Client Integration

**Goal**: Set up robust HTTP client for acme-devops-api communication

**Tasks**:
1. Implement HTTP client configuration:
   - Base URL configuration (localhost:8000 for development)
   - Timeout settings (30 seconds)
   - Error handling for all HTTP operations
   - Connection testing via health endpoint
2. Add API endpoint mapping:
   - `/health` - API health check
   - `/api/v1/deployments` - Deployment data
   - `/api/v1/metrics` - Performance metrics
   - `/api/v1/health` - Service health status
   - `/api/v1/logs` - Log entries

**HTTP Client Features**:
- **Connection Pooling**: Single AsyncClient instance
- **Error Handling**: Explicit try/except for all HTTP operations
- **Timeouts**: 30-second timeout for all requests
- **Logging**: Request/response logging at appropriate levels
- **Health Checks**: Verify API availability on startup

**API Integration Points**:
Based on acme-devops-api documentation:
- **Base URL**: http://localhost:8000
- **Health Endpoint**: GET /health (simple health check)
- **API Endpoints**:
  - GET /api/v1/deployments (with filtering: application, environment, limit, offset)
  - GET /api/v1/metrics (with filtering: application, environment, time_range)
  - GET /api/v1/health (with filtering: environment, application, detailed)
  - GET /api/v1/logs (with filtering: application, environment, level, limit)

### Phase 4: Docker Configuration

**Goal**: Create Docker setup for the HTTP MCP server

**Tasks**:
1. Create `Dockerfile` for http-mcp-server:
   - Use Python 3.11-slim base image
   - Install UV package manager
   - Copy project files
   - Install dependencies with UV
   - Configure proper entrypoint
2. Update top-level `docker-compose.yml`:
   - Add http-mcp-server service
   - Configure networking with acme-devops-api
   - Set environment variables for API connection
   - Define service dependencies

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install UV package manager
RUN pip install --no-cache-dir uv

# Copy project files
COPY . .

# Install dependencies
RUN uv sync

# Expose port (if needed for HTTP transport)
EXPOSE 3000

# Run server
CMD ["uv", "run", "python", "server.py"]
```

**Docker Compose Integration**:
```yaml
services:
  acme-devops-api:
    # Existing configuration
    
  http-mcp-server:
    build:
      context: ./http-mcp-server
      dockerfile: Dockerfile
    depends_on:
      - acme-devops-api
    environment:
      - API_BASE_URL=http://acme-devops-api:8000
      - LOG_LEVEL=INFO
    networks:
      - mcp-network
    restart: unless-stopped

networks:
  mcp-network:
    driver: bridge
```

### Phase 5: Makefile Integration

**Goal**: Update Makefile with HTTP MCP server targets (constitutional requirement)

**Tasks**:
1. Add HTTP MCP server targets to existing Makefile:
   - Installation and dependency management
   - Development and testing commands
   - Docker operations
   - Cleanup operations

**Makefile Additions**:
```makefile
# HTTP MCP Server Configuration
HTTP_SERVER_DIR = http-mcp-server

.PHONY: http-install http-run http-docker-build http-docker-up http-docker-down http-clean http-help

# Install HTTP MCP server dependencies
http-install:
	@echo "Installing HTTP MCP server dependencies..."
	cd $(HTTP_SERVER_DIR) && uv sync

# Run HTTP MCP server directly (development)
http-run:
	@echo "Starting HTTP MCP server..."
	cd $(HTTP_SERVER_DIR) && uv run python server.py

# Build HTTP MCP server Docker image
http-docker-build:
	@echo "Building HTTP MCP server Docker image..."
	docker-compose build http-mcp-server

# Start HTTP MCP server with Docker Compose
http-docker-up:
	@echo "Starting HTTP MCP server with Docker..."
	docker-compose up -d http-mcp-server

# Stop HTTP MCP server Docker container
http-docker-down:
	@echo "Stopping HTTP MCP server..."
	docker-compose stop http-mcp-server

# Clean HTTP MCP server artifacts
http-clean:
	@echo "Cleaning HTTP MCP server artifacts..."
	cd $(HTTP_SERVER_DIR) && rm -rf __pycache__ .pytest_cache .venv
	docker-compose rm -f http-mcp-server

# Show HTTP MCP server help
http-help:
	@echo "HTTP MCP Server Commands:"
	@echo "  http-install      - Install dependencies"
	@echo "  http-run          - Run server directly"
	@echo "  http-docker-build - Build Docker image"
	@echo "  http-docker-up    - Start with Docker"
	@echo "  http-docker-down  - Stop Docker container"
	@echo "  http-clean        - Clean artifacts"

# Update main help target
help:
	@echo "Available commands:"
	@echo "  install           - Install all dependencies"
	@echo "  run               - Run STDIO MCP server"
	@echo "  http-install      - Install HTTP MCP server dependencies"
	@echo "  http-run          - Run HTTP MCP server"
	@echo "  docker-up         - Start all services with Docker"
	@echo "  docker-down       - Stop all Docker services"
	@echo "  clean             - Clean all artifacts"
	@echo "  help              - Show this help message"
```

### Phase 6: MCP Configuration

**Goal**: Update MCP configuration for HTTP server integration

**Tasks**:
1. Update `.mcp.json` to include HTTP server configuration
2. Configure proper command and arguments for HTTP server
3. Document server capabilities and limitations

**MCP Configuration Update**:
```json
{
  "mcpServers": {
    "stdio-server-uv": {
      "command": "uv",
      "args": [
        "--directory",
        "stdio-mcp-server",
        "run",
        "python",
        "-m",
        "src.server"
      ]
    },
    "http-server-uv": {
      "command": "uv",
      "args": [
        "--directory",
        "http-mcp-server",
        "run",
        "python",
        "server.py"
      ]
    }
  }
}
```

### Phase 7: Documentation

**Goal**: Create comprehensive documentation for the HTTP MCP server

**Tasks**:
1. Create `http-mcp-server/README.md` with:
   - Server description and purpose
   - Requirements and dependencies
   - Installation instructions
   - Usage examples
   - API integration details
   - Docker deployment guide
   - Troubleshooting guide

**README Structure**:
```markdown
# HTTP MCP Server

HTTP-based MCP server for consuming the acme-devops-api REST API.

## Features
- FastMCP framework integration
- Asynchronous HTTP client (httpx)
- acme-devops-api integration
- Docker support
- Constitutional compliance

## Requirements
- Python 3.11+
- UV package manager
- acme-devops-api running on localhost:8000

## Installation
[Installation steps]

## Usage
[Usage examples]

## API Integration
[API endpoint documentation]

## Docker Deployment
[Docker instructions]
```

## Technical Requirements

### Dependencies
- **Python**: 3.11 or higher (constitutional requirement)
- **UV**: Latest version for dependency management (constitutional requirement)
- **FastMCP**: Latest stable version for MCP protocol handling
- **httpx**: Latest stable version for async HTTP client operations

### Constitutional Compliance
- **Simplicity First**: Single file architecture initially
- **Explicit Error Handling**: All HTTP operations wrapped in try/except blocks
- **Type Safety**: Full type hints on all functions
- **Logging to stderr**: All logging configured to stderr only
- **Make Automation**: All operations accessible through Makefile targets
- **Human-in-the-Loop**: This plan requires approval before implementation

### HTTP Client Configuration
- **Base URL**: http://localhost:8000 (development), configurable via environment
- **Timeout**: 30 seconds for all requests
- **Connection Pooling**: Single AsyncClient instance per server
- **Error Handling**: Comprehensive HTTP error handling
- **Retries**: Basic retry logic for transient failures

### acme-devops-api Integration
Based on API documentation analysis:
- **Health Check**: GET /health (simple health check for load balancers)
- **API Version**: v1 (all endpoints prefixed with /api/v1)
- **Response Format**: Consistent JSON format with status, data, timestamp
- **Error Handling**: Standardized error responses
- **Filtering**: Query parameters for application, environment, pagination

## Success Criteria

1. **Server Initialization**: HTTP MCP server starts without errors
2. **API Connection**: Successfully connects to acme-devops-api
3. **Health Verification**: Confirms API health endpoint accessibility
4. **Protocol Compliance**: Proper MCP protocol handling
5. **Docker Integration**: Runs correctly in Docker container
6. **Make Commands**: All Makefile targets execute successfully
7. **Error Handling**: Graceful handling of API connection failures
8. **Logging**: Proper structured logging to stderr only

## Future Enhancements (Not in Initial Scope)

These will be implemented in subsequent phases:
- MCP tool implementations for API endpoints
- Resource providers for API data
- Advanced error recovery and retry logic
- Performance optimizations and caching
- Comprehensive unit and integration tests
- Monitoring and observability features
- Production deployment configurations

## Implementation Order

1. **Phase 1**: Project Setup (10-15 min)
2. **Phase 2**: Basic Server Implementation (20-25 min)
3. **Phase 3**: HTTP Client Integration (15-20 min)
4. **Phase 4**: Docker Configuration (10-15 min)
5. **Phase 5**: Makefile Integration (10 min)
6. **Phase 6**: MCP Configuration (5 min)
7. **Phase 7**: Documentation (10-15 min)

**Total Estimated Time**: 80-105 minutes

## Notes & Considerations

1. **HTTP vs STDIO**: This implementation uses HTTP transport which is better suited for network services and API integration compared to STDIO transport used by the existing server.

2. **API Dependency**: The server requires acme-devops-api to be running and accessible. Health checks will verify connectivity on startup.

3. **Async Architecture**: Both FastMCP and httpx use async/await patterns, ensuring non-blocking operations.

4. **Constitutional Compliance**: All implementation follows the established constitutional principles, particularly around error handling, logging, and automation.

5. **Single File Start**: Following the "simplicity first" principle, we start with a single file architecture that can be refactored later if needed.

6. **No Tools Initially**: Per requirements, the server will not expose any tools, resources, or prompts initially - these will be added in future phases.

## Questions for Implementation

1. **Environment Configuration**: Should API base URL be configurable via environment variables?
2. **Error Recovery**: What level of retry logic should be implemented for API failures?
3. **Logging Level**: Should logging level be configurable via environment variables?
4. **Health Check Frequency**: Should the server periodically check API health?
5. **Docker Networking**: Should we use a custom Docker network for service communication?

## References

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [httpx Documentation](https://www.python-httpx.org/)
- [acme-devops-api Documentation](../acme-devops-api/README.md)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [UV Documentation](https://docs.astral.sh/uv/)
- [Project Constitution](.specify/memory/constitution.md)

---

**Plan Version**: 1.0  
**Created**: 2025-01-05  
**Status**: Ready for Implementation
