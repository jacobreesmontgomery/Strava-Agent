from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .coaching import Message


class SessionContext(BaseModel):
    """Model for managing session context and conversation history."""

    session_id: str = Field(description="Unique session identifier")
    messages: list[Message] = Field(
        default_factory=list, description="Conversation history"
    )
    created_at: Optional[str] = Field(
        default=None, description="Session creation timestamp"
    )
    last_accessed: Optional[str] = Field(
        default=None, description="Last access timestamp"
    )

    @field_validator("created_at", "last_accessed", mode="before")
    @classmethod
    def set_default_timestamps(cls, v: Optional[str]) -> str:
        """Set current timestamp if not provided."""
        if v is None:
            return datetime.now().isoformat()
        return v
