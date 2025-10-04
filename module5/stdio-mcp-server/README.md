# STDIO MCP Server

A minimal Model Context Protocol (MCP) server using STDIO transport, built with the official MCP Python SDK.

## Overview

This server implements the MCP protocol for enabling AI assistants (like Claude Desktop) to access tools, resources, and prompts via standard input/output communication.

### Available Tools

- **ping**: Test connectivity and server responsiveness
- **get_deployment_status**: Query deployment information from DevOps CLI
- **check_health**: Check health status of deployed applications
- **promote_release**: Promote application releases between environments

#### Ping Tool

Test connectivity by sending a message to the server and receiving an echoed response.

**Purpose**: Verify that the MCP server is running and responsive.

**Usage with MCP Inspector**:
```json
{
  "method": "tools/call",
  "params": {
    "name": "ping",
    "arguments": {
      "message": "test"
    }
  }
}
```

**Parameters**:
- `message` (string, required): The message to echo back

**Returns**:
- String in format: `"Pong: {message}"`

**Example**:
- Input: `{"message": "Hello, MCP!"}`
- Output: `"Pong: Hello, MCP!"`

**Features**:
- Preserves Unicode and special characters
- Maintains exact whitespace
- Validates parameter types (string required)

---

### DevOps CLI Wrapper Tools

Tools for interacting with the DevOps CLI (`./acme-devops-cli/devops-cli`) to query deployment information, check health, and manage releases across environments.

#### get_deployment_status

Query deployment status for applications across environments with optional filtering.

**Purpose**: Retrieve current deployment information including versions, deploy times, and status across all applications and environments.

**Usage with MCP Inspector**:
```json
{
  "method": "tools/call",
  "params": {
    "name": "get_deployment_status",
    "arguments": {
      "application": "web-app",
      "environment": "prod"
    }
  }
}
```

**Parameters**:
- `application` (string, optional): Filter by application ID (e.g., "web-app", "api-service")
- `environment` (string, optional): Filter by environment (e.g., "prod", "staging", "uat")

**Returns**:
- JSON object with deployment information:
  - `status`: "success" or "error"
  - `deployments`: Array of deployment objects
  - `total_count`: Number of deployments returned
  - `filters_applied`: Object showing which filters were used
  - `timestamp`: ISO 8601 timestamp of query

**Examples**:

1. **Get all deployments** (no filters):
   ```json
   {
     "arguments": {}
   }
   ```
   Returns deployments across all applications and environments.

2. **Filter by application**:
   ```json
   {
     "arguments": {
       "application": "web-app"
     }
   }
   ```
   Returns all deployments for "web-app" across all environments.

3. **Filter by environment**:
   ```json
   {
     "arguments": {
       "environment": "prod"
     }
   }
   ```
   Returns all production deployments across all applications.

4. **Filter by both**:
   ```json
   {
     "arguments": {
       "application": "web-app",
       "environment": "prod"
     }
   }
   ```
   Returns only web-app production deployments.

**Example Output**:
```json
{
  "status": "success",
  "deployments": [
    {
      "id": "deploy-001",
      "applicationId": "web-app",
      "environment": "prod",
      "version": "v2.1.3",
      "status": "deployed",
      "deployedAt": "2024-01-15T10:30:00Z",
      "deployedBy": "alice@company.com",
      "commitHash": "abc123def456"
    }
  ],
  "total_count": 1,
  "filters_applied": {
    "application": "web-app",
    "environment": "prod"
  },
  "timestamp": "2025-10-04T17:00:00Z"
}
```

**Error Handling**:
- Timeout (>30s): Returns error with timeout message
- CLI not found: Returns error indicating missing CLI tool
- Invalid JSON: Returns error with parse details
- CLI execution failure: Returns error with exit code and stderr

**Notes**:
- All CLI interactions use async subprocess execution with timeout management
- Environment names are validated and normalized (case-insensitive)

---

#### check_health

Check the health status of deployed applications across environments.

**Purpose**: Monitor application health by executing health checks via the DevOps CLI.

