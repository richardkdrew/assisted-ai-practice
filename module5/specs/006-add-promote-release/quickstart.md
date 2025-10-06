# Quickstart: Promote Release Tool Integration

**Feature**: 006-add-promote-release
**Created**: 2025-10-05
**Purpose**: End-to-end integration examples and usage scenarios for the promote-release tool

## Prerequisites

1. **MCP Server Running**: `make dev` or `make run` in stdio-mcp-server directory
2. **DevOps CLI Installed**: `../acme-devops-cli/devops-cli` must be executable
3. **MCP Inspector** (for testing): `npx @modelcontextprotocol/inspector stdio-mcp-server`

## Quick Reference

### Tool Signature

```typescript
promote_release(
  app: string,        // Application name (required, non-empty)
  version: string,    // Version identifier (required, non-empty)
  from_env: string,   // Source environment (required: dev|staging|uat|prod)
  to_env: string      // Target environment (required: dev|staging|uat|prod)
) → PromotionResult
```

### Valid Promotion Paths

```
dev → staging
staging → uat
uat → prod
```

**No skipping, no backward promotion allowed.**

## Integration Scenarios

### Scenario 1: Standard Non-Production Promotion (dev → staging)

**Use Case**: Promote a tested feature from development to staging

**MCP Request** (JSON-RPC 2.0):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "promote_release",
    "arguments": {
      "app": "web-api",
      "version": "1.2.3",
      "from_env": "dev",
      "to_env": "staging"
    }
  }
}
```

**Expected Response** (Success):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\"status\": \"success\", \"promotion\": {\"app\": \"web-api\", \"version\": \"1.2.3\", \"from_env\": \"dev\", \"to_env\": \"staging\", \"cli_output\": \"Deployment successful: web-api v1.2.3 promoted to staging\\nRollout completed in 25s\", \"cli_stderr\": \"\", \"execution_time_seconds\": 27.5}, \"production_deployment\": false, \"timestamp\": \"2025-10-05T14:30:00.123Z\"}"
    }]
  }
}
```

**Logs (stderr)**:
```
2025-10-05 14:29:32 - stdio-mcp-server - INFO - Executing DevOps CLI: promote web-api 1.2.3 dev staging
2025-10-05 14:30:00 - stdio-mcp-server - DEBUG - CLI command completed in 27.50s
```

**Verification**:
1. Check staging environment: `get_deployment_status(application="web-api", environment="staging")`
2. Verify version is "1.2.3" in response

---

### Scenario 2: Production Deployment (uat → prod)

**Use Case**: Promote a validated release to production with enhanced logging

**MCP Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "promote_release",
    "arguments": {
      "app": "mobile-app",
      "version": "2.0.1-beta",
      "from_env": "uat",
      "to_env": "prod"
    }
  }
}
```

**Expected Response** (Success):
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\"status\": \"success\", \"promotion\": {\"app\": \"mobile-app\", \"version\": \"2.0.1-beta\", \"from_env\": \"uat\", \"to_env\": \"prod\", \"cli_output\": \"Production deployment complete: mobile-app v2.0.1-beta\\nHealth checks passed\\nTraffic cutover complete\", \"cli_stderr\": \"\", \"execution_time_seconds\": 145.2}, \"production_deployment\": true, \"timestamp\": \"2025-10-05T15:00:00.456Z\"}"
    }]
  }
}
```

**Logs (stderr) - Enhanced for Production**:
```
2025-10-05 14:57:35 - stdio-mcp-server - WARNING - PRODUCTION DEPLOYMENT: Promoting mobile-app v2.0.1-beta from uat to PRODUCTION
2025-10-05 14:57:35 - stdio-mcp-server - INFO - Production promotion audit trail: app=mobile-app, version=2.0.1-beta, from=uat, timestamp=2025-10-05T14:57:35.123Z, caller=MCP
2025-10-05 14:57:35 - stdio-mcp-server - INFO - Executing DevOps CLI: promote mobile-app 2.0.1-beta uat prod
2025-10-05 15:00:00 - stdio-mcp-server - DEBUG - CLI command completed in 145.20s
```

**Note**: `production_deployment: true` flag in response indicates this was a production deployment.

---

### Scenario 3: Case-Insensitive Environment Normalization

**Use Case**: User provides uppercase environment names; system normalizes to lowercase

**MCP Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "promote_release",
    "arguments": {
      "app": "admin-portal",
      "version": "v3.1.0",
      "from_env": "STAGING",
      "to_env": "UAT"
    }
  }
}
```

**Expected Behavior**:
- Environments normalized to "staging" and "uat"
- CLI receives lowercase: `promote admin-portal v3.1.0 staging uat`
- Response shows normalized values:

```json
{
  "promotion": {
    "from_env": "staging",
    "to_env": "uat"
  }
}
```

---

### Scenario 4: Validation Error - Empty Parameter

**Use Case**: Client provides empty app name; validation fails immediately

**MCP Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "promote_release",
    "arguments": {
      "app": "   ",
      "version": "1.0.0",
      "from_env": "dev",
      "to_env": "staging"
    }
  }
}
```

