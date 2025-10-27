# Module 8 Project: Investigator Agent

**System Context:**

The Investigator Agent is part of the Release Confidence System team that helps build confidence in software releases by investigating changes, assessing risks, and producing actionable reports. This agent inspects the state of a feature and determines if it is sufficiently prepared to be promoted to the next stage of development. For example, from the Development environment to UAT, or from UAT to production.

Your task is to build the Investigator Agent. What follows is the agent's acceptance criteria. The agent can be built using any tools you like. We recommend building it from scratch at first using your favorite programming language and coding assistant, but you can also use a popular SDK, such as LangChain, PydanticAI, and CrewAI, or even a no-code solution such as n8n.

If you're following our recommendation, you'll find instructions for using `DESIGN.md` and `STEPS.md` after the acceptance criteria that will (hopefully) make things easier for you.

## Prerequisites

Before starting this module, you should have completed Module 7 (Detective Agent) with working implementations of:

- ✅ Basic conversation loop with LLM provider
- ✅ Provider abstraction (at least one provider working)
- ✅ Observability (traces and spans with OpenTelemetry)
- ✅ Context window management (basic truncation)
- ✅ Retry mechanism with exponential backoff
- ✅ System prompt engineering
- ✅ Tool abstraction and execution loop
- ✅ Evaluation framework

This module extends the Detective Agent with advanced context engineering capabilities to handle large information spaces.

## Acceptance Criteria

### Can identify features and retrieve metadata
**Acceptance Criteria:**
- JIRA tool retrieves metadata for ALL features (no parameters)
- Returns array with: folder, jira_key, feature_id, summary, status, data_quality
- Agent identifies which feature user is asking about from natural language query
- Agent extracts feature_id for subsequent tool calls
- Feature ID → folder mapping utility created
- Tool handles missing JIRA file gracefully with clear error messages
- Feature metadata visible in conversation and traces
- Automated tests verify tool behavior
- Manual CLI test demonstrates feature identification for all 4 features

### Can analyze features using analysis data
**Acceptance Criteria:**
- Analysis tool retrieves different types of analysis data (metrics + reviews):
  - metrics/performance_benchmarks: Performance benchmarks
  - metrics/pipeline_results: Pipeline run results
  - metrics/security_scan_results: Security scan results
  - metrics/test_coverage_report: Test coverage statistics
  - metrics/unit_test_results: Unit test results
  - reviews/security: Security review results
  - reviews/stakeholders: Stakeholder reviews
  - reviews/uat: UAT environment test results
- Agent uses feature ID → folder mapping for analysis queries
- Agent calls multiple analysis types during assessment
- Tool handles missing analysis files gracefully
- Analysis data incorporated into decision-making
- Automated tests verify all 8 analysis types
- Manual CLI test shows multi-analysis assessment

### Can review documentation
**Acceptance Criteria:**
- list_docs tool lists available documentation for a feature
- read_doc tool retrieves document contents
- Agent uses list_docs before read_doc
- Tools handle missing docs gracefully
- Large documents (>10KB) trigger special handling
- Documentation completeness factored into decisions
- Automated tests verify both doc tools
- Manual CLI test demonstrates doc review workflow

### Can manage context with sub-conversations (Phase 2 workflow)
**Acceptance Criteria:**
- Phase 2 tools (get_analysis, read_doc) execute in sub-conversations
- Sub-conversations created for each Phase 2 tool call
- Sub-conversations have isolated message history
- Specialized system prompts generated based on analysis purpose
- Summaries extracted from each sub-conversation
- Only summaries added to main conversation (not full sub-conv data)
- Main conversation stays under token limits (focused on Phase 1 and Phase 3)
- Sub-conversation spans visible in traces
- Token usage tracked separately for main and sub-conversations
- Compression ratio visible in observability
- Automated tests verify sub-conversation creation
- Manual test with multiple analysis calls shows context management working
- Agent follows three-phase workflow: identify → analyze in sub-convs → assess

### Can maintain memory (Optional)
**Memory System Acceptance Criteria:**
- Memory system selected and configured (Graffiti MCP, vector DB, or file-based)
- Agent stores feature assessments after completion
- Agent retrieves relevant past assessments before new assessment
- Memory includes: feature_id, decision, justification, key_metrics, timestamp
- Memory operations visible in traces
- Agent gracefully handles memory system unavailability
- Automated tests verify memory storage and retrieval
- Manual test shows agent learning from past assessments

**Note:** Memory is optional. Students can choose their implementation approach or skip this feature.

### Can be comprehensively evaluated
**Evaluation Dimensions:**
1. Feature Identification Evaluation
2. Tool Usage Evaluation
3. Decision Quality Evaluation
4. Context Management Evaluation
5. Error Handling Evaluation
6. Regression Tracking

