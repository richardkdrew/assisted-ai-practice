# Test Coverage Improvement Tasks

**Generated**: 2025-10-22
**Current Coverage**: 75% (1361 statements, 341 missing)
**Target Coverage**: 85-90%
**Effort Estimate**: 17-23 hours

---

## Task Breakdown

### Priority 1: Critical Blockers (5-7 hours)

#### Task 1.1: Evaluation System Tests
**Module**: `src/investigator_agent/evaluations/`
**Current Coverage**: 0% (207 lines untested)
**Target Coverage**: 80%
**Effort**: 4-6 hours
**Tests to Add**: 25-30

**Test File**: `src/investigator_agent/evaluations/evaluator_test.py`

```python
"""Tests for InvestigatorEvaluator."""
import pytest
from investigator_agent.evaluations.evaluator import InvestigatorEvaluator
from investigator_agent.evaluations.scenarios import get_scenarios

class TestInvestigatorEvaluator:
    """Test evaluation system."""

    def test_evaluate_scenario_feature_identification_correct(self):
        """Test feature identification with correct match."""
        scenario = {
            "name": "test",
            "expected_feature_id": "FEAT-MS-001",
            "expected_tools": ["get_jira_data"],
            "expected_decision": "ready"
        }

        result = {
            "identified_feature_id": "FEAT-MS-001",
            "tool_calls": ["get_jira_data", "get_analysis"],
            "decision": "ready",
            "justification": "all tests passing"
        }

        evaluator = InvestigatorEvaluator()
        scores = evaluator._evaluate_scenario(scenario, result)

        assert scores["feature_identification"] == 1.0
        assert "feature_id" in scores["details"]

    def test_evaluate_scenario_feature_identification_incorrect(self):
        """Test feature identification with wrong feature."""
        scenario = {
            "expected_feature_id": "FEAT-MS-001",
            # ... other fields
        }
        result = {"identified_feature_id": "FEAT-QR-002"}

        evaluator = InvestigatorEvaluator()
        scores = evaluator._evaluate_scenario(scenario, result)

        assert scores["feature_identification"] == 0.0

    def test_evaluate_scenario_tool_usage_perfect_match(self):
        """Test tool usage F1 score with perfect match."""
        scenario = {
            "expected_tools": ["get_jira_data", "get_analysis", "read_doc"]
        }
        result = {
            "tool_calls": ["get_jira_data", "get_analysis", "read_doc"]
        }

        evaluator = InvestigatorEvaluator()
        scores = evaluator._evaluate_scenario(scenario, result)

        # F1 score should be 1.0 (precision=1.0, recall=1.0)
        assert scores["tool_usage"] == 1.0
        assert scores["details"]["tool_usage"]["precision"] == 1.0
        assert scores["details"]["tool_usage"]["recall"] == 1.0

    def test_evaluate_scenario_tool_usage_missing_tool(self):
        """Test tool usage F1 score with missing expected tool."""
        scenario = {
            "expected_tools": ["get_jira_data", "get_analysis"]
        }
        result = {
            "tool_calls": ["get_jira_data"]  # Missing get_analysis
        }

        evaluator = InvestigatorEvaluator()
        scores = evaluator._evaluate_scenario(scenario, result)

        # Precision = 1/1 = 1.0, Recall = 1/2 = 0.5, F1 = 2*1*0.5/(1+0.5) = 0.67
        assert 0.66 < scores["tool_usage"] < 0.68

    def test_evaluate_scenario_tool_usage_extra_tool(self):
        """Test tool usage F1 score with unexpected tool."""
        scenario = {
            "expected_tools": ["get_jira_data"]
        }
        result = {
            "tool_calls": ["get_jira_data", "list_docs"]  # Extra tool
        }

        evaluator = InvestigatorEvaluator()
        scores = evaluator._evaluate_scenario(scenario, result)

        # Precision = 1/2 = 0.5, Recall = 1/1 = 1.0, F1 = 2*0.5*1/(0.5+1) = 0.67
        assert 0.66 < scores["tool_usage"] < 0.68

    def test_evaluate_scenario_decision_quality_exact_match(self):
        """Test decision quality with exact match and keywords."""
        scenario = {
            "expected_decision": "ready",
            "justification_keywords": ["tests", "passing", "approved"]
        }
        result = {
            "decision": "ready",
            "justification": "All tests are passing and stakeholders approved"
        }

        evaluator = InvestigatorEvaluator()
        scores = evaluator._evaluate_scenario(scenario, result)

        # Exact match (0.5) + 3 keywords found (3 * 0.1) = 0.8
        assert scores["decision_quality"] >= 0.8

    def test_evaluate_scenario_decision_quality_partial_credit(self):
        """Test decision quality with adjacent decision (partial credit)."""
        scenario = {
            "expected_decision": "ready",
            "justification_keywords": []
        }
        result = {
            "decision": "borderline",  # Adjacent to "ready"
            "justification": ""
        }

        evaluator = InvestigatorEvaluator()
        scores = evaluator._evaluate_scenario(scenario, result)

        # Adjacent decision gets 0.3 partial credit
        assert scores["decision_quality"] == 0.3

    def test_evaluate_scenario_decision_quality_wrong_decision(self):
        """Test decision quality with completely wrong decision."""
        scenario = {
            "expected_decision": "ready",
            "justification_keywords": []
        }
        result = {
            "decision": "not_ready",  # Not adjacent
            "justification": ""
        }

        evaluator = InvestigatorEvaluator()
        scores = evaluator._evaluate_scenario(scenario, result)

        assert scores["decision_quality"] == 0.0

    def test_evaluate_scenario_context_management_used(self):
        """Test context management with sub-conversation usage."""
        scenario = {
            "expect_subconversation": True
        }
        result = {
            "used_subconversation": True
        }

        evaluator = InvestigatorEvaluator()
        scores = evaluator._evaluate_scenario(scenario, result)

        assert scores["context_management"] == 1.0

    def test_evaluate_scenario_context_management_not_used(self):
        """Test context management when not expected."""
        scenario = {
            "expect_subconversation": False
        }
        result = {
            "used_subconversation": False
        }

        evaluator = InvestigatorEvaluator()
        scores = evaluator._evaluate_scenario(scenario, result)

        assert scores["context_management"] == 1.0

    def test_evaluate_scenario_overall_score_calculation(self):
        """Test overall score is weighted average."""
        scenario = {
            "expected_feature_id": "FEAT-MS-001",
            "expected_tools": ["get_jira_data"],
            "expected_decision": "ready",
            "expect_subconversation": False
        }
        result = {
            "identified_feature_id": "FEAT-MS-001",  # 1.0
            "tool_calls": ["get_jira_data"],          # 1.0
            "decision": "ready",                      # 0.5 base
            "justification": "tests passing",         # +0.1
            "used_subconversation": False             # 1.0
        }

        evaluator = InvestigatorEvaluator()
        scores = evaluator._evaluate_scenario(scenario, result)

        # Overall = 0.2*1.0 + 0.3*1.0 + 0.4*0.6 + 0.1*1.0 = 0.84
        assert 0.83 < scores["overall"] < 0.85

    @pytest.mark.asyncio
    async def test_run_evaluation_suite_all_scenarios(self):
        """Test running all 8 scenarios."""
        evaluator = InvestigatorEvaluator()

        # Mock agent for testing
        class MockAgent:
            async def run_scenario(self, scenario):
                return {
                    "identified_feature_id": scenario["expected_feature_id"],
                    "tool_calls": scenario["expected_tools"],
                    "decision": scenario["expected_decision"],
                    "justification": "mock justification",
                    "used_subconversation": scenario.get("expect_subconversation", False)
                }

        results = await evaluator.run_evaluation_suite(MockAgent())

        assert len(results["scenarios"]) == 8
        assert results["summary"]["total"] == 8
        assert results["summary"]["pass_rate"] >= 0.9  # Should pass with perfect mock

    def test_compare_to_baseline_no_regression(self):
        """Test comparison when no regression detected."""
        current = {
            "summary": {
                "average_scores": {
                    "overall": 0.75,
                    "feature_identification": 0.85
                }
            }
        }
        baseline = {
            "summary": {
                "average_scores": {
                    "overall": 0.73,
                    "feature_identification": 0.83
                }
            }
        }

        evaluator = InvestigatorEvaluator()
        comparison = evaluator.compare_to_baseline(current, baseline)

        assert not comparison["has_regression"]
        assert comparison["deltas"]["overall"] > 0

    def test_compare_to_baseline_regression_detected(self):
        """Test comparison when regression detected (>5% drop)."""
        current = {
            "summary": {
                "average_scores": {"overall": 0.65}
            }
        }
        baseline = {
            "summary": {
                "average_scores": {"overall": 0.75}
            }
        }

        evaluator = InvestigatorEvaluator()
        comparison = evaluator.compare_to_baseline(current, baseline)

        assert comparison["has_regression"]
        assert "overall" in comparison["regressions"]
        assert comparison["deltas"]["overall"] < -0.05

    def test_compare_to_baseline_improvement_detected(self):
        """Test comparison when improvement detected (>5% gain)."""
        current = {
            "summary": {
                "average_scores": {"overall": 0.85}
            }
        }
        baseline = {
            "summary": {
                "average_scores": {"overall": 0.75}
            }
        }

        evaluator = InvestigatorEvaluator()
        comparison = evaluator.compare_to_baseline(current, baseline)

        assert not comparison["has_regression"]
        assert "overall" in comparison["improvements"]
        assert comparison["deltas"]["overall"] > 0.05

    def test_save_baseline(self, tmp_path):
        """Test saving baseline to file."""
        results = {
            "summary": {
                "average_scores": {"overall": 0.75}
            }
        }

        evaluator = InvestigatorEvaluator()
        baseline_file = tmp_path / "baseline.json"
        evaluator.save_baseline(results, str(baseline_file))

        assert baseline_file.exists()
        loaded = evaluator.load_baseline(str(baseline_file))
        assert loaded["summary"]["average_scores"]["overall"] == 0.75

    def test_load_baseline_not_found(self):
        """Test loading non-existent baseline returns None."""
        evaluator = InvestigatorEvaluator()
        loaded = evaluator.load_baseline("nonexistent.json")

        assert loaded is None

    # Edge cases
    def test_evaluate_scenario_empty_tool_lists(self):
        """Test evaluation with empty tool lists."""
        scenario = {"expected_tools": []}
        result = {"tool_calls": []}

        evaluator = InvestigatorEvaluator()
        scores = evaluator._evaluate_scenario(scenario, result)

        # F1 undefined when both are empty, should default to 1.0
        assert scores["tool_usage"] == 1.0

    def test_evaluate_scenario_missing_fields(self):
        """Test evaluation with missing result fields."""
        scenario = {
            "expected_feature_id": "FEAT-MS-001",
            "expected_tools": [],
            "expected_decision": "ready"
        }
        result = {}  # Missing all fields

        evaluator = InvestigatorEvaluator()
        scores = evaluator._evaluate_scenario(scenario, result)

        # Should handle gracefully with 0 scores
        assert scores["feature_identification"] == 0.0
        assert scores["decision_quality"] == 0.0

    def test_evaluate_scenario_case_insensitive_decision(self):
        """Test decision matching is case-insensitive."""
        scenario = {"expected_decision": "ready"}
        result = {"decision": "READY", "justification": ""}

        evaluator = InvestigatorEvaluator()
        scores = evaluator._evaluate_scenario(scenario, result)

        assert scores["decision_quality"] >= 0.5  # Exact match score

    def test_f1_score_calculation_edge_cases(self):
        """Test F1 score calculation edge cases."""
        evaluator = InvestigatorEvaluator()

        # Perfect match
        f1 = evaluator._calculate_f1(["a", "b"], ["a", "b"])
        assert f1 == 1.0

        # No overlap
        f1 = evaluator._calculate_f1(["a"], ["b"])
        assert f1 == 0.0

        # Partial overlap
        f1 = evaluator._calculate_f1(["a", "b"], ["a", "c"])
        # Precision = 1/2, Recall = 1/2, F1 = 0.5
        assert 0.49 < f1 < 0.51

    # Integration test
    @pytest.mark.asyncio
    async def test_full_evaluation_workflow(self, tmp_path):
        """Test complete evaluation workflow."""
        evaluator = InvestigatorEvaluator()

        # Run evaluation
        class MockAgent:
            async def run_scenario(self, scenario):
                return {
                    "identified_feature_id": scenario["expected_feature_id"],
                    "tool_calls": scenario["expected_tools"],
                    "decision": scenario["expected_decision"],
                    "justification": "mock",
                    "used_subconversation": False
                }

        results = await evaluator.run_evaluation_suite(MockAgent())

        # Save baseline
        baseline_file = tmp_path / "v1.json"
        evaluator.save_baseline(results, str(baseline_file))

        # Load and compare
        baseline = evaluator.load_baseline(str(baseline_file))
        comparison = evaluator.compare_to_baseline(results, baseline)

        assert comparison["deltas"]["overall"] == 0.0  # Identical
        assert not comparison["has_regression"]
```

