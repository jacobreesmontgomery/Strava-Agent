"""Pydantic models for coaching agent requests and responses."""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Any


class CoachingRequestModel(BaseModel):
    """Model for incoming coaching requests."""

    query: str = Field(
        description="The coaching question or topic the user wants to discuss",
        min_length=1,
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session ID for maintaining conversation context",
    )


class CoachingResponseModel(BaseModel):
    """Model for coaching agent responses."""

    response: str = Field(description="The coaching advice or response from the agent")
    session_id: Optional[str] = Field(
        default=None, description="Session ID for tracking the conversation"
    )
    metadata: Optional[dict[str, Any]] = Field(
        default=None, description="Additional metadata about the response"
    )


class ErrorResponseModel(BaseModel):
    """Model for error responses."""

    detail: str = Field(description="Error message")
    error_code: Optional[str] = Field(
        default=None, description="Error code for client-side handling"
    )


class Message(BaseModel):
    """Model for individual conversation messages."""

    query: str = Field(description="User's query")
    response: str = Field(description="Agent's response")
    timestamp: str = Field(description="Message timestamp")
