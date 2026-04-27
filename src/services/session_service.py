"""Session management service."""

from typing import Optional, Any
from logging import getLogger
from uuid import uuid4
from datetime import datetime, timezone

from models.sessions import SessionContext, Message

logger = getLogger(__name__)


class SessionService:
    """Service for managing user sessions and conversation history."""

    def __init__(self):
        """Initialize the session service."""
        self.sessions: dict[str, SessionContext] = {}

    def create_session(self) -> str:
        """
        Create a new session.

        Returns:
            str: The new session ID
        """
        session_id = uuid4().hex
        self.sessions[session_id] = SessionContext(
            session_id=session_id,
            messages=[],
        )
        logger.info(f"Created new session: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[SessionContext]:
        """
        Retrieve a session by ID.

        Args:
            session_id (str): The session ID to retrieve

        Returns:
            Optional[SessionContext]: Session data or None if not found
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.last_accessed = self._get_timestamp()
            return session
        return None

    def add_message(self, session_id: str, query: str, response: str) -> bool:
        """
        Add a message to a session.

        Args:
            session_id (str): The session ID
            query (str): The user's query
            response (str): The agent's response

        Returns:
            bool: True if successful, False if session not found
        """
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return False

        session = self.sessions[session_id]
        timestamp = self._get_timestamp()
        session.messages.append(
            Message(
                query=query,
                response=response,
                timestamp=timestamp,
            )
        )
        session.last_accessed = timestamp
        return True

    def get_session_history(self, session_id: str) -> Optional[dict[str, Any]]:
        """
        Get complete session history.

        Args:
            session_id (str): The session ID

        Returns:
            Optional[dict]: Session history or None if not found
        """
        session = self.get_session(session_id=session_id)
        if not session:
            return None

        return {
            "session_id": session.session_id,
            "messages": [msg.model_dump() for msg in session.messages],
            "created_at": session.created_at,
            "last_accessed": session.last_accessed,
            "message_count": len(session.messages),
        }

    def clear_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id (str): The session ID to delete

        Returns:
            bool: True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session: {session_id}")
            return True
        logger.warning(f"Session {session_id} not found for clearing")
        return False

    def list_sessions(self) -> list[dict[str, Any]]:
        """
        List all active sessions.

        Returns:
            list: Summary of all sessions
        """
        return [
            {
                "session_id": session.session_id,
                "message_count": len(session.messages),
                "created_at": session.created_at,
                "last_accessed": session.last_accessed,
            }
            for session in self.sessions.values()
        ]

    def get_session_context(self, session_id: str) -> Optional[SessionContext]:
        """
        Get session context for coaching request processing.

        Args:
            session_id (str): The session ID

        Returns:
            Optional[SessionContext]: Session context with messages or None if not found
        """
        return self.get_session(session_id=session_id)

    @staticmethod
    def _get_timestamp() -> str:
        """
        Get current timestamp.

        Returns:
            str: ISO format timestamp
        """
        return datetime.now(timezone.utc).isoformat()