**Acceptance Criteria**:
- [ ] All 25-30 tests passing
- [ ] Coverage on evaluator.py >= 80%
- [ ] Coverage on scenarios.py >= 50% (data-heavy module)
- [ ] CI passing

---

#### Task 1.2: Fix Flaky Retry Test
**Module**: `tests/retry_test.py`
**Current Issue**: Timing-based assertion too strict
**Effort**: 30 minutes - 1 hour

**Fix Option A: Widen Tolerance** (Recommended)

```python
def test_jitter_adds_randomness(self):
    """Test that jitter adds randomness to retry delays."""
    delays = []
    for _ in range(5):
        call_times = []

        async def failing_operation():
            call_times.append(asyncio.get_event_loop().time())
            response = httpx.Response(500, request=httpx.Request("GET", "http://test.com"))
            raise httpx.HTTPStatusError("", request=response.request, response=response)

        config = RetryConfig(max_attempts=2, initial_delay=0.1, backoff_factor=1.0, jitter=True)

        with pytest.raises(httpx.HTTPStatusError):
            await with_retry(failing_operation, config, "test_operation")

        if len(call_times) >= 2:
            delays.append(call_times[1] - call_times[0])

    # OLD: assert all(0.04 < d < 0.16 for d in delays)
    # NEW: Widen tolerance to account for system variability
    assert all(0.03 < d < 0.20 for d in delays), f"Delays out of range: {delays}"
    assert len(set(delays)) > 1, "Delays should vary due to jitter"
```

