# Investigator Agent Implementation Steps

## Recommended Order of Implementation

This section outlines an incremental, iterative approach to building the Investigator Agent. Each step builds on the previous Detective Agent implementation, adding context engineering capabilities. Each step has clear acceptance criteria.

**Prerequisites:** The student should have completed Module 7 (Detective Agent) with working implementations of:
- Basic conversation loop
- Provider abstraction (at least one provider)
- Observability (traces and spans)
- Context window management (basic truncation)
- Retry mechanism
- System prompt engineering
- Tool abstraction and execution loop
- Evaluation framework

This module extends that foundation with advanced context engineering techniques.

---

## Step 0: Verify Detective Agent Foundation

**Goal:** Ensure the base agent from Module 7 is working correctly before adding new capabilities.

**Tasks:**
- Clone or continue from Module 7 implementation
- Run existing tests to verify all components work
- Verify conversation persistence works
- Verify tool execution loop works end-to-end
- Verify observability traces are being generated

**Acceptance Criteria:**
- All Module 7 tests pass
- Can have a conversation with the agent via CLI
- Can see traces being generated
- Tool execution works (even if using different tools than Investigator needs)

---

## Step 1: Add JIRA Tool

**Goal:** Enable the agent to retrieve feature metadata for all features in the system.

**Important Context:** The test data is already provided in the `incoming_data/` directory with four features. The JIRA tool will return metadata for ALL four features at once, allowing the agent to identify which feature the user is asking about.

### 1.1: Understand Test Data Structure

**Tasks:**
- Review the existing test data in `incoming_data/`
- Understand the four feature scenarios:
  1. **Maintenance Scheduling & Alert System** - Production-Ready (✅ READY)
  2. **QR Code Check-in/out with Mobile App** - Development/UAT (❌ NOT READY)
  3. **Advanced Resource Reservation System** - UAT (🔄 AMBIGUOUS)
  4. **Contribution Tracking & Community Credits** - UAT (🔄 PARTIAL)
- Note the JIRA metadata format that will be returned:
  - `folder`: Folder name for file system mapping
  - `jira_key`: JIRA issue key
  - `feature_id`: Feature ID for tool queries
  - `summary`: Feature name
  - `status`: Current status
  - `data_quality`: Data quality indicator

**Existing Data Structure:**
```
incoming_data/
├── feature1/  (Maintenance Scheduling)
├── feature2/  (QR Code Check-in)
├── feature3/  (Resource Reservation)
└── feature4/  (Contribution Tracking)
```

**Acceptance Criteria:**
- Understand all four feature scenarios
- Understand JIRA metadata structure
- Understand folder → feature_id mapping pattern
- Ready to implement tool that returns all feature metadata

### 1.2: Implement get_jira_data Tool

**Tasks:**
- Create tool definition for `get_jira_data` (no parameters - returns all features)
- Implement handler that:
  - Reads JIRA metadata file containing all four features
  - Returns array of feature metadata objects
  - Handles missing file gracefully
- Create feature ID mapping utility (feature_id → folder)
  - This will be shared across all tools
  - Maps feature_id to the correct folder in `incoming_data/`
- Register tool with agent
- Add unit tests for tool handler

**Tool Definition:**
```python
{
  "name": "get_jira_data",
  "description": "Retrieves metadata for all features in the system. Returns an array with folder, jira_key, feature_id, summary, status, and data_quality for each feature. Call this at the start of an assessment to identify which feature the user is asking about.",
  "parameters": {
    "type": "object",
    "properties": {},
    "required": []
  }
}
```

**Acceptance Criteria:**
- Tool is registered with agent (no parameters)
- Tool handler reads JIRA metadata file
- Tool returns array with all 4 features
- Each feature has: folder, jira_key, feature_id, summary, status, data_quality
- Feature ID → folder mapping utility created
- Tool handles missing file with clear error message
- Tool execution is traced in observability
- Unit tests verify tool behavior
- Manual CLI test shows agent receives all feature metadata

### 1.3: Update System Prompt

**Tasks:**
- Update agent's system prompt to include:
  - Role: "You are an Investigator Agent for a Release Confidence System"
  - Purpose: Assess whether features are ready for promotion
  - Three-phase workflow pattern
  - Phase 1 instructions: Call get_jira_data to identify features
  - Available tools and when to use them
  - Output format (clear decision + justification)
