"""DocuMind AI — FastAPI Application Entrypoint."""

import time
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import Any

import structlog
import uvicorn
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse

from documind import __version__
from documind.api.whatsapp_webhook import router as whatsapp_router
from documind.config.logging import configure_logging
from documind.config.settings import get_settings

_LATENCY_MS_MULTIPLIER = 1000
_LATENCY_MS_PRECISION = 2


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle events."""
    settings = get_settings()
    configure_logging(settings.app_log_level)
    app_logger = structlog.get_logger("documind.lifecycle")
    app_logger.info(
        "DocuMind AI service starting up",
        version=__version__,
        env=settings.app_env,
        host=settings.app_host,
        port=settings.app_port,
    )
    yield
    app_logger.info("DocuMind AI service shutting down")


def create_app() -> FastAPI:
    """Factory creating and configuring the FastAPI application instance."""
    app = FastAPI(
        title="DocuMind AI",
        version=__version__,
        description="WhatsApp Document Assistant powered by Microsoft Azure and RAG",
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def logging_middleware(request: Request, call_next: Callable[[Request], Any]) -> Response:
        start_time = time.perf_counter()
        http_logger = structlog.get_logger("documind.http")
        try:
            response: Response = await call_next(request)
            latency_ms = round(
                (time.perf_counter() - start_time) * _LATENCY_MS_MULTIPLIER,
                _LATENCY_MS_PRECISION,
            )
            http_logger.info(
                "HTTP request processed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                latency_ms=latency_ms,
            )
            return response
        except Exception as exc:
            latency_ms = round(
                (time.perf_counter() - start_time) * _LATENCY_MS_MULTIPLIER,
                _LATENCY_MS_PRECISION,
            )
            http_logger.error(
                "Unhandled HTTP exception during request",
                method=request.method,
                path=request.url.path,
                latency_ms=latency_ms,
                error=str(exc),
            )
            raise

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        error_logger = structlog.get_logger("documind.errors")
        error_logger.error(
            "Unhandled internal server exception", path=request.url.path, exc_info=exc
        )
        settings = get_settings()
        content: dict[str, Any] = {
            "error": "InternalServerError",
            "message": "An unexpected error occurred while processing the request.",
        }
        if settings.app_env == "dev":
            content["detail"] = str(exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=content,
        )

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        """Health check endpoint for container probes and load balancers."""
        return {"status": "ok", "version": __version__}

    app.include_router(whatsapp_router)

    return app


app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "documind.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "dev",
    )
