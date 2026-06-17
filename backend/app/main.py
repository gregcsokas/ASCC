import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator, Awaitable, Callable

from fastapi import FastAPI, APIRouter
from starlette.requests import Request
from starlette.responses import Response
from tortoise.contrib.fastapi import tortoise_exception_handlers

import app.core.logging_config
from app.accidents.routers import router as accidents_router
from app.core.database import register_orm
from app.core.version import get_version

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifespan event handler."""
    async with register_orm(app):
        yield

app = FastAPI(
    title="ASCC",
    description="Aviation Safety Coding Challenge",
    version=get_version(),
    lifespan=lifespan,
    exception_handlers=tortoise_exception_handlers()
)

@app.middleware("http")
async def log_request(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """Middleware to log incoming requests."""
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start_time
    client = request.client
    client_addr = f"{client.host}:{client.port}" if client else "-"
    logger.info(
        f"{client_addr} - {request.method} {request.url.path} "
        f"Status: {response.status_code} Process time: {process_time:.4f}s"
    )
    return response

app.include_router(accidents_router, prefix="/api")

@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": get_version()
    }