- Test that agent behavior reflects new system prompt

**Example System Prompt Addition:**
```
You are an Investigator Agent for a Release Confidence System. Your role is to
determine whether a feature is ready to be promoted to the next stage of development
(e.g., from Development to UAT, or from UAT to Production).

You follow a three-phase workflow:

PHASE 1: Feature Identification
- Call get_jira_data() to retrieve metadata for all 4 features
- Identify which feature the user is asking about based on their natural language query
- Extract the feature_id for use in subsequent tool calls

PHASE 2: Data Gathering (will be added in later steps)
- Gather analysis data and documentation about the feature
- Each data gathering operation will happen in a focused sub-analysis

PHASE 3: Final Assessment
- Synthesize all gathered information
- Make a clear go/no-go decision with specific justification

For now, start by calling get_jira_data() and identifying the relevant feature.
```

**Acceptance Criteria:**
- System prompt updated with Investigator Agent role
- System prompt explains three-phase workflow
- System prompt explains get_jira_data returns all features
- Agent calls get_jira_data at start of assessment
- Agent identifies correct feature from user query
- Agent extracts feature_id correctly
- Manual testing confirms agent behavior matches prompt

### 1.4: Verify End-to-End with JIRA Tool

**Tasks:**
- Test agent via CLI with queries about each of the four features:
  - "Is the maintenance scheduling feature ready for production?"
  - "What's the status of the QR code check-in feature?"
  - "Tell me about the reservation system"
  - "Can we promote the contribution tracking feature?"
- Verify agent calls get_jira_data tool (with no parameters)
- Verify agent receives all 4 features
- Verify agent correctly identifies which feature user is asking about
- Verify agent extracts correct feature_id
- Check traces to ensure tool execution is captured

**Acceptance Criteria:**
- Agent calls get_jira_data() at start (no parameters)
- Agent receives metadata for all 4 features
- Agent correctly identifies feature from natural language query
- Agent extracts correct feature_id from metadata
- Agent mentions feature details (status, data_quality) in response
- Tool calls visible in traces with timing
- Conversation is coherent and follows Phase 1 workflow

---

## Step 2: Add Analysis Tool

**Goal:** Enable the agent to retrieve and analyze various types of analysis data (metrics and reviews).

### 2.1: Understand Analysis Test Data

**Important Context:** The test data is already provided in `incoming_data/` with analysis files for each feature.

**Tasks:**
- Review the existing analysis data structure in `incoming_data/featureN/`
- Understand the two types of analysis data:
  - **Metrics** (`metrics/` folder): Performance benchmarks, pipeline results, security scans, test coverage, unit test results
  - **Reviews** (`reviews/` folder): Security reviews, stakeholder reviews, UAT reviews
- Note the 8 available analysis types:
  - `metrics/performance_benchmarks`
  - `metrics/pipeline_results`
  - `metrics/security_scan_results`
  - `metrics/test_coverage_report`
  - `metrics/unit_test_results`
  - `reviews/security`
  - `reviews/stakeholders`
  - `reviews/uat`
- Understand how data varies by feature scenario:
  - **Maintenance Scheduling** (Ready): All analysis shows green signals
  - **QR Code Check-in** (Not Ready): Multiple analysis types show failures
  - **Resource Reservation** (Ambiguous): Mixed signals across analysis types
  - **Contribution Tracking** (Partial): Some gaps in analysis data

**Existing Structure:**
```
incoming_data/feature1/
├── jira/
├── metrics/
│   ├── performance_benchmarks.json
│   ├── pipeline_results.json
│   ├── security_scan_results.json
│   ├── test_coverage_report.json
│   └── unit_test_results.json
├── planning/ (docs)
└── reviews/
    ├── security.json
    ├── stakeholders.json
    └── uat.json
```

**Acceptance Criteria:**
- Understand all 8 analysis types
- Understand metrics vs reviews distinction
- Know how analysis data aligns with feature scenarios
- Ready to implement tool that retrieves specific analysis types

### 2.2: Implement get_analysis Tool

**Tasks:**
- Create tool definition for `get_analysis`
- Implement handler that:
  - Accepts `feature_id` and `analysis_type` parameters
  - Uses feature ID → folder mapping utility (from Step 1)
  - Maps analysis_type to correct file path (metrics/ or reviews/ subfolder)
  - Reads and returns JSON data
  - Handles missing files gracefully
