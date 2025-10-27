# Investigator Agent Design Specification

## Overview
A foundational LLM agent design built from first principles with advanced context engineering capabilities. This document describes the **what** and **why** of the system architecture - independent of programming language or specific technology choices.

## Use Case: Release Confidence System

**System Context:** A Release Confidence System helps build confidence in software releases by investigating changes, assessing risks, and producing actionable reports.

**Agent Role:** The Investigator Agent determines whether a feature is sufficiently prepared to be promoted to the next stage of development (e.g., from Development to UAT, or from UAT to Production). Unlike the Detective Agent which focuses on high-level release summaries, the Investigator Agent performs deep analysis across multiple data sources to assess feature readiness.

**Scenario:**
When a feature is being considered for promotion, the Investigator Agent:
1. Identifies the feature based on user request or feature ID
2. Retrieves feature metadata from JIRA (status, assignee, description)
3. Analyzes test results and metrics data (coverage, performance, error rates)
4. Reviews planning documentation (design docs, architecture docs, requirements)
5. Synthesizes information across all sources
6. Makes a go/no-go decision with justification

The agent has access to multiple tools and must manage context carefully to avoid exceeding token limits.

**Example Workflow:**
```
User: "Is the reservation feature ready for production?"

Agent thinks:
- Need to identify which feature matches "reservation feature"
- Get metadata for all features to find the right one
- Gather analysis data and documentation for that feature
- Synthesize decision

Agent actions (Three-Phase Workflow):

PHASE 1: Feature Identification
1. get_jira_data() → Returns metadata for all 4 features
2. Identifies "Advanced Resource Reservation System" as match
3. Maps to feature_id for subsequent queries

PHASE 2: Data Gathering (in Sub-Conversations)
4. [Sub-conv 1] get_analysis(feature_id="...", analysis_type="reviews/uat")
   → Summarizes UAT review findings
5. [Sub-conv 2] list_docs(feature_id="...") then read_doc(path="...")
   → Summarizes design documentation completeness
6. [Sub-conv 3] get_analysis(feature_id="...", analysis_type="metrics/test_coverage_report")
   → Summarizes test coverage status

PHASE 3: Final Assessment
7. Synthesizes all summaries from sub-conversations
8. Makes go/no-go decision with clear justification
9. Returns: "Not ready - UAT shows ambiguous results, incomplete test data..."
```

**Three-Phase Workflow Pattern:**

This agent follows a structured three-phase approach:

1. **Phase 1: Feature Identification**
   - Agent calls `get_jira_data()` (no parameters, returns all features)
   - Agent receives metadata for all 4 features
   - Agent identifies which feature matches user's natural language query
   - Agent extracts `feature_id` for use in subsequent tool calls
   - This happens in the main conversation thread

2. **Phase 2: Data Gathering via Sub-Conversations**
   - Agent determines what data to gather (`get_analysis`, `list_docs`, `read_doc`)
   - **Each tool call happens in its own sub-conversation**
   - Each sub-conversation produces a summary
   - Summaries (not raw data) are added to main conversation
   - This preserves context window for main decision-making thread

3. **Phase 3: Final Assessment**
   - Agent synthesizes all summaries from Phase 2
   - Makes readiness decision based on synthesized information
   - Provides clear justification citing specific findings
   - This happens in the main conversation thread

**Feature ID Mapping:**

All analysis and documentation tools accept a `feature_id` parameter. Tools must map this to the correct folder:
- Each feature has a `folder` field in JIRA metadata
- Tools use `feature_id` → `folder` mapping to locate files
- This mapping is consistent across all tools (common utility function)

## Design Philosophy

1. **Transparency Over Magic**: Every component and abstraction must be justified and minimal
2. **Observability First**: Complete visibility into agent behavior and performance
3. **Provider Agnostic**: Support multiple LLM providers through a common interface
4. **Tool-Enabled**: Enable agent capabilities through external tools
5. **Context Engineering**: Intelligent management of context to handle large information spaces
6. **Memory-Augmented**: Leverage memory systems to maintain context across conversations
7. **Resilient**: Graceful handling of failures and retries
8. **Extensible**: Clean interfaces for future capabilities

## Core Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                         Agent Core                          │
│  - Conversation Management                                  │
│  - Message Orchestration                                    │
│  - Context Window Management                                │
│  - Tool Execution Loop                                      │
│  - Sub-Conversation Management                              │
│  - Memory Integration                                       │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┴──────────┬───────────────────┬──────────┐
        │                    │                   │          │
