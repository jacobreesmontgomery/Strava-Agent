"""Session management routes."""

from fastapi import APIRouter, HTTPException, status, Depends
from logging import getLogger

from setup.dependencies import get_session_service
from services.session_service import SessionService

logger = getLogger(__name__)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("/create")
async def create_session(
    session_service: SessionService = Depends(get_session_service),
) -> dict:
    """
    Create a new session.

    Args:
        session_service: Session service dependency

    Returns:
        dict: New session ID and details
    """
    try:
        session_id = session_service.create_session()
        return {
            "session_id": session_id,
            "message": "Session created successfully",
        }
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session",
        )


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
) -> dict:
    """
    Retrieve session details.

    Args:
        session_id: The session ID to retrieve
        session_service: Session service dependency

    Returns:
        dict: Session details and history

    Raises:
        HTTPException: If session not found
    """
    try:
        history = session_service.get_session_history(session_id=session_id)
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found",
            )
        return history
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session",
        )


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
) -> dict:
    """
    Delete a session.

    Args:
        session_id: The session ID to delete
        session_service: Session service dependency

    Returns:
        dict: Confirmation message

    Raises:
        HTTPException: If session not found
    """
    try:
        cleared = session_service.clear_session(session_id=session_id)
        if not cleared:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found",
            )
        return {"message": f"Session {session_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session",
        )


@router.get("")
async def list_sessions(
    session_service: SessionService = Depends(get_session_service),
) -> dict:
    """
    List all active sessions.

    Args:
        session_service: Session service dependency

    Returns:
        dict: List of active sessions
    """
    try:
        sessions = session_service.list_sessions()
        return {
            "sessions": sessions,
            "count": len(sessions),
        }
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list sessions",
        )