**Fix Option B: Mock Time** (More Complex)

```python
def test_jitter_adds_randomness_mocked(self):
    """Test jitter with mocked time."""
    import random
    from unittest.mock import patch

    with patch('investigator_agent.retry.strategy.random.uniform') as mock_uniform:
        # Mock uniform to return predictable but varying values
        mock_uniform.side_effect = [0.95, 1.05, 0.92, 1.08, 0.97]

        # ... rest of test
```

**Recommendation**: Use Option A (simpler, more robust)

**Acceptance Criteria**:
- [ ] Test passes 100 consecutive times locally
- [ ] Test passes in CI without flakes
- [ ] Assertions still validate jitter behavior

---

### Priority 2: High-Value Tests (7-9 hours)

#### Task 2.1: Agent Memory Integration Tests
**Module**: `src/investigator_agent/agent.py`
**Lines**: Lines 178-208, 222-223, 255-286
**Current Coverage**: 0% (30 lines untested)
**Target Coverage**: 90%
**Effort**: 3-4 hours
**Tests to Add**: 10-12

**Test File**: Expand `src/investigator_agent/agent_test.py`

```python
@pytest.mark.asyncio
async def test_send_message_with_memory_retrieval(mock_provider, temp_store):
    """Test that agent retrieves relevant memories during conversation."""
    # Setup agent with memory store
    memory_store = FileMemoryStore(Path("test_memory"))

    # Pre-populate memory
    memory = Memory(
        id="mem_1",
        feature_id="FEAT-MS-001",
        decision="ready",
        justification="All tests passing",
        key_findings={"test_coverage": "95%"},
        timestamp=datetime.now()
    )
    memory_store.store(memory)

    agent = Agent(
        provider=mock_provider,
        store=temp_store,
        config=Config(),
        memory_store=memory_store
    )

    # Mock provider to check if memory context is included
    mock_provider.send_message = AsyncMock(return_value=ChatResponse(
        id="resp_1",
        content=[TextContent(text="Based on past assessments...")],
        model="test",
        stop_reason="end_turn",
        usage=Usage(input_tokens=10, output_tokens=20)
    ))

    conversation = agent.new_conversation()
    await agent.send_message(conversation, "Is FEAT-MS-001 ready?")

    # Verify memory was retrieved and added to conversation
    call_args = mock_provider.send_message.call_args
    messages = call_args[0][0]

    # Should have memory context in messages
    memory_context_found = any("past assessments" in str(msg) for msg in messages)
    assert memory_context_found

@pytest.mark.asyncio
async def test_retrieve_relevant_memories_formats_context(mock_provider, temp_store):
    """Test that memory context is properly formatted for LLM."""
    memory_store = FileMemoryStore(Path("test_memory"))

    memory = Memory(
        id="mem_1",
        feature_id="FEAT-MS-001",
        decision="ready",
        justification="Tests pass",
        key_findings={"coverage": "95%"},
        timestamp=datetime(2025, 1, 1, 12, 0, 0)
    )
    memory_store.store(memory)

    agent = Agent(
        provider=mock_provider,
        store=temp_store,
        config=Config(),
        memory_store=memory_store
    )

    # Retrieve memories
    context = await agent.retrieve_relevant_memories("FEAT-MS-001")

    # Verify formatting
    assert "Feature ID: FEAT-MS-001" in context
    assert "Decision: ready" in context
    assert "Justification: Tests pass" in context
    assert "2025-01-01" in context  # Timestamp formatted

@pytest.mark.asyncio
async def test_memory_retrieval_error_graceful_degradation(mock_provider, temp_store):
    """Test agent continues when memory retrieval fails."""
    # Setup memory store that raises errors
    class FailingMemoryStore:
        def retrieve(self, **kwargs):
            raise RuntimeError("Database connection failed")

    agent = Agent(
        provider=mock_provider,
        store=temp_store,
        config=Config(),
        memory_store=FailingMemoryStore()
    )

    mock_provider.send_message = AsyncMock(return_value=ChatResponse(
        id="resp_1",
        content=[TextContent(text="Response without memory")],
        model="test",
        stop_reason="end_turn",
        usage=Usage(input_tokens=10, output_tokens=20)
    ))

    conversation = agent.new_conversation()

    # Should not raise, should continue without memory
    response = await agent.send_message(conversation, "test message")
    assert response is not None
    assert mock_provider.send_message.called

@pytest.mark.asyncio
async def test_agent_without_memory_store(mock_provider, temp_store):
    """Test agent works normally when memory_store=None."""
    agent = Agent(
        provider=mock_provider,
        store=temp_store,
        config=Config(),
        memory_store=None  # No memory
    )

    mock_provider.send_message = AsyncMock(return_value=ChatResponse(
        id="resp_1",
        content=[TextContent(text="Response")],
        model="test",
        stop_reason="end_turn",
        usage=Usage(input_tokens=10, output_tokens=20)
    ))

    conversation = agent.new_conversation()
    response = await agent.send_message(conversation, "test")

    assert response is not None
    # No memory retrieval should occur
    assert mock_provider.send_message.call_count == 1

# ... 6-8 more tests for:
# - Multiple memory results
# - Memory limit parameter
# - Memory query empty results
# - Memory context token limits
# - Memory retrieval with observability
```

