from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.message import SenderType


class MessageCreate(BaseModel):
    conversation_id: UUID
    sender_type: SenderType
    text: str = Field(min_length=1)
    external_message_id: str | None = Field(default=None, max_length=255)
    external_event_id: str | None = Field(default=None, max_length=255)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    external_message_id: str | None
    external_event_id: str | None
    conversation_id: UUID
    sender_type: SenderType
    text: str
    created_at: datetime