**Expected Response** (Error):
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "error": {
    "code": -32602,
    "message": "app cannot be empty"
  }
}
```

**Logs (stderr)**:
```
2025-10-05 15:05:00 - stdio-mcp-server - WARNING - Environment validation failed: app cannot be empty
```

**Verification**: No CLI execution occurs (fail-fast)

---

### Scenario 5: Validation Error - Invalid Environment

**Use Case**: Client provides invalid environment name

**MCP Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "promote_release",
    "arguments": {
      "app": "web-api",
      "version": "1.0.0",
      "from_env": "development",
      "to_env": "staging"
    }
  }
}
```

**Expected Response** (Error):
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "error": {
    "code": -32602,
    "message": "Invalid environment: development. Must be one of: dev, staging, uat, prod"
  }
}
```

**Verification**: Error message lists all valid environment options for self-correction

---

### Scenario 6: Validation Error - Invalid Promotion Path (Skipping)

**Use Case**: Client attempts to skip staging environment (dev → uat)

**MCP Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tools/call",
  "params": {
    "name": "promote_release",
    "arguments": {
      "app": "web-api",
      "version": "1.0.0",
      "from_env": "dev",
      "to_env": "uat"
    }
  }
}
```

**Expected Response** (Error):
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "error": {
    "code": -32602,
    "message": "invalid promotion path: dev→uat (valid next environment from dev: staging)"
  }
}
```

**Verification**: Error message indicates correct next environment

---

### Scenario 7: Validation Error - Backward Promotion

**Use Case**: Client attempts backward promotion (prod → staging)

**MCP Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "tools/call",
  "params": {
    "name": "promote_release",
    "arguments": {
      "app": "web-api",
      "version": "1.0.0",
      "from_env": "prod",
      "to_env": "staging"
    }
  }
}
```

**Expected Response** (Error):
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "error": {
    "code": -32602,
    "message": "invalid promotion path: prod→staging (backward or invalid promotion not allowed)"
  }
}
```

---

### Scenario 8: CLI Execution Failure - Version Not Found

**Use Case**: Version doesn't exist in source environment; CLI returns error

**MCP Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "method": "tools/call",
  "params": {
    "name": "promote_release",
    "arguments": {
      "app": "web-api",
      "version": "9.9.9",
      "from_env": "dev",
      "to_env": "staging"
    }
  }
}
```

**Expected Response** (Error):
```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "error": {
    "code": -32000,
    "message": "Promotion failed: Error: Version 9.9.9 not found in dev environment"
  }
}
```

**Logs (stderr)**:
```
2025-10-05 15:10:00 - stdio-mcp-server - INFO - Executing DevOps CLI: promote web-api 9.9.9 dev staging
2025-10-05 15:10:02 - stdio-mcp-server - WARNING - CLI stderr: Error: Version 9.9.9 not found in dev environment
2025-10-05 15:10:02 - stdio-mcp-server - ERROR - Promotion failed: Error: Version 9.9.9 not found in dev environment
```

**Verification**: CLI error message is included in MCP error response for user debugging

---

### Scenario 9: CLI Timeout (Long-Running Deployment)

**Use Case**: Deployment exceeds 300-second timeout

**MCP Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 9,
  "method": "tools/call",
  "params": {
    "name": "promote_release",
    "arguments": {
      "app": "slow-app",
      "version": "1.0.0",
      "from_env": "dev",
      "to_env": "staging"
    }
  }
}
```

**Expected Response** (Error after 300s):
```json
{
  "jsonrpc": "2.0",
  "id": 9,
  "error": {
    "code": -32000,
    "message": "Promotion operation timed out after 300 seconds. The deployment may still be in progress. Check deployment status manually."
  }
}
```

**Logs (stderr)**:
```
2025-10-05 15:15:00 - stdio-mcp-server - INFO - Executing DevOps CLI: promote slow-app 1.0.0 dev staging
2025-10-05 15:20:00 - stdio-mcp-server - ERROR - Promotion timed out after 300s: slow-app v1.0.0 dev→staging
```

**User Action**: Check deployment status with `get_deployment_status(application="slow-app", environment="staging")` to verify if deployment eventually completed.

---

## Testing with MCP Inspector

### Manual Test Session

1. **Start MCP Inspector**:
   ```bash
   cd stdio-mcp-server
   make dev
   ```

2. **Open Inspector UI** in browser (URL provided in terminal)

3. **Select promote_release tool** from tools list

4. **Test Valid Promotion**:
   - app: "web-api"
   - version: "1.0.0"
   - from_env: "dev"
   - to_env: "staging"
   - **Expected**: Success response with `production_deployment: false`

5. **Test Production Deployment**:
   - app: "web-api"
   - version: "1.0.0"
   - from_env: "uat"
   - to_env: "prod"
   - **Expected**: Success with `production_deployment: true` and WARNING logs

6. **Test Validation Errors**:
   - Empty app: app="", version="1.0.0", from_env="dev", to_env="staging"
     - **Expected**: Error "app cannot be empty"
   - Invalid env: app="test", version="1.0.0", from_env="test", to_env="staging"
     - **Expected**: Error listing valid environments
   - Invalid path: app="test", version="1.0.0", from_env="dev", to_env="prod"
     - **Expected**: Error "invalid promotion path: dev→prod"

---

## Client Integration Examples

### Python Client (using MCP SDK)

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def promote_to_staging(app: str, version: str):
    """Promote an app version from dev to staging."""
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "stdio-mcp-server.src.server"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "promote_release",
                arguments={
                    "app": app,
                    "version": version,
                    "from_env": "dev",
                    "to_env": "staging"
                }
            )

            if result.content[0].text:
                import json
                data = json.loads(result.content[0].text)
                print(f"Promotion status: {data['status']}")
                print(f"Execution time: {data['promotion']['execution_time_seconds']}s")

# Usage
await promote_to_staging("web-api", "1.2.3")
```

