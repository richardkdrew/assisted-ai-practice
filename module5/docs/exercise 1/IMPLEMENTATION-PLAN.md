# MCP STDIO Server Implementation Plan

## Overview

This plan outlines the implementation of a minimal Python-based MCP (Model Context Protocol) server using STDIO communication. The server will use the official MCP Python SDK and be managed with UV for dependency management.

## Project Structure

```
module5/
├── stdio-mcp-server/           # Main server directory
│   ├── src/
│   │   ├── __init__.py
│   │   └── server.py          # Main server implementation
│   ├── pyproject.toml         # UV project configuration
│   ├── .python-version        # Python version specification
│   └── README.md              # Server-specific documentation
├── Makefile                   # Project automation commands
├── .gitignore                 # Git ignore patterns (update)
└── .mcp.json                  # MCP configuration (update)
```

## Implementation Phases

### Phase 1: Project Setup

**Goal**: Initialize the Python project structure with UV

**Tasks**

1. Create `stdio-mcp-server` directory
2. Initialize UV project with `uv init`
3. Set Python version to 3.11+ (recommended for MCP)
4. Add MCP SDK dependency (`mcp` package from PyPI)
5. Configure `pyproject.toml` with:
   - Project metadata (name, version, description)
   - Dependencies (mcp SDK)
   - Entry point configuration
   - Build system requirements

**Files to Create**:
- `stdio-mcp-server/pyproject.toml`
- `stdio-mcp-server/.python-version`
- `stdio-mcp-server/src/__init__.py`

### Phase 2: Basic Server Implementation
**Goal**: Create a minimal MCP server that handles protocol handshake

**Tasks**:
1. Create `server.py` with:
   - Import necessary MCP SDK components
   - Initialize server instance
   - Set up STDIO transport
   - Implement server lifecycle handlers (initialize, shutdown)
   - Configure proper error handling
   - Add structured logging
2. Implement protocol handshake:
   - Handle initialization request
   - Return server capabilities (empty for now)
   - Support protocol version negotiation

**Key Components**:
```python
# Pseudo-code structure
from mcp.server import Server
from mcp.server.stdio import stdio_server
import logging

# Server initialization
server = Server("stdio-mcp-server")

# Lifecycle handlers
@server.initialize()
async def handle_initialize():
    # Return server info and capabilities
    pass

# Main entry point
async def main():
    async with stdio_server() as streams:
        await server.run(
            streams[0],
            streams[1],
            server.create_initialization_options()
        )
```

**Files to Create**:
- `stdio-mcp-server/src/server.py`

### Phase 3: Error Handling & Logging
**Goal**: Implement robust error handling and logging

**Tasks**:
1. Configure Python logging:
   - Set up structured logging to stderr (stdout reserved for MCP protocol)
   - Add log levels (DEBUG, INFO, WARNING, ERROR)
   - Include contextual information (timestamps, component names)
2. Add error handling for:
   - Protocol errors (malformed messages)
   - Transport errors (I/O failures)
   - Server initialization failures
   - Graceful shutdown on errors
3. Implement signal handlers:
   - SIGINT (Ctrl+C) for graceful shutdown
   - SIGTERM for process termination

**Error Handling Strategy**:
- Catch and log all exceptions
- Return proper MCP error responses
- Ensure server doesn't crash on client errors
- Clean up resources on shutdown

### Phase 4: Makefile & Project Automation
**Goal**: Create Makefile for common operations

**Tasks**:
Create Makefile in project root with targets:
- `make install`: Install dependencies via UV
- `make dev`: Run MCP Inspector for testing
- `make run`: Run the server directly
- `make lint`: Run code quality checks (ruff)
- `make format`: Format code (ruff format)
- `make clean`: Clean up build artifacts and caches
- `make help`: Display available commands

**Makefile Structure**:
```makefile
.PHONY: install dev run lint format clean help

STDIO_SERVER_DIR = stdio-mcp-server

install:
	cd $(STDIO_SERVER_DIR) && uv sync

dev:
	cd $(STDIO_SERVER_DIR) && uv run mcp dev src/server.py

run:
	cd $(STDIO_SERVER_DIR) && uv run python -m src.server

# ... additional targets
```