- Register tool with agent
- Add unit tests for tool handler

**Tool Definition:**
```python
{
  "name": "get_analysis",
  "description": "Retrieves analysis and metrics data for a feature. Available analysis types: metrics/performance_benchmarks, metrics/pipeline_results, metrics/security_scan_results, metrics/test_coverage_report, metrics/unit_test_results, reviews/security, reviews/stakeholders, reviews/uat",
  "parameters": {
    "type": "object",
    "properties": {
      "feature_id": {
        "type": "string",
        "description": "The feature identifier from get_jira_data"
      },
      "analysis_type": {
        "type": "string",
        "enum": [
          "metrics/performance_benchmarks",
          "metrics/pipeline_results",
          "metrics/security_scan_results",
          "metrics/test_coverage_report",
          "metrics/unit_test_results",
          "reviews/security",
          "reviews/stakeholders",
          "reviews/uat"
        ],
        "description": "Type of analysis to retrieve (includes path: metrics/* or reviews/*)"
      }
    },
    "required": ["feature_id", "analysis_type"]
  }
}
```

**Acceptance Criteria:**
- Tool is registered with agent
- Tool uses feature ID → folder mapping utility
- Tool handler reads correct file based on both parameters
- Tool handles both metrics/ and reviews/ paths
- Tool returns valid JSON data
- Tool handles missing analysis files with clear error message
- Tool execution is traced in observability
- Unit tests verify all 8 analysis types
- Manual CLI test shows agent can call tool with different analysis types

### 2.3: Update System Prompt for Analysis

**Tasks:**
- Update system prompt to mention get_analysis tool
- Add guidance on Phase 2 workflow (data gathering)
- Note that get_analysis will be used in sub-conversations (Phase 4)
- Include decision criteria examples

**Example Addition:**
```
PHASE 2: Data Gathering (updated)
After identifying the feature, gather relevant analysis data using get_analysis:
- reviews/uat for UAT test results
- metrics/test_coverage_report for code coverage
- metrics/security_scan_results for security issues
- reviews/stakeholders for stakeholder feedback
- reviews/security for security review status

You can also review planning documentation using list_docs and read_doc.

For now, call get_analysis directly. In later steps, this will happen in sub-conversations.
```

**Acceptance Criteria:**
- System prompt updated with get_analysis tool information
- System prompt lists all 8 analysis types
- System prompt mentions both metrics and reviews
- Agent uses get_analysis tool when assessing features
- Agent can request different analysis types

### 2.4: Verify End-to-End with Analysis

**Tasks:**
- Test agent with feature assessment queries
- Verify agent calls get_jira_data first (Phase 1)
- Verify agent calls get_analysis multiple times (Phase 2)
- Verify agent uses different analysis types
- Verify agent cites specific analysis findings in assessment
- Check traces for all tool calls

**Acceptance Criteria:**
- Agent calls get_jira_data first (Phase 1)
- Agent identifies correct feature and feature_id
- Agent then calls get_analysis multiple times (Phase 2)
- Agent uses different analysis types (metrics and reviews)
- Agent incorporates analysis data into assessment
- Agent provides specific justifications citing analysis results
- All tool calls visible in traces with correct parameters

---

## Step 3: Add Documentation Tools

**Goal:** Enable the agent to list and read planning documentation.

### 3.1: Understand Documentation Test Data

**Important Context:** The test data already includes extensive planning documentation in `incoming_data/featureN/planning/` directories.

**Tasks:**
- Review the existing planning documentation in `incoming_data/featureN/planning/`
- Understand the documentation files available:
  - Large files (>10KB): ARCHITECTURE.md, DESIGN_DOC.md, DATABASE_SCHEMA.md
  - Medium files: DEPLOYMENT_PLAN.md, TEST_STRATEGY.md, USER_STORIES.md
  - Smaller files: Various planning and specification documents
- Note how documentation completeness varies by feature:
  - **Maintenance Scheduling** (Ready): Complete, thorough documentation
  - **QR Code Check-in** (Not Ready): Some docs missing or incomplete
  - **Resource Reservation** (Ambiguous): Documentation present but gaps
  - **Contribution Tracking** (Partial): Mixed documentation quality