┌───────▼────────┐   ┌───────▼────────┐   ┌──────▼────┐     │
│    Provider    │   │      Tool      │   │  Retry    │     │
│   Abstraction  │   │   Abstraction  │   │  Manager  │     │
└───────┬────────┘   └───────┬────────┘   └───────┬───┘     │
        │                    │                    │         │
   ┌────┴────┐          ┌────┴────────────┐   ┌───┴──────┐  │
   │Provider │          │  Feature Tools  │   │ Backoff  │  │
   │  Impls  │          │  - JIRA         │   │ Strategy │  │
   └─────────┘          │  - Metrics      │   └──────────┘  │
        │               │  - Docs         │                 │
   ┌────┴────────┐      └─────────────────┘                 │
   │             │                                          │
┌──▼────────┐ ┌──▼─────────┐               ┌────────────────▼─┐
│ Anthropic │ │ OpenRouter │               │ Sub-Conversation │
└───────────┘ └────────────┘               │      Manager     │
                                           └───────┬──────────┘
        ┌──────────────────┐                       │
        │  Observability   │                 ┌─────▼──────────┐
        │    (Traces,      │                 │ Memory System  │
        │   Metrics, Logs) │                 │ - Vector DB    │
        └──────────────────┘                 │ - Graph DB     │
          (Cross-cutting)                    └────────────────┘
```

## Data Models

### Message
Represents a single message in a conversation.

**Properties:**
- `role`: Identifies the message sender (user, assistant, system)
- `content`: The message text content
- `timestamp`: When the message was created
- `metadata`: Extensible storage for provider-specific data, token counts, etc.

**Design Rationale:**
- Simple, immutable structure
- Provider-agnostic (maps to all LLM APIs)
- Metadata allows for future extensibility without breaking changes

### Conversation
Represents an ongoing dialogue between user and agent.

**Properties:**
- `id`: Unique identifier for this conversation
- `system_prompt`: Initial instructions/context for the agent
- `messages`: Ordered list of messages in the conversation
- `created_at`: Conversation start time
- `metadata`: Provider info, model name, conversation-level stats
- `sub_conversations`: Optional list of sub-conversation IDs for context management

**Design Rationale:**
- Encapsulates all state needed to resume a conversation
- System prompt separate from messages (some providers require this)
- Metadata tracks conversation-level information (total tokens, cost, etc.)
- Sub-conversations enable context partitioning for complex workflows

### SubConversation
Represents a focused conversation thread for specific analysis tasks.

**Properties:**
- `id`: Unique identifier for this sub-conversation
- `parent_id`: ID of the parent conversation
- `purpose`: Description of what this sub-conversation is analyzing
- `system_prompt`: Specialized instructions for this analysis
- `messages`: Messages specific to this analysis
- `summary`: Condensed result to return to parent conversation
- `created_at`: When this sub-conversation started
- `completed_at`: When analysis was complete

**Design Rationale:**
- Isolates detailed analysis to prevent context pollution
- Allows deep investigation without exhausting parent conversation tokens
- Summary mechanism enables information compression
- Parent tracking maintains conversation hierarchy

### Tool Definition
Represents a callable tool that the agent can use.

**Properties:**
- `name`: Unique identifier for the tool
- `description`: What the tool does (used by LLM to decide when to call it)
- `parameters`: JSON schema defining expected inputs
- `handler`: Function that executes the tool logic

**Design Rationale:**
- Simple, declarative tool registration
- Provider-agnostic definition (maps to different tool calling formats)
- Schema-driven validation ensures type safety

### Tool Call
Represents a request from the LLM to execute a tool.

**Properties:**
- `id`: Unique identifier for this tool call
- `name`: Which tool to execute
- `arguments`: JSON object with tool parameters
- `timestamp`: When the call was requested

### Tool Result
Represents the outcome of executing a tool.

**Properties:**
- `tool_call_id`: Links back to the originating tool call
- `content`: The result (success data or error message)
- `success`: Boolean indicating success/failure
- `timestamp`: When execution completed
- `metadata`: Execution time, error details, etc.

### MemoryEntry
Represents a piece of information stored in the agent's memory system.

**Properties:**
- `id`: Unique identifier for this memory
- `content`: The information to remember
- `embedding`: Vector representation for similarity search
- `metadata`: Feature ID, timestamp, source, relevance scores
- `relationships`: Connections to other memories (for graph-based storage)

**Design Rationale:**
- Enables retrieval of relevant context from past interactions
- Vector embeddings support semantic search
- Graph relationships support reasoning across connected concepts
- Metadata enables filtering and relevance scoring

## Component Specifications

### 1. Provider Abstraction

**Purpose:** Enable swapping LLM providers without changing agent logic.

**Interface:**
```
complete(messages, temperature, max_tokens, ...) -> Message
  - Send messages to LLM provider
  - Return assistant's response
  - Handle provider-specific formatting