**Acceptance Criteria**:
- [ ] 10-12 tests passing
- [ ] Coverage on lines 178-208, 222-223, 255-286 >= 90%
- [ ] All error paths tested
- [ ] Observability verified

---

#### Task 2.2: MCP Store TODO Completion
**Module**: `src/investigator_agent/memory/mcp_store.py`
**Lines**: 20 TODOs + untested error paths
**Current Coverage**: 83% (20 lines missing)
**Target Coverage**: 95%
**Effort**: 4-5 hours
**Code Changes**: Complete 4 TODOs
**Tests to Add**: 10

**Code Changes**:

```python
# src/investigator_agent/memory/mcp_store.py

# TODO 1: Parse ChromaDB response (line 189)
async def retrieve(self, query: str | None = None, ...) -> list[Memory]:
    # ... existing code ...

    # Parse results and reconstruct Memory objects
    if query:
        # Semantic search result parsing
        response_data = json.loads(result_json)
        memories = []

        for doc, metadata in zip(response_data["documents"][0], response_data["metadatas"][0]):
            memory = Memory(
                id=metadata["memory_id"],
                feature_id=metadata["feature_id"],
                decision=metadata["decision"],
                justification=self._extract_justification(doc),
                key_findings=self._extract_key_findings(doc),
                timestamp=datetime.fromisoformat(metadata["timestamp"]),
                metadata=metadata
            )
            memories.append(memory)

        return memories
    else:
        # Get documents result parsing
        # ... similar parsing

def _extract_justification(self, document_text: str) -> str:
    """Extract justification from document text."""
    lines = document_text.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("Justification:"):
            return lines[i+1].strip()
    return ""

def _extract_key_findings(self, document_text: str) -> dict[str, Any]:
    """Extract key findings from document text."""
    # Find Key Findings section and parse JSON
    start_idx = document_text.find("Key Findings:")
    if start_idx == -1:
        return {}

    json_start = document_text.find("{", start_idx)
    json_end = document_text.rfind("}")

    if json_start != -1 and json_end != -1:
        try:
            return json.loads(document_text[json_start:json_end+1])
        except json.JSONDecodeError:
            return {}
    return {}

# TODO 2: Parse retrieve_by_id result (line 217)
async def retrieve_by_id(self, memory_id: str) -> Memory | None:
    # ... existing code ...

    response_data = json.loads(result_json)
    if not response_data["ids"]:
        return None

    # Similar parsing as retrieve()
    doc = response_data["documents"][0]
    metadata = response_data["metadatas"][0]

    return Memory(
        id=metadata["memory_id"],
        feature_id=metadata["feature_id"],
        decision=metadata["decision"],
        justification=self._extract_justification(doc),
        key_findings=self._extract_key_findings(doc),
        timestamp=datetime.fromisoformat(metadata["timestamp"]),
        metadata=metadata
    )

# TODO 3: Parse Graphiti results (line 393)
async def retrieve(self, query: str | None = None, ...) -> list[Memory]:
    # ... existing code ...

    response_data = json.loads(result_json)
    memories = []

    for episode in response_data.get("episodes", []):
        # Extract memory info from episode metadata
        metadata = episode.get("metadata", {})

        memory = Memory(
            id=metadata.get("memory_id", episode["uuid"]),
            feature_id=metadata.get("feature_id", ""),
            decision=metadata.get("decision", ""),
            justification=episode.get("content", ""),
            key_findings={},  # Could parse from content
            timestamp=datetime.fromisoformat(episode["created_at"]),
            metadata=metadata
        )
        memories.append(memory)

    return memories

# TODO 4: Implement clear_all for Graphiti (line 447)
async def clear_all(self) -> bool:
    """Clear all memories from the graph."""
    try:
        await self.mcp_client.call_tool("graphiti_clear_graph", {})
        logger.info("Cleared all memories from Graphiti")
        return True
    except Exception as e:
        logger.error(f"Failed to clear memories: {e}", exc_info=True)
        return False
```