**Existing Structure:**
```
incoming_data/feature1/
├── jira/
├── metrics/
├── planning/
│   ├── ARCHITECTURE.md (large, >10KB)
│   ├── DESIGN_DOC.md (large, >10KB)
│   ├── DATABASE_SCHEMA.md (large)
│   ├── DEPLOYMENT_PLAN.md (medium)
│   ├── TEST_STRATEGY.md (medium)
│   └── ... (more planning docs)
└── reviews/
```

**Acceptance Criteria:**
- Understand documentation structure in planning/ folders
- Identify which docs are large (will trigger sub-conversations)
- Understand how doc completeness aligns with feature scenarios
- Ready to implement list_docs and read_doc tools

### 3.2: Implement list_docs Tool

**Tasks:**
- Create tool definition for `list_docs`
- Implement handler that:
  - Accepts `feature_id` parameter
  - Uses feature ID → folder mapping utility (from Step 1)
  - Scans `planning/` directory for the feature
  - Returns array of document metadata (path, name, size)
  - Handles missing planning directory gracefully
- Register tool with agent
- Add unit tests

**Tool Definition:**
```python
{
  "name": "list_docs",
  "description": "Lists available planning documentation files for a feature. Returns metadata about each document including path, name, and size.",
  "parameters": {
    "type": "object",
    "properties": {
      "feature_id": {
        "type": "string",
        "description": "The feature identifier from get_jira_data"
      }
    },
    "required": ["feature_id"]
  }
}
```

**Acceptance Criteria:**
- Tool is registered with agent
- Tool uses feature ID → folder mapping utility
- Tool handler scans correct planning/ directory
- Tool returns array of document metadata
- Metadata includes: path, name, size (bytes)
- Tool handles missing planning directory gracefully
- Unit tests verify tool behavior for all features

### 3.3: Implement read_doc Tool

**Tasks:**
- Create tool definition for `read_doc`
- Implement handler that:
  - Accepts `path` parameter
  - Reads markdown file from filesystem
  - Returns file contents as string
  - Handles missing files gracefully
  - Add size warnings for large files
- Register tool with agent
- Add unit tests

**Tool Definition:**
```python
{
  "name": "read_doc",
  "description": "Retrieves the contents of a documentation file. Use list_docs first to see available documents.",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Path to the document (from list_docs output)"
      }
    },
    "required": ["path"]
  }
}
```

**Acceptance Criteria:**
- Tool is registered with agent
- Tool handler reads correct file
- Tool returns full file contents
- Tool handles missing files with clear error
- Tool execution is traced with file size in metadata
- Unit tests verify tool behavior

### 3.4: Update System Prompt for Documentation

**Tasks:**
- Update system prompt to mention doc tools
- Add guidance on checking documentation completeness
- Note that design and architecture docs are important for production readiness

**Example Addition:**
```
You should also review planning documentation:
1. Use list_docs to see available documentation
2. Read critical documents like design.md and architecture.md
3. Assess whether documentation is complete and thorough
4. Look for any gaps or concerns mentioned in the documentation

Complete and thorough documentation is required for production promotion.
```

**Acceptance Criteria:**
- System prompt updated with documentation tools
- Agent uses list_docs before read_doc
- Agent reads relevant documentation files
- Agent assesses documentation completeness

### 3.5: Identify Context Window Problem

**Tasks:**
- Test agent with feature that has large documentation
- Try to read multiple large docs (design.md + architecture.md)
- Observe that context window fills up quickly
- See degraded performance or errors due to token limits
- Document the problem in preparation for Step 4

**Expected Behavior:**
- Agent calls list_docs successfully
- Agent calls read_doc for first large document
- Agent may struggle to process second large document
- Token count approaches limit
- May see context truncation affecting decision quality

**Acceptance Criteria:**
- Can reproduce context window pressure with large docs
- Token usage visible in traces showing near-limit conditions
- Clear motivation for implementing sub-conversations in next step

---

## Step 4: Add Sub-Conversation Context Management

**Goal:** Enable the agent to analyze data in isolated sub-conversations, implementing the Phase 2 workflow pattern.

**Context:** This is the **core capability** of Module 8. Phase 2 tools (`get_analysis`, `read_doc`) should execute in sub-conversations, with only summaries returning to the main thread. This keeps the main conversation focused on decision-making (Phase 1 and Phase 3) while detailed analysis happens in isolated contexts.

### 4.1: Design Sub-Conversation Data Model

