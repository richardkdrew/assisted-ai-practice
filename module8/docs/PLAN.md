# Investigator Agent Implementation Plan (Python)

## Overview
Python implementation of the Investigator Agent. See [DESIGN.md](DESIGN.md) for more about **what** the agent does and **why** design decisions were made.

This document covers **how** to build the agent in Python - specific packages, project structure, testing approach, and implementation details.

## Prerequisites

This implementation builds on the Module 7 Detective Agent. You should have:
- ✅ Working conversation loop with LLM provider
- ✅ Provider abstraction implemented
- ✅ OpenTelemetry observability working
- ✅ Basic context window management (truncation)
- ✅ Retry mechanism with exponential backoff
- ✅ Tool abstraction and execution loop
- ✅ Evaluation framework foundation

## Implementation Goals
- Clear, readable Python code that shows exactly what's happening
- Multi-provider support (building on Module 7)
- Enhanced OpenTelemetry observability (sub-conversations, context management)
- Sub-conversation pattern for context management
- Feature investigation tools (JIRA, metrics, docs)
- Optional memory system integration
- Comprehensive evaluation framework
- Interaction persistence

## Implementation Constitution
- Clear, readable Python code that shows exactly what's happening
- For interfaces, use Protocol, and DO NOT use an ABC
- Place unit tests in the same folder as the code under test
- Unit tests have a `_test.py` suffix and DO NOT have a `test_` prefix
- The `/tests` folder should only contain integration tests and common test assets
- When you're running tests and Python scripts, remember that the `python` binary is in the virtual environment
- Use `uv venv` to create the venv and `uv add` when adding dependencies
- Never use `pip` or `uv pip` and never create `requirements.txt`

## Implementation Steps
The recommended order of implementation is defined in [STEPS.md](STEPS.md). The phases of implementation defined later in this document align with this progression of steps.

## Technology Stack
- **Python 3.13.7** with async/await
- **uv** for dependency and venv management
- **httpx** for HTTP client (async, HTTP/2 support)
- **OpenTelemetry SDK** for traces and metrics
- **pydantic** for configuration and validation
- **pytest** + **pytest-asyncio** for testing
- **respx** for mocking httpx in tests

## Additional Dependencies (for this module)
- **tiktoken** or similar for token counting
- **Optional: vector DB client** (if implementing memory with vectors)
- **Optional: Graffiti MCP client** (if implementing graph-based memory)

<instructions_for_ai_assistant>
Read @DESIGN.md and @STEPS.md. Complete the rest of this document with implementation steps that align to these design principles. The design allows for flexibility in certain areas. When you have multiple options, ask the user what their preference is - do not make assumptions or fundamental design decisions on your own.

Key areas where you should ask for user preferences:
1. Memory system approach (Graffiti MCP, vector DB, file-based, or skip)
2. Sub-conversation summarization strategy (LLM-based or rule-based)
3. Token counting approach (tiktoken, API-based estimation, or provider-specific)
4. Test data generation (manual creation or programmatic generation)

After gathering user preferences, create a detailed implementation plan following the structure below.
</instructions_for_ai_assistant>

## Project Structure