**Tests**:

```python
# src/investigator_agent/memory/mcp_store_test.py

@pytest.mark.asyncio
async def test_chroma_retrieve_parses_response_correctly():
    """Test ChromaDB response parsing."""
    mock_client = AsyncMock()
    mock_client.call_tool = AsyncMock(return_value=json.dumps({
        "documents": [[
            "Feature: FEAT-001\nDecision: ready\nJustification: Tests pass\n\nKey Findings:\n{\"coverage\": \"95%\"}"
        ]],
        "metadatas": [[
            {
                "memory_id": "mem_1",
                "feature_id": "FEAT-001",
                "decision": "ready",
                "timestamp": "2025-01-01T12:00:00"
            }
        ]],
        "distances": [[0.1]]
    }))

    store = MCPChromaMemoryStore(mock_client)
    store._initialized = True

    memories = await store.retrieve(query="test", limit=5)

    assert len(memories) == 1
    assert memories[0].id == "mem_1"
    assert memories[0].feature_id == "FEAT-001"
    assert memories[0].decision == "ready"
    assert memories[0].key_findings["coverage"] == "95%"

@pytest.mark.asyncio
async def test_chroma_retrieve_handles_network_error():
    """Test network error handling."""
    mock_client = AsyncMock()
    mock_client.call_tool = AsyncMock(side_effect=Exception("Connection refused"))

    store = MCPChromaMemoryStore(mock_client)
    store._initialized = True

    memories = await store.retrieve(query="test")

    # Should return empty list on error
    assert memories == []

@pytest.mark.asyncio
async def test_chroma_retrieve_by_id_parses_response():
    """Test retrieve_by_id response parsing."""
    mock_client = AsyncMock()
    mock_client.call_tool = AsyncMock(return_value=json.dumps({
        "ids": ["mem_1"],
        "documents": ["Feature: FEAT-001\nDecision: ready"],
        "metadatas": [{
            "memory_id": "mem_1",
            "feature_id": "FEAT-001",
            "decision": "ready",
            "timestamp": "2025-01-01T12:00:00"
        }]
    }))

    store = MCPChromaMemoryStore(mock_client)
    store._initialized = True

    memory = await store.retrieve_by_id("mem_1")

    assert memory is not None
    assert memory.id == "mem_1"

@pytest.mark.asyncio
async def test_graphiti_retrieve_parses_episodes():
    """Test Graphiti episode parsing."""
    mock_client = AsyncMock()
    mock_client.call_tool = AsyncMock(return_value=json.dumps({
        "episodes": [
            {
                "uuid": "ep_1",
                "content": "Feature assessment for FEAT-001",
                "created_at": "2025-01-01T12:00:00",
                "metadata": {
                    "memory_id": "mem_1",
                    "feature_id": "FEAT-001",
                    "decision": "ready"
                }
            }
        ]
    }))

    store = MCPGraphitiMemoryStore(mock_client)

    memories = await store.retrieve(query="test")

    assert len(memories) == 1
    assert memories[0].id == "mem_1"
    assert memories[0].feature_id == "FEAT-001"

@pytest.mark.asyncio
async def test_graphiti_clear_all():
    """Test clear_all implementation."""
    mock_client = AsyncMock()
    mock_client.call_tool = AsyncMock(return_value="Cleared")

    store = MCPGraphitiMemoryStore(mock_client)

    result = await store.clear_all()

    assert result is True
    mock_client.call_tool.assert_called_once_with("graphiti_clear_graph", {})

# ... 5 more tests for edge cases
```