**Tasks:**
- Define SubConversation data structure
- Include fields: id, parent_id, purpose, system_prompt, messages, summary, created_at, completed_at
- Define how sub-conversations link to parent conversation
- Plan how summaries flow back to main conversation

**Acceptance Criteria:**
- SubConversation data model defined
- Clear relationship to parent Conversation
- Summary mechanism designed
- Data model documented

### 4.2: Implement Sub-Conversation Manager

**Tasks:**
- Create sub-conversation creation logic
- Implement specialized system prompt generation based on purpose
- Implement conversation isolation (sub-conv has own message history)
- Implement summary generation when sub-conversation completes
- Link sub-conversations to parent for observability

**Key Functions:**
```python
create_sub_conversation(purpose, parent_id, context_summary) -> SubConversation
  - Create new sub-conversation with focused purpose
  - Generate specialized system prompt
  - Initialize with context summary from parent
  - Link to parent conversation

execute_in_sub_conversation(sub_conv, tool_call) -> SubConversation
  - Execute tool call within sub-conversation context
  - Maintain isolation from parent conversation
  - Track tokens separately

summarize_sub_conversation(sub_conv) -> str
  - Generate concise summary of findings
  - Compress detailed analysis into key points
  - Return summary for addition to parent conversation
```

**Acceptance Criteria:**
- Can create sub-conversations programmatically
- Sub-conversations have isolated message history
- Specialized system prompts generated based on purpose
- Summaries can be extracted from sub-conversations
- Parent-child relationship tracked

### 4.3: Integrate Sub-Conversations into Agent Core

**Tasks:**
- Detect when tool result is large (e.g., >5000 tokens)
- Automatically create sub-conversation for analysis
- Execute analysis in sub-conversation
- Generate summary and add to main conversation (not full sub-conv)
- Update send_message flow to handle sub-conversations

**Decision Logic:**
```python
if tool_result.size > LARGE_CONTENT_THRESHOLD:
    # Create sub-conversation for analysis
    sub_conv = create_sub_conversation(
        purpose=f"Analyze {tool_name} output",
        parent_id=main_conversation.id,
        context_summary=get_conversation_context(main_conversation)
    )

    # Execute in sub-conversation
    analysis = analyze_in_sub_conversation(sub_conv, tool_result)

    # Summarize and return to main conversation
    summary = summarize_sub_conversation(sub_conv)
    add_message(main_conversation, summary)
else:
    # Small content, add directly to main conversation
    add_message(main_conversation, tool_result)
```

**Acceptance Criteria:**
- Agent detects large tool results
- Sub-conversations created automatically for large content
- Analysis happens in isolated context
- Summaries added to main conversation
- Main conversation remains manageable size
- Token budgets tracked separately for main and sub-conversations

### 4.4: Update Observability for Sub-Conversations

**Tasks:**
- Add sub-conversation spans to traces
- Link sub-conversation spans to parent conversation
- Track token usage separately for sub-conversations
- Include summary compression ratio in metrics
- Make sub-conversations visible in trace output

**New Trace Attributes:**
- `sub_conversation.id`
- `sub_conversation.parent_id`
- `sub_conversation.purpose`
- `sub_conversation.tokens.input`
- `sub_conversation.tokens.output`
- `sub_conversation.compression_ratio`

**Acceptance Criteria:**
- Sub-conversations create their own spans
- Sub-conversation spans nested under parent conversation
- Token usage tracked separately
- Compression ratios visible in traces
- Can correlate sub-conversations to parent in trace files

### 4.5: Verify Sub-Conversation Context Management

**Tasks:**
- Test with feature that has multiple large documents
- Verify agent creates sub-conversations for large docs
- Verify main conversation stays under token limits
- Verify summaries capture key information
- Verify agent can process multiple large docs successfully
- Check traces for sub-conversation spans

**Test Scenarios:**
- Read single large doc: Should use sub-conversation
- Read multiple large docs: Should use multiple sub-conversations
- Read small doc: Should NOT use sub-conversation
- Make decision based on summarized large doc analysis

**Acceptance Criteria:**
- Agent successfully processes multiple large documents
- Main conversation token count stays manageable
- Sub-conversations visible in traces
- Summaries preserve critical information
- Final decision quality maintained despite compression
- No context window errors

---

## Step 5: Add Memory System (Optional)

**Goal:** Enable the agent to remember past assessments and learn from previous decisions.

