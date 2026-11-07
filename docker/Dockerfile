# Build with: docker build -f docker/Dockerfile .

# Stage 1: Builder
FROM python:3.13-slim AS builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy lockfile + spec para installs reproducibles desde uv.lock
COPY pyproject.toml uv.lock ./

# Instalar solo dependencias de producción usando el lockfile (hashes incluidos)
RUN uv sync --frozen --no-dev --no-install-project

# Stage 2: Runtime
FROM python:3.13-slim AS runtime

WORKDIR /app

# Install uv en runtime (para poder ejecutar uvicorn desde el venv)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create non-root user
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m -s /bin/bash appuser

# Copiar el venv del builder y el código fuente
COPY --from=builder /app/.venv /app/.venv
COPY src /app/src

# Configure environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT="/app/.venv"

# Change ownership to appuser
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Health check using standard Python library
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "documind.main:app", "--host", "0.0.0.0", "--port", "8000"]