**Acceptance Criteria**:
- [ ] All 4 TODOs completed
- [ ] 10 new tests passing
- [ ] Coverage on mcp_store.py >= 95%
- [ ] Real MCP integration test (optional, requires Docker)

---

### Priority 3: Nice-to-Have (5-7 hours)

#### Task 3.1: Observability Exporter Tests
**Module**: `src/investigator_agent/observability/exporter.py`
**Lines**: 29 lines untested (69% uncovered)
**Current Coverage**: 31%
**Target Coverage**: 80%
**Effort**: 2-3 hours
**Tests to Add**: 6-8

```python
# src/investigator_agent/observability/exporter_test.py
def test_file_span_exporter_export_single_span(tmp_path):
    """Test exporting a single span."""
    exporter = FileSpanExporter(traces_dir=str(tmp_path))

    span = create_mock_span(
        name="test_operation",
        trace_id="trace_123",
        span_id="span_456"
    )

    result = exporter.export([span])

    assert result == SpanExportResult.SUCCESS

    # Verify file created
    trace_file = tmp_path / "trace_123.json"
    assert trace_file.exists()

def test_file_span_exporter_export_multiple_spans_same_trace(tmp_path):
    """Test exporting multiple spans for same trace."""
    exporter = FileSpanExporter(traces_dir=str(tmp_path))

    span1 = create_mock_span(name="op1", trace_id="trace_1", span_id="span_1")
    span2 = create_mock_span(name="op2", trace_id="trace_1", span_id="span_2")

    exporter.export([span1])
    exporter.export([span2])

    # Should have single file with both spans
    trace_file = tmp_path / "trace_1.json"
    data = json.loads(trace_file.read_text())

    assert len(data["spans"]) == 2

def test_file_span_exporter_shutdown():
    """Test shutdown flushes pending spans."""
    exporter = FileSpanExporter()

    # Add spans
    exporter.export([create_mock_span()])

    # Shutdown should succeed
    result = exporter.shutdown()
    assert result is True

# ... 3-5 more tests
```

