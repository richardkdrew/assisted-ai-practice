# MCP STDIO Server - Constitution

<!--
SYNC IMPACT REPORT
==================
Version Change: 1.1.0 → 1.2.0
Rationale: Added Principle VIII (Automation via Make) - mandates use of make commands for all development tasks

Modified Principles: None
Added Sections: Principle VIII - Automation via Make
Removed Sections: None

Templates Status:
✅ plan-template.md - reviewed, no conflicts
✅ spec-template.md - reviewed, no conflicts
✅ tasks-template.md - reviewed, compatible

Previous Version: 1.0.0 → 1.1.0 (Added Principle VII - Commit Discipline)
-->

## Core Principles

### I. Simplicity First
Build a minimal, functional MCP server using STDIO. Prioritize simplicity and clarity over cleverness. Do only what's necessary to make it work.

**Rationale**: Minimal implementations are easier to understand, debug, and maintain. Complexity should be justified, not default.

### II. Explicit Over Implicit
Every external interaction MUST have explicit error handling. This includes:
- File I/O operations
- JSON parsing
- STDIO communication
- All network/IPC operations

Code MUST be explicit and clear, favoring readability over cleverness.

**Rationale**: Silent failures and implicit behavior lead to difficult debugging. Explicit error handling and clear code make issues immediately visible.

### III. Type Safety & Documentation
- Use type hints for all function signatures
- Provide structured logging throughout using Python's `logging` module
- Log levels: DEBUG for development, INFO for operations, ERROR for failures
- Log to stderr only (keep stdout clean for MCP protocol)

**Rationale**: Type hints catch errors early and serve as inline documentation. Structured logging to stderr ensures MCP protocol integrity while maintaining observability.

### IV. Human-in-the-Loop Development
No code generation or file changes without explicit human approval. Before implementing:
1. Explain the approach
2. Discuss trade-offs
3. Wait for human confirmation
4. Then proceed with implementation

Build in small, testable chunks with incremental progress.

**Rationale**: Human oversight prevents over-engineering and ensures solutions align with actual needs. Incremental development allows course correction.

### V. Standard Libraries & Stable Dependencies
- **Primary Language**: Python 3.11+
- **Dependency Management**: UV only (no pip, poetry, or other tools)
- **Libraries**: Official/standard libraries preferred
- No experimental or beta packages
- External dependencies MUST be well-maintained and stable

**Rationale**: Standard libraries reduce dependency risks. UV provides fast, reproducible builds. Stable dependencies minimize breaking changes.

### VI. MCP Protocol Compliance
- Communication via stdin/stdout only
- JSON-RPC 2.0 message format
- Clean stdout (no print statements, no logging to stdout)
- All diagnostics to stderr
- Graceful shutdown handling

**Rationale**: MCP STDIO requires strict I/O separation. Any output to stdout corrupts the protocol stream.

### VII. Commit Discipline
After each completed feature or logical unit of work:
- MUST create a git commit
- Commit message MUST be descriptive and follow conventional commit format
- Commit MUST represent a working, testable state
- MUST NOT commit broken or incomplete code

**Rationale**: Regular commits create checkpoints for rollback, make code review easier, and maintain clear project history. Each commit should represent a coherent, functional change.

### VIII. Automation via Make
All development tasks MUST be executed through make commands:
- MUST use Makefile for all common operations (install, test, run, build, deploy)
- MUST NOT run raw commands directly (uv, docker, pytest, etc.)
- All make targets MUST be documented with inline comments
- CI/CD pipelines MUST use make targets, not direct commands

**Examples**:
- ✅ `make install` (correct)
- ❌ `cd stdio-mcp-server && uv sync` (wrong)
- ✅ `make docker-up` (correct)
- ❌ `docker-compose up -d` (wrong)

**Rationale**: Centralized automation ensures consistency across environments, provides self-documenting workflows, and prevents command drift. Make targets abstract implementation details and enforce project standards.

## Anti-Patterns

The following practices are PROHIBITED:

- ❌ **Over-engineering**: Resist the urge to add "nice to have" features
- ❌ **Assumptions**: Ask when requirements are unclear
- ❌ **Silent failures**: Every error MUST be logged and handled
- ❌ **Mixed concerns**: Keep MCP protocol separate from business logic
- ❌ **Dependency bloat**: Justify every external package

**Rationale**: These anti-patterns increase complexity without adding value. They make codebases harder to maintain and debug.

## Decision Framework

When faced with a choice, prefer:

1. **Explicit over implicit** - clear code beats clever code
2. **Standard over novel** - use established patterns
3. **Simple over complete** - MVP first, enhance later
4. **Tested over theoretical** - prove it works before moving on

**Rationale**: This framework prioritizes maintainability and reliability over novelty. Proven patterns reduce risk.

## Communication Standards

When communicating during development:

- Be direct and concise
- Explain *why*, not just *what*
- Surface trade-offs and alternatives
- Ask clarifying questions early
- Confirm understanding before implementing

**Rationale**: Clear communication prevents misunderstandings and wasted effort. Understanding the "why" enables better decision-making.

## Governance

### Amendment Procedure
1. Proposed changes MUST be documented with rationale
2. Impact on existing code and templates MUST be assessed
3. Version MUST be incremented according to semantic versioning:
   - **MAJOR**: Backward incompatible governance/principle removals or redefinitions
   - **MINOR**: New principle/section added or materially expanded guidance
   - **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements
4. All dependent templates and documentation MUST be updated for consistency

### Compliance Review
- All code changes MUST align with these principles
- Deviations MUST be explicitly justified and documented
- Constitution takes precedence over convenience
- Any complexity MUST demonstrate clear value over simpler alternatives

### Version Control
Constitution changes MUST be committed with descriptive messages following the pattern:
`docs: amend constitution to vX.Y.Z (brief description of changes)`

**Version**: 1.2.0 | **Ratified**: 2025-10-04 | **Last Amended**: 2025-10-04