### TypeScript Client

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function promoteRelease(
  app: string,
  version: string,
  fromEnv: string,
  toEnv: string
) {
  const transport = new StdioClientTransport({
    command: "uv",
    args: ["run", "python", "-m", "stdio-mcp-server.src.server"]
  });

  const client = new Client({
    name: "promotion-client",
    version: "1.0.0"
  }, {
    capabilities: {}
  });

  await client.connect(transport);

  const result = await client.callTool({
    name: "promote_release",
    arguments: { app, version, from_env: fromEnv, to_env: toEnv }
  });

  const data = JSON.parse(result.content[0].text);

  if (data.production_deployment) {
    console.warn("🚨 Production deployment completed!");
  }

  return data;
}

// Usage
await promoteRelease("web-api", "1.2.3", "uat", "prod");
```

---

## Common Patterns

### Pattern 1: Sequential Promotion Pipeline

Promote through entire pipeline (dev → staging → uat → prod):

```python
async def full_pipeline_promotion(app: str, version: str):
    """Promote through entire pipeline with verification at each stage."""
    stages = [
        ("dev", "staging"),
        ("staging", "uat"),
        ("uat", "prod"),
    ]

    for from_env, to_env in stages:
        print(f"Promoting {app} v{version}: {from_env} → {to_env}")

        result = await session.call_tool(
            "promote_release",
            arguments={
                "app": app,
                "version": version,
                "from_env": from_env,
                "to_env": to_env
            }
        )

        data = json.loads(result.content[0].text)

        if data["status"] != "success":
            raise RuntimeError(f"Promotion failed at {from_env}→{to_env}")

        # Wait for verification before next stage
        await verify_deployment(app, version, to_env)

        print(f"✅ {to_env} deployment verified")

    print("🎉 Full pipeline promotion complete!")
```

### Pattern 2: Rollback Workflow (Manual)

If promotion fails, promote previous stable version:

```python
async def rollback_to_stable(app: str, stable_version: str, target_env: str):
    """Rollback to a known stable version by re-promoting."""
    # Determine source environment (one level below target)
    source_map = {"staging": "dev", "uat": "staging", "prod": "uat"}
    from_env = source_map.get(target_env)

    if not from_env:
        raise ValueError(f"Cannot rollback to {target_env}")

    print(f"Rolling back {app} in {target_env} to {stable_version}")

    result = await session.call_tool(
        "promote_release",
        arguments={
            "app": app,
            "version": stable_version,
            "from_env": from_env,
            "to_env": target_env
        }
    )

    data = json.loads(result.content[0].text)
    if data["status"] == "success":
        print(f"✅ Rollback complete: {app} v{stable_version} in {target_env}")
    else:
        raise RuntimeError("Rollback failed")
```

---

## Troubleshooting

### Issue: "CLI tool not found"

**Symptom**: Error message indicating devops-cli not found

**Solution**:
1. Verify CLI exists: `ls -la ../acme-devops-cli/devops-cli`
2. Check executable permission: `chmod +x ../acme-devops-cli/devops-cli`
3. Verify path in server.py line 133 matches your CLI location

### Issue: Timeout on all promotions

**Symptom**: All promotions timeout after 300s

**Solution**:
1. Check if devops-cli is actually executing: `./acme-devops-cli/devops-cli status`
2. Review stderr logs for subprocess errors
3. If deployments legitimately take >300s, consider requesting timeout increase in future spec update

### Issue: Production deployments not logging warnings

**Symptom**: No WARNING logs for production deployments

**Solution**:
1. Check logging level: Ensure `logging.basicConfig(level=logging.INFO)` or lower
2. Verify stderr output is being captured (check terminal where MCP server runs)
3. Confirm `to_env == "prod"` (case-sensitive check in code)

---

## Next Steps

1. **Implement Tests**: See [contracts/validation.schema.json](contracts/validation.schema.json) for test cases
2. **Implement Validation Functions**: Add to `stdio-mcp-server/src/validation.py`
3. **Implement promote_release Tool**: Add to `stdio-mcp-server/src/server.py`
4. **Manual Testing**: Use MCP Inspector to verify all scenarios
5. **Integration Testing**: Build client workflows using patterns above

---

**Ready for Implementation**: All integration scenarios documented and testable.
