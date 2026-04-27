"""FastAPI server setup for the Coaching Agent application."""

from uvicorn import run
from logging import basicConfig, getLogger, INFO
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.coaching import router as coaching_router
from routes.sessions import router as session_router
from setup.dependencies import init_services

basicConfig(
    level=INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle events."""
    logger.info("Coaching Agent API starting up...")
    try:
        init_services()
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

    yield

    logger.info("Coaching Agent API shutting down...")


app = FastAPI(
    title="Coaching Agent API",
    description="API for interacting with an AI-powered coaching agent",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(coaching_router)
app.include_router(session_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the Coaching Agent API",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
