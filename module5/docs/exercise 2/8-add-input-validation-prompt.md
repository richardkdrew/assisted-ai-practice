# Prompt for your AI assistant:

I want to add some input validation to my MCP server for better user experience and defense-in-depth security.

Let's focus on environment name validation as a key pattern:

1. Validate environment names against known environments (dev, staging, prod, etc.) before making API calls
2. Provide immediate feedback without HTTP request overhead
3. Show how MCP validation differs from API validation

This demonstrates validation at the MCP layer while the API handles comprehensive business logic validation.

Please create an implementation plan for environment validation that shows this pattern clearly. Purge all contents from the `IMPLEMENTATION-PLAN.md` file and reuse it for this new plan.

**Learning Note**: While the API already handles comprehensive validation, adding validation at the MCP layer teaches important patterns:

- Defense in Depth: Real systems validate at multiple layers
- User Experience: Immediate feedback without HTTP request overhead
- Error Handling: Different error types require different handling approaches

Expected Outcome:

- Understanding of multi-layer validation patterns
- Improved user experience with immediate feedback
- Clear distinction between MCP and API validation roles