```
investigator-agent/
├── pyproject.toml              # uv project configuration
├── .python-version             # Python version (3.13.7)
├── README.md                   # Project overview and usage
├── cli.py                      # Command-line interface
├── incoming_data/              # Test data
│   ├── featureN/
│   │   ├── jira/
│   │   │   ├── feature_issue.json           # Feature metadata
│   │   │   └── issue_changelog.json
│   │   ├── metrics/                         # Analysis
│   │   │   ├── performance_benchmarks.json
│   │   │   ├── pipeline_results.json
│   │   │   ├── security_scan_results.json
│   │   │   ├── test_coverage_report.json
│   │   │   └── unit_test_coverage.json
│   │   ├── planning/                        # Docs
│   │   │   ├── ARCHITECTURE.md
│   │   │   ├── DATABASE_SCHEMA.md
│   │   │   ├── DEPLOYMENT_PLAN.md
│   │   │   ├── DESIGN_DOC.md
│   │   │   └── ... (more)
│   │   └── reviews/                         # Analysis
│   │       ├── security.json
│   │       ├── stakeholders.json
│   │       └── uat.json
│   └── featuresN/               # Feature test data
│       └── ...
│
├── src/
│   └── investigator/
│       ├── __init__.py
│       ├── models.py           # Data models (Message, Conversation, SubConversation, etc.)
│       ├── config.py           # Configuration (from Module 7)
│       ├── provider/           # Provider abstraction (from Module 7)
│       │   ├── __init__.py
│       │   ├── protocol.py
│       │   ├── anthropic.py
│       │   ├── openrouter.py
│       │   └── ... (other providers)
│       ├── tools/               # Tool abstraction and implementations
│       │   ├── __init__.py
│       │   ├── protocol.py
│       │   ├── registry.py
│       │   ├── jira.py         # NEW: JIRA tool
│       │   ├── jira_test.py
│       │   ├── metrics.py      # NEW: Metrics tool
│       │   ├── metrics_test.py
│       │   ├── docs.py         # NEW: Documentation tools
│       │   └── docs_test.py
│       ├── context/            # NEW: Context management
│       │   ├── __init__.py
│       │   ├── manager.py      # Context window management
│       │   ├── sub_conversation.py  # Sub-conversation implementation
│       │   └── sub_conversation_test.py
│       ├── memory/             # NEW: Optional memory system
│       │   ├── __init__.py
│       │   ├── protocol.py
│       │   ├── graffiti.py    # Optional: Graffiti MCP implementation
│       │   ├── vector.py      # Optional: Vector DB implementation
│       │   └── file_based.py  # Simple file-based implementation
│       ├── observability/     # Observability (from Module 7, enhanced)
│       │   ├── __init__.py
│       │   ├── tracer.py
│       │   └── metrics.py
│       ├── retry.py           # Retry mechanism (from Module 7)
│       ├── agent.py           # Agent core (enhanced from Module 7)
│       ├── agent_test.py
│       └── persistence.py     # Conversation persistence (from Module 7)
├── evaluations/               # NEW: Evaluation system
│   ├── __init__.py
│   ├── scenarios.py          # Test scenario definitions
│   ├── evaluators.py         # Evaluation dimension implementations
│   ├── runner.py             # Evaluation runner
│   ├── regression.py         # Baseline and regression tracking
│   └── report.py             # Report generation
├── tests/                    # Integration tests
│   ├── test_integration.py
│   └── test_evaluation.py
├── traces/                   # OpenTelemetry trace output
├── conversations/            # Saved conversations
├── baselines/                # Evaluation baselines
└── memory_store/            # Optional: Memory storage
```

## Phase-by-Phase Implementation Plan

### Phase 1: Add JIRA Tool

Building on Module 7's tool abstraction.

**Important Context:** Test data is already provided in `incoming_data/` with 4 features. JIRA tool will return metadata for ALL features at once.

#### 1.1: Understand Test Data Structure

**Tasks:**
- Review existing test data in `incoming_data/feature1/` through `incoming_data/feature4/`
- Understand the 4 feature scenarios:
  1. Maintenance Scheduling & Alert System (✅ READY)
  2. QR Code Check-in/out with Mobile App (❌ NOT READY)
  3. Advanced Resource Reservation System (🔄 AMBIGUOUS)
  4. Contribution Tracking & Community Credits (🔄 PARTIAL)
- Note JIRA metadata format: folder, jira_key, feature_id, summary, status, data_quality

**Deliverables:**
- Understanding of all 4 feature scenarios
- Understanding of JIRA metadata structure

**Tests:**
- N/A - data already exists

#### 1.2: Implement JIRA Tool

**File:** `src/investigator/tools/jira.py`

