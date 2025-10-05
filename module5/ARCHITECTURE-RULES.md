# Architecture Rules & Conventions

**Project**: DevOps MCP Server & CLI Tools  
**Version**: 2.0  
**Last Updated**: 2025-01-05  
**Constitution Version**: 1.2.0

> **⚠️ MANDATORY**: This document references the official constitution at `.specify/memory/constitution.md` and `CLAUDE.md`. Those documents are the authoritative source of truth. This file provides quick reference and implementation patterns.

---

## 🏗️ Constitutional Principles (v1.2.0)

### I. Simplicity First
Build minimal, functional solutions. Prioritize clarity over cleverness. Do only what's necessary.

### II. Explicit Over Implicit  
**MANDATORY**: Explicit error handling for ALL external interactions (File I/O, JSON parsing, STDIO, network/IPC). Code must be clear and readable.

### III. Type Safety & Documentation
**REQUIRED**: Type hints on all functions, structured logging to stderr only, log levels: DEBUG/INFO/ERROR.

### IV. Human-in-the-Loop Development
**STOP before implementing**: Explain approach → Discuss trade-offs → Wait for confirmation → Then proceed.

### V. Standard Libraries & Stable Dependencies
Python 3.11+, UV only (no pip/poetry), prefer standard libraries, justify external dependencies.

### VI. MCP Protocol Compliance
stdin/stdout communication, JSON-RPC 2.0, clean stdout (NO prints/logs), all diagnostics to stderr.

### VII. Commit Discipline
**MUST** commit after each feature, conventional format, working state only, NO broken code.

### VIII. Automation via Make
**MANDATORY**: All tasks through make commands. NO direct uv/docker/pytest commands.

---

## 📁 Project Structure Patterns

### Directory Organization
```
project-root/
├── specs/                    # Feature specifications (business requirements)
├── docs/                     # Implementation documentation  
├── stdio-mcp-server/         # MCP server implementation
│   ├── src/                  # Source code
│   ├── tests/                # Test files
│   └── pyproject.toml        # Python dependencies
├── acme-devops-cli/          # CLI tool implementation
├── acme-devops-api/          # API server implementation
└── data/                     # Shared data files
```

### File Naming Conventions
- **Specs**: `001-feature-name/` (numbered directories)
- **Tests**: `test_*.py` (pytest convention)
- **Docs**: `UPPERCASE.md` for major docs, `lowercase.md` for guides
- **Config**: `.mcp.json`, `pyproject.toml`, `docker-compose.yml`
- **Constitution**: `.specify/memory/constitution.md` (authoritative source)

---

## 🔧 MCP Server Architecture

### Core Components Structure (Constitutional Requirements)
```python
# 1. Imports & Configuration
import asyncio, logging, sys
from fastmcp import FastMCP

# 2. Logging Configuration (CONSTITUTIONAL: stderr only)
def configure_logging() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr  # CRITICAL: Must be stderr, not stdout
    )
    return logging.getLogger(__name__)

# 3. FastMCP Server Instance
mcp = FastMCP("server-name")

# 4. Tools Implementation (REQUIRED: Type hints + error handling)
@mcp.tool()
async def tool_name(param: str) -> dict[str, Any]:
    """Docstring with Args/Returns/Raises (REQUIRED)"""
    try:
        # CONSTITUTIONAL: Explicit error handling for all external interactions
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

# 5. Entry Point
if __name__ == "__main__":
    logger.info("Starting server")  # Goes to stderr
    mcp.run(transport="stdio")
```

### Tool Implementation Patterns (Constitutional Requirements)

#### 1. Parameter Validation (CONSTITUTIONAL: Explicit validation)
```python
# REQUIRED: Validate all inputs explicitly
env = validate_environment(env)  # Centralized validation
app = validate_non_empty("app", app)
```

#### 2. CLI Command Execution (CONSTITUTIONAL: Error handling)
```python
# REQUIRED: Explicit error handling for external interactions
try:
    result = await execute_cli_command(args, timeout=30.0)
    if result.returncode != 0:
        logger.error(f"CLI failed: {result.stderr}")
        raise RuntimeError(f"CLI failed: {result.stderr}")
except asyncio.TimeoutError:
    logger.error("CLI execution timed out")
    raise RuntimeError("CLI timed out")
except FileNotFoundError:
    logger.error("CLI tool not found")
    raise RuntimeError("CLI tool not found")
```

#### 3. Type Hints (CONSTITUTIONAL: Required on all functions)
```python
from typing import Any, Optional

async def tool_name(
    param1: str,
    param2: Optional[str] = None
) -> dict[str, Any]:
    """REQUIRED: Docstring with Args/Returns/Raises"""
    pass
```

#### 4. Response Structure
```python
return {
    "status": "success" | "error",
    "data": {...},  # Main response data
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "metadata": {...}  # Additional context
}
```

---

## 🛡️ Validation Layer Architecture

