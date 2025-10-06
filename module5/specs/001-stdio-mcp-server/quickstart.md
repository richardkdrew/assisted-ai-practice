# Quickstart: STDIO MCP Server

**Feature**: 001-stdio-mcp-server
**Date**: 2025-10-04
**Purpose**: Manual testing procedure to verify all acceptance criteria

---

## Prerequisites

- Python 3.11+ installed
- UV installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Repository cloned and on branch `001-stdio-mcp-server`

---

## Setup

### Step 1: Install Dependencies

```bash
cd module5
make install
```

**Expected Output**:
```
cd stdio-mcp-server && uv sync
Resolved X packages in Yms
Installed Z packages in Zms
```

**Verification**:
- No errors during dependency installation
- `stdio-mcp-server/.venv/` directory created
- MCP SDK installed (check with `uv pip list`)

---

## Test Scenario 1: Server Initialization

**Acceptance Criteria**: AS-1 - Server initializes successfully when started by client

### Step 1.1: Start MCP Inspector

```bash
make dev
```

**Expected Output** (stderr):
```
2025-10-04 12:00:00 - root - INFO - Starting MCP server
2025-10-04 12:00:00 - root - INFO - Server ready to accept connections
```

**Expected Behavior**:
- MCP Inspector opens in web browser
- Server process starts without errors
- Logs appear in stderr (terminal output)

### Step 1.2: Verify Inspector Connection

**Expected in Browser**:
- Inspector UI loads successfully
- Connection status: "Connected"
- Server listed as available

✅ **PASS**: Server initialized and ready
❌ **FAIL**: Document errors and check stderr logs

---

## Test Scenario 2: Protocol Handshake

**Acceptance Criteria**: AS-2 - Server completes initialization handshake

### Step 2.1: Send Initialize Request

In MCP Inspector:
1. Click "Initialize" or send initialize message
2. Observe request/response

**Expected Request** (displayed in Inspector):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "mcp-inspector",
      "version": "1.0.0"
    }
  }
}
```

**Expected Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {},
      "resources": {},
      "prompts": {}
    },
    "serverInfo": {
      "name": "stdio-mcp-server",
      "version": "0.1.0"
    }
  }
}
```

**Expected Logs** (stderr):
```
INFO - Received initialize request from client: mcp-inspector
INFO - Sending initialization response
```

✅ **PASS**: Handshake completed, capabilities empty as expected
❌ **FAIL**: Check response format against contract in `contracts/initialize.json`

---

## Test Scenario 3: Message Processing

**Acceptance Criteria**: AS-3 - Server processes valid JSON-RPC messages

### Step 3.1: Verify Message Round-Trip

Using Inspector, send any valid request (if supported) or observe initialize message handling.

**Verification Points**:
- Request appears in Inspector sent messages
- Response appears in Inspector received messages
- Request ID matches response ID
- No errors in stderr logs

✅ **PASS**: Messages processed correctly
❌ **FAIL**: Check for protocol violations or crashes

---

## Test Scenario 4: Error Handling

**Acceptance Criteria**: AS-4 - Server handles errors gracefully without crashing

### Step 4.1: Send Malformed JSON

In Inspector (if possible) or via manual stdin test:
```
echo '{"invalid json' | uv run python -m src.server
```

**Expected Response**:
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "error": {
    "code": -32700,
    "message": "Parse error"
  }
}
```

**Expected Logs** (stderr):
```
ERROR - JSON parse error: Expecting value: line 1 column 1 (char 0)
```

**Verification**:
- Server did NOT crash
- Error response matches contract in `contracts/error-response.json`
- Error logged to stderr

✅ **PASS**: Error handled gracefully
❌ **FAIL**: If server crashed, check error handling implementation

### Step 4.2: Send Invalid Method

In Inspector, attempt to call non-existent method:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "nonexistent_method",
  "params": {}
}
```

