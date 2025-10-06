# Prompt for your AI assistant

I need to implement my first MCP tool that makes HTTP requests to the REST API. Let's start with `get-deployment-status` which should call:
`GET http://localhost:8000/api/v1/deployments`

This implementation should include:

- A robust HTTP client wrapper function for making API calls safely
- The `get-deployment-status` MCP tool that uses this wrapper
- Proper error handling and timeout management
- JSON parsing of API responses
- Parameter validation (application and environment parameters are optional for now)

Please create an implementation plan that includes both the HTTP client wrapper and the first tool so I can test that everything works together. Purge all contents from the `IMPLEMENTATION_PLAN.md` file and reuse it for this new plan.

## Testing

- Make sure the API server is running: ./acme-devops-api/api-server
- Test with MCP Inspector: npx @modelcontextprotocol/inspector python acme-devops-mcp/http_server/main.py
- Call get-deployment-status with no parameters to get all deployments
- Verify you get JSON data back from the API
- Test error handling by stopping the API server

## Expected Outcome

- Working HTTP client function
- Working get-deployment-status tool that you can test immediately
- Proper error handling and JSON parsing