**Evaluation Acceptance Criteria:**
- Eval framework runs test scenarios automatically
- At least 8 test scenarios covering:
  - Ready for promotion (all metrics green)
  - Not ready (clear failures)
  - Borderline cases (judgment required)
  - Error handling (missing data, bad files)
  - Context management (large docs)
- Feature identification evaluated for correctness
- Tool usage evaluated for correctness and ordering
- Decision quality measured against expected outcomes
- Context management verified (sub-conversations used appropriately)
- Error handling scenarios validate robustness
- Regression tracking compares to baseline
- Structured JSON reports generated for automation
- Eval results include pass/fail and diagnostic details
- At least 70% of scenarios pass
- Automated tests verify eval framework itself
- Documentation explains how to add new eval cases
- CLI supports baseline establishment and comparison

### Observability (Enhanced from Module 7)
**Additional Observability Acceptance Criteria:**
- Sub-conversation spans captured in traces
- Sub-conversation spans nested under parent conversation
- Token usage tracked separately for sub-conversations
- Compression ratio (original vs summary) captured
- Memory operations traced (if memory implemented)
- All new tools (JIRA, metrics, docs) traced with timing
- Trace files show complete workflow including sub-conversations
- Can correlate sub-conversations to parent via trace IDs

### Context Window Management (Enhanced from Module 7)
**Additional Context Window Acceptance Criteria:**
- Sub-conversation pattern implemented
- Summaries preserve critical information
- Main conversation token count stays under 90% of limit
- Can process multiple large documents without context errors
- Sub-conversation overhead tracked in metrics

### Has clear purpose and behavior
**Prompt Engineering Acceptance Criteria:**
- System prompt defines Investigator Agent role
- System prompt explains feature readiness assessment task
- System prompt describes all available tools and when to use them
- System prompt includes decision criteria (test thresholds, required docs, etc.)
- System prompt explains sub-conversation behavior
- Agent behavior reflects system prompt instructions
- Tested with various features and scenarios

## Building an agent from scratch (with help)

This process has 2 main parts:
1. Create the implementation plan
2. Iteratively follow the steps in the plan

Everything you and your assistant need to know to implement the Investigator Agent is in `DESIGN.md`. We also recommend a specific order when adding features to your agent. Inside `STEPS.md` you'll find an order of implementation that mirrors the acceptance criteria above and builds incrementally on your Module 7 Detective Agent.

We've also provided `PLAN.md` which is an example starter file that a Python developer might use. Feel free to edit this file according to your preferences and language choice. Once you're happy with it, you're ready to begin.

## Test Data

**Important:** The test data is already provided in the `incoming_data/` directory. You do NOT need to create it.

The test data includes **4 features** with different readiness scenarios:

| Feature | Complexity | Stage | Readiness | Description |
|---------|-----------|-------|-----------|-------------|
| **Maintenance Scheduling & Alert System** | Medium | Production-Ready | ✅ READY | Clear success case - all gates passed, complete docs, green metrics |
| **QR Code Check-in/out with Mobile App** | High | Development/UAT | ❌ NOT READY | Multiple blockers - clear failures in testing and implementation |
| **Advanced Resource Reservation System** | High | UAT | 🔄 AMBIGUOUS | Mixed signals - incomplete data, requires judgment |
| **Contribution Tracking & Community Credits** | Medium-High | UAT | 🔄 PARTIAL | Right stage but not ready for next - some gaps remain |

Each feature in `incoming_data/featureN/` includes:
- `jira/`: JIRA metadata (feature_issue.json, issue_changelog.json)
- `metrics/`: 5 different JSON metric files
  - performance_benchmarks.json
  - pipeline_results.json
  - security_scan_results.json
  - test_coverage_report.json
  - unit_test_results.json
- `reviews/`: 3 different JSON review files
  - security.json
  - stakeholders.json
  - uat.json
- `planning/`: Multiple markdown documentation files (10+ files per feature)
  - ARCHITECTURE.md (large, >10KB)
  - DESIGN_DOC.md (large, >10KB)
  - DATABASE_SCHEMA.md (large)
  - DEPLOYMENT_PLAN.md, TEST_STRATEGY.md, USER_STORIES.md, etc.

**Total data size:** Approximately 1+ MB across all features

The data is realistic and specifically designed to challenge the agent's decision-making and context management capabilities.

## Steps

### Step 0: Verify Detective Agent Foundation

Before starting, ensure your Module 7 Detective Agent is working:

```bash
# Run existing tests
pytest

# Test basic conversation
python cli.py

# Verify traces are being generated
ls traces/
```

All Module 7 functionality should work before proceeding.

### Step 1: Create the implementation plan

The first step is to create the plan you're going to use going forward. Here is an example prompt you can use to create it. Feel free to modify it before using it.

