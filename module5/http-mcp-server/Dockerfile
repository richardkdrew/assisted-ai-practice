FROM python:3.11-slim

WORKDIR /app

# Install UV package manager
RUN pip install --no-cache-dir uv

# Copy project files
COPY . .

# Install dependencies
RUN uv sync

# Expose port (if needed for HTTP transport)
EXPOSE 3000

# Run server
CMD ["uv", "run", "python", "server.py"]
