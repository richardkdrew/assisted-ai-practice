# Research: STDIO MCP Server

**Feature**: 001-stdio-mcp-server
**Date**: 2025-10-04

## Research Decisions

### 1. MCP SDK Setup & Best Practices

**Decision**: Use official `mcp` package from PyPI (latest stable version)

**Rationale**:
- Official SDK maintained by Anthropic ensures protocol compliance
- Provides built-in STDIO transport implementation
- Handles JSON-RPC 2.0 message framing automatically
- Includes type definitions and async/await patterns
- Actively maintained with regular updates

**Alternatives Considered**:
- **Implement protocol manually**: Rejected - violates Constitution Principle I (Simplicity First). Would require implementing JSON-RPC framing, stream handling, protocol negotiation from scratch.
- **Use alternative MCP libraries**: Rejected - no mature alternatives exist; unofficial libraries lack stability guarantees (violates Principle V).

**Implementation Notes**:
- Add `mcp` to pyproject.toml dependencies
- SDK requires Python 3.10+ (we're using 3.11+)
- Import pattern: `from mcp.server import Server` and `from mcp.server.stdio import stdio_server`

---

### 2. UV Project Configuration

**Decision**: Initialize with `uv init` and configure Python 3.11+ via `.python-version`

**Rationale**:
- UV mandated by Constitution Principle V
- Fast dependency resolution (10-100x faster than pip)
- Reproducible builds with automatic lock file management
- Seamless virtual environment handling (no manual venv activation)
- Compatible with standard Python packaging (pyproject.toml)

**Configuration Details**:
```toml
# pyproject.toml structure
[project]
name = "stdio-mcp-server"
version = "0.1.0"
description = "Minimal MCP server using STDIO transport"
requires-python = ">=3.11"
dependencies = ["mcp"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Entry Point Strategy**:
- Use `python -m src.server` pattern (standard Python module execution)
- Avoids need for console_scripts entry point in initial version
- Simpler for development and testing

---

### 3. STDIO Transport Pattern

**Decision**: Use MCP SDK's `stdio_server()` async context manager

**Rationale**:
- SDK provides battle-tested implementation of STDIO handling
- Automatically separates stdin (protocol input) and stdout (protocol output)
- Handles low-level stream buffering and framing
- Integrates seamlessly with asyncio event loop

**Pattern**:
```python
from mcp.server.stdio import stdio_server

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )
```

**Error Handling**:
- SDK handles stream-level errors (EOF, broken pipe)
- Application adds error logging for protocol-level errors
- Malformed JSON triggers error response, not crash

---

### 4. Logging Configuration

**Decision**: Python standard library `logging` module with `StreamHandler` configured to stderr

**Rationale**:
- Standard library (no external dependency)
- Structured logging with configurable levels
- Clean separation: stdout for MCP protocol, stderr for diagnostics
- Familiar patterns for Python developers

**Configuration**:
```python
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)
```

**Log Levels**:
- **DEBUG**: Development-time details (message contents, state transitions)
- **INFO**: Operational events (server started, client connected, shutdown initiated)
- **ERROR**: Error conditions (parse failures, protocol errors, exceptions)

**Critical Requirement**: NEVER log to stdout - this would corrupt MCP protocol messages

---

### 5. Signal Handling for Graceful Shutdown

**Decision**: Use Python `signal` module with asyncio `Event` for coordinated shutdown

**Rationale**:
- Standard approach for Unix signal handling in async applications
- Allows cleanup before exit (close streams, flush logs, update state)
- Compatible with MCP SDK's async patterns
- Handles both SIGINT (CTRL+C) and SIGTERM (process termination)

**Pattern**:
```python
import signal
import asyncio

shutdown_event = asyncio.Event()

def handle_shutdown(signum, frame):
    logger.info(f"Received signal {signum}, initiating shutdown")
    shutdown_event.set()

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

# In main loop:
await shutdown_event.wait()  # Block until signal received
# Perform cleanup...
```

**Cleanup Steps**:
1. Log shutdown initiation
2. Stop accepting new requests
3. Complete in-flight requests (if any)
4. Close STDIO streams
5. Exit with status 0

---

### 6. MCP Inspector Integration

**Decision**: Use `uv run mcp dev src/server.py` for interactive testing during development

**Rationale**:
- `mcp` package includes development tools
- Inspector provides web UI for testing protocol interactions
- Validates handshake, message format, error responses
- No additional test infrastructure needed for MVP

**Testing Workflow**:
1. Run `make dev` (wrapper for `uv run mcp dev src/server.py`)
2. Inspector opens in browser
3. Interact with server via web UI
4. Verify: handshake completion, capabilities advertisement, error handling
5. Check stderr for logging output

**Production Configuration**:
- .mcp.json configures how Claude Desktop launches the server
- Uses `uv run python -m src.server` (no Inspector)
- Configuration already exists in repository root

---

## Summary of Technical Decisions

| Area | Decision | Key Reason |
|------|----------|------------|
| **SDK** | Official MCP Python package | Protocol compliance, simplicity |
| **Package Manager** | UV | Constitutional requirement, speed |
| **Python Version** | 3.11+ | Modern async features, type hints |
| **Transport** | MCP SDK stdio_server() | Battle-tested, correct I/O separation |
| **Logging** | stdlib logging to stderr | Standard, structured, protocol-safe |
| **Shutdown** | signal + asyncio.Event | Graceful cleanup, standard pattern |
| **Testing** | MCP Inspector (mcp dev) | Official tool, interactive validation |
| **Entry Point** | python -m src.server | Simple, standard Python module execution |

## Open Questions Resolved

✅ **Message buffering strategy**: Rely on MCP SDK's async queue handling (default behavior)
✅ **Max message size**: No explicit limit in v1 (SDK handles typical sizes < 10MB)
✅ **Startup time requirement**: <5 seconds target (typical for Python async server init)

All research complete - ready for Phase 1 (Design & Contracts).
