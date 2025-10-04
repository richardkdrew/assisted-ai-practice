# STDIO MCP Server

A minimal Model Context Protocol (MCP) server using STDIO transport, built with the official MCP Python SDK.

## Overview

This server implements the MCP protocol for enabling AI assistants (like Claude Desktop) to access tools, resources, and prompts via standard input/output communication. Version 1.0 provides the core server infrastructure with empty capabilities - tools, resources, and prompts will be added in future versions.

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
- **Total**: 12 tests, all passing ✓

## Architecture

### Components

- **`src/server.py`**: Main server implementation
  - Server state management (ServerState, SessionState enums)
  - Logging configuration (stderr only)
  - Signal handlers (SIGINT, SIGTERM)
  - MCP protocol handlers
  - Main event loop

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
│   └── server.py          # Main server implementation
├── tests/
│   ├── __init__.py
│   ├── test_initialize.py # Initialize handshake tests
│   ├── test_error_handling.py # Error handling tests
│   └── test_shutdown.py   # Graceful shutdown tests
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
