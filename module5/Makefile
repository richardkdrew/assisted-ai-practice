# Makefile for STDIO MCP Server
# Provides convenient commands for common operations

.PHONY: install dev run lint format clean help test

STDIO_SERVER_DIR = stdio-mcp-server

help: ## Display this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies via UV
	cd $(STDIO_SERVER_DIR) && uv sync

dev: ## Run MCP Inspector for interactive testing
	cd $(STDIO_SERVER_DIR) && uv run mcp dev src/server.py

run: ## Run the server directly (for production use)
	cd $(STDIO_SERVER_DIR) && uv run python -m src.server

test: ## Run all tests with pytest
	cd $(STDIO_SERVER_DIR) && uv run pytest tests/ -v

lint: ## Run code quality checks (future: add ruff)
	@echo "Linting not yet configured"

format: ## Format code (future: add ruff format)
	@echo "Formatting not yet configured"

clean: ## Clean up build artifacts and caches
	find $(STDIO_SERVER_DIR) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find $(STDIO_SERVER_DIR) -type f -name "*.pyc" -delete 2>/dev/null || true
	find $(STDIO_SERVER_DIR) -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find $(STDIO_SERVER_DIR) -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf $(STDIO_SERVER_DIR)/dist 2>/dev/null || true
