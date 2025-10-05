# Prompt for your AI Assistant

I need to create an MCP server using HTTP communication that will consume a REST API. Help me set up a basic project structure in the `http-mcp-server` folder for a [Python] MCP server.

## Requirements

- Use the official MCP libraries for my chosen language (FastMCP)
- Create a basic server that can handle MCP protocol messages
- Include proper error handling and logging
- Set up the project with `[uv]` for dependency management
- Include HTTP client capabilities (httpx for Python)
- Do not expose any tools, resources, or prompts from the server yet, they will be added in a future phase
- Use Docker - compose at the top most level and Dockerfile at the project level to run the MCP server
- Use Makefile to control all apsects of the dev experience
- Use a sinagle file architecture to start with, we will refine laer if needs be

Please create an implementation plan in `IMPLEMENTATION_PLAN.md` for the initial project structure and a minimal server that can start up and handle basic MCP protocol handshake but without any tools, resources, or prompts yet.

Expected Outcome:

- Project directory with proper structure
- Basic MCP server that can start without errors
- Package configuration file (package.json, pyproject.toml, etc.)
- HTTP client library properly configured
- The server isn't exposing any tools, resources, or prompts yet