estimate_tokens(messages) -> int
  - Estimate token count for messages
  - Used for context window management

get_capabilities() -> ProviderCapabilities
  - Report what this provider supports
  - (tools, vision, streaming, etc.)
```

**Providers to Support:**
- **OpenRouter** (Various models via OpenRouter API)
- **Anthropic** (Claude models via Messages API)
- **Ollama** (Local models via Ollama API)

**Design Considerations:**
- Keep interface minimal - don't abstract away important provider differences
- Each provider should handle its own API format translation
- Provider should report capabilities (some may not support tool calling, etc.)
- Errors should be normalized (rate limit, auth, network, validation)

**Error Handling:**
- `AuthenticationError`: Invalid API key or credentials
- `RateLimitError`: Provider rate limiting (should trigger retry)
- `ValidationError`: Invalid request format
- `NetworkError`: Connection issues (should trigger retry)
- `ProviderError`: Other provider-specific errors

### 2. Tool Abstraction

**Purpose:** Enable agent to interact with external systems and extend its capabilities.

**Interface:**
```
register_tool(definition) -> void
  - Register a new tool with the agent
  - Validates tool definition schema
  - Makes tool available for LLM to call

execute_tool(tool_call) -> ToolResult
  - Execute a specific tool with given arguments
  - Validate arguments against schema
  - Handle execution errors gracefully
  - Return structured result

get_tools() -> list[ToolDefinition]
  - Get all registered tools
  - Used to send tool definitions to LLM provider

format_tools_for_provider(provider) -> ProviderToolFormat
  - Convert tool definitions to provider-specific format
  - Anthropic uses specific JSON schema
  - Ollama and OpenRouter may use different format
```

**Feature Investigation Tools:**

#### Get JIRA Data
Retrieves feature metadata for ALL features in the system.

- **Parameters:** None (returns all features)
- **Returns:** JSON array with metadata for all features, each containing:
  - `folder`: Folder name (used for file system mapping)
  - `jira_key`: JIRA issue key
  - `feature_id`: Feature ID (used for tool queries)
  - `summary`: Feature name
  - `status`: Current status (Development, UAT, Production-Ready, etc.)
  - `data_quality`: Data quality indicator
- **Implementation:** Reads JIRA metadata file containing all features
- **Usage:** Called once at start of assessment to enable feature identification and mapping

#### Get Analysis
Retrieves analysis and metrics data for a feature.

- **Parameters:**
  - `feature_id` (string): The feature identifier
  - `analysis_type` (string): Type of metrics to retrieve
    - `"metrics/performance_benchmarks"`: Performance benchmarks
    - `"metrics/pipeline_results"`: Pipeline run results
    - `"metrics/security_scan_results"`: Security scan results
    - `"metrics/test_coverage_report"`: Test coverage statistics
    - `"metrics/unit_test_results"`: Unit test results
    - `"reviews/security"`: Security review results
    - `"reviews/stakeholders"`: Stakeholder reviews
    - `"reviews/uat"`: UAT environment test results
- **Returns:** JSON object with requested metrics data
- **Implementation:** Reads from JSON files in `incoming_data/{feature_num}/{analysis_type}.json`

#### List Docs
Lists available documentation files for a feature.

- **Parameters:**
  - `feature_id` (string): The feature identifier
- **Returns:** Array of document metadata objects
  - `path`: Relative path to document
  - `name`: Document name
  - `size`: File size
- **Implementation:** Scans `incoming_data/{feature_num}/planning` directory

#### Read Doc
Retrieves the contents of a documentation file.

- **Parameters:**
  - `path` (string): Path to the document (from list_docs)
- **Returns:** String containing document contents
- **Implementation:** Reads markdown file from filesystem
- **Note:** Large documents may require summarization in sub-conversation

**Tool Execution Flow:**
1. LLM indicates it wants to call a tool (returns tool_use block)
2. Agent validates tool call against registered tools
3. Agent executes tool handler with provided arguments
4. Agent formats result into tool_result message
5. Agent sends tool_result back to LLM
6. LLM processes result and continues conversation

**Error Handling:**
- `ToolNotFoundError`: Requested tool not registered
- `InvalidArgumentsError`: Arguments don't match schema
- `ToolExecutionError`: Tool handler raised an exception
- `ToolTimeoutError`: Tool execution exceeded time limit

### 3. Context Window Management

**Purpose:** Ensure conversation history fits within model's token limits while preserving critical information.

**Strategy Options:**

#### A. Truncation (Baseline)
- Keep system prompt + N most recent messages
- Discard older messages when limit approached
- **Pros**: Simple, predictable
- **Cons**: Loses important context from earlier in conversation

#### B. Sub-Conversation Pattern (Recommended for Investigator Agent)
- Main conversation maintains high-level flow
- Detailed analysis happens in sub-conversations
- Sub-conversation results summarized before adding to main thread
- **Pros**: Preserves main conversation coherence, enables deep analysis
- **Cons**: Requires careful orchestration

**How Sub-Conversations Work:**
1. Agent detects need for detailed analysis (e.g., reading large document)
2. Agent creates sub-conversation with focused purpose
3. Sub-conversation has its own system prompt and message history
4. Agent performs analysis in sub-conversation (can use multiple tool calls)
5. Agent generates concise summary of findings
6. Summary added to main conversation (not full sub-conversation)
7. Sub-conversation archived for observability

**Example:**
```
Main Conversation:
- User: "Is payment-gateway ready for production?"
- Agent: [Calls get_jira_data]
- Agent: [Calls get_metrics for uat-results]
- Agent: [Calls list_docs]
- Agent: [Sees large design.md - creates sub-conversation]