### Phase 5: Configuration & Documentation
**Goal**: Configure the server and provide documentation

**Tasks**:
1. Update `.mcp.json` to include server configuration:
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

2. Update `.gitignore` to exclude:
   - Python cache files (`__pycache__`, `*.pyc`)
   - Virtual environments (`.venv`)
   - UV lock files (optional, depending on preference)
   - Build artifacts (`dist/`, `*.egg-info`)

3. Create `stdio-mcp-server/README.md` with:
   - Server description
   - Requirements (Python 3.11+, UV)
   - Installation instructions
   - Usage examples
   - Testing with MCP Inspector
   - Architecture overview

## Technical Requirements

### Dependencies
- **Python**: 3.11 or higher
- **UV**: Latest version for dependency management
- **MCP SDK**: Official `mcp` package from PyPI (latest stable version)

### Protocol Compliance
- Follow MCP specification (2024-11-05 or latest)
- Implement STDIO transport as per spec
- Support protocol version negotiation
- Handle initialization handshake correctly
- Return proper capability advertisement (empty for phase 1)

### Code Quality
- Type hints for all functions
- Docstrings for modules and functions
- Clean code structure and separation of concerns
- Async/await patterns for I/O operations
- Comprehensive error handling

### Testing Strategy (for future phases)
- Manual testing with MCP Inspector
- Protocol compliance verification
- Error scenario testing
- Integration testing with MCP clients (Claude Desktop)

## Success Criteria

1. **Server Starts Successfully**: Server initializes without errors
2. **Protocol Handshake**: Completes MCP initialization handshake
3. **STDIO Communication**: Properly reads from stdin and writes to stdout
4. **Error Handling**: Gracefully handles errors and logs them
5. **Clean Shutdown**: Properly cleans up resources on exit
6. **MCP Inspector**: Successfully connects and shows server info
7. **Makefile Commands**: All make targets execute successfully
8. **Documentation**: README provides clear setup and usage instructions

## Future Enhancements (Not in Scope)
These will be implemented in subsequent phases:
- Tool implementations
- Resource providers
- Prompt templates
- Advanced error recovery
- Performance optimizations
- Unit and integration tests
- CI/CD pipeline
- Docker containerization

## Notes & Considerations

1. **STDIO vs HTTP**: This implementation uses STDIO (standard input/output) which is simpler and suitable for local development and integration with desktop applications like Claude Desktop. HTTP-based servers are better for network services.

2. **Logging to stderr**: Since stdout is used for MCP protocol messages, all logging MUST go to stderr to avoid corrupting the protocol stream.

3. **Async Architecture**: The MCP SDK uses async/await patterns, so all handlers and the main loop are asynchronous.

4. **UV Benefits**: UV provides fast dependency resolution, reproducible builds, and seamless virtual environment management.

5. **No Premature Features**: This initial implementation focuses solely on the server infrastructure. Tools, resources, and prompts will be added in future phases once the foundation is solid.

## Implementation Order

1. Phase 1: Project Setup (5-10 min)
2. Phase 2: Basic Server Implementation (15-20 min)
3. Phase 3: Error Handling & Logging (10-15 min)
4. Phase 4: Makefile & Automation (10 min)
5. Phase 5: Configuration & Documentation (10 min)

**Total Estimated Time**: 50-65 minutes

## Questions for Discussion

1. **Python Version**: Prefer 3.11, 3.12, or latest 3.13?
2. **Logging Format**: JSON structured logs or human-readable format?
3. **Development Tools**: Should we include ruff/black/mypy in dependencies?
4. **Lock Files**: Should `uv.lock` be committed to git or gitignored?
5. **Server Name**: Is "stdio-mcp-server" a good name, or prefer something more specific?
6. **Entry Point**: Use `python -m src.server` or create a dedicated CLI entry point?

## References
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [UV Documentation](https://docs.astral.sh/uv/)
- [MCP STDIO Transport Spec](https://spec.modelcontextprotocol.io/specification/2024-11-05/basic/transports/#stdio)
