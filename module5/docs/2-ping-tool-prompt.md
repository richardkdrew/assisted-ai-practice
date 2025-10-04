**Prompt for your AI assistant:**
```
Now I need to add a simple "ping" tool to my MCP server in `stdio_server` to test connectivity.

The ping tool should:
- Accept a "message" parameter (string)
- Return a response like "Pong: {message}" 
- Be properly registered with the MCP server
- Include appropriate input schema validation

Please create an implementation plan for adding this ping tool. Purge all contents from the `IMPLEMENTATION_PLAN.md` file and reuse it for this new plan.
```

**Expected Outcome:**
- Working ping tool that responds to MCP tool calls
- Proper tool registration and schema definition
- You can wait to verify this is all working until the next step