**Tasks:**
- Create `JiraTool` class implementing tool protocol
- Implement `get_jira_data() -> list[dict]` handler (NO parameters - returns all features)
- Read JIRA metadata file containing all 4 features
- Create feature ID → folder mapping utility (shared across tools)
- Handle file not found gracefully
- Add comprehensive error handling

**File:** `src/investigator/tools/jira_test.py`

**Tests:**
- Test successful retrieval of all 4 features
- Test that return includes: folder, jira_key, feature_id, summary, status, data_quality
- Test missing JIRA file handling
- Test feature ID → folder mapping utility
- Test tool registration

**Deliverables:**
- Working JIRA tool (returns all features)
- Feature ID → folder mapping utility
- Passing unit tests
- Tool integrated with existing tool registry

#### 1.3: Update System Prompt

**File:** `src/investigator/config.py`

**Tasks:**
- Update default system prompt with Investigator Agent role
- Add JIRA tool usage instructions
- Add initial decision-making guidance

**Tests:**
- Manual CLI test: Ask about feature readiness
- Verify agent calls get_jira_data
- Verify agent uses JIRA data in response

#### 1.4: Integration Testing

**Tasks:**
- CLI test with each feature
- Verify tool calls in traces
- Verify conversation persistence includes tool calls

**Acceptance:**
- Agent identifies feature from user query
- Agent calls get_jira_data correctly
- Agent provides assessment based on JIRA data
- All visible in traces

---

### Phase 2: Add Analysis Tool

Building on Phase 1.

**Important Context:** Test data already includes analysis files (metrics + reviews) in `incoming_data/featureN/`.

#### 2.1: Understand Analysis Test Data

**Tasks:**
- Review existing analysis data in `incoming_data/featureN/metrics/` and `incoming_data/featureN/reviews/`
- Understand the 8 analysis types:
  - 5 metrics: performance_benchmarks, pipeline_results, security_scan_results, test_coverage_report, unit_test_results
  - 3 reviews: security, stakeholders, uat
- Note how data varies by feature scenario

**Deliverables:**
- Understanding of all 8 analysis types
- Understanding of metrics vs reviews distinction

**Tests:**
- N/A - data already exists

#### 2.2: Implement Analysis Tool

**File:** `src/investigator/tools/analysis.py`