**Expected Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "error": {
    "code": -32601,
    "message": "Method not found"
  }
}
```

✅ **PASS**: Unknown method rejected properly
❌ **FAIL**: Check method routing logic

---

## Test Scenario 5: Graceful Shutdown

**Acceptance Criteria**: AS-5 - Server shuts down cleanly on SIGINT/SIGTERM

### Step 5.1: Interrupt Server

With Inspector running, press `CTRL+C` in terminal.

**Expected Logs** (stderr):
```
INFO - Received signal 2, initiating shutdown
INFO - Closing streams
INFO - Server stopped
```

**Expected Behavior**:
- Server exits within 2 seconds
- No error messages during shutdown
- Exit code: 0 (check with `echo $?`)

✅ **PASS**: Clean shutdown
❌ **FAIL**: If hangs or errors, check signal handling

---

## Test Scenario 6: MCP Inspector Full Integration

**Acceptance Criteria**: AS-6 - Inspector successfully connects and displays server info

### Step 6.1: Full Inspector Test

1. Run `make dev`
2. Verify all Inspector panels:
   - **Server Info**: Shows "stdio-mcp-server" v0.1.0
   - **Capabilities**: Shows empty tools, resources, prompts
   - **Connection**: Status "Connected"

3. Try multiple initialize/request cycles
4. Verify no memory leaks (repeated requests don't grow logs excessively)

✅ **PASS**: Full integration working
❌ **FAIL**: Document specific Inspector issues

---

## Test Scenario 7: Claude Desktop Configuration

**Acceptance Criteria**: AS-7 - Server configurable via .mcp.json for Claude Desktop

### Step 7.1: Verify Configuration File

Check `.mcp.json` in repository root:
```json
{
  "mcpServers": {
    "stdio-server": {
      "command": "uv",
      "args": [
        "--directory",
        "module5/stdio-mcp-server",
        "run",
        "python",
        "-m",
        "src.server"
      ]
    }
  }
}
```

**Verification**:
- File exists at repository root
- Command points to UV
- Args correctly reference server module
- Server name is "stdio-server"

### Step 7.2: Test Launch via .mcp.json (Manual)

If Claude Desktop is installed:
1. Copy .mcp.json to Claude Desktop config location
2. Restart Claude Desktop
3. Verify server appears in MCP servers list
4. Test connection

✅ **PASS**: Configuration valid
⚠️ **SKIP**: If Claude Desktop not available, verify JSON syntax only

---

## Success Criteria Summary

All scenarios must pass for feature acceptance:

- [x] **AS-1**: Server initializes successfully
- [x] **AS-2**: Handshake completes with correct response
- [x] **AS-3**: Messages processed via stdin/stdout
- [x] **AS-4**: Errors handled without crashes
- [x] **AS-5**: Graceful shutdown on signals
- [x] **AS-6**: MCP Inspector integration works
- [x] **AS-7**: .mcp.json configuration valid

---

## Troubleshooting

### Server Won't Start

```bash
# Check Python version
python3 --version  # Should be 3.11+

# Check UV installation
uv --version

# Reinstall dependencies
cd stdio-mcp-server
uv sync --reinstall
```

### No Logs Appearing

- Verify logs go to stderr (not stdout)
- Check log level configuration
- Try running with DEBUG level

### Inspector Can't Connect

- Verify server is actually running
- Check for port conflicts
- Try restarting Inspector

### JSON Parse Errors

- Verify message format against contracts/
- Check for trailing newlines or malformed JSON
- Use JSON validator before sending

---

## Next Steps After Quickstart

Once all scenarios pass:
1. Commit the working implementation
2. Update README.md with usage instructions
3. Consider adding automated tests (pytest)
4. Plan next feature phase (tools, resources, or prompts)

---

**Test Date**: _____________
**Tester**: _____________
**Result**: ✅ PASS / ❌ FAIL
**Notes**: _____________
