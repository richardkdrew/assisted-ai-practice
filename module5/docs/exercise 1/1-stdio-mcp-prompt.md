# Prompt for your AI Assistant

I need to create an MCP server using stdio communication. Help me set up a basic project structure in the `acme-devops-mcp` folder for a [Python] MCP server.

## Requirements

- Use the official MCP libraries for my chosen language (FastMCP)
- Create a basic server that can handle MCP protocol messages
- Include proper error handling and logging
- Set up the project with `[uv]` for dependency management
- Do not expose any tools, resources, or prompts from the server yet, they will be added in a future phase
- Ignore the `http_server` folder and do NOT alter it
- Use Docker - compose at teh top most level adn Dockerfile at the project level to run the MCP server
- Use Makefile to control all apsects of the dev experience

Please create an implementation plan in `IMPLEMENTATION_PLAN.md` for the initial project structure for a minimal server that can start up and handle basic MCP protocol handshake. We will implement the plan once we've finished collaborating on the plan.

## Expected Outcome

- Project directory with proper structure
- Basic MCP server that can start without errors
- Package configuration file (package.json, pyproject.toml, etc.)
- The server isn't exposing any tools, resources, or prompts yet