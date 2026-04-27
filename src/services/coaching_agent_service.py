"""Service layer for the coaching agent."""

from typing import Optional
from logging import getLogger
from coaching_agent import CoachingAgent
from models.coaching import (
    CoachingRequestModel,
    CoachingResponseModel,
)
from models.sessions import SessionContext
from services.session_service import SessionService
from utils.langchain import get_final_response

logger = getLogger(__name__)


class CoachingAgentService:
    """Service class for handling coaching agent logic and orchestration."""

    def __init__(self, session_service: Optional[SessionService] = None):
        """Initialize the coaching agent service with a CoachingAgent instance.

        Args:
            session_service: Optional SessionService instance for managing sessions
        """
        try:
            self.agent = CoachingAgent()
        except Exception as e:
            logger.error(f"Failed to initialize CoachingAgent: {e}")
            raise

        self.session_service = session_service or SessionService()

    async def process_coaching_request(
        self, request: CoachingRequestModel
    ) -> CoachingResponseModel:
        """
        Process a coaching request through the agent and return a response.

        Args:
            request (CoachingRequestModel): The incoming coaching request

        Returns:
            CoachingResponseModel: The coaching agent's response

        Raises:
            Exception: If agent invocation fails
        """
        try:
            if request.session_id:
                session_id = request.session_id
                session_context = self.session_service.get_session_context(
                    session_id=session_id
                )
                if not session_context:
                    logger.warning(f"Session {session_id} not found, creating new")
                    session_id = self.session_service.create_session()
                    session_context = self._create_empty_session_context(
                        session_id=session_id
                    )
            else:
                session_id = self.session_service.create_session()
                session_context = self._create_empty_session_context(
                    session_id=session_id
                )

            logger.info(f"Processing coaching request for session: {session_id}")
            response = await self._ainvoke_agent(
                query=request.query, session_context=session_context
            )

            self.session_service.add_message(
                session_id=session_id, query=request.query, response=response
            )
            updated_context = self.session_service.get_session_context(
                session_id=session_id
            )

            coaching_response = CoachingResponseModel(
                response=response,
                session_id=session_id,
                metadata={
                    "session_active": True,
                    "message_count": (
                        len(updated_context.messages) if updated_context else 0
                    ),
                },
            )

            logger.info(f"Successfully processed request for session: {session_id}")
            return coaching_response

        except Exception as e:
            logger.error(f"Error processing coaching request: {e}")
            raise

    async def _ainvoke_agent(self, query: str, session_context: SessionContext) -> str:
        """
        Invoke the coaching agent with the query.

        Args:
            query (str): The user's coaching question
            session_context (SessionContext): Session context with conversation history

        Returns:
            str: The agent's response
        """
        try:
            enhanced_query = (
                self._build_context_aware_query(
                    query=query, session_context=session_context
                )
                if session_context.messages
                else query
            )

            response = await self.agent.ainvoke(query=enhanced_query)

            return get_final_response(response=response)
        except Exception as e:
            logger.error(f"Error invoking agent: {e}")
            raise

    def _build_context_aware_query(
        self, query: str, session_context: SessionContext
    ) -> str:
        """
        Build a context-aware query using previous messages.

        Args:
            query (str): The current query
            session_context (SessionContext): Session context with message history

        Returns:
            str: Enhanced query with context
        """
        context_summary = f"Previous messages: {len(session_context.messages)}\n"
        for i, msg in enumerate(session_context.messages[-3:], 1):
            context_summary += f"{i}. User asked: {msg.query[:50]}...\n"

        return f"{context_summary}\nCurrent question: {query}"

    def _create_empty_session_context(self, session_id: str) -> SessionContext:
        """
        Create an empty session context with current timestamp.

        Args:
            session_id (str): The session ID

        Returns:
            SessionContext: Empty session context
        """
        return SessionContext(
            session_id=session_id,
            messages=[],
        )