**Note:** This step is optional. Students can choose to implement memory using:
- Graffiti MCP (recommended for graph-based memory)
- Vector database (for semantic memory)
- File-based storage (for simple memory)
- Skip entirely and move to evaluations

### 5.1: Choose Memory System

**Tasks:**
- Review memory options (Graffiti MCP, vector DB, file-based)
- Decide on approach based on learning goals
- Set up chosen memory system
- Create memory storage location

**Acceptance Criteria:**
- Memory system selected and justified
- Memory system installed/configured if needed
- Storage location created
- Can connect to memory system from agent

### 5.2: Design Memory Schema

**Tasks:**
- Define what information to store
  - Feature assessments (feature_id, decision, justification, timestamp)
  - Key findings (risks identified, metrics values)
  - Patterns (common issues, recurring problems)
- Define memory retrieval triggers
  - When starting new assessment, check for similar features
  - When encountering new pattern, check for precedents
- Design memory entry format

**Example Memory Entry:**
```json
{
  "id": "mem_001",
  "type": "feature_assessment",
  "feature_id": "payment-gateway",
  "decision": "not_ready",
  "justification": "UAT error rate 2.3% exceeds 1% threshold",
  "key_metrics": {
    "uat_pass_rate": 0.987,
    "error_rate": 0.023
  },
  "timestamp": "2025-10-15T10:30:00Z",
  "relationships": ["similar_to:user-auth"]
}
```

**Acceptance Criteria:**
- Memory schema defined
- Retrieval triggers identified
- Memory entry format documented
- Schema supports learning from past assessments

### 5.3: Implement Memory Operations

**Tasks:**
- Implement store_memory function
- Implement retrieve_memories function
- Implement relate_memories function (if using graph DB)
- Add error handling for memory system unavailability

**Key Functions:**
```python
store_memory(content, metadata) -> MemoryID
  - Store feature assessment
  - Generate embeddings if using vector search
  - Create relationships if using graph

retrieve_memories(query, limit, filters) -> list[Memory]
  - Search for similar past assessments
  - Filter by feature type, decision, timestamp
  - Return most relevant memories

relate_memories(source, target, relationship) -> void
  - Link related features
  - Track patterns across features
```

**Acceptance Criteria:**
- Can store memory entries
- Can retrieve relevant memories
- Can create relationships (if applicable)
- Error handling for memory system failures
- Unit tests for memory operations

### 5.4: Integrate Memory into Agent Workflow

**Tasks:**
- Check memory at start of feature assessment
- Store assessment results after decision
- Include relevant past assessments in agent context
- Update system prompt to mention memory capability

**Integration Points:**
```python
# At start of assessment
past_assessments = retrieve_memories(
    query=f"feature assessments similar to {feature_id}",
    limit=3
)
if past_assessments:
    add_context("Similar past assessments: ..." + summarize(past_assessments))

# After making decision
store_memory(
    content=assessment_summary,
    metadata={
        "feature_id": feature_id,
        "decision": decision,
        "key_metrics": metrics
    }
)
```

**Acceptance Criteria:**
- Agent retrieves relevant memories before assessment
- Agent incorporates past learnings into decision
- Agent stores new assessments after completion
- Memory operations visible in traces
- Memory enhances decision quality

### 5.5: Verify Memory System

**Tasks:**
- Assess same feature twice, verify agent remembers
- Assess similar features, verify agent finds related memories
- Test with memory system unavailable (graceful degradation)
- Verify stored memories are retrievable
- Check traces for memory operations

**Acceptance Criteria:**
- Agent remembers past assessments
- Agent finds relevant similar assessments
- Agent gracefully handles memory system failures
- Memory operations traced and timed
- Memory improves assessment quality

---

## Step 6: Add Evaluation System

**Goal:** Validate that the Investigator Agent correctly assesses feature readiness across multiple scenarios.

### 6.1: Design Evaluation Test Cases

**Tasks:**
- Create test scenarios covering:
  - Feature identification (correct feature from user query)
  - Tool usage (calls right tools in right order)
  - Decision quality (correct ready/not ready decisions)
  - Context management (uses sub-conversations appropriately)
  - Error handling (handles missing data gracefully)
- Define expected behaviors for each scenario
- Create ground truth assessments