**Acceptance Criteria**:
- [ ] 6-8 tests passing
- [ ] Coverage on exporter.py >= 80%

---

#### Task 3.2: Graphiti Integration Test
**Module**: `graphiti/graphiti_mcp_server.py`
**Current Testing**: Syntax validation only
**Effort**: 3-4 hours (requires Docker setup)
**Tests to Add**: 5-7

```python
# graphiti/test_integration.py
@pytest.mark.integration
@pytest.mark.asyncio
async def test_graphiti_server_starts():
    """Test Graphiti server starts and responds."""
    # Requires: docker-compose up neo4j graphiti-mcp

    client = MCPClient(server_url="http://localhost:8000/sse")
    await client.connect()

    tools = await client.list_tools()
    assert "graphiti_add_episode" in [t.name for t in tools]

    await client.disconnect()

@pytest.mark.integration
@pytest.mark.asyncio
async def test_graphiti_add_and_search_episode():
    """Test adding and searching episodes."""
    client = MCPClient(server_url="http://localhost:8000/sse")
    await client.connect()

    # Add episode
    await client.call_tool("graphiti_add_episode", {
        "content": "Feature FEAT-001 is ready for production",
        "metadata": {"feature_id": "FEAT-001"}
    })

    # Search
    results = await client.call_tool("graphiti_search", {
        "query": "FEAT-001 ready",
        "limit": 5
    })

    assert "FEAT-001" in results

    await client.disconnect()

# ... 3-5 more integration tests
```