Sub-Conversation (isolated context):
- System: "You are analyzing design.md for payment-gateway feature..."
- Agent: [Calls read_doc for design.md]
- Agent: [Analyzes 50KB of design documentation]
- Agent: Summary - "Design doc shows complete OAuth2 flow, handles edge cases..."

Main Conversation (continued):
- Agent: [Receives summary: "Design doc shows complete OAuth2 flow..."]
- Agent: [Makes final decision based on all gathered info]
- Agent: Response to user with decision and justification
```

#### C. Memory-Augmented Context (Advanced)
- Store important information in external memory system
- Retrieve relevant context on-demand based on current query
- Combine with sub-conversations for maximum flexibility
- **Pros**: Scales to very large information spaces
- **Cons**: Requires memory system setup and management

**Implementation Approach:**
```
manage_context(conversation, provider_limits) -> ManagedContext
  - Input: full conversation, provider's token/message limits
  - Output: pruned/managed conversation that fits limits
  - Strategy: configurable (truncation, sub-conversation, memory-augmented)

create_sub_conversation(purpose, parent_id) -> SubConversation
  - Input: purpose of analysis, parent conversation ID
  - Output: new sub-conversation with specialized system prompt
  - Tracks relationship to parent for observability

summarize_sub_conversation(sub_conversation) -> Summary
  - Input: completed sub-conversation
  - Output: concise summary for parent conversation
  - Compression ratio configurable (e.g., 10:1)
```

**Token Budget Allocation:**
- Reserve tokens for system prompt (fixed)
- Reserve tokens for response (max_tokens parameter)
- Remaining budget for conversation history
- Safety margin (10% buffer for estimation errors)

### 4. Memory System Integration

**Purpose:** Enable agent to maintain context across conversations and retrieve relevant information efficiently.

**Memory Types:**

#### A. Vector Database (Semantic Memory)
- Store embeddings of important information
- Enable semantic search ("find similar features that had UAT issues")
- Quick retrieval of relevant past decisions

**Use Cases:**
- "What issues did we find in similar payment features?"
- "Retrieve all features that failed UAT due to error rates"
- Store summaries of past feature assessments

#### B. Graph Database (Relational Memory)
- Store relationships between entities (features, components, dependencies)
- Enable reasoning about connections
- Track feature dependencies and impacts

**Use Cases:**
- "What other features depend on payment-gateway?"
- "Which components are affected by this feature?"
- Map feature relationships for impact analysis

**Recommended Approach:**
- Use Graffiti MCP for graph-based memory storage
- Alternatively, use file-based storage with simple indexing
- Store feature assessment results for future reference
- Enable learning from past decisions

**Memory Operations:**
```
store_memory(content, metadata) -> MemoryID
  - Store information with associated metadata
  - Generate embeddings if using vector search
  - Create relationships if using graph storage

