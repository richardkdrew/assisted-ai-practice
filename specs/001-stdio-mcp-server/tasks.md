# Tasks: STDIO MCP Server

**Input**: Design documents from `/specs/001-stdio-mcp-server/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `module5/stdio-mcp-server/src/`, `module5/stdio-mcp-server/tests/`
- Server directory: `module5/stdio-mcp-server/`
- All paths relative to repository root

---

## Phase 3.1: Setup

- [x] **T001** Create stdio-mcp-server directory structure in module5/stdio-mcp-server/ with src/, tests/ subdirectories

- [x] **T002** Initialize UV project in module5/stdio-mcp-server/ with `uv init` and create .python-version file with Python 3.11

- [x] **T003** Configure module5/stdio-mcp-server/pyproject.toml with project metadata, MCP SDK dependency, and build system

- [x] **T004** [P] Create module5/stdio-mcp-server/src/__init__.py as empty package marker

- [x] **T005** Install MCP SDK dependency with `cd module5/stdio-mcp-server && uv add mcp`

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

Note: Since this is a protocol implementation using the MCP SDK, we're creating integration tests that verify protocol compliance rather than traditional unit tests. The MCP SDK handles the low-level JSON-RPC framing, so our tests focus on correct server behavior.

- [x] **T006** [P] Create module5/stdio-mcp-server/tests/__init__.py as empty test package marker

- [x] **T007** [P] Create integration test for initialize handshake in module5/stdio-mcp-server/tests/test_initialize.py - verify server responds to initialize request with correct capabilities structure per contracts/initialize.json

- [x] **T008** [P] Create integration test for error handling in module5/stdio-mcp-server/tests/test_error_handling.py - verify malformed JSON returns proper error response per contracts/error-response.json without server crash

- [x] **T009** [P] Create integration test for graceful shutdown in module5/stdio-mcp-server/tests/test_shutdown.py - verify server handles SIGINT/SIGTERM signals and exits cleanly

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

- [ ] **T010** Create ServerState and SessionState enums in module5/stdio-mcp-server/src/server.py based on data-model.md state machines

- [ ] **T011** Implement logging configuration in module5/stdio-mcp-server/src/server.py - configure Python logging to stderr with structured format per research.md

- [ ] **T012** Implement Server class initialization in module5/stdio-mcp-server/src/server.py - create MCP Server instance with name "stdio-mcp-server" and version "0.1.0"

- [ ] **T013** Implement initialize handler in module5/stdio-mcp-server/src/server.py - handle initialization request and return server capabilities (empty tools/resources/prompts for v1)

- [ ] **T014** Implement signal handlers in module5/stdio-mcp-server/src/server.py - register SIGINT and SIGTERM handlers for graceful shutdown per research.md

- [ ] **T015** Implement main() async function in module5/stdio-mcp-server/src/server.py - set up stdio_server context manager and run server event loop

- [ ] **T016** Add __main__ entry point to module5/stdio-mcp-server/src/server.py - enable `python -m src.server` execution with asyncio.run(main())

- [ ] **T017** Implement error handling for JSON parse errors in module5/stdio-mcp-server/src/server.py - catch JSONDecodeError and return error response per contracts/error-response.json

- [ ] **T018** Implement error handling for invalid method calls in module5/stdio-mcp-server/src/server.py - return "Method not found" error per JSON-RPC 2.0 spec

---

## Phase 3.4: Integration & Configuration

- [ ] **T019** [P] Create module5/Makefile with targets: install, dev, run, lint, format, clean, help per plan.md Phase 4

- [ ] **T020** [P] Update module5/.gitignore to exclude Python cache files (__pycache__, *.pyc), .venv/, build artifacts (dist/, *.egg-info)

- [ ] **T021** Update module5/.mcp.json to configure stdio-server with uv command and correct args for launching module5/stdio-mcp-server

---

## Phase 3.5: Documentation & Polish

- [ ] **T022** [P] Create module5/stdio-mcp-server/README.md with server description, requirements (Python 3.11+, UV), installation instructions, usage examples, and testing with MCP Inspector

- [ ] **T023** [P] Add type hints to all functions in module5/stdio-mcp-server/src/server.py per Constitution Principle III

- [ ] **T024** [P] Add docstrings to Server class and main functions in module5/stdio-mcp-server/src/server.py

- [ ] **T025** Run manual testing procedure from specs/001-stdio-mcp-server/quickstart.md - verify all 7 test scenarios pass

- [ ] **T026** Verify MCP Inspector integration with `make dev` - confirm successful connection, handshake, and capabilities display

---

## Dependencies

**Setup before everything**:
- T001-T005 must complete before any other tasks

**Tests before implementation (TDD)**:
- T006-T009 (tests) must complete before T010-T018 (implementation)

**Core implementation order**:
- T010 (enums) before T012 (Server class)
- T011 (logging) before all other implementation
- T012 (Server init) before T013-T018
- T013 (initialize handler) before T015 (main loop)
- T014 (signal handlers) before T015 (main loop)
- T015 (main loop) integrates T012-T014

**Integration after core**:
- T019-T021 (config) after T010-T018 (implementation)

**Documentation last**:
- T022-T024 (docs) after T010-T018 (implementation)
- T025-T026 (validation) after ALL other tasks

---

## Parallel Execution Examples

### Setup Phase (can run in parallel after directory structure exists)
```bash
# After T001 completes, run T002-T005 in parallel:
# Terminal 1:
cd module5/stdio-mcp-server && uv init && echo "3.11" > .python-version

