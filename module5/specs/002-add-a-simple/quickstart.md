# Quickstart: Ping Tool

**Feature**: 002-add-a-simple
**Purpose**: Verify the ping tool implementation works correctly

## Prerequisites

- MCP server running with ping tool registered
- MCP client configured (Claude Desktop or MCP Inspector)
- Docker (if using docker-based server)

## Test Scenarios

### Scenario 1: Basic Ping Test

**Objective**: Verify ping tool responds with correct format

**Steps**:
1. Start the MCP server:
   ```bash
   make dev  # or make docker-test for Docker
   ```

2. In MCP Inspector, call the ping tool:
   ```json
   {
     "method": "tools/call",
     "params": {
       "name": "ping",
       "arguments": {
         "message": "test"
       }
     }
   }
   ```

3. **Expected Result**:
   ```json
   {
     "content": [
       {
         "type": "text",
         "text": "Pong: test"
       }
     ]
   }
   ```

**Success Criteria**: ✅ Response contains "Pong: test"

### Scenario 2: Empty Message

**Objective**: Verify empty strings are handled correctly

**Steps**:
1. Call ping tool with empty message:
   ```json
   {
     "method": "tools/call",
     "params": {
       "name": "ping",
       "arguments": {
         "message": ""
       }
     }
   }
   ```

2. **Expected Result**:
   ```json
   {
     "content": [
       {
         "type": "text",
         "text": "Pong: "
       }
     ]
   }
   ```

**Success Criteria**: ✅ Response contains "Pong: " (with space after colon)

### Scenario 3: Special Characters

**Objective**: Verify Unicode and special characters are preserved

**Steps**:
1. Call ping tool with special characters:
   ```json
   {
     "method": "tools/call",
     "params": {
       "name": "ping",
       "arguments": {
         "message": "Hello! @#$% 世界"
       }
     }
   }
   ```

2. **Expected Result**:
   ```json
   {
     "content": [
       {
         "type": "text",
         "text": "Pong: Hello! @#$% 世界"
       }
     ]
   }
   ```

**Success Criteria**: ✅ All characters preserved exactly

### Scenario 4: Invalid Input - Missing Parameter

**Objective**: Verify proper error handling for missing parameters

**Steps**:
1. Call ping tool without message parameter:
   ```json
   {
     "method": "tools/call",
     "params": {
       "name": "ping",
       "arguments": {}
     }
   }
   ```

2. **Expected Result**:
   ```json
   {
     "error": {
       "code": -32602,
       "message": "Invalid params"
     }
   }
   ```

**Success Criteria**: ✅ Returns JSON-RPC error with code -32602

### Scenario 5: Invalid Input - Wrong Type

**Objective**: Verify type validation works

**Steps**:
1. Call ping tool with number instead of string:
   ```json
   {
     "method": "tools/call",
     "params": {
       "name": "ping",
       "arguments": {
         "message": 123
       }
     }
   }
   ```

2. **Expected Result**:
   ```json
   {
     "error": {
       "code": -32602,
       "message": "Invalid params"
     }
   }
   ```

**Success Criteria**: ✅ Returns JSON-RPC error with code -32602

## Running Automated Tests

```bash
# Run all tests
make test

# Run only ping tool tests
make test ARGS="-k test_ping"
```

**Expected Output**:
```
tests/test_ping_tool.py::test_ping_basic PASSED
tests/test_ping_tool.py::test_ping_empty PASSED
tests/test_ping_tool.py::test_ping_special_chars PASSED
tests/test_ping_tool.py::test_ping_missing_param PASSED
tests/test_ping_tool.py::test_ping_invalid_type PASSED

===== 5 passed in 0.5s =====
```

## Verification Checklist

- [ ] Ping tool appears in server capabilities list
- [ ] Basic ping test returns "Pong: {message}"
- [ ] Empty string returns "Pong: "
- [ ] Special characters are preserved
- [ ] Missing parameter returns validation error
- [ ] Invalid type returns validation error
- [ ] All automated tests pass

## Troubleshooting

**Tool not found**:
- Check tool is decorated with `@mcp.tool()` in server.py
- Verify server restarted after code changes

**Validation errors not working**:
- Ensure type hint is `message: str` not `message`
- Verify FastMCP version is >= 2.0.0

**Unicode characters corrupted**:
- Check Python version is 3.11+ (UTF-8 by default)
- Verify stdout encoding is UTF-8

---

**Total Test Time**: ~2 minutes
**Automation Level**: Fully automated via pytest
