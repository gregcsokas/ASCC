import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator, Awaitable, Callable

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

import app.core.logging_config
from app.core.version import get_version

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifespan event handler."""
    yield

app = FastAPI(
    title="ASCC",
    description="Aviation Safety Coding Challenge",
    version=get_version(),
    lifespan=lifespan
)

@app.middleware("http")
async def log_request(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """Middleware to log incoming requests."""
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} Status: {response.status_code} Process time: {process_time:.4f}s")
    return response

@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": get_version()
    }