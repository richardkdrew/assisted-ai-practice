# Makefile for MCP Servers (STDIO and HTTP)
# Provides convenient commands for common operations
# Per Constitution: MUST use make commands for all development tasks

.PHONY: install dev run lint format clean help test inspector docker-build docker-up docker-down docker-logs docker-test docker-inspector docker-clean
.PHONY: http-install http-run http-docker-build http-docker-up http-docker-down http-clean http-help api-up api-down kill-ports

STDIO_SERVER_DIR = stdio-mcp-server
HTTP_SERVER_DIR = http-mcp-server

help: ## Display this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

kill-ports: ## Kill processes on common development ports (3001, 5173, 6274, 6277, 8000, 5000)
	@echo "Killing processes on common development ports..."
	@echo "Checking port 3001 (FastMCP Inspector)..."
	@lsof -ti:3001 | xargs kill -9 2>/dev/null || echo "  No process on port 3001"
	@echo "Checking port 5173 (MCP Inspector)..."
	@lsof -ti:5173 | xargs kill -9 2>/dev/null || echo "  No process on port 5173"
	@echo "Checking port 6274 (MCP Inspector UI)..."
	@lsof -ti:6274 | xargs kill -9 2>/dev/null || echo "  No process on port 6274"
	@echo "Checking port 6277 (MCP Proxy Server)..."
	@lsof -ti:6277 | xargs kill -9 2>/dev/null || echo "  No process on port 6277"
	@echo "Checking port 8000 (FastAPI/DevOps API)..."
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "  No process on port 8000"
	@echo "Checking port 5000 (Flask API)..."
	@lsof -ti:5000 | xargs kill -9 2>/dev/null || echo "  No process on port 5000"
	@echo "Port cleanup complete!"

start-docker: ## Start Docker Desktop (macOS)
	@echo "Starting Docker Desktop..."
	@open -a Docker || echo "Docker Desktop not found. Please install Docker Desktop or start it manually."
	@echo "Waiting for Docker to start..."
	@sleep 10
	@docker info >/dev/null 2>&1 && echo "Docker is running!" || echo "Docker may still be starting. Please wait and try again."

http-dev-local: ## Run HTTP MCP server with local API (no Docker required)
	@echo "Starting local acme-devops-api with uv..."
	@cd acme-devops-api && uv run python app.py &
	@echo "Waiting for local API to be ready..."
	@sleep 3
	@echo "Starting HTTP MCP server with FastMCP Inspector..."
	@echo "FastMCP Inspector will be available at http://localhost:3001"
	@echo "Local API available at http://localhost:8000"
	cd $(HTTP_SERVER_DIR) && uv run fastmcp dev server.py

# Development Commands (UV-based)
install: ## Install dependencies via UV
	cd $(STDIO_SERVER_DIR) && uv sync

dev: ## Run FastMCP Inspector for interactive testing
	cd $(STDIO_SERVER_DIR) && uv run fastmcp dev src/server.py

inspector: ## Run MCP Inspector with npx (works better than dev)
	npx @modelcontextprotocol/inspector uv --directory $(STDIO_SERVER_DIR) run python -m src.server

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
	docker-compose run --rm stdio-mcp-server

# HTTP MCP Server Commands
http-install: ## Install HTTP MCP server dependencies
	@echo "Installing HTTP MCP server dependencies..."
	cd $(HTTP_SERVER_DIR) && uv sync

http-run: ## Run HTTP MCP server directly (development)
	@echo "Starting HTTP MCP server..."
	cd $(HTTP_SERVER_DIR) && uv run python server.py

http-dev: ## Run HTTP MCP server with FastMCP Inspector (includes API dependency)
	@echo "Starting acme-devops-api dependency..."
	@make api-up
	@echo "Waiting for API to be ready..."
	@sleep 5
	@echo "Starting HTTP MCP server with FastMCP Inspector..."
	@echo "FastMCP Inspector will be available at http://localhost:3001"
	cd $(HTTP_SERVER_DIR) && uv run fastmcp dev server.py

http-docker-build: ## Build HTTP MCP server Docker image
	@echo "Building HTTP MCP server Docker image..."
	docker-compose build http-mcp-server

http-docker-up: ## Start HTTP MCP server with Docker Compose (includes API dependency)
	@echo "Starting HTTP MCP server with dependencies..."
	docker-compose up -d acme-devops-api http-mcp-server

http-docker-down: ## Stop HTTP MCP server Docker container
	@echo "Stopping HTTP MCP server..."
	docker-compose stop http-mcp-server

http-clean: ## Clean HTTP MCP server artifacts
	@echo "Cleaning HTTP MCP server artifacts..."
	find $(HTTP_SERVER_DIR) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find $(HTTP_SERVER_DIR) -type f -name "*.pyc" -delete 2>/dev/null || true
	find $(HTTP_SERVER_DIR) -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find $(HTTP_SERVER_DIR) -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf $(HTTP_SERVER_DIR)/dist 2>/dev/null || true

http-help: ## Show HTTP MCP server help
	@echo "HTTP MCP Server Commands:"
	@echo "  http-install      - Install dependencies"
	@echo "  http-run          - Run server directly"
	@echo "  http-dev          - Run with MCP Inspector (includes API)"
	@echo "  http-docker-build - Build Docker image"
	@echo "  http-docker-up    - Start with Docker"
	@echo "  http-docker-down  - Stop Docker container"
	@echo "  http-clean        - Clean artifacts"

# acme-devops-api Commands
api-up: ## Start acme-devops-api for HTTP MCP server
	@echo "Starting acme-devops-api..."
	docker-compose up -d acme-devops-api

api-down: ## Stop acme-devops-api
	@echo "Stopping acme-devops-api..."
	docker-compose stop acme-devops-api

# Combined Commands
all-up: ## Start all services (STDIO MCP, HTTP MCP, and API)
	@echo "Starting all services..."
	docker-compose up -d

all-down: ## Stop all services
	@echo "Stopping all services..."
	docker-compose down

all-clean: clean http-clean ## Clean all artifacts
	@echo "All artifacts cleaned"
