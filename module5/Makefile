# Makefile for STDIO MCP Server
# Provides convenient commands for common operations
# Per Constitution: MUST use make commands for all development tasks

.PHONY: install dev run lint format clean help test docker-build docker-up docker-down docker-logs docker-test docker-inspector docker-clean

STDIO_SERVER_DIR = stdio-mcp-server

help: ## Display this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Development Commands (UV-based)
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

# Docker Commands (Recommended for Production)
docker-build: ## Build Docker image for MCP server
	docker-compose build mcp-server

docker-up: ## Start MCP server in Docker (detached)
	docker-compose up -d mcp-server

docker-down: ## Stop and remove MCP server container
	docker-compose down

docker-logs: ## View MCP server logs (follow mode)
	docker-compose logs -f mcp-server

docker-test: ## Run server in Docker with MCP Inspector
	docker-compose --profile inspector up -d
	@echo "MCP Inspector available at http://localhost:5173"

docker-inspector: docker-test ## Alias for docker-test

docker-clean: ## Stop containers and remove images
	docker-compose down --rmi all --volumes --remove-orphans

docker-interactive: ## Run MCP server in Docker interactive mode (STDIO)
	docker-compose run --rm mcp-server
