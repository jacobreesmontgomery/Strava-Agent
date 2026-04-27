"""Setup module for dependency injection and service initialization."""

from logging import getLogger
from typing import Optional
from services.coaching_agent_service import CoachingAgentService
from services.session_service import SessionService

logger = getLogger(__name__)

# Singleton instances
_coaching_agent_service: Optional[CoachingAgentService] = None
_session_service: Optional[SessionService] = None


def init_services():
    """Initialize all services."""
    global _coaching_agent_service, _session_service

    try:
        logger.info("Initializing services...")
        _session_service = SessionService()
        _coaching_agent_service = CoachingAgentService()
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise


def get_coaching_agent_service() -> CoachingAgentService:
    """
    Get the CoachingAgentService instance (FastAPI dependency).

    Returns:
        CoachingAgentService: The service instance

    Raises:
        RuntimeError: If services not initialized
    """
    if _coaching_agent_service is None:
        raise RuntimeError("Services not initialized. Call init_services() first.")
    return _coaching_agent_service


def get_session_service() -> SessionService:
    """
    Get the SessionService instance (FastAPI dependency).

    Returns:
        SessionService: The service instance

    Raises:
        RuntimeError: If services not initialized
    """
    if _session_service is None:
        raise RuntimeError("Services not initialized. Call init_services() first.")
    return _session_service
