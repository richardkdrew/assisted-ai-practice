# Dockerfile for STDIO MCP Server
# Multi-stage build for minimal final image

# Stage 1: Builder
FROM python:3.11-slim AS builder

# Install UV package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY .python-version .
COPY src/ src/

# Install dependencies (creates .venv)
RUN uv sync --frozen

# Stage 2: Runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy UV and virtual environment from builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Set environment to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Health check (simple Python import check)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import src.server; print('OK')" || exit 1

# Run the server
# Note: STDIO servers read from stdin, write to stdout
# Docker will connect these to container I/O
CMD ["python", "-m", "src.server"]
