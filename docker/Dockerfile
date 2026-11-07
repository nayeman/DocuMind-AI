# Build with: docker build -f docker/Dockerfile .

# Stage 1: Builder
FROM python:3.13-slim AS builder

WORKDIR /app

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy lockfile + spec for reproducible installs
COPY pyproject.toml uv.lock ./

# Create virtual environment and install production dependencies
ENV UV_PROJECT_ENVIRONMENT="/app/.venv"
RUN uv venv /app/.venv && uv pip install --no-cache -r pyproject.toml --require-hashes

# Stage 2: Runtime
FROM python:3.13-slim AS runtime

WORKDIR /app

# Create non-root user
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m -s /bin/bash appuser

# Copy virtual environment and application code
COPY --from=builder /app/.venv /app/.venv
COPY src /app/src

# Configure environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Change ownership to appuser
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Health check using standard Python library
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "documind.main:app", "--host", "0.0.0.0", "--port", "8000"]