**Example Test Cases:**
```python
[
  {
    "id": "ready_for_production",
    "feature_id": "payment-gateway",
    "user_query": "Is payment-gateway ready for production?",
    "expected_tools": ["get_jira_data", "get_metrics", "list_docs", "read_doc"],
    "expected_decision": "ready",
    "expected_justification_includes": ["UAT pass rate", "all metrics green"],
    "expected_sub_conversations": True  # Should use for large docs
  },
  {
    "id": "not_ready_test_failures",
    "feature_id": "user-profile",
    "user_query": "Can we promote user-profile to production?",
    "expected_decision": "not_ready",
    "expected_justification_includes": ["test failures", "UAT"],
    "risk_level": "high"
  },
  {
    "id": "missing_feature_data",
    "feature_id": "nonexistent-feature",
    "expected_error_handling": True,
    "expected_message_includes": ["not found", "does not exist"]
  }
]
```

**Acceptance Criteria:**
- At least 8 test scenarios defined
- Scenarios cover ready, not ready, borderline cases
- Scenarios test error handling
- Scenarios test context management
- Ground truth defined for each scenario
- Test cases documented

### 6.2: Implement Evaluation Dimensions

**Tasks:**
- Implement feature identification evaluator
- Implement tool usage evaluator
- Implement decision quality evaluator
- Implement context management evaluator
- Implement error handling evaluator
- Each evaluator returns score and diagnostic info

**Evaluator Functions:**
```python
def eval_feature_identification(agent_output, expected):
    # Did agent identify correct feature?
    correct = agent_output.feature_id == expected.feature_id
    return {"score": 1.0 if correct else 0.0, "correct": correct}

def eval_tool_usage(agent_output, expected):
    # Did agent call right tools?
    tools_called = set(agent_output.tool_calls)
    tools_expected = set(expected.tools)
    recall = len(tools_called & tools_expected) / len(tools_expected)
    precision = len(tools_called & tools_expected) / len(tools_called)
    return {"score": (recall + precision) / 2, "recall": recall, "precision": precision}

def eval_decision_quality(agent_output, expected):
    # Was decision correct?
    decision_correct = agent_output.decision == expected.decision
    # Were key points mentioned in justification?
    justification_quality = check_justification_coverage(
        agent_output.justification,
        expected.key_points
    )
    return {
        "score": (decision_correct * 0.6 + justification_quality * 0.4),
        "decision_correct": decision_correct,
        "justification_quality": justification_quality
    }

def eval_context_management(agent_output, expected):
    # Did agent use sub-conversations appropriately?
    if expected.should_use_sub_conversations:
        used_sub_convs = len(agent_output.sub_conversations) > 0
        score = 1.0 if used_sub_convs else 0.5
    else:
        score = 1.0
    return {"score": score, "sub_conversations_used": len(agent_output.sub_conversations)}
```

**Acceptance Criteria:**
- Each evaluator implemented and tested
- Evaluators return scores between 0.0 and 1.0
- Evaluators include diagnostic information
- Evaluators handle edge cases gracefully
- Unit tests for each evaluator

### 6.3: Implement Evaluation Runner

**Tasks:**
- Create evaluation runner that:
  - Loads test scenarios
  - Runs agent for each scenario
  - Applies all evaluators
  - Collects results
  - Generates summary report
- Add command-line interface for running evals
- Save detailed results to JSON

**Evaluation Runner:**
```python
def run_evaluation(test_suite, agent):
    results = []
    for scenario in test_suite:
        # Run agent
        response = agent.send_message(scenario.user_query)

        # Extract observability data
        trace = get_trace(response.trace_id)

        # Apply evaluators
        scores = {
            "feature_id": eval_feature_identification(response, scenario),
            "tool_usage": eval_tool_usage(trace, scenario),
            "decision": eval_decision_quality(response, scenario),
            "context_mgmt": eval_context_management(trace, scenario),
            "error_handling": eval_error_handling(response, scenario)
        }

        # Aggregate
        overall_score = calculate_weighted_score(scores)
        results.append({
            "scenario": scenario.id,
            "scores": scores,
            "overall": overall_score,
            "passed": overall_score >= 0.7
        })

    return generate_report(results)
```

**Acceptance Criteria:**
- Evaluation runner executes all test scenarios
- Each scenario evaluated across all dimensions
- Results include per-scenario and overall scores
- Results saved to JSON file
- CLI command to run evaluations
- Detailed diagnostic output available