```
Read @PLAN.md and follow your additional instructions inside it. I would like to use OpenRouter as the first provider. For the context window management strategy, I would like to use the sub-conversation pattern as described in the design doc.
```

Review the plan it created:
- Are the tasks broken down to sufficient detail to avoid overwhelm during implementation?
- Does it follow the same STEPS order?
- Did it add or remove any sections?
- Briefly look over the code - anything unusual?

You may need to collaborate with your assistant to get the planning doc where you're happy with it.

### Step 2: Iterate over the steps in the plan

This is where you get to decide how much you want to bite off at a time. Hopefully the plan is already broken down well enough. When you're considering the next piece of work, if it doesn't have enough detail, or if it needs to be broken down further, work with your assistant to update PLAN.md until you're happy with what you know it's going to build, or happy enough with the mystery ;)

Here is an example prompt that is a good one to start each step with. Sometimes it may be enough for your assistant to finish it, sometimes it will require some back and forth. Start over if it's too far off at the beginning.

#### Remember to: START EACH STEP WITH A NEW ASSISTANT SESSION

```
Please complete step 1.1 in @PLAN.md. Refer to the appropriate section in @DESIGN.md to ensure you're meeting all of the acceptance criteria.
```

Don't be satisfied with all green on your test run. Test it manually. Make sure you can see what you expect to see in the traces (responses, errors, tool calls, sub-conversations, context compression, memory operations, etc). Have your assistant create CLI interfaces so you can _verify_ everything is actually working.

#### Remember to: STAGE/COMMIT THE WORKING TREE

After each major step, commit your working code:

```bash
git add .
git commit -m "Step X.Y: [description]"
```

This gives you safe rollback points if needed.

### Step-by-Step Workflow

The recommended progression (detailed in `STEPS.md`):

1. **Step 1: Add JIRA Tool**
   - Create test data structure
   - Implement get_jira_data tool
   - Update system prompt
   - Verify end-to-end

2. **Step 2: Add Analysis Tool**
   - Understand analysis test data (8 types: 5 metrics + 3 reviews)
   - Implement get_analysis tool
   - Update system prompt with Phase 2 guidance
   - Verify multi-analysis assessment

3. **Step 3: Add Documentation Tools**
   - Understand documentation test data (planning/ folders)
   - Implement list_docs tool (scans planning/ directory)
   - Implement read_doc tool (reads markdown files)
   - Update system prompt
   - Observe context window pressure (motivates Step 4)

4. **Step 4: Add Sub-Conversation Context Management**
   - Design SubConversation data model
   - Implement sub-conversation manager
   - Integrate into agent core
   - Update observability for sub-conversations
   - Verify context management with large docs

5. **Step 5: Add Memory System (Optional)**
   - Choose memory approach
   - Design memory schema
   - Implement memory operations
   - Integrate into agent workflow
   - Verify memory learning

6. **Step 6: Add Evaluation System**
   - Design evaluation test cases
   - Implement evaluation dimensions
   - Implement evaluation runner
   - Implement regression tracking
   - Verify evaluation system

7. **Step 7: Final Integration and Polish**
   - End-to-end testing
   - Performance review
   - Documentation
   - Final evaluation run

### Verification Guidelines

For each step:

- ✅ **Run automated tests** - Ensure code quality
- ✅ **Run manual CLI tests** - Verify actual behavior
- ✅ **Check traces** - Ensure observability is capturing everything
- ✅ **Verify tokens** - Ensure context management is working
- ✅ **Test edge cases** - Missing data, errors, large files

Don't move to the next step until the current step is fully working.

### When You're Done

Repeat until Investigator Agent is ready for duty:

> _All of the acceptance criteria are met_

The agent should be able to:
- Accept natural language queries about feature readiness
- Identify the feature and gather all relevant data (JIRA, metrics, docs)
- Manage context effectively using sub-conversations for large content
- Make sound decisions with clear justifications
- Remember past assessments (if memory implemented)
- Pass comprehensive evaluations (>70% success rate)

:)

## Tips for Success

1. **Build incrementally** - Each step adds one capability
2. **Verify thoroughly** - Don't skip manual testing
3. **Watch your tokens** - Context management is critical here
4. **Use traces** - They show what's really happening
5. **Commit often** - Safe rollback points are invaluable
6. **Test with real scenarios** - The test data should challenge the agent

## Key Learnings from This Module

By completing this exercise, you'll learn:

- **Context Engineering**: How to manage large information spaces without exhausting context windows
- **Sub-Conversation Patterns**: A critical technique for complex agent workflows
- **Information Synthesis**: How agents can analyze multiple data sources and make decisions
- **Memory Integration**: How to give agents long-term memory (optional)
- **Comprehensive Evaluation**: How to test agents across multiple dimensions
- **Real-world Agent Design**: Practical patterns for production agent systems

Good luck!