### Centralized Validation (`src/validation.py`)
- **Environment Names**: Hardcoded whitelist (dev, staging, uat, prod)
- **Promotion Paths**: Strict forward flow only
- **Parameter Validation**: Non-empty strings, trimmed whitespace
- **Security**: Defense-in-depth, validate before CLI execution

### Validation Functions
```python
validate_environment(env: str | None) -> str | None
validate_non_empty(param_name: str, value: str) -> str
validate_promotion_path(from_env: str, to_env: str) -> None
```

---

## 📊 Data & Configuration Patterns

### Environment Configuration
- **Valid Environments**: `["dev", "staging", "uat", "prod"]`
- **Promotion Flow**: `dev → staging → uat → prod`
- **No Skipping**: Must follow sequential promotion
- **No Backward**: Cannot promote to earlier environment

### JSON Data Structure
```json
{
  "status": "success",
  "data": [...],
  "total_count": 0,
  "filters_applied": {...},
  "timestamp": "2025-01-05T14:21:00Z"
}
```

---

## 🧪 Testing Architecture

### Test Organization
- **Unit Tests**: `test_*.py` files alongside source
- **Integration Tests**: `test_integration_*.py`
- **CLI Tests**: Mock subprocess calls
- **Error Tests**: Validate error handling paths

### Test Patterns
```python
# Async test pattern
@pytest.mark.asyncio
async def test_function_name():
    # Arrange
    # Act  
    # Assert
```

---

## 📝 Documentation Standards

### Code Documentation
- **Docstrings**: Google style with Args/Returns/Raises
- **Type Hints**: Full typing for all functions
- **Comments**: Explain WHY, not WHAT
- **Constitution References**: Link to principles where applicable

### File Headers
```python
"""
Module description.

Brief explanation of purpose and key patterns.
Reference to Constitution principles if applicable.
"""
```

---

## 🚀 Deployment & Operations (Constitutional Requirements)

### Make Commands (CONSTITUTIONAL: Mandatory automation)
```bash
# REQUIRED: Use make commands only
make install          # ✅ Install dependencies
make run             # ✅ Run server
make test            # ✅ Run tests
make docker-up       # ✅ Start with Docker

# PROHIBITED: Direct commands
uv sync              # ❌ Use: make install
docker-compose up    # ❌ Use: make docker-up
```

### CLI Tool Integration
- **Path**: `../acme-devops-cli/devops-cli`
- **Timeout**: 30s default, 300s for promotions
- **Output**: JSON format preferred
- **Error Handling**: Check return codes, log stderr

### MCP Configuration
```json
{
  "mcpServers": {
    "stdio-server-uv": {
      "command": "uv",
      "args": ["--directory", "stdio-mcp-server", "run", "python", "-m", "src.server"]
    }
  }
}
```

---

## ⚠️ Constitutional Violations (PROHIBITED)

### NEVER Do (Constitutional Violations)
- ❌ Log to stdout (breaks MCP protocol - Principle VI)
- ❌ Skip error handling (violates Principle II)
- ❌ Use direct commands instead of make (violates Principle VIII)
- ❌ Commit broken code (violates Principle VII)
- ❌ Skip human approval (violates Principle IV)
- ❌ Add complexity without justification (violates Principle I)

### ALWAYS Do (Constitutional Requirements)
- ✅ Explicit error handling for ALL external interactions (Principle II)
- ✅ Type hints on ALL functions (Principle III)
- ✅ Structured logging to stderr only (Principle III)
- ✅ Use make commands for all tasks (Principle VIII)
- ✅ Get human approval before implementing (Principle IV)
- ✅ Commit after each working feature (Principle VII)

---

## 🔄 Evolution Guidelines

### Adding New Tools
1. Follow `@mcp.tool()` decorator pattern
2. Implement full parameter validation
3. Use centralized CLI execution
4. Add comprehensive error handling
5. Write tests for all paths
6. Update this document

### Modifying Validation
1. Update `src/validation.py` first
2. Ensure backward compatibility
3. Update all affected tools
4. Add migration notes here

---

## 📚 Quick Reference

### Authoritative Sources (READ THESE FIRST)
- `.specify/memory/constitution.md` - **CONSTITUTIONAL REQUIREMENTS** (v1.2.0)
- `CLAUDE.md` - **DEVELOPMENT GUIDELINES** (mandatory)
- `ARCHITECTURE-RULES.md` - This file (quick reference only)

### Key Implementation Files
- `stdio-mcp-server/src/server.py` - Implementation patterns
- `stdio-mcp-server/src/validation.py` - Validation patterns
- `.mcp.json` - MCP configuration
- `Makefile` - **REQUIRED** automation commands

### Constitutional Commands (MANDATORY)
```bash
# REQUIRED: Use make commands only
make help            # Show all available commands
make install         # Install dependencies
make run            # Run server
make test           # Run tests
make docker-up      # Start with Docker

# PROHIBITED: Direct commands (Constitutional violation)
# uv sync            # ❌ Use: make install
# docker-compose up  # ❌ Use: make docker-up
```

---

*This document should be referenced at the start of each development session to ensure architectural consistency.*