**Usage with MCP Inspector**:
```json
{
  "method": "tools/call",
  "params": {
    "name": "check_health",
    "arguments": {
      "env": "prod"
    }
  }
}
```

**Parameters**:
- `env` (string, optional): Environment to check (dev, staging, uat, prod). If not provided, checks all environments.

**Returns**:
- JSON object with health check results:
  - `status`: "success" or "error"
  - `health_checks`: Array of health check objects
  - `environment`: Environment checked (or "all")
  - `timestamp`: ISO 8601 timestamp of check

**Environment Validation**:
- Valid environments: `dev`, `staging`, `uat`, `prod`
- Case-insensitive (e.g., "PROD", "prod", "Prod" all accepted)
- Whitespace is automatically trimmed
- Invalid environments rejected immediately with clear error message

**Error Handling**:
- Timeout (>30s): Returns error with timeout message
- CLI not found: Returns error indicating missing CLI tool
- Invalid environment: Returns validation error before CLI execution
- CLI execution failure: Returns error with exit code and stderr

---

#### promote_release

Promote an application release from one environment to the next in the deployment pipeline.

**Purpose**: Safely promote application versions through the deployment pipeline with comprehensive validation and production safeguards.

**Deployment Pipeline**: dev → staging → uat → prod

**Usage with MCP Inspector**:
```json
{
  "method": "tools/call",
  "params": {
    "name": "promote_release",
    "arguments": {
      "app": "web-api",
      "version": "1.2.3",
      "from_env": "staging",
      "to_env": "uat"
    }
  }
}
```

**Parameters** (all required):
- `app` (string): Application identifier (e.g., "web-api", "mobile-app")
- `version` (string): Version to promote (e.g., "1.2.3", "v2.0.1")
- `from_env` (string): Source environment (dev, staging, uat)
- `to_env` (string): Target environment (staging, uat, prod)

**Returns**:
- JSON object with promotion results:
  - `status`: "success" or error thrown
  - `promotion`: Object with app, version, from_env, to_env, cli_output, execution_time
  - `production_deployment`: Boolean flag (true if promoting to prod)
  - `timestamp`: ISO 8601 timestamp

**Validation Rules**:

1. **Non-Empty Parameters**: All 4 parameters required and non-empty after trimming whitespace
2. **Environment Names**: Must be one of: dev, staging, uat, prod (case-insensitive)
3. **Promotion Path**: Must follow strict forward flow:
   - ✅ Valid: dev→staging, staging→uat, uat→prod
   - ❌ Invalid: Skipping environments (dev→uat, dev→prod, staging→prod)
   - ❌ Invalid: Backward promotion (staging→dev, prod→uat, etc.)
   - ❌ Invalid: Same environment (dev→dev)

**Production Safeguards**:
- Enhanced logging for all production promotions
- Audit trail logged to stderr with timestamp and caller
- Non-blocking (promotion proceeds after logging)
- `production_deployment: true` flag in response

**Timeout**: 300 seconds (5 minutes) for long-running deployments

**Examples**:

1. **Promote from dev to staging**:
   ```json
   {
     "arguments": {
       "app": "web-api",
       "version": "1.2.3",
       "from_env": "dev",
       "to_env": "staging"
     }
   }
   ```

2. **Promote to production** (with safeguards):
   ```json
   {
     "arguments": {
       "app": "mobile-app",
       "version": "2.0.1",
       "from_env": "uat",
       "to_env": "prod"
     }
   }
   ```

**Error Handling**:
- Empty parameters: Validation error before CLI execution
- Invalid environment: Validation error with list of valid options
- Invalid promotion path: Validation error with valid next environment
- Timeout (>300s): RuntimeError with helpful message about checking status manually
- CLI execution failure: RuntimeError with CLI stderr output