# Terminal 2:
# Edit pyproject.toml

# Terminal 3:
touch module5/stdio-mcp-server/src/__init__.py

# Terminal 4:
cd module5/stdio-mcp-server && uv add mcp
```

### Test Writing Phase (all independent files)
```bash
# T006-T009 can run in parallel:
# Terminal 1:
# Create tests/__init__.py

# Terminal 2:
# Create tests/test_initialize.py

# Terminal 3:
# Create tests/test_error_handling.py

# Terminal 4:
# Create tests/test_shutdown.py
```

### Documentation Phase (all independent files)
```bash
# T022-T024 can run in parallel:
# Terminal 1:
# Create README.md

# Terminal 2:
# Add type hints

# Terminal 3:
# Add docstrings
```

---

## Notes

- **[P] tasks**: Different files, no dependencies between them
- **Commit after each task**: Per Constitution Principle VII
- **Tests must fail first**: Verify failing tests before implementing (TDD)
- **MCP SDK handles protocol**: We implement handlers, SDK manages JSON-RPC framing
- **All logs to stderr**: CRITICAL - stdout reserved for MCP protocol messages
- **Type hints required**: All functions must have type hints per Constitution

---

## Task Validation Checklist

*GATE: Verify before marking tasks.md complete*

- [x] All contracts have corresponding tests
  - ✅ initialize.json → T007 (test_initialize.py)
  - ✅ error-response.json → T008 (test_error_handling.py)

- [x] All entities have implementation tasks
  - ✅ MCP Server entity → T010-T012 (enums, logging, Server class)
  - ✅ Protocol Session → T013 (initialize handler)
  - ✅ Message handling → T017-T018 (error handling)

- [x] All tests come before implementation
  - ✅ T006-T009 (tests) before T010-T018 (implementation)

- [x] Parallel tasks truly independent
  - ✅ T004 creates different file than T003, T005
  - ✅ T006-T009 all create different test files
  - ✅ T019-T021 create different config files
  - ✅ T022-T024 modify different aspects

- [x] Each task specifies exact file path
  - ✅ All tasks include full path from module5/stdio-mcp-server/

- [x] No task modifies same file as another [P] task
  - ✅ Verified - [P] tasks all touch different files

---

## Success Criteria

All tasks complete when:
1. ✅ Server starts without errors
2. ✅ MCP Inspector connects successfully
3. ✅ Initialize handshake completes correctly
4. ✅ Error handling works (no crashes on bad input)
5. ✅ Graceful shutdown on SIGINT/SIGTERM
6. ✅ All logs go to stderr (stdout clean for protocol)
7. ✅ All tests pass
8. ✅ Type hints on all functions
9. ✅ Quickstart manual test scenarios pass

**Estimated Total Tasks**: 26
**Estimated Time**: 4-6 hours (includes testing and documentation)

---

*Based on Constitution v1.1.0 - See `.specify/memory/constitution.md`*
*Design artifacts: plan.md, research.md, data-model.md, contracts/, quickstart.md*
