"""Routes for the coaching agent API."""

from fastapi import APIRouter, HTTPException, status, Depends
from logging import getLogger

from models.coaching import CoachingRequestModel, CoachingResponseModel
from services.coaching_agent_service import CoachingAgentService
from setup.dependencies import get_coaching_agent_service

logger = getLogger(__name__)

router = APIRouter(prefix="/api/coaching", tags=["coaching"])


@router.post(
    "/ask",
    response_model=CoachingResponseModel,
)
async def ask_coaching_agent(
    request: CoachingRequestModel,
    coaching_service: CoachingAgentService = Depends(get_coaching_agent_service),
) -> CoachingResponseModel:
    """
    Ask the coaching agent a question.

    Args:
        request: The coaching request with query and optional session_id
        coaching_service: Coaching agent service dependency

    Returns:
        CoachingResponseModel: The agent's coaching response

    Raises:
        HTTPException: If request processing fails
    """
    try:
        response = await coaching_service.process_coaching_request(request=request)
        return response
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error processing coaching request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process coaching request",
        )


@router.post("/health")
async def health_check(
    coaching_service: CoachingAgentService = Depends(get_coaching_agent_service),
) -> dict:
    """
    Health check endpoint for the coaching agent.

    Args:
        coaching_service: Coaching agent service dependency

    Returns:
        dict: Health status
    """
    try:
        # Verify agent is initialized
        if coaching_service.agent:
            return {"status": "healthy", "message": "Coaching agent is ready"}
        else:
            return {"status": "unhealthy", "message": "Coaching agent not initialized"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed",
        )