retrieve_memories(query, limit, filters) -> list[Memory]
  - Semantic search for relevant memories
  - Filter by metadata (feature_id, timestamp, etc.)
  - Return top-k most relevant results

relate_memories(source_id, target_id, relationship) -> void
  - Create relationship between two memories
  - Enable graph-based reasoning
```

### 5. Retry Mechanism

**Purpose:** Handle transient failures gracefully without losing conversation state.

**Retry Scenarios:**
- Rate limiting (429 errors)
- Network timeouts
- Temporary server errors (500, 502, 503)

**Non-Retry Scenarios:**
- Authentication errors (401, 403)
- Validation errors (400)
- Not found (404)
- Permanent errors

**Retry Strategy:**
```
execute_with_retry(operation, retry_config) -> Result
  - Attempt operation
  - On retryable failure:
    - Wait with exponential backoff
    - Retry up to max_attempts
    - Track retry attempts in observability
  - On non-retryable failure:
    - Fail immediately with clear error
```

**Retry Configuration:**
- `max_attempts`: Maximum retry attempts (e.g., 3)
- `initial_delay`: First retry delay (e.g., 1s)
- `max_delay`: Cap on backoff delay (e.g., 60s)
- `backoff_factor`: Multiplier for exponential backoff (e.g., 2)
- `jitter`: Add randomness to prevent thundering herd

### 6. Agent Core

**Purpose:** Orchestrate all components to enable conversation with LLM.

**Responsibilities:**
- Maintain conversation state
- Coordinate provider calls
- Manage context window before each call
- Execute tool calling loop
- Manage sub-conversations
- Interface with memory systems
- Handle retries for failed requests
- Emit observability events

**Key Operations:**
```
send_message(content) -> AssistantResponse
  1. Create user message
  2. Add to conversation
  3. Check if memory retrieval needed
  4. Manage context window (may create sub-conversation)
  5. Call provider with retry logic
  6. Check if response contains tool calls
  7. If tool calls:
     a. Execute each tool
     b. Check if sub-conversation needed for large data
     c. Add tool results to conversation (or sub-conversation)
     d. Call provider again (loop back to step 5)
  8. If no tool calls:
     a. Add assistant response to conversation
     b. Store important information in memory
     c. Return response to caller

create_sub_conversation(purpose, context_summary) -> SubConversation
  - Create isolated conversation for detailed analysis
  - Specialized system prompt based on purpose
  - Link to parent conversation for tracking

complete_sub_conversation(sub_conv_id) -> Summary
  - Generate summary of sub-conversation findings
  - Return condensed results to parent conversation
  - Archive sub-conversation for observability

register_tool(tool_def) -> void
  - Register a tool for the agent to use
  - Tool becomes available in all subsequent LLM calls

get_history(limit) -> list[Message]
  - Retrieve conversation history
  - Optional limit for recent N messages

get_context() -> ConversationContext
  - Get metadata about current conversation
  - Message count, token usage, provider info, trace IDs, tool calls
```

**State Management:**
- Agent holds current conversation in memory
- Sub-conversations tracked and linked to parent
- Conversation is mutable (messages added over time)
- Tool definitions registered at agent initialization
- Memory system connection maintained throughout session

### 7. Observability System

**Purpose:** Complete visibility into agent behavior without cluttering business logic.

**Design Principle:** Observability should be _as invisible as reasonable_ in the code but comprehensive in output. Use OpenTelemetry formats.

**Observability Layers:**

#### Traces
- **Conversation Trace**: Entire user interaction
- **Agent Operation Spans**: send_message, context management, tool execution
- **Sub-Conversation Spans**: Detailed analysis operations
- **Provider Call Spans**: LLM API request/response
- **Tool Execution Spans**: Individual tool calls with timing
- **Memory Operation Spans**: Store and retrieve operations
- **Retry Spans**: Track retry attempts and backoff

**Trace Attributes:**
- Standard OpenTelemetry fields
- Conversation ID
- Sub-conversation ID (if applicable)
- Parent conversation ID (for sub-conversations)
- Message count
- Token counts (input, output, total)
- Model name, provider name
- Temperature, max_tokens
- Context window state (tokens used, tokens available)
- Tool call stats (tool name, execution time, success/failure)
- Memory operation stats (queries, results, timing)
- Retry info (attempt number, backoff time)

#### Metrics
- **LLM Call Duration**: Time for provider.complete()
- **Token Usage**: Input/output tokens per call
- **Sub-Conversation Count**: Number of sub-conversations created
- **Context Compression Ratio**: Original vs final token count
- **Error Rates**: By provider, by error type
- **Retry Rates**: How often retries are needed
- **Tool Execution Duration**: Time per tool call
- **Tool Success Rates**: Success/failure by tool
- **Memory Query Duration**: Time for memory retrieval
- **Memory Hit Rate**: Relevance of retrieved memories
- **Costs**: Estimated cost per call (based on provider pricing)

#### Logs
- Errors with full context
- Retry attempts with reasons
- Context window pruning events
- Sub-conversation creation and completion
- Tool execution events (calls, results, errors)
- Memory operations (stores, retrievals)

**Instrumentation Approach:**
- Decorators for automatic function tracing
- Context managers for custom spans
- Middleware for HTTP auto-instrumentation
- Structured logging with correlation IDs

**Trace Context Propagation:**
- Each conversation has a trace ID
- Sub-conversations inherit parent trace context
- All operations link to conversation trace
- Trace IDs included in saved interactions
- Enables correlation between interactions and traces
- Each trace should be placed in its own file
- Each message, response, or other operation should create a new span
- All spans belonging to a trace should be saved in the trace file

### 8. Evaluation System

**Purpose:** Validate agent behavior through automated evaluation and regression tracking.

**Design Principle:** Unlike traditional software testing that verifies deterministic behavior, agent evaluations must account for the probabilistic nature of LLMs while maintaining quality standards.

**Interface:**
```
run_evaluation(test_suite) -> EvaluationResults
  - Execute test scenarios against agent
  - Measure behavior across multiple dimensions
  - Generate structured results

save_baseline(results, version_id) -> void
  - Store results as baseline for future comparison
  - Enable regression detection

compare_to_baseline(current, baseline) -> Comparison
  - Calculate deltas for all metrics
  - Identify regressions and improvements
  - Flag significant changes
```

**Evaluation Dimensions:**

#### 1. Feature Identification
- Does the agent correctly identify the feature ID from user input?
- Does it handle ambiguous feature names appropriately?
- Does it ask for clarification when needed?

#### 2. Tool Usage (Behavioral Validation)
- Does the agent call the correct tools for assessment?
- Are they called in a reasonable order?
- Does it retrieve all necessary data before making decision?
- Are parameters valid and appropriate?
- Does it use sub-conversations for large data appropriately?

#### 3. Decision Quality (Output Validation)
- Does the readiness assessment match expected outcome?
- Are key risks identified in justification?
- Is reasoning sound given the data?
- Does the agent avoid hallucinating information?
- Does it cite specific data sources correctly?

#### 4. Context Management
- Does the agent manage token budget effectively?
- Are sub-conversations used appropriately?
- Is information compression effective?
- Does it maintain coherence across long interactions?

#### 5. Memory Utilization
- Does the agent store appropriate information?
- Are memory retrievals relevant to the query?
- Does it learn from past assessments?

#### 6. Error Handling (Robustness Validation)
- Does the agent handle missing data gracefully?
- Are errors reported clearly?
- Does it make appropriate decisions with incomplete information?
- Does it degrade gracefully rather than fail?

**Test Suite Composition:**

#### Feature Readiness Scenarios
- **Ready for promotion**: All metrics green, docs complete, tests passing
- **Not ready - test failures**: UAT tests failing above threshold
- **Not ready - missing docs**: Critical design documentation missing
- **Not ready - performance**: Performance metrics below requirements
- **Not ready - security**: Security scan shows vulnerabilities
- **Borderline**: Some concerns but overall acceptable

#### Edge Cases
- Missing JIRA data
- Incomplete metrics files
- Very large documentation requiring sub-conversations
- Multiple features with similar names
- Conflicting signals (tests pass but metrics poor)

#### Error Scenarios
- Tool failures (file not found, network errors)
- Malformed JSON in metrics
- Timeout during document analysis
- Memory system unavailable (if implemented)

**Evaluation Approaches:**
- **Ground Truth Comparison**: Compare decision to known correct assessment
- **Rubric-Based Scoring**: Define criteria and score responses
- **LLM-as-Judge**: Use separate LLM to evaluate quality of reasoning

**Regression Tracking:**
- Establish baseline performance metrics
- Track pass rates, scores, and behavior over time
- Detect degradations (>5% drop triggers warning)
- Monitor improvements and changes

**Report Format:**
```json
{
  "summary": {
    "pass_rate": 0.85,
    "total_scenarios": 15,
    "avg_scores": {
      "tool_usage": 0.92,
      "decision_quality": 0.88,
      "context_management": 0.85
    }
  },
  "scenarios": [
    {
      "id": "ready_for_production",
      "status": "passed",
      "scores": {
        "feature_identification": 1.0,
        "tool_usage": 0.9,
        "decision_quality": 0.95
      },
      "details": "Correctly identified all risks and approved feature"
    }
  ],
  "regression_analysis": {
    "regressions": [],
    "improvements": ["context_management up 12%"]
  }
}
```

**Design Rationale:**
- Machine-readable output enables CI/CD integration
- Multi-dimensional scoring captures different quality aspects
- Regression tracking prevents silent quality erosion
- Structured reports speed up debugging and improvement

## Feature Data Organization

The test data is organized by feature ID with the following structure:

```
incoming_data/
├── featureN/
│   ├── jira/
│   │   ├── feature_issue.json           # Feature metadata
│   │   └── issue_changelog.json
│   ├── metrics/                         # Analysis
│   │   ├── performance_benchmarks.json
│   │   ├── pipeline_results.json
│   │   ├── security_scan_results.json
│   │   ├── test_coverage_report.json
│   │   └── unit_test_coverage.json
│   ├── planning/                        # Docs
│   │   ├── ARCHITECTURE.md
│   │   ├── DATABASE_SCHEMA.md
│   │   ├── DEPLOYMENT_PLAN.md
│   │   ├── DESIGN_DOC.md
│   │   └── ... (more)
│   └── reviews/                         # Analysis
│       ├── security.json
│       ├── stakeholders.json
│       └── uat.json
```

**Total Data Size:** Approximately 1+ MB of text data across all features

**Test Features:**

The test data includes four features with different readiness scenarios:

| Feature | Complexity | Stage | Readiness | Key Characteristics |
|---------|-----------|-------|-----------|---------------------|
| **Maintenance Scheduling & Alert System** | Medium | Production-Ready | ✅ READY | Clear-cut success case, all gates passed, complete documentation, all metrics green |
| **QR Code Check-in/out with Mobile App** | High | Development/UAT | ❌ NOT READY | Multiple critical blockers, clear failures in testing, incomplete implementation |
| **Advanced Resource Reservation System** | High | UAT | 🔄 AMBIGUOUS | Mixed signals, incomplete data, uncertainty in assessment, requires judgment |
| **Contribution Tracking & Community Credits** | Medium-High | UAT | 🔄 PARTIAL | Right stage for UAT, but not ready for production promotion yet, some gaps |

**Feature Scenario Design Rationale:**

1. **Maintenance Scheduling** (Ready)
   - Tests agent's ability to recognize when all criteria are met
   - Validates positive decision-making
   - All analysis data shows green signals
   - Complete, high-quality documentation

2. **QR Code Check-in** (Not Ready)
   - Tests agent's ability to identify clear blockers
   - Multiple failure signals across different data sources
   - Tests citation of specific issues in justification

3. **Advanced Resource Reservation** (Ambiguous)
   - Tests agent's handling of uncertainty and incomplete data
   - Mixed signals across different analysis types
   - Tests nuanced decision-making and risk assessment
   - Most realistic scenario - requires judgment

4. **Contribution Tracking** (Partial)
   - Tests agent's ability to distinguish "in right stage" from "ready for next stage"
   - Some progress made but gaps prevent promotion
   - Tests understanding of stage-appropriate readiness criteria

## Implementation Progression

The Investigator Agent builds on the Detective Agent foundation with these new capabilities:

1. **JIRA Tool**: Feature metadata retrieval
2. **Metrics Tool**: Multi-type metrics analysis
3. **Documentation Tools**: List and read planning docs
4. **Sub-Conversations**: Context management for large data
5. **Memory System** (optional): Learning across assessments
6. **Enhanced Evals**: Testing all new capabilities

Each capability should be added incrementally with verification before moving to the next.
