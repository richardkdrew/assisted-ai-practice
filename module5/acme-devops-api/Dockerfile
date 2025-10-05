FROM python:3.13-slim

WORKDIR /app

# Install UV package manager
RUN pip install --no-cache-dir uv

# Copy project files
COPY . .

# Install dependencies
RUN uv sync

# Expose port for API
EXPOSE 8000

# Run API server
CMD ["uv", "run", "python", "app.py"]
