# HTTP MCP Server

HTTP-based Model Context Protocol server for consuming the acme-devops-api REST API.

## Features

- **FastMCP Framework**: Modern MCP protocol handling with HTTP transport
- **Asynchronous HTTP Client**: Non-blocking API communication using httpx
- **acme-devops-api Integration**: Direct integration with DevOps REST API
- **Docker Support**: Containerized deployment with docker-compose
- **Constitutional Compliance**: Follows project constitution v1.2.0
- **Single File Architecture**: Simple, maintainable codebase
- **Comprehensive Error Handling**: Explicit error handling for all external interactions
- **Structured Logging**: All logs to stderr with timestamps and context

## Requirements

- **Python**: 3.11 or higher
- **UV**: Package manager for dependency management
- **acme-devops-api**: Running on localhost:8000 (or configured URL)
- **Docker**: Optional, for containerized deployment

## Quick Start

### 1. Install Dependencies

```bash
# Using make (constitutional requirement)
make http-install

# Or directly with UV
cd http-mcp-server && uv sync
```

### 2. Start acme-devops-api

```bash
# Start the API server
make api-up

# Or manually
cd acme-devops-api && ./api-server
```

### 3. Run HTTP MCP Server

```bash
# Using make (constitutional requirement)
make http-run

# Or directly with UV
cd http-mcp-server && uv run python server.py
```

### 4. Test the Server

The server provides basic tools for testing:

- `ping(message)` - Echo test for connectivity
- `check_api_health()` - Verify acme-devops-api connection

### 5. Interactive Testing with FastMCP Inspector

For interactive testing and development:

```bash
# Start HTTP MCP server with FastMCP Inspector (includes API dependency)
make http-dev

# This will:
# 1. Start acme-devops-api in Docker
# 2. Wait for API to be ready
# 3. Launch HTTP MCP server with FastMCP Inspector
# 4. Open web interface at http://localhost:3001
```

## Docker Deployment

### Build and Run

```bash
# Build Docker image
make http-docker-build

# Start HTTP server with API dependency (recommended)
make http-docker-up

# Or start all services
make all-up
```

### Environment Variables

- `API_BASE_URL` - Base URL for acme-devops-api (default: http://localhost:8000)
- `HTTP_TIMEOUT` - HTTP request timeout in seconds (default: 30.0)
- `LOG_LEVEL` - Logging level (default: INFO)

### Docker Compose Services

```yaml
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d acme-devops-api http-mcp-server

# View logs
docker-compose logs -f http-mcp-server
```

## API Integration

The server integrates with acme-devops-api endpoints:

### Available Endpoints

- **GET /health** - Basic health check
- **GET /api/v1/deployments** - Deployment data with filtering
- **GET /api/v1/metrics** - Performance metrics
- **GET /api/v1/health** - Service health status
- **GET /api/v1/logs** - Log entries with filtering

### Connection Configuration

```python
# Default configuration
API_BASE_URL = "http://localhost:8000"
HTTP_TIMEOUT = 30.0

# Docker configuration
API_BASE_URL = "http://acme-devops-api:8000"
```

## MCP Client Configuration

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
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

## Available Tools

### Current Tools

1. **ping(message: str) -> str**
   - Test server connectivity
   - Returns: "Pong: {message}"

2. **check_api_health() -> dict**
   - Verify acme-devops-api connection
   - Returns: Health status with response times

### Future Tools (Planned)

- `get_deployments()` - Retrieve deployment information
- `get_metrics()` - Fetch performance metrics
- `get_logs()` - Access log entries
- `get_health_status()` - Check service health

## Development

### Project Structure

```
http-mcp-server/
├── server.py              # Main server implementation
├── pyproject.toml         # UV project configuration
├── Dockerfile             # Container configuration
└── README.md              # This file
```

### Code Architecture

- **Single File Design**: Following constitutional "Simplicity First" principle
- **Async/Await**: Non-blocking operations throughout
- **Type Hints**: Full typing on all functions
- **Error Handling**: Explicit try/catch for all external interactions
- **Logging**: Structured logging to stderr only

### Constitutional Compliance

This server follows the project constitution v1.2.0:

- ✅ **Simplicity First**: Single file architecture
- ✅ **Explicit Error Handling**: All HTTP operations wrapped
- ✅ **Type Safety**: Full type hints
- ✅ **Logging to stderr**: No stdout pollution
- ✅ **Make Automation**: All tasks via Makefile
- ✅ **Standard Dependencies**: FastMCP and httpx only

### Adding New Tools

1. Define the tool function with `@mcp.tool()` decorator
2. Add proper type hints and docstring
3. Implement error handling for HTTP operations
4. Test with acme-devops-api endpoints
5. Update this README

Example:

```python
@mcp.tool()
async def get_deployments(
    application: Optional[str] = None,
    environment: Optional[str] = None
) -> dict[str, Any]:
    """Get deployment data from acme-devops-api."""
    try:
        client = await get_http_client()
        params = {}
        if application:
            params["application"] = application
        if environment:
            params["environment"] = environment
        
        response = await client.get("/api/v1/deployments", params=params)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to get deployments: {e}")
        raise RuntimeError(f"Deployment query failed: {e}")
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   ```
   Error: Cannot connect to acme-devops-api at http://localhost:8000
   ```
   - Ensure acme-devops-api is running: `make api-up`
   - Check API health: `curl http://localhost:8000/health`

2. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'fastmcp'
   ```
   - Install dependencies: `make http-install`

3. **Docker Build Fails**
   ```
   Error building http-mcp-server
   ```
   - Check Dockerfile syntax
   - Ensure all files are present
   - Try: `make http-clean && make http-docker-build`

### Debugging

1. **Enable Debug Logging**
   ```bash
   export LOG_LEVEL=DEBUG
   make http-run
   ```

2. **Check API Connectivity**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/api/v1/health
   ```

3. **View Docker Logs**
   ```bash
   docker-compose logs -f http-mcp-server
   docker-compose logs -f acme-devops-api
   ```

## Make Commands

All development tasks use make commands (constitutional requirement):

```bash
# HTTP MCP Server
make http-install      # Install dependencies
make http-run          # Run server directly
make http-docker-build # Build Docker image
make http-docker-up    # Start with Docker
make http-docker-down  # Stop Docker container
make http-clean        # Clean artifacts

# API Management
make api-up            # Start acme-devops-api
make api-down          # Stop acme-devops-api

# Combined Operations
make all-up            # Start all services
make all-down          # Stop all services
make all-clean         # Clean all artifacts

# Help
make help              # Show all available commands
make http-help         # Show HTTP server commands
```

## Contributing

1. Follow the project constitution v1.2.0
2. Use make commands for all operations
3. Add type hints to all functions
4. Include comprehensive error handling
5. Log to stderr only
6. Test with acme-devops-api integration

## License

This project is part of the MCP servers examples and follows the same licensing terms.

---

**Server Version**: 0.1.0  
**Last Updated**: 2025-01-05  
**Constitution**: v1.2.0  
**Status**: Ready for Development
