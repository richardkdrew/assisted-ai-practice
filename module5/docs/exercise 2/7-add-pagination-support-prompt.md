# Prompt for your AI assistant

I need to add pagination support to my tools that return large datasets, specifically `get-deployment-status` and `get-log-entries`.

The API supports pagination with `limit` and `offset` parameters. I want to:

- Add `limit` and `offset` parameters to relevant tools
- Provide clear feedback about pagination in responses
- Handle pagination metadata from API responses
- Include appropriate defaults (e.g., limit=50)

Please create a detailed implementation plan for adding pagination support with good user experience. Purge all contents from the `IMPLEMENTATION-PLAN.md` file and reuse it for this new plan.

## Expected Outcome

- Tools with pagination support
- Clear pagination feedback in responses
- Good default values for pagination
