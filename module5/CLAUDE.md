# MCP STDIO Server - Claude Code Development Guidelines

**Last Updated**: 2025-10-04
**Constitution Version**: 1.2.0

## ⚠️ MANDATORY: Read This First

**MANDATORY**: All development MUST follow the constitutional requirements defined in [.specify/memory/constitution.md](.specify/memory/constitution.md). The constitution supersedes all other development practices and contains mandatory requirements for:

- **Specification-First Development**: No implementation without approved specs
- **Test-Driven Development (TDD)**: Tests written and approved before implementation
- **Progress Tracking**: Use TodoWrite tool for all multi-step tasks
- **Architectural Consistency**: Follow established patterns and structure
- **Human-in-the-Loop**: No autonomous code changes without explicit approval

Before making ANY code changes, you MUST review and follow the constitution.

## Core Principles (Quick Reference)

### 1. Simplicity First
- Build minimal, functional solutions
- No "nice to have" features
- Justify any complexity

### 2. Explicit Over Implicit
- **MANDATORY**: Explicit error handling for ALL external interactions:
  - File I/O operations
  - JSON parsing
  - STDIO communication
  - Network/IPC operations
- Code must be clear and readable

### 3. Type Safety & Documentation
- **REQUIRED**: Type hints on all function signatures
- **REQUIRED**: Structured logging via Python's `logging` module
- Log levels: DEBUG (dev), INFO (ops), ERROR (failures)
- **CRITICAL**: Log to stderr ONLY (stdout reserved for MCP protocol)

### 4. Human-in-the-Loop
**STOP before implementing. You MUST:**
1. Explain the approach
2. Discuss trade-offs
3. Wait for human confirmation
4. Then proceed

Build in small, testable increments.

### 5. Dependencies
- **Language**: Python 3.11+
- **Package Manager**: UV only (no pip, poetry, etc.)
- **Libraries**: Prefer Python standard library
- **External Dependencies**: Must be stable and well-maintained
- Justify every external package

### 6. MCP Protocol Compliance
- **stdin/stdout**: Communication only
- **JSON-RPC 2.0**: Message format
- **Clean stdout**: NO print statements, NO logs to stdout
- **stderr**: All diagnostics go here
- **Graceful shutdown**: Handle SIGINT/SIGTERM

### 7. Commit Discipline
After EACH completed feature:
- **MUST** create git commit
- **MUST** use conventional commit format (e.g., `feat:`, `fix:`, `docs:`)
- **MUST** represent working, testable state
- **MUST NOT** commit broken/incomplete code

## ❌ Prohibited Anti-Patterns

- Over-engineering (no unnecessary features)
- Making assumptions (ask for clarification)
- Silent failures (all errors must be logged and handled)
- Mixed concerns (keep MCP protocol separate from business logic)
- Dependency bloat (justify every package)

## Decision Framework

When faced with a choice, prefer:
1. **Explicit over implicit** → clear code beats clever code
2. **Standard over novel** → use established patterns
3. **Simple over complete** → MVP first, enhance later
4. **Tested over theoretical** → prove it works before moving on

## Active Technologies

**Language**: Python 3.11+
**Framework**: MCP Python SDK (official)
**Package Manager**: UV
**Protocol**: MCP STDIO (JSON-RPC 2.0)
**Deployment**: Docker with docker-compose (recommended)
**Testing**: MCP Inspector (manual), pytest
**Automation**: Make (REQUIRED for all tasks)

## Project Structure

```
module5/
├── stdio-mcp-server/           # Main server directory
│   ├── src/
│   │   ├── __init__.py
│   │   └── server.py          # Main server implementation
│   ├── tests/
│   │   ├── test_initialize.py # Initialize handshake tests
│   │   ├── test_error_handling.py # Error handling tests
│   │   └── test_shutdown.py   # Graceful shutdown tests
│   ├── pyproject.toml         # UV project configuration
│   ├── .python-version        # Python version (3.11+)
│   ├── Dockerfile             # Multi-stage Docker build
│   ├── .dockerignore          # Docker build exclusions
│   └── README.md              # Server documentation
├── .specify/
│   ├── memory/
│   │   └── constitution.md    # Project constitution (source of truth)
│   └── templates/             # Planning templates
├── Makefile                   # Project automation (REQUIRED)
├── docker-compose.yml         # Docker orchestration
├── .mcp.json                  # MCP client configuration
└── CLAUDE.md                  # This file
```

## ⚠️ MANDATORY: Use Make Commands

**CONSTITUTIONAL REQUIREMENT**: All development tasks MUST use make commands. Direct command execution bypasses project standards and automation.