**Tasks:**
- Create `AnalysisTool` class
- Implement `get_analysis(feature_id: str, analysis_type: str) -> dict` handler
- Use feature ID → folder mapping utility (from Phase 1)
- Validate analysis_type against enum (8 types)
- Map to correct file path (metrics/* or reviews/*)
- Handle missing files gracefully

**File:** `src/investigator/tools/analysis_test.py`

**Tests:**
- Test all 8 analysis types for each feature
- Test invalid analysis type
- Test missing analysis file
- Test feature ID → folder mapping
- Test tool registration

**Deliverables:**
- Working analysis tool
- Passing unit tests

#### 2.3: Update System Prompt with Phase 2 Guidance

**File:** `src/investigator/config.py`

**Tasks:**
- Add get_analysis tool to system prompt
- Update Phase 2 description to mention data gathering
- List all 8 analysis types
- Note that sub-conversations will be added in Phase 4
- For now, call get_analysis directly

**Tests:**
- Manual CLI test with feature assessment
- Verify multiple get_analysis calls
- Verify decision incorporates analysis data

#### 2.4: Integration Testing

**Tasks:**
- Test complete workflow with JIRA + analysis
- Verify agent calls get_jira_data first (Phase 1)
- Verify agent identifies correct feature
- Verify agent checks multiple analysis types (Phase 2)
- Verify decision justification cites specific analysis findings
- Check traces for all tool calls

**Acceptance:**
- Agent follows Phase 1 → Phase 2 workflow
- Agent uses feature ID from JIRA data for analysis queries
- Agent calls multiple analysis types
- Agent provides data-driven decisions
- All captured in traces with correct parameters

---

### Phase 3: Add Documentation Tools

Building on Phase 2.

#### 3.1: Create Documentation Test Data

**Tasks:**
- Create `data/features/*/docs/` directories
- Write substantial markdown files:
  - design.md (10-20KB) - Feature design details
  - architecture.md (10-20KB) - Technical architecture
  - requirements.md (5-10KB) - Feature requirements
- Ensure content is realistic and challenging
- Vary completeness by feature scenario
- Target >1MB total across all features

**Deliverables:**
- 12+ documentation files
- Substantial, realistic content
- Varied completeness

**Tests:**
- Verify files exist
- Verify file sizes appropriate
- Verify content quality

#### 3.2: Implement Documentation Tools

**File:** `src/investigator/tools/docs.py`

**Tasks:**
- Create `DocsTool` class
- Implement `list_docs(feature_id: str) -> list[dict]` handler
  - Scan docs directory
  - Return metadata: path, name, size, modified
- Implement `read_doc(path: str) -> str` handler
  - Read file contents
  - Handle large files
  - Return as string

**File:** `src/investigator/tools/docs_test.py`

**Tests:**
- Test list_docs for each feature
- Test read_doc for various files
- Test missing docs directory
- Test missing file
- Test tool registration

**Deliverables:**
- Working list_docs and read_doc tools
- Passing unit tests

#### 3.3: Update System Prompt

**File:** `src/investigator/config.py`

**Tasks:**
- Add documentation tools to system prompt
- Emphasize documentation completeness for production
- Guide: use list_docs first, then read_doc

**Tests:**
- Manual CLI test
- Verify agent uses list_docs before read_doc
- Verify agent reads relevant docs

#### 3.4: Observe Context Window Pressure

**Tasks:**
- Test with feature with multiple large docs
- Try reading design.md + architecture.md
- Monitor token usage in traces
- Observe degradation or errors
- Document the problem

**Expected Outcome:**
- Context window fills quickly with large docs
- Agent may struggle with multiple docs
- Clear motivation for Phase 4

**Acceptance:**
- Can reproduce context window pressure
- Token usage near limits visible in traces
- Ready for sub-conversation solution

---

### Phase 4: Add Sub-Conversation Context Management

Building on Phase 3. This is the **core new capability** for Module 8.

#### 4.1: Design Sub-Conversation Data Model

**File:** `src/investigator/models.py`

**Tasks:**
- Add `SubConversation` class:
  - `id`: Unique identifier
  - `parent_id`: Parent conversation ID
  - `purpose`: Description of analysis task
  - `system_prompt`: Specialized prompt
  - `messages`: Isolated message history
  - `summary`: Condensed results
  - `created_at`: Timestamp
  - `completed_at`: Optional timestamp
- Add `sub_conversations` field to `Conversation` class

**Tests:**
- Test SubConversation creation
- Test linking to parent

**Deliverables:**
- SubConversation data model
- Updated Conversation model

#### 4.2: Implement Sub-Conversation Manager

**File:** `src/investigator/context/sub_conversation.py`

**Tasks:**
- Create `SubConversationManager` class
- Implement `create_sub_conversation(purpose, parent_id, context_summary) -> SubConversation`
  - Generate specialized system prompt based on purpose
  - Initialize with context summary
  - Link to parent
- Implement `execute_in_sub_conversation(sub_conv, operation) -> SubConversation`
  - Maintain isolation from parent
  - Track tokens separately
- Implement `summarize_sub_conversation(sub_conv) -> str`
  - Generate concise summary (user preference: LLM-based or rule-based)
  - Compress detailed analysis

**File:** `src/investigator/context/sub_conversation_test.py`

**Tests:**
- Test sub-conversation creation
- Test isolation (messages don't leak to parent)
- Test summarization
- Test token tracking

**Deliverables:**
- Working SubConversationManager
- Passing unit tests

#### 4.3: Integrate into Agent Core

**File:** `src/investigator/agent.py`

**Tasks:**
- Update `send_message` workflow:
  - After tool execution, check result size
  - If >THRESHOLD (e.g., 5000 tokens), create sub-conversation
  - Execute analysis in sub-conversation
  - Generate summary
  - Add summary to main conversation (not full result)
- Add `_analyze_in_sub_conversation(content, purpose) -> str` method
- Track sub-conversations in conversation object

**Tests:**
- Test small content (no sub-conv)
- Test large content (creates sub-conv)
- Test token limits maintained
- Test summary quality

**Deliverables:**
- Enhanced agent with sub-conversation support
- Passing tests

#### 4.4: Update Observability

**File:** `src/investigator/observability/tracer.py`

**Tasks:**
- Add sub-conversation span creation
- Link sub-conv spans to parent trace
- Add attributes:
  - sub_conversation.id
  - sub_conversation.parent_id
  - sub_conversation.purpose
  - sub_conversation.tokens.input
  - sub_conversation.tokens.output
  - sub_conversation.compression_ratio
- Ensure spans nested correctly

**Tests:**
- Verify sub-conv spans in traces
- Verify nesting
- Verify attributes captured

**Deliverables:**
- Enhanced observability for sub-conversations
- Sub-conv visible in trace files

#### 4.5: Integration Testing

**Tasks:**
- Test with feature with multiple large docs
- Verify sub-conversations created
- Verify main conversation stays under limits
- Verify summaries preserve key info
- Verify decision quality maintained
- Check traces

**Acceptance:**
- Can process multiple large docs successfully
- Main conversation token count manageable
- Sub-conversations visible in traces
- Summaries effective
- No context window errors

---

### Phase 5: Add Memory System (Optional)

This phase is optional. Ask user which approach to take.

#### User Decision Point

Ask user to choose:
1. **Graffiti MCP** (graph-based memory)
2. **Vector database** (semantic memory)
3. **File-based** (simple memory)
4. **Skip** (no memory)

Based on choice, implement appropriate subsection below.

#### 5.1: Setup Memory System

**Tasks (vary by choice):**

**If Graffiti MCP:**
- Install Graffiti MCP client
- Configure connection
- Test basic operations

**If Vector DB:**
- Choose vector DB (Chroma, Qdrant, etc.)
- Install client
- Setup database
- Configure embeddings

**If File-based:**
- Design file storage format
- Create memory directory
- Design indexing strategy

**Deliverables:**
- Memory system configured and accessible

#### 5.2: Implement Memory Operations

**File:** `src/investigator/memory/protocol.py` (interface)
**File:** `src/investigator/memory/[chosen].py` (implementation)

**Tasks:**
- Implement `store_memory(content, metadata) -> str`
- Implement `retrieve_memories(query, limit, filters) -> list[Memory]`
- Implement `relate_memories(source, target, relationship) -> void` (if graph-based)
- Add error handling for unavailable memory system

**Tests:**
- Test store operation
- Test retrieve operation
- Test filtering
- Test error handling

**Deliverables:**
- Working memory operations
- Passing tests

#### 5.3: Integrate into Agent

**File:** `src/investigator/agent.py`

**Tasks:**
- Add memory retrieval at start of assessment
- Add memory storage after decision
- Update system prompt to mention memory
- Handle memory unavailability gracefully

**Tests:**
- Test memory retrieval
- Test memory storage
- Test graceful degradation when unavailable

**Deliverables:**
- Agent with memory capabilities
- Passing tests

#### 5.4: Update Observability

**File:** `src/investigator/observability/tracer.py`

**Tasks:**
- Add memory operation spans
- Track query time
- Track results count
- Track relevance scores

**Deliverables:**
- Memory operations visible in traces

#### 5.5: Verification

**Tasks:**
- Assess same feature twice
- Verify agent remembers first assessment
- Assess similar features
- Verify agent finds related memories
- Test with memory unavailable

**Acceptance:**
- Agent retrieves and uses memories
- Memories improve decisions
- Graceful degradation works
- All traced

---

### Phase 6: Add Comprehensive Evaluation System

Building on Module 7's evaluation foundation.

#### 6.1: Design Test Scenarios

**File:** `evaluations/scenarios.py`

**Tasks:**
- Define 8+ test scenarios:
  - Ready for production (maintenance)
  - Not ready - test failures (qr-code)
  - Borderline case (reservations)
  - Not ready - missing docs (contributions)
  - Missing feature data
  - Large docs requiring sub-conversations
  - Multiple features in sequence (memory test, if implemented)
  - Error handling scenarios
- For each scenario, define:
  - `id`: Unique identifier
  - `feature_id`: Feature to assess
  - `user_query`: Natural language query
  - `expected_tools`: Tools that should be called
  - `expected_decision`: ready/not_ready/borderline
  - `expected_justification_includes`: Key points
  - `expected_sub_conversations`: Boolean
  - `expected_memory_retrieval`: Boolean (if memory)

**Deliverables:**
- Scenario definitions in code
- At least 8 scenarios
- Coverage across all capabilities

#### 6.2: Implement Evaluation Dimensions

**File:** `evaluations/evaluators.py`

**Tasks:**
- Implement `eval_feature_identification(agent_output, expected) -> dict`
- Implement `eval_tool_usage(agent_output, expected) -> dict`
- Implement `eval_decision_quality(agent_output, expected) -> dict`
- Implement `eval_context_management(agent_output, expected) -> dict`
- Implement `eval_error_handling(agent_output, expected) -> dict`
- Each returns: `{"score": float, ...diagnostic_info}`

**Tests:**
- Unit tests for each evaluator
- Test with sample data
- Verify scoring logic

**Deliverables:**
- Working evaluators
- Passing tests

#### 6.3: Implement Evaluation Runner

**File:** `evaluations/runner.py`

**Tasks:**
- Create `run_evaluation(scenarios, agent) -> EvaluationResults`
- For each scenario:
  - Run agent with scenario query
  - Extract trace data
  - Apply all evaluators
  - Calculate overall score
  - Determine pass/fail
- Generate summary statistics
- Save detailed results to JSON

**Tests:**
- Integration test with mock scenarios
- Verify all scenarios executed
- Verify results format

**Deliverables:**
- Working evaluation runner
- Results saved to JSON

#### 6.4: Implement Regression Tracking

**File:** `evaluations/regression.py`

**Tasks:**
- Implement `save_baseline(results, version_id) -> void`
  - Save to `baselines/{version_id}.json`
- Implement `compare_to_baseline(current, baseline) -> Comparison`
  - Calculate deltas
  - Identify regressions (>5% drop)
  - Identify improvements (>5% gain)
  - Generate comparison report

**Tests:**
- Test baseline save/load
- Test comparison logic
- Test regression detection

**Deliverables:**
- Baseline management
- Regression detection

#### 6.5: Create CLI for Evaluations

**File:** `cli.py` (update)

**Tasks:**
- Add `eval` command to CLI
  - `python cli.py eval` - Run all evaluations
  - `python cli.py eval --baseline v1` - Save as baseline
  - `python cli.py eval --compare v1` - Compare to baseline
- Display results in terminal
- Save results to file

**Deliverables:**
- CLI commands for evaluation
- Human-readable output

#### 6.6: Run Initial Evaluation

**Tasks:**
- Run full evaluation suite
- Review results
- Identify failures
- Fix agent or test scenarios as needed
- Iterate until >70% pass rate
- Save initial baseline

**Acceptance:**
- All scenarios execute
- >70% pass rate
- Results documented
- Baseline established

---

### Phase 7: Final Integration and Polish

#### 7.1: End-to-End Testing

**Tasks:**
- Test each feature scenario completely
- Test error scenarios
- Test long conversations
- Test with memory (if implemented)
- Verify all traces complete

**Acceptance:**
- All capabilities work together
- No obvious bugs
- Traces complete and useful

#### 7.2: Performance Review

**Tasks:**
- Measure average tokens per assessment
- Measure tool calls per assessment
- Measure sub-conversations per assessment
- Measure latency
- Calculate cost per assessment
- Document findings

**Deliverables:**
- Performance documentation
- Optimization opportunities identified

#### 7.3: Documentation

**File:** `README.md`

**Tasks:**
- Project overview
- Installation instructions
- Usage examples
- Tool documentation
- Context management explanation
- Evaluation system usage
- Known limitations

**Deliverables:**
- Complete README
- Usage examples

#### 7.4: Final Evaluation

**Tasks:**
- Run complete evaluation suite
- Compare to baseline
- Document final results
- Celebrate! 🎉

**Acceptance:**
- >70% pass rate maintained
- No regressions
- Agent ready for use

---

## Next Steps

Once this plan is approved:

1. Review with user for any adjustments
2. Begin Phase 1, Step 1.1
3. Implement incrementally, testing thoroughly
4. Commit after each major milestone
5. Complete all phases

## Key Design Decisions - CONFIRMED ✅

The following design decisions have been finalized:

### 1. **Provider: Anthropic** ✅
- Using Anthropic Claude API directly
- Primary model: `claude-3-haiku-20240307` (cost-effective for main operations)
- Summarization model: `claude-3-haiku-20240307` (fast and cheap for sub-conversations)

### 2. **Memory System: File-based** ✅
**Choice:** File-based memory with option to upgrade later

**Rationale:**
- Simple implementation with no external dependencies
- Transparent and easy to debug (JSON files)
- Sufficient for 4-feature evaluation scope
- Upgradeable to vector DB or Graffiti via Protocol pattern
- Zero additional cost or setup complexity

**Implementation:**
- JSON files stored in `memory_store/` directory
- Indexed by feature_id and assessment_date
- Basic text search for retrieval (no embeddings initially)
- Memory protocol allows future swapping to vector DB

### 3. **Sub-conversation Summarization: LLM-based** ✅
**Choice:** LLM-based summarization using Claude Haiku

**Rationale:**
- Superior quality for distilling technical content
- Semantic understanding preserves context
- Handles varying content types (docs, metrics, reviews)
- Consistent with overall agent architecture
- Cost-effective with Haiku (fast + cheap)

**Implementation:**
- Use `claude-3-haiku-20240307` for all summaries
- Specialized system prompt: "Extract key findings relevant to production readiness"
- Target compression ratio: 10:1 (10KB → 1KB)
- Include specific metrics, risks, and recommendations

### 4. **Token Counting: tiktoken** ✅
**Choice:** tiktoken library for local token estimation

**Rationale:**
- Fast and accurate-enough (~90% accurate for Claude)
- No API calls needed (instant, free)
- Deterministic and well-maintained
- Sufficient accuracy for context window management

**Implementation:**
- Install: `uv add tiktoken`
- Use `cl100k_base` encoding (closest to Claude)
- Helper functions in `context/manager.py`:
  - `count_tokens(text: str) -> int`
  - `estimate_message_tokens(message: Message) -> int`
- Trigger sub-conversations at ~5000 token threshold

### 5. **Test Data: Use Existing Documentation** ✅
**Status:** Documentation already exists and is ready!

**Available Data:**
- ✅ 35 markdown files across 4 features (~487KB total)
- ✅ JIRA metadata in `incoming_data/featureN/jira/`
- ✅ Metrics data in `incoming_data/featureN/metrics/`
- ✅ Reviews data in `incoming_data/featureN/reviews/`
- ✅ Planning docs in `incoming_data/featureN/planning/` (6 docs per feature)
  - API_SPECIFICATION.md (~17KB)
  - ARCHITECTURE.md (~25KB)
  - DATABASE_SCHEMA.md (~18KB)
  - DEPLOYMENT_PLAN.md (~15KB)
  - DESIGN_DOC.md (~14KB)
  - USER_STORY.md (~3KB)

**No creation needed** - proceed directly with implementation!