**Acceptance Criteria**:
- [ ] Integration tests passing with Docker
- [ ] CI configured to run integration tests (optional)
- [ ] Docker Compose verified working

---

## Summary

### Total Effort: 17-23 hours

| Priority | Tasks | Tests | Effort |
|----------|-------|-------|--------|
| P1 | Evaluation + Flaky test | 26-31 | 5-7h |
| P2 | Memory + MCP TODOs | 20-22 | 7-9h |
| P3 | Observability + Graphiti | 11-15 | 5-7h |

### Coverage Progression

| After Phase | Coverage | Change |
|-------------|----------|--------|
| Current | 75% | - |
| Phase 1 | 85% | +10% |
| Phase 2 | 88% | +3% |
| Phase 3 | 90% | +2% |

### Implementation Order

**Week 1**:
1. Day 1-2: Task 1.1 (Evaluation tests)
2. Day 2: Task 1.2 (Fix flaky test)
3. Day 3: Task 2.1 (Memory tests)

**Week 2**:
4. Day 4-5: Task 2.2 (MCP TODOs)
5. Day 6: Task 3.1 (Observability)
6. Day 7: Task 3.2 (Graphiti integration) - Optional

---

## Appendix: Test Utilities

### Mock Helpers

```python
# tests/conftest.py additions

@pytest.fixture
def mock_memory_store():
    """Mock memory store for testing."""
    class MockMemoryStore:
        def __init__(self):
            self.memories = []

        def store(self, memory):
            self.memories.append(memory)
            return memory.id

        def retrieve(self, **kwargs):
            return self.memories

    return MockMemoryStore()

@pytest.fixture
def sample_memory():
    """Sample memory for testing."""
    return Memory(
        id="mem_test",
        feature_id="FEAT-TEST-001",
        decision="ready",
        justification="Test passed",
        key_findings={"test": "data"},
        timestamp=datetime.now()
    )
```
