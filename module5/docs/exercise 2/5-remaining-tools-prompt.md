# Prompt for your AI assistant:

Now that I have a working HTTP client wrapper and one tool, I'd like to implement the remaining core tools:

1. `get-performance-metrics` - calls `GET /api/v1/metrics` with optional application, environment, and time_range parameters
2. `check-environment-health` - calls `GET /api/v1/health` with optional environment and application parameters
3. `get-log-entries` - calls `GET /api/v1/logs` with optional application, environment, level, and limit parameters

Each tool should:

- Use the same HTTP client wrapper we created
- Validate input parameters appropriately
- Handle and report errors consistently
- Pass query parameters correctly to the API

Please create an implementation plan for these three additional tools. Purge all contents from the `IMPLEMENTATION_PLAN.md` file and reuse it for this new plan.

