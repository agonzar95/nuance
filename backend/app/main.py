"""Nuance Backend - Executive Function Prosthetic API."""

import uuid
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.logging_config import (
    bind_request_context,
    clear_request_context,
    configure_logging,
    get_logger,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler for startup/shutdown."""
    # Startup
    configure_logging()
    logger = get_logger(__name__)
    logger.info(
        "Application starting",
        environment=settings.environment,
        version="0.1.0",
    )
    yield
    # Shutdown
    logger.info("Application shutting down")


app = FastAPI(
    title="Nuance API",
    description="Executive Function Prosthetic for neurodivergent users",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
origins = settings.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    """Middleware to add request ID to logging context."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Bind request context for all logs within this request
    bind_request_context(request_id=request_id)

    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        clear_request_context()


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint returning welcome message."""
    return {"message": "Executive Function Prosthetic API"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