### 6.4: Implement Regression Tracking

**Tasks:**
- Save evaluation results as baseline
- Compare new results to baseline
- Identify regressions (>5% drop in any metric)
- Identify improvements (>5% gain in any metric)
- Generate comparison report

**Regression Tracking:**
```python
def save_baseline(results, version_id):
    # Save results as baseline for future comparison
    save_json(f"baselines/{version_id}.json", results)

def compare_to_baseline(current, baseline):
    comparison = {
        "regressions": [],
        "improvements": [],
        "stable": []
    }

    for scenario in current.scenarios:
        baseline_scenario = find_baseline_scenario(baseline, scenario.id)
        delta = scenario.overall_score - baseline_scenario.overall_score

        if delta < -0.05:
            comparison["regressions"].append({
                "scenario": scenario.id,
                "delta": delta,
                "current": scenario.overall_score,
                "baseline": baseline_scenario.overall_score
            })
        elif delta > 0.05:
            comparison["improvements"].append({...})
        else:
            comparison["stable"].append({...})

    return comparison
```

**Acceptance Criteria:**
- Can save evaluation results as baseline
- Can compare current results to baseline
- Regressions identified and reported
- Improvements identified and reported
- Comparison report includes all scenarios
- CLI supports baseline save and compare operations

### 6.5: Verify Evaluation System

**Tasks:**
- Run full evaluation suite
- Verify all scenarios execute
- Review pass/fail results
- Check for any obvious failures
- Iterate on agent or test cases as needed
- Establish initial baseline

**Acceptance Criteria:**
- Evaluation suite runs without errors
- At least 70% of scenarios pass
- Results are consistent across runs (accounting for LLM variance)
- Baseline established for future comparison
- Evaluation documentation complete
- CI/CD integration possible (if desired)

---

## Step 7: Final Integration and Polish

**Goal:** Ensure all components work together smoothly and the agent is ready for use.

### 7.1: End-to-End Testing

**Tasks:**
- Test complete workflow for each feature scenario
- Verify all tools work correctly
- Verify sub-conversations triggered appropriately
- Verify memory system works (if implemented)
- Verify observability captures everything
- Test error scenarios

**Test Scenarios:**
- Assess feature with complete data (all tools, large docs, memory)
- Assess feature with missing data (error handling)
- Assess multiple features in sequence (memory learning)
- Assess borderline feature (complex decision-making)

**Acceptance Criteria:**
- All features can be assessed successfully
- Sub-conversations used when appropriate
- Memory system functioning (if implemented)
- Error handling works gracefully
- Traces capture complete workflow
- Agent provides high-quality assessments

### 7.2: Performance Review

**Tasks:**
- Review token usage across typical assessments
- Review latency for complete assessments
- Review sub-conversation overhead
- Identify optimization opportunities
- Document performance characteristics

**Metrics to Review:**
- Average tokens per assessment
- Number of tool calls per assessment
- Number of sub-conversations per assessment
- End-to-end latency
- Cost per assessment (token usage × pricing)

**Acceptance Criteria:**
- Performance metrics documented
- No obvious performance problems
- Token usage within reasonable bounds
- Sub-conversations providing value (not overhead)

### 7.3: Documentation

**Tasks:**
- Document all tools and their usage
- Document sub-conversation behavior
- Document memory system (if implemented)
- Document evaluation system
- Create usage examples
- Document known limitations

**Acceptance Criteria:**
- README with agent overview
- Tool documentation complete
- Context management strategy documented
- Evaluation framework documented
- Usage examples provided
- Limitations clearly stated

### 7.4: Final Evaluation Run

**Tasks:**
- Run complete evaluation suite
- Compare to baseline
- Verify no regressions
- Document final results
- Celebrate completion!

**Acceptance Criteria:**
- All evaluations pass (>70% success rate)
- No regressions from baseline
- Results documented
- Agent ready for deployment

---

## Summary

The Investigator Agent builds on the Detective Agent foundation with these key additions:

1. **Feature Investigation Tools**: JIRA, metrics, and documentation access
2. **Advanced Context Management**: Sub-conversations for large data analysis
3. **Memory System**: Optional learning from past assessments
4. **Comprehensive Evaluations**: Multi-dimensional testing

The incremental approach ensures each capability is working before adding the next, with clear verification steps throughout.