**Example Output**:
```json
{
  "status": "success",
  "promotion": {
    "app": "web-api",
    "version": "1.2.3",
    "from_env": "staging",
    "to_env": "uat",
    "cli_output": "Deployment successful: web-api v1.2.3 promoted to uat",
    "cli_stderr": "",
    "execution_time_seconds": 45.2
  },
  "production_deployment": false,
  "timestamp": "2025-10-05T14:30:00Z"
}
```

**Notes**:
- All environment names normalized to lowercase before CLI execution
- Promotion paths enforced at MCP layer for immediate feedback
- Production deployments logged with enhanced audit trail
- CLI timeout set to 300s for long-running deployments

---

## Requirements

- **Python**: 3.11 or higher
- **UV**: Package manager ([installation instructions](https://docs.astral.sh/uv/))
- **MCP SDK**: Installed automatically via UV

## Installation

1. **Install dependencies** (from the module5 directory):
   ```bash
   make install
   ```

   Or directly:
   ```bash
   cd stdio-mcp-server
   uv sync
   ```

2. **Verify installation**:
   ```bash
   uv run python -m src.server --help
   ```

## Usage

### Docker (Recommended for Production)

**Prerequisites**: Docker and Docker Compose installed

#### Quick Start with Docker Compose

From the `module5` directory:

```bash
# Build and start the server
docker-compose up -d mcp-server

# View logs
docker-compose logs -f mcp-server

# Stop the server
docker-compose down
```

#### With MCP Inspector (Testing)

```bash
# Start server and inspector
docker-compose --profile inspector up -d

# Inspector available at http://localhost:5173
# Server logs: docker-compose logs -f mcp-server
```

#### Interactive Mode (STDIO)

```bash
# Run with interactive terminal
docker-compose run --rm mcp-server

# Send JSON-RPC messages via stdin, receive via stdout
# Press Ctrl+D to exit
```

#### Build Docker Image Manually

```bash
cd stdio-mcp-server
docker build -t stdio-mcp-server:latest .
docker run -it stdio-mcp-server:latest
```

### Development Mode (with MCP Inspector)

The MCP Inspector provides an interactive web UI for testing the server:

```bash
make dev
```

Or directly:
```bash
cd stdio-mcp-server
uv run mcp dev src/server.py
```

This will:
- Start the MCP server
- Launch the Inspector web interface
- Allow you to test initialize handshake and server capabilities

### Production Mode

Run the server directly (typically launched by an MCP client):

```bash
make run
```

Or:
```bash
cd stdio-mcp-server
uv run python -m src.server
```

### Integration with Claude Desktop

The server is pre-configured in `module5/.mcp.json`:

```json
{
    "mcpServers": {
        "stdio-server": {
            "command": "uv",
            "args": [
                "--directory",
                "stdio-mcp-server",
                "run",
                "python",
                "-m",
                "src.server"
            ]
        }
    }
}
```

To use with Claude Desktop:
1. Copy `.mcp.json` to your Claude Desktop configuration directory
2. Restart Claude Desktop
3. The server will be available as "stdio-server"

## Testing

Run the test suite:

```bash
make test
```

Or:
```bash
cd stdio-mcp-server
uv run pytest tests/ -v
```

**Test Coverage**:
- Initialize handshake (3 tests)
- Error handling (4 tests)
- Graceful shutdown (5 tests)
- Ping tool (7 tests)
- Promotion validation (15 tests)
- Promote release integration (8 tests)
- **Total**: 42 tests, all passing ✓

## Architecture

### Components

- **`src/server.py`**: Main server implementation
  - Server state management (ServerState, SessionState enums)
  - Logging configuration (stderr only)
  - Signal handlers (SIGINT, SIGTERM)
  - MCP protocol handlers
  - Main event loop

### Docker Architecture

- **Multi-stage build**: Builder stage + minimal runtime stage
- **Base image**: Python 3.11-slim (minimal footprint)
- **Package manager**: UV (fast, reproducible)
- **Image size**: ~150MB (optimized)
- **Health checks**: Python import verification
- **Resource limits**: Configurable via docker-compose.yml

### Protocol Compliance

- **Transport**: STDIO (stdin for requests, stdout for responses)
- **Format**: JSON-RPC 2.0
- **Logging**: All diagnostics to stderr (stdout reserved for protocol)
- **Capabilities**: Empty for v1 (tools, resources, prompts all return `[]`)
- **Shutdown**: Graceful handling of SIGINT and SIGTERM

### State Machine

**Server States**:
```
UNINITIALIZED → INITIALIZING → READY → SHUTTING_DOWN → STOPPED
```

**Session States**:
```
NOT_STARTED → HANDSHAKE → ACTIVE → CLOSED
```

## Development

### Project Structure

```
stdio-mcp-server/
├── src/
│   ├── __init__.py
│   ├── server.py          # Main server implementation
│   └── validation.py      # Environment and parameter validation
├── tests/
│   ├── __init__.py
│   ├── test_initialize.py # Initialize handshake tests
│   ├── test_error_handling.py # Error handling tests
│   ├── test_shutdown.py   # Graceful shutdown tests
│   ├── test_ping.py       # Ping tool tests
│   ├── test_promotion_validation.py # Validation layer tests
│   └── test_promote_release.py # Promote release integration tests
├── pyproject.toml         # UV project configuration
├── .python-version        # Python 3.11
└── README.md              # This file
```

### Code Standards

Per project constitution (`.specify/memory/constitution.md`):

1. **Simplicity First**: Minimal implementation, no unnecessary features
2. **Explicit Error Handling**: All external interactions have try/except
3. **Type Safety**: Type hints on all function signatures
4. **Logging to stderr**: NEVER log to stdout (protocol reserved)
5. **UV Only**: No pip, poetry, or other package managers
6. **Commit Discipline**: Commit after each logical unit of work

### Adding Capabilities

To add tools/resources/prompts in future versions:

1. Update handlers in `src/server.py`:
   ```python
   @mcp_server.list_tools()
   async def list_tools() -> list:
       return [
           # Your tool definitions here
       ]
   ```

2. Add corresponding tests in `tests/`
3. Update this README with new capabilities
4. Follow TDD: write tests first, then implementation

## Troubleshooting

### Server won't start

```bash
# Check Python version
python3 --version  # Should be 3.11+

# Check UV installation
uv --version

# Reinstall dependencies
cd stdio-mcp-server
uv sync --reinstall
```

### No logs appearing

- Verify logs go to **stderr**, not stdout
- Check log level (default: INFO)
- Try running with explicit logging:
  ```bash
  uv run python -m src.server 2>&1 | tee server.log
  ```

### Inspector can't connect

- Verify server is running
- Check for port conflicts
- Try restarting Inspector: `make dev`

### Tests failing

```bash
# Run tests with verbose output
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_initialize.py -v

# Run with debugging
uv run pytest tests/ -vv --tb=long
```

### Docker Issues

#### Build fails

```bash
# Check Docker is running
docker --version
docker-compose --version

# Rebuild without cache
cd module5
docker-compose build --no-cache mcp-server

# Check build logs
docker-compose build mcp-server 2>&1 | tee build.log
```

#### Container won't start

```bash
# Check container logs
docker-compose logs mcp-server

# Check container status
docker-compose ps

# Verify health check
docker inspect stdio-mcp-server | grep -A 10 Health
```

#### STDIO not working in container

- Ensure `stdin_open: true` and `tty: true` in docker-compose.yml
- Use `docker-compose run --rm mcp-server` for interactive mode
- Check that protocol messages go to stdout and logs to stderr

#### Resource limits too restrictive

Edit docker-compose.yml to increase limits:
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'      # Increase from 0.5
      memory: 512M     # Increase from 256M
```

## References

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [UV Documentation](https://docs.astral.sh/uv/)
- [Project Constitution](../.specify/memory/constitution.md)

## License

This is a practice implementation for learning purposes.

## Version

**Current**: 0.1.0

**Changelog**:
- v0.1.0 (2025-10-04): Initial release with core server infrastructure

---

Built with [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) and [UV](https://docs.astral.sh/uv/)