### Development Commands (UV-based)

```bash
# Install dependencies
make install

# Run with MCP Inspector (testing)
make dev

# Run server directly (production)
make run

# Run tests
make test

# Clean build artifacts
make clean

# Show all available commands
make help
```

### Docker Commands (Recommended for Production)

```bash
# Build Docker image
make docker-build

# Start server in background
make docker-up

# View server logs
make docker-logs

# Stop server
make docker-down

# Run server with MCP Inspector
make docker-test

# Run server in interactive mode (STDIO)
make docker-interactive

# Clean up Docker resources
make docker-clean
```

### ❌ DO NOT Run Direct Commands

```bash
# WRONG: Direct UV commands
uv sync                    # ❌ Use: make install
uv run python -m src.server # ❌ Use: make run

# WRONG: Direct Docker commands
docker-compose up          # ❌ Use: make docker-up
docker-compose build       # ❌ Use: make docker-build

# CORRECT: Always use make
make install               # ✅
make docker-up             # ✅
```

## Code Style (Python)

### Type Hints (REQUIRED)
```python
from typing import Any, Optional
import logging

async def handle_request(
    request: dict[str, Any]
) -> dict[str, Any]:
    """Handle MCP request with explicit types."""
    pass
```

### Error Handling (REQUIRED)
```python
import sys
import json

try:
    data = json.loads(raw_input)
except json.JSONDecodeError as e:
    logging.error(f"JSON parse error: {e}")
    # Handle error appropriately
    raise
```

### Logging (REQUIRED)
```python
import logging
import sys

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # CRITICAL: Must be stderr!
)

logger = logging.getLogger(__name__)

# Usage
logger.info("Server started")
logger.error("Error occurred", exc_info=True)
```

### STDIO Separation (CRITICAL)
```python
import sys

# CORRECT: Write MCP protocol to stdout
sys.stdout.write(json_message)
sys.stdout.flush()

# CORRECT: Write diagnostics to stderr
sys.stderr.write("Debug info\n")
# OR use logging (automatically goes to stderr if configured)
logger.info("Debug info")

# WRONG: These corrupt the protocol stream
print("Message")  # ❌ Goes to stdout
```

## Recent Changes

1. **Integration tests added** (2025-10-05): Added 12 integration tests for list-releases and check-health tools using FastMCP Client with in-memory transport pattern - provides fast, reliable end-to-end testing without external processes
2. **Feature 004-now-that-i implemented** (2025-10-04): Two additional DevOps CLI tools (list-releases & check-health) - extends existing CLI wrapper with release history queries and environment health checks, 13 contract tests + 12 integration tests = 25 tests total
3. **Feature 003-cli-wrapper implemented** (2025-10-04): DevOps CLI wrapper with get_deployment_status tool - subprocess execution module and MCP tools for wrapping external CLI
4. **FastMCP migration** (2025-10-04): Migrated from MCP SDK to FastMCP framework for simpler server implementation
5. **Feature 002-add-a-simple implemented** (2025-10-04): Ping tool added with 7 passing tests

## Pre-Implementation Checklist

Before writing ANY code, verify:

- [ ] I have explained my approach to the human
- [ ] I have discussed trade-offs and alternatives
- [ ] I have received explicit human confirmation
- [ ] I understand which principle(s) apply to this change
- [ ] I have a plan for error handling
- [ ] I know where logs will go (stderr only!)
- [ ] I will add type hints to all functions
- [ ] I will commit after completion with conventional commit message

## Pre-Commit Checklist

Before committing code, verify:

- [ ] All functions have type hints
- [ ] All external interactions have error handling
- [ ] All logging goes to stderr (no stdout pollution)
- [ ] Code is explicit and readable
- [ ] No unnecessary complexity added
- [ ] Tests pass (when tests exist)
- [ ] Code represents working, testable state
- [ ] Commit message follows conventional format

## Quick Reference: Constitutional Violations

If you find yourself about to:
- Add a feature without asking → **STOP** (Principle IV)
- Skip error handling → **STOP** (Principle II)
- Use `print()` statements → **STOP** (Principle VI)
- Add a new dependency → **STOP & JUSTIFY** (Principle V)
- Commit broken code → **STOP** (Principle VII)
- Make code "clever" → **STOP & SIMPLIFY** (Principle I)

## Questions?

When in doubt:
1. Check the [constitution](.specify/memory/constitution.md)
2. Ask the human for clarification
3. Prefer the simpler approach

---

**Remember**: The constitution is not a suggestion—it's mandatory. Following it prevents bugs, maintains quality, and ensures the project stays maintainable